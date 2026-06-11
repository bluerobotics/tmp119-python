"""Shared pytest fixtures.

The tests run without hardware by substituting a fake ``smbus`` module for the
real one. The fake is injected into ``sys.modules`` here, before ``tmp119`` is
imported anywhere, so the library's top-level ``import smbus`` resolves to this
in-memory stand-in instead of a physical I2C bus.
"""

import sys
import types

import pytest


class FakeSMBus:
    """In-memory stand-in for ``smbus.SMBus`` used for hardware-free testing.

    Registers are stored big-endian as ``[msb, lsb]``, matching how the TMP119
    transfers its 16-bit registers over I2C. Tests can read/modify ``regs`` to
    simulate device state.
    """

    def __init__(self, bus):
        self.bus = bus
        self.regs = {
            0x00: [0x00, 0x00],  # TEMP
            0x01: [0x02, 0x20],  # CONFIG (power-on default 0x0220)
            0x0F: [0x21, 0x17],  # DEVICE_ID (0x2117)
        }

    def read_i2c_block_data(self, address, register, length):
        return list(self.regs[register])[:length]

    def write_i2c_block_data(self, address, register, data):
        self.regs[register] = list(data)


_fake_smbus = types.ModuleType("smbus")
_fake_smbus.SMBus = FakeSMBus
sys.modules["smbus"] = _fake_smbus


@pytest.fixture
def sensor():
    """A TMP119 backed by a fresh in-memory FakeSMBus."""
    import tmp119
    return tmp119.TMP119()
