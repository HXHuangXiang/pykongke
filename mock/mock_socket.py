import socket
import logging
import asyncio
import math
from pykongke import utils

_PORT = 27431

_LOGGER = logging.getLogger('mock_socket')


class Socket(object):
    def __init__(self, callback):
        self._sock = None
        self._callback = callback
        self._task = None
        self._loop = None

    def send(self, address, mac, password, action, action_type, msg_type='lan_device'):
        cmd = '%s%%%s%%%s%%%s%%%s' % (msg_type, mac, password, action, action_type)
        if not action or not action:
            cmd = ''
        message = utils.encrypt(cmd)
        self._sock.sendto(message, address)
        _LOGGER.debug('send %s %s', address[0], cmd or '(empty)')

    def _handle_message(self):
        message, address = self._sock.recvfrom(256)
        message = utils.decrypt(message)
        _LOGGER.debug('receive %s %s %s', *address, message or '(empty)')

        device, *data = message.split('%')

        if len(data) < 4 or device != 'lan_phone':
            _LOGGER.error('incorrect request %s', message)
        else:
            self._callback(address, *data)

    async def _do_receive(self):
        try:
            await asyncio.sleep(math.inf)
        except asyncio.CancelledError:
            pass

    def open(self, loop=None):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('0.0.0.0', _PORT))
        self._sock.setblocking(False)
        self._loop = loop or asyncio.get_running_loop()
        self._loop.add_reader(self._sock.fileno(), self._handle_message)
        self._task = asyncio.create_task(self._do_receive())

    def close(self):
        self._task and self._task.cancel()
        if self._loop is not None and self._sock is not None:
            self._loop.remove_reader(self._sock.fileno())
            self._loop = None
        self._sock and self._sock.close()
