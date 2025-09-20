import aio_pika
import json


class RabbitMQClient:
    def __init__(self, amqp_url: str, queue_name: str):
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None
        self.queue: aio_pika.Queue | None = None

    async def connect(self):
        """Создание соединения и канала"""
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)

    async def send(self, payload: dict):
        """Отправка сообщения в очередь"""
        if not self.channel:
            raise RuntimeError("RabbitMQ connection is not initialized")

        message = aio_pika.Message(body=json.dumps(payload).encode())
        await self.channel.default_exchange.publish(
            message, routing_key=self.queue_name
        )

    async def close(self):
        """Закрыть соединение"""
        if self.connection:
            await self.connection.close()
