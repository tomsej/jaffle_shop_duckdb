FROM public.ecr.aws/lambda/python:3.9

RUN pip3 install dbt-duckdb[glue] aws-lambda-powertools[parser] pandas

# Folders
COPY macros ${LAMBDA_TASK_ROOT}/macros/
COPY models ${LAMBDA_TASK_ROOT}/models/
COPY seeds ${LAMBDA_TASK_ROOT}/seeds/
COPY tests ${LAMBDA_TASK_ROOT}/tests/
COPY analysis ${LAMBDA_TASK_ROOT}/analysis/
# Files
COPY profiles.yml \
     dbt_project.yml \
     jaffle_shop.duckdb \
     lambda/handler.py ${LAMBDA_TASK_ROOT}

CMD [ "handler.handler" ] 