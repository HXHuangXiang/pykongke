import socket
import math
import logging
import asyncio
from . import error
from . import utils

_PORT = 27431

_LOGGER = logging.getLogger(__name__)

_requests = []
_receivers_count = 0
_message_handlers = []
_receive_task = None
_receive_loop = None
_sock = None


def _get_sock():
    global _sock
    if _sock is None:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        _sock.setblocking(False)
    return _sock


def send(ip, mac, password, action, action_type, device_type='lan_phone'):
    address = (ip, _PORT)
    cmd = '%s%%%s%%%s%%%s%%%s' % (device_type, mac, password, action, action_type)
    message = utils.encrypt(cmd)
    _get_sock().sendto(message, address)
    _LOGGER.debug('send %s %s', ip, cmd)


def _handle_message(sock):
    message, (address, _) = sock.recvfrom(256)
    message = utils.decrypt(message)
    _LOGGER.debug('receive %s %s', address, message or '(empty)')

    device, *data = message.split('%')
    if len(data) < 4 or device != 'lan_device':
        return _LOGGER.error('incorrect response %s', message)

    mac, _, _, response_type = data

    for request in _requests:
        if not request['future'].done() and request['mac'] == mac and request['request_type'].startswith(response_type[:-3]):
            request['future'].set_result((address, *data))
            break

    for callback in _message_handlers:
        callback(address, *data)


async def _do_receive(loop=None):
    sock = _get_sock()

    try:
        await asyncio.sleep(math.inf)
    except asyncio.CancelledError:
        pass


async def send_message(params, retry=2, loop=None, **kwargs):
    loop = asyncio.get_running_loop()
    request = {
        'mac': params[1],
        'request_type': params[4],
        'future': loop.create_future()
    }
    _requests.append(request)

    add_receiver(loop=loop)
    send(*params)

    try:
        return await asyncio.wait_for(request['future'], timeout=1)
    except asyncio.TimeoutError:
        if retry > 0:
            return await send_message(params, retry=retry-1, loop=loop)
        raise error.Timeout('connect timeout')
    finally:
        _requests.remove(request)
        remove_receiver()


def add_message_handler(handler, loop=None):
    _message_handlers.append(handler)
    add_receiver(loop=loop)


def remove_message_handler(handler):
    _message_handlers.remove(handler)
    remove_receiver()


def add_receiver(loop=None):
    global _receivers_count, _receive_task, _receive_loop
    if _receivers_count == 0:
        loop = asyncio.get_running_loop()
        sock = _get_sock()
        loop.add_reader(sock.fileno(), _handle_message, sock)
        _receive_loop = loop
        _receive_task = asyncio.create_task(_do_receive(loop=loop))
    _receivers_count += 1


def remove_receiver():
    global _receivers_count, _receive_loop
    if _receivers_count <= 0:
        _receivers_count = 0
        return

    _receivers_count -= 1
    if _receivers_count == 0:
        _receive_task and _receive_task.cancel()
        if _receive_loop is not None and _sock is not None:
            _receive_loop.remove_reader(_sock.fileno())
            _receive_loop = None
