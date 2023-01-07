import multiprocessing.dummy
import queue
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from typing import Callable, Dict, Optional, Sequence

import dbt.flags as dbt_flags
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.parser import BaseModel, event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
metrics = Metrics()


class Event(BaseModel):
    dbt_cmd: str
    copy_files: Optional[Dict[str, str]]


class Model(BaseModel):
    model_id: str
    path: str
    status: str
    message: Optional[str]
    execution_time: float


class Result(BaseModel):
    succeeded: bool
    elapsed_time: float
    models: Sequence[Model]


class ThreadedContext:
    """Replace Multiprocessing context with threaded context."""

    Process = threading.Thread
    Lock = threading.Lock
    RLock = threading.RLock
    Queue = queue.Queue


class LoggerWriter:
    log_levels = {
        "[DEBUG]": 10,
        "[INFO]": 20,
        "[WARN]": 30,
        "[ERROR]": 40,
        "[CRITICAL]": 50,
    }

    def __init__(self, logger):
        self.logger = logger

    def write(self, msg):
        if msg and not msg.isspace():
            split_msg = msg.split("\t")
            message = split_msg[-1] if split_msg[-1] != "\n" else None
            level = self.log_levels.get(split_msg[0], 20)
            self.logger.log(level, message)

    def flush(self):
        pass


class CustomThreadPool:
    """
    Override multiprocessing ThreadPool with a ThreadPoolExecutor that doesn't use
    any hared memory semaphore locks
    """

    def __init__(self, num_threads):
        self.pool = ThreadPoolExecutor(max_workers=num_threads)

    def apply_async(self, func, args, callback):
        """Provide the same interface expected by dbt.task.runnable."""

        def future_callback(future):
            result = future.result()
            return callback(result)

        self.pool.submit(func, *args).add_done_callback(future_callback)

    def close(self):
        pass

    def join(self):
        """
        shutdown(wait=True) mimics "join", whereas shutdown(wait=False) mimics
        terminate.
        """
        self.pool.shutdown(wait=True)


def pool_owerride(processes: Optional[int] = None, initializer=None, initargs=()):
    """Helper to privide stame interface as multiprocessing.dummy.Pool"""
    return CustomThreadPool(processes)


def process_results(results, succeeded: str) -> Result:
    models = []
    for result in results.results:
        model = Model(
            model_id=result.node.identifier,
            path=result.node.path,
            status=str(result.status),
            message=result.message,
            execution_time=result.execution_time,
        )
        models.append(model)
    return Result(succeeded=succeeded, elapsed_time=results.elapsed_time, models=models)


@lambda_handler_decorator
def middleware_before(handler, event: dict, context: LambdaContext) -> Callable:
    # Copy files
    copy_files = event.get("copy_files")
    if copy_files:
        for src, tgt in copy_files.items():
            logger.info(f"Copying file {src} to {tgt}.")
            shutil.copyfile(src, tgt)
    # Replace multiprocessing with multithreading
    multiprocessing.dummy.Pool = pool_owerride
    dbt_flags.MP_CONTEXT = ThreadedContext()
    return handler(event, context)


@middleware_before
@event_parser(model=Event)
@logger.inject_lambda_context(log_event=True)
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event: Event, _: LambdaContext) -> dict:
    import dbt.main as dbt_main

    dbt_main.log_manager._file_handler.disabled = True

    try:
        dbt_args = event.dbt_cmd.split()
        with redirect_stdout(LoggerWriter(logger)):  # type: ignore
            results, succeeded = dbt_main.handle_and_check(dbt_args)
    except Exception as e:
        logger.exception(e)
        raise
    body = process_results(results, succeeded)
    metrics.add_metric(
        name="ExecutionTime", unit=MetricUnit.Seconds, value=body.elapsed_time
    )
    status_code = 200 if succeeded else 400
    return {"statusCode": status_code, "body": body.dict()}
