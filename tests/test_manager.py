from pykongke import manager
from pykongke.device.basetoggle import BaseToggle
from pykongke.device.k1 import K1
from pykongke.device.k2 import K2


def test_get_device_cache_uses_ip_and_device_type():
    ip = '1.2.3.4'

    default_device = manager.get_device(ip)
    k1_device = manager.get_device(ip, 'k1')
    k2_device = manager.get_device(ip, 'k2')

    assert isinstance(default_device, BaseToggle)
    assert isinstance(k1_device, K1)
    assert isinstance(k2_device, K2)
    assert manager.get_device(ip) is default_device
    assert manager.get_device(ip, 'k1') is k1_device
    assert manager.get_device(ip, 'k2') is k2_device
    assert default_device is not k1_device
    assert k1_device is not k2_device
