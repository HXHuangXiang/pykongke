# Repository Notes

This project is an asyncio-based LAN client for Konke smart devices. It sends encrypted UDP commands to devices on port `27431` and listens for encrypted UDP responses on the same socket.

## Runtime Shape

- `pykonkeio/socket.py` owns UDP send/receive state. The socket is created lazily on first use, and receiver callbacks are registered before outgoing command packets are sent to avoid missing fast LAN responses.
- `pykonkeio/manager.py` handles discovery and device instance caching. Devices are cached by `(ip, device_type)` so the same IP can be represented as different explicit models when needed.
- `pykonkeio/device/` contains device models. Most switch-like devices inherit from `BaseToggle`; power strips inherit from `BaseMul`; K2 and MiniK add IR/RF behavior through mixins.
- `pykonkeio/mixin/ir.py` and `pykonkeio/mixin/rf.py` implement learn/emit/remove flows over the `uart` action type.

## Development

Install test dependencies:

```bash
python -m pip install -e ".[test]"
```

Run tests:

```bash
python -m pytest -q -s
```

The tests use UDP sockets and may need a non-sandboxed environment. Mock devices live under `mock/` and emulate LAN responses for the pytest suite.

## Manual Device Checks

Example commands against a real MiniK:

```bash
python -m pykonkeio get_status minik 172.17.30.221
python -m pykonkeio turn_on minik 172.17.30.221
python -m pykonkeio turn_off minik 172.17.30.221
```

## Maintenance Notes

- Public action names are CLI-facing and use 1-based socket indexes, such as `turn_on_socket2`; internal device methods use 0-based indexes.
- Keep receiver registration before UDP sends in search and command flows.
- `loop` parameters remain in some public signatures for compatibility, but runtime code should use the current running loop.
- RF single-key removal currently sends `operate#3035#delete#group#id`; comments suggest `deletekey`. Confirm with a real device or protocol trace before changing this command.
