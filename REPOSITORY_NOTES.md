# Repository Notes

Original project: `jedmeng/python-konkeio`. This fork keeps GPLv3 licensing and publishes under the new `pykongke` distribution/import/CLI name.

Distribution name: `pykongke`. Current release line: `3.x`. Import package: `pykongke`. CLI command: `pykongke`.

This project is an asyncio-based LAN client for Konke smart devices. It sends encrypted UDP commands to devices on port `27431` and listens for encrypted UDP responses on the same socket.

## Runtime Shape

- `pykongke/socket.py` owns UDP send/receive state. The socket is created lazily on first use, and receiver callbacks are registered before outgoing command packets are sent to avoid missing fast LAN responses.
- `pykongke/manager.py` handles discovery and device instance caching. Devices are cached by `(ip, device_type)` so the same IP can be represented as different explicit models when needed.
- `pykongke/device/` contains device models. Most switch-like devices inherit from `BaseToggle`; power strips inherit from `BaseMul`; K2 and MiniK add IR/RF behavior through mixins.
- `pykongke/mixin/ir.py` and `pykongke/mixin/rf.py` implement learn/emit/remove flows over the `uart` action type.

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
python -m pykongke get_status minik 172.17.30.221
python -m pykongke turn_on minik 172.17.30.221
python -m pykongke turn_off minik 172.17.30.221
```

## Maintenance Notes

- Public action names are CLI-facing and use 1-based socket indexes, such as `turn_on_socket2`; internal device methods use 0-based indexes.
- Keep receiver registration before UDP sends in search and command flows.
- `loop` parameters remain in some public signatures for compatibility, but runtime code should use the current running loop.
- RF single-key removal currently sends `operate#3035#delete#group#id`; comments suggest `deletekey`. Confirm with a real device or protocol trace before changing this command.
