import pytest
import random
from mock.mock_micmul import MockMicMul
from pykonkeio.device.micmul import MicMul
from pykonkeio import manager as client_manager


@pytest.fixture(scope='module')
def server(device_address, request):
    if not device_address:
        mock_server = MockMicMul()
        request.addfinalizer(lambda: mock_server.stop())
        return mock_server


@pytest.fixture(scope='module')
def client(device_address):
    client_manager.clear_device_info()
    return MicMul(device_address or '127.0.0.1')


# noinspection 801,PyShadowingNames
@pytest.mark.asyncio
async def test_turn_on(server: MockMicMul, client: MicMul):
    if server:
        server.start()

    for i in range(client.socket_count):
        await client.turn_on(i)
        assert client.status[i] == 'open'
        if server:
            assert server.status[i] == 'open'


# noinspection 801,PyShadowingNames
@pytest.mark.asyncio
async def test_turn_off(server: MockMicMul, client: MicMul):
    if server:
        server.start()

    for i in range(client.socket_count):
        await client.turn_off(i)
        assert client.status[i] == 'close'
        if server:
            assert server.status[i] == 'close'


# noinspection 801,PyShadowingNames
@pytest.mark.asyncio
async def test_turn_on_all(server: MockMicMul, client: MicMul):
    if server:
        server.start()

    await client.turn_on_all()
    for i in range(client.socket_count):
        assert client.status[i] == 'open'
        if server:
            assert server.status[i] == 'open'


# noinspection 801,PyShadowingNames
@pytest.mark.asyncio
async def test_turn_off_all(server: MockMicMul, client: MicMul):
    if server:
        server.start()

    await client.turn_off_all()
    for i in range(client.socket_count):
        assert client.status[i] == 'close'
        if server:
            assert server.status[i] == 'close'


# noinspection 801,PyShadowingNames
@pytest.mark.asyncio
async def test_do_socket_actions(client: MicMul, monkeypatch):
    called = []

    async def turn_on(index):
        called.append(('on', index))
        client.status[index] = 'open'

    async def turn_off(index):
        called.append(('off', index))
        client.status[index] = 'close'

    monkeypatch.setattr(client, 'turn_on', turn_on)
    monkeypatch.setattr(client, 'turn_off', turn_off)

    client.status = ['open', 'close', 'close', 'close']
    assert await client.do('get_status1') == 'on'
    assert await client.do('get_status2') == 'off'

    await client.do('turn_on_socket2')
    assert client.status[1] == 'open'

    await client.do('turn_off_socket1')
    assert client.status[0] == 'close'
    assert called == [('on', 1), ('off', 0)]


# noinspection 801,PyShadowingNames
@pytest.mark.asyncio
async def test_update_resets_updating_after_error(client: MicMul, monkeypatch):
    async def raise_error(*_, **__):
        raise RuntimeError('boom')

    monkeypatch.setattr(client, 'send_message', raise_error)

    with pytest.raises(RuntimeError):
        await client.update()

    assert client.is_updating is False


# noinspection 801,PyShadowingNames
@pytest.mark.asyncio
async def test_update(server: MockMicMul, client: MicMul):
    if server:
        server.start()
        server.status = list(['close'] * client.socket_count)
        await client.update()
        assert client.status == server.status

        server.status = list(['open'] * client.socket_count)
        await client.update()
        assert client.status == server.status

        server.status = list(['close'] * client.socket_count)
        await client.update()
        assert client.status == server.status

        server.status = list(random.choice(('open', 'close')) for _ in client.status)
        await client.update()
        assert client.status == server.status

    else:
        await client.turn_off_all()
        await client.update()
        assert client.status == list(['close'] * client.socket_count)

        await client.turn_on_all()
        await client.update()
        assert client.status == list(['open'] * client.socket_count)

        status = ['open'] * client.socket_count
        for i, _ in enumerate(client.status):
            if random.choice((True, False)):
                await client.turn_off(i)
                status[i] = 'close'
        await client.update()
        assert client.status == status

        await client.turn_off_all()
        await client.update()
        assert client.status == list(['close'] * client.socket_count)
