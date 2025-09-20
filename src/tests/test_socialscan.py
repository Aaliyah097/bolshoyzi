import pytest
from executor.me.socialscan import AsyncSocialscan


@pytest.mark.asyncio
async def test_async_socialscan():
    res = await AsyncSocialscan().request('name.boltz@gmail.com')
    print(res)
