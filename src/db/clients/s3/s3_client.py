from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aioboto3  # type: ignore
from botocore.config import Config  # type: ignore
from db.settings.creds import creds


CONFIG = Config(signature_version="s3v4", max_pool_connections=25, retries={"max_attempts": 3})
session = aioboto3.Session()

@asynccontextmanager
async def get_client() -> AsyncGenerator[aioboto3.Session.client, None]:
    async with session.client(
        "s3",
        endpoint_url=creds.S3_ENDPOINT,
        aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY,
        config=CONFIG,
    ) as client:
        yield client
