"""Driver for the Texas Instruments TMP119 high-accuracy temperature sensor."""

try:
    import smbus
except ImportError:
    print('Try sudo apt-get install python3-smbus')

# Valid units
UNITS_Centigrade = 1
UNITS_Fahrenheit = 2
UNITS_Kelvin = 3

# Conversion averaging mode (AVG[1:0], config register bits 6:5).
# More averaging reduces noise but lengthens the conversion cycle.
TMP119_AVERAGE_1X = 0   # No averaging
TMP119_AVERAGE_8X = 1   # 8 averaged conversions (power-on default)
TMP119_AVERAGE_32X = 2  # 32 averaged conversions
TMP119_AVERAGE_64X = 3  # 64 averaged conversions

# Minimum standby delay between conversions in continuous-conversion mode
# (CONV[2:0], config register bits 9:7). The total cycle time also depends on
# the averaging setting (see datasheet Table 8-6).
TMP119_DELAY_0_MS = 0
TMP119_DELAY_125_MS = 1
TMP119_DELAY_250_MS = 2
TMP119_DELAY_500_MS = 3
TMP119_DELAY_1000_MS = 4  # power-on default
TMP119_DELAY_4000_MS = 5
TMP119_DELAY_8000_MS = 6
TMP119_DELAY_16000_MS = 7


class TMP119:

    # Registers
    _TEMP_REG = 0x00
    _CONFIG_REG = 0x01
    _DEVICE_ID_REG = 0x0F
    _DEVICE_ID = 0x2117

    # CONV[2:0] (standby delay), config register bits 9:7
    _CONV_SHIFT = 7
    _CONV_MASK = 0x0380
    # AVG[1:0] (averaging), config register bits 6:5
    _AVG_SHIFT = 5
    _AVG_MASK = 0x0060

    # Each LSB of the temperature register represents this many degrees C
    _LSB_C = 0.0078125

    def __init__(self, bus=1, address=0x48):
        """Create a sensor on the given I2C bus and address.

        The TMP119 supports up to four I2C addresses (0x48 - 0x4B), selected by
        the ADD0 pin. The default address (ADD0 to GND) is 0x48.
        """
        self._address = address

        # Degrees C
        self._temperature = 0

        try:
            self._bus = smbus.SMBus(bus)
        except Exception:
            print("Bus %d is not available." % bus)
            print("Available busses are listed as /dev/i2c*")
            self._bus = None

    def init(self):
        """Verify the device and configure it for the fastest update rate.

        Returns True on success, False if the bus is unavailable or the device
        ID does not match. Call set_averaging()/set_read_delay() afterwards to
        trade speed for lower noise.
        """
        if self._bus is None:
            print("No bus!")
            return False

        if self.get_device_id() != self._DEVICE_ID:
            return False

        # Configure for the fastest update rate: no averaging and the shortest
        # standby delay, giving a ~15.5 ms conversion cycle (datasheet Table
        # 8-6). Clearing the AVG and CONV bits sets AVG = 1X and delay = 0 ms.
        config = self.get_config()
        config &= ~(self._AVG_MASK | self._CONV_MASK)
        return self.set_config(config)

    def read(self):
        """Read the latest conversion and update the stored temperature.

        Returns True on success, False if the bus is unavailable.
        """
        if self._bus is None:
            print("No bus!")
            return False

        # The TMP119 powers up in continuous-conversion mode, so the
        # temperature register always holds the most recent conversion.
        raw = self._read_register(self._TEMP_REG)

        # Data is in 2's complement format
        if raw > 32767:
            raw -= 65536

        self._temperature = raw * self._LSB_C
        return True

    def temperature(self, conversion=UNITS_Centigrade):
        """Return the most recent temperature in the requested units.

        Defaults to degrees Centigrade. Call read() to update the value.
        """
        if conversion == UNITS_Fahrenheit:
            return (9 / 5) * self._temperature + 32
        elif conversion == UNITS_Kelvin:
            return self._temperature + 273.15
        return self._temperature

    def set_averaging(self, avg):
        """Set the conversion averaging mode, preserving other config bits."""
        config = self.get_config()
        config = (config & ~self._AVG_MASK) | \
            ((avg << self._AVG_SHIFT) & self._AVG_MASK)
        return self.set_config(config)

    def set_read_delay(self, delay):
        """Set the standby delay between conversions, preserving other bits."""
        config = self.get_config()
        config = (config & ~self._CONV_MASK) | \
            ((delay << self._CONV_SHIFT) & self._CONV_MASK)
        return self.set_config(config)

    def get_config(self):
        """Read the raw 16-bit configuration register (address 0x01)."""
        return self._read_register(self._CONFIG_REG)

    def set_config(self, config):
        """Write the raw 16-bit configuration register (address 0x01).

        Read-only bits are ignored by the device.
        """
        return self._write_register(self._CONFIG_REG, config)

    def get_device_id(self):
        """Read the raw 16-bit device ID register (address 0x0F)."""
        return self._read_register(self._DEVICE_ID_REG)

    # The TMP119 transfers 16-bit registers MSB first. smbus word transfers are
    # little-endian, so we use block transfers and order the bytes ourselves.
    def _read_register(self, register):
        data = self._bus.read_i2c_block_data(self._address, register, 2)
        return (data[0] << 8) | data[1]

    def _write_register(self, register, value):
        value &= 0xFFFF
        self._bus.write_i2c_block_data(
            self._address, register, [(value >> 8) & 0xFF, value & 0xFF])
        return True
