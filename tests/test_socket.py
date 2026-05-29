import importlib


def test_socket_import_does_not_create_udp_socket():
    import pykonkeio.socket as client_socket

    client_socket = importlib.reload(client_socket)

    assert client_socket._sock is None


def test_socket_send_initializes_udp_socket(monkeypatch):
    import pykonkeio.socket as client_socket

    created = []

    class FakeSocket:
        def setsockopt(self, *args):
            pass

        def setblocking(self, flag):
            pass

        def sendto(self, message, address):
            created.append((message, address))

    def fake_socket(*args):
        created.append(args)
        return FakeSocket()

    monkeypatch.setattr(client_socket.socket, 'socket', fake_socket)
    monkeypatch.setattr(client_socket, '_sock', None)

    client_socket.send('127.0.0.1', 'mac', 'password', 'check', 'relay')

    assert client_socket._sock is not None
    assert created[0] == (client_socket.socket.AF_INET, client_socket.socket.SOCK_DGRAM)
    assert created[1][1] == ('127.0.0.1', 27431)


def test_remove_receiver_does_not_underflow():
    import pykonkeio.socket as client_socket

    client_socket._receivers_count = 0

    client_socket.remove_receiver()

    assert client_socket._receivers_count == 0
