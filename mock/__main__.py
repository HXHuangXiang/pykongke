import logging
import argparse
import sys
import asyncio


async def main():
    parser = argparse.ArgumentParser(prog="pykongke")
    parser.add_argument('device', help='device type')

    args = parser.parse_args()
    device_type = args.device.lower()

    if device_type == 'k1':
        from .mock_k1 import MockK1
        device = MockK1()
    elif device_type == 'k2':
        from .mock_k2 import MockK2
        device = MockK2()
    elif device_type == 'minik':
        from .mock_minik import MockMiniK
        device = MockMiniK()
    elif device_type == 'kbulb':
        from .mock_kbulb import MockKBulb
        device = MockKBulb()
    elif device_type == 'klight':
        from .mock_klight import MockKLight
        device = MockKLight()
    elif device_type == 'micmul':
        from .mock_micmul import MockMicMul
        device = MockMicMul()
    elif device_type == 'mul':
        from .mock_mul import MockMul
        device = MockMul()
    else:
        logging.error('Device not support: %s', device_type)
        return False

    device.start()
    try:
        await asyncio.Future()
    finally:
        device.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        datefmt='%Y/%m/%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(message)s')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
