from typing import Any

from aws_cdk import App, Duration, Environment, RemovalPolicy, Stack
from aws_cdk.aws_lambda import DockerImageCode, DockerImageFunction
from aws_cdk.aws_s3 import BlockPublicAccess, Bucket
from constructs import Construct

MEMORY_SIZE = 10240
TIMEOUT_MINUTES = 15
FUNCTION_NAME = "dbt-duckdb"
S3_BUCKET = "dbt-duckdb-jaffle-shop"


class LambdaDbtDuckDBStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a S3 bucket
        s3_instance = Bucket(
            self,
            "dbtDuckDBS3Bucket",
            bucket_name=S3_BUCKET,
            block_public_access=BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True,
            ),
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
            versioned=False,
        )

        # Create Docker Lambda
        fn = DockerImageFunction(
            self,
            "dbtDuckDB",
            function_name=FUNCTION_NAME,
            description="Run dbt-duckdb with AWS lambda.",
            timeout=Duration.minutes(TIMEOUT_MINUTES),
            memory_size=MEMORY_SIZE,
            code=DockerImageCode.from_image_asset(
                directory=".", file="lambda/Dockerfile"
            ),
            retry_attempts=0,
            environment={
                # Wee need to set home to /tmp to be able to install duckdb extensions
                "HOME": "/tmp",
                # For setting where dbt log should be written
                "DBT_ROOT": "/tmp",
                "S3_BUCKET": S3_BUCKET,
                # dbt settings
                "DBT_PROFILES_DIR": "/var/task",
                "DBT_USE_EXPERIMENTAL_PARSER": "true",
                "DBT_PARTIAL_PARSE": "true",
                "DBT_CACHE_SELECTED_ONLY": "true",
                "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
                "DBT_USE_COLORS": "false",
                "DBT_WRITE_JSON": "false",
                "DBT_LOG_FORMAT": "json",
                # Powertools settings
                "POWERTOOLS_SERVICE_NAME": FUNCTION_NAME,
                "POWERTOOLS_METRICS_NAMESPACE": FUNCTION_NAME,
                # Log level
                "LOG_LEVEL": "INFO",
            },
        )

        s3_instance.grant_read_write(identity=fn)


############################### Synth ##############################
# Create CDK application
env_EU = Environment(account="531497945401", region="eu-central-1")
app = App()
lambda_stack = LambdaDbtDuckDBStack(app, "LambdaDbtDuckDBStack", env=env_EU)
app.synth()
