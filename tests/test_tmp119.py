import pytest

import tmp119

# Config register bit masks (mirrors the private constants in the driver)
AVG_MASK = 0x0060
CONV_MASK = 0x0380


def test_device_id(sensor):
    assert sensor.get_device_id() == 0x2117


def test_init_success_clears_avg_and_conv(sensor):
    assert sensor.init() is True
    assert sensor.get_config() & (AVG_MASK | CONV_MASK) == 0


def test_init_preserves_unrelated_config_bits(sensor):
    # Set a bit outside the AVG/CONV masks; init() must leave it untouched.
    sensor._bus.regs[0x01] = [0x82, 0x20]  # 0x8220
    assert sensor.init() is True
    assert sensor.get_config() == 0x8000


def test_init_fails_on_wrong_device_id(sensor):
    sensor._bus.regs[0x0F] = [0x00, 0x00]
    assert sensor.init() is False


def test_init_returns_false_without_bus(sensor):
    sensor._bus = None
    assert sensor.init() is False


def test_read_returns_false_without_bus(sensor):
    sensor._bus = None
    assert sensor.read() is False


def test_read_positive_temperature(sensor):
    sensor._bus.regs[0x00] = [0x0C, 0x80]  # 3200 * 0.0078125 = 25.0 C
    assert sensor.read() is True
    assert sensor.temperature() == pytest.approx(25.0)


def test_read_negative_temperature(sensor):
    sensor._bus.regs[0x00] = [0xFF, 0x00]  # -256 * 0.0078125 = -2.0 C
    sensor.read()
    assert sensor.temperature() == pytest.approx(-2.0)


def test_temperature_unit_conversions(sensor):
    sensor._bus.regs[0x00] = [0x0C, 0x80]  # 25.0 C
    sensor.read()
    assert sensor.temperature(tmp119.UNITS_Centigrade) == pytest.approx(25.0)
    assert sensor.temperature(tmp119.UNITS_Fahrenheit) == pytest.approx(77.0)
    assert sensor.temperature(tmp119.UNITS_Kelvin) == pytest.approx(298.15)


def test_set_averaging(sensor):
    assert sensor.set_averaging(tmp119.TMP119_AVERAGE_64X) is True
    assert sensor.get_config() & AVG_MASK == (3 << 5)


def test_set_read_delay(sensor):
    assert sensor.set_read_delay(tmp119.TMP119_DELAY_16000_MS) is True
    assert sensor.get_config() & CONV_MASK == (7 << 7)


def test_set_averaging_preserves_read_delay(sensor):
    sensor.set_read_delay(tmp119.TMP119_DELAY_8000_MS)
    sensor.set_averaging(tmp119.TMP119_AVERAGE_32X)
    assert sensor.get_config() & CONV_MASK == (6 << 7)
    assert sensor.get_config() & AVG_MASK == (2 << 5)


def test_set_config_round_trips_16_bits(sensor):
    sensor.set_config(0xABCD)
    assert sensor.get_config() == 0xABCD
