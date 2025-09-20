from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    MONGO_HOST: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_PORT: int
    MONGO_AUTH_SOURCE: str
    MONGO_DB_NAME: str

    @property
    def mongodb_conn_string(self) -> str:
        return f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:{self.MONGO_INITDB_ROOT_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB_NAME}?authSource=admin"


class S3Settings(BaseSettings):
    S3_ENDPOINT: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_BUCKET: str


class TGBotCredentials(BaseSettings):
    TGBOT_API_KEY: str


class PostgresCredentials(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str

    @property
    def pg_conn_string(self) -> str:
        return (
            f"postgresql://:@?dsn=postgresql://:@{self.POSTGRES_HOST}/"
            f"{self.POSTGRES_DB}&port={self.POSTGRES_PORT}&user={self.POSTGRES_USER}&password={self.POSTGRES_PASSWORD}"
        )

    @property
    def async_pg_conn_string(self) -> str:
        return (
            f"postgresql+asyncpg://:@{self.POSTGRES_HOST}/"
            f"{self.POSTGRES_DB}?port={self.POSTGRES_PORT}&user={self.POSTGRES_USER}&password={self.POSTGRES_PASSWORD}"
        )


class RabbitMQCredentials(BaseSettings):
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672

    @property
    def rabbitmq_conn_string(self) -> str:
        return f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"


class Credentials(
    PostgresCredentials, 
    RabbitMQCredentials, 
    TGBotCredentials,
    S3Settings,
    MongoSettings
):
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore'
    )


creds = Credentials()
