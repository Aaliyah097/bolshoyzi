import pytest
from db.clients.rabbit.client import RabbitMQClient
from db.settings.creds import creds
from distributor.user_req import UserReq


@pytest.mark.asyncio
async def test_add_task():
    rabbit = RabbitMQClient(creds.rabbitmq_conn_string, 'tasks')
    await rabbit.connect()
    try:
        user_req = UserReq(user_id=414308039, payload='name.boltz@gmail.com', script_name='my_email')
        await rabbit.send(user_req.model_dump())
    finally:
        await rabbit.close()
