# tmp119-python

A Python module to interface with the TMP119 temperature sensor. The TMP119 is
an ultra-high-accuracy, low-power digital temperature sensor from Texas
Instruments with an I2C-compatible interface. Tested on Raspberry Pi with
Raspberry Pi OS.

The python SMBus library must be installed.

    sudo apt-get install python3-smbus

# Usage

    import tmp119

### TMP119(bus=1, address=0x48)

    sensor = tmp119.TMP119()            # Use default I2C bus 1, address 0x48
    sensor = tmp119.TMP119(0)           # Specify I2C bus 0
    sensor = tmp119.TMP119(1, 0x49)     # Specify bus and I2C address

The TMP119 supports up to four I2C addresses, selected by the ADD0 pin:

    0x48 (ADD0 to GND, default)
    0x49 (ADD0 to V+)
    0x4A (ADD0 to SDA)
    0x4B (ADD0 to SCL)

### init()

Initialize the sensor. This needs to be called before using any other methods.
It verifies the device ID and configures the sensor for the fastest update rate
(no averaging, no added standby delay, ~15.5 ms cycle). Call `set_averaging()` /
`set_read_delay()` afterwards to trade speed for lower noise.

    sensor.init()

Returns True if the sensor was successfully initialized, False otherwise.

### read()

Read the sensor and update the temperature. The TMP119 runs in
continuous-conversion mode, so this always returns the latest result.

    sensor.read()

Returns True if the read was successful, False otherwise.

### temperature(conversion=UNITS_Centigrade)

Get the most recent temperature measurement.

    sensor.temperature()                        # Centigrade (default)
    sensor.temperature(tmp119.UNITS_Fahrenheit)  # Fahrenheit

Valid arguments are:

    tmp119.UNITS_Centigrade
    tmp119.UNITS_Fahrenheit
    tmp119.UNITS_Kelvin

Returns the most recent temperature in the requested units, or temperature in
degrees Centigrade if invalid units specified. Call `read()` to update.

### set_averaging(avg)

Set the conversion averaging mode. More averaging reduces noise but takes
longer to produce each result. Returns True if the write succeeded.

    sensor.set_averaging(tmp119.TMP119_AVERAGE_64X)

Valid arguments are (with the time each takes per result):

    tmp119.TMP119_AVERAGE_1X    # 15.5 ms
    tmp119.TMP119_AVERAGE_8X    # 125 ms
    tmp119.TMP119_AVERAGE_32X   # 500 ms
    tmp119.TMP119_AVERAGE_64X   # 1 s

### set_read_delay(delay)

Set the *minimum* standby delay between conversions in continuous-conversion
mode. The actual time between readings is the greater of this standby delay and
the averaging time (see datasheet Table 8-6); for example, `TMP119_AVERAGE_64X`
always yields at least a ~1 s cycle because the averaging alone takes 1 s,
regardless of the delay setting. Returns True if the write succeeded.

    sensor.set_read_delay(tmp119.TMP119_DELAY_1000_MS)

Valid arguments are:

    tmp119.TMP119_DELAY_NONE
    tmp119.TMP119_DELAY_125_MS
    tmp119.TMP119_DELAY_250_MS
    tmp119.TMP119_DELAY_500_MS
    tmp119.TMP119_DELAY_1000_MS
    tmp119.TMP119_DELAY_4000_MS
    tmp119.TMP119_DELAY_8000_MS
    tmp119.TMP119_DELAY_16000_MS

### get_config() / set_config(config)

Read or write the raw 16-bit configuration register (address 0x01) for advanced
use. `set_config()` returns True if the write succeeded; read-only bits are
ignored by the device.

    config = sensor.get_config()
    sensor.set_config(config)

# Reference

You can find the [TMP119 datasheet here](https://www.ti.com/lit/ds/symlink/tmp119.pdf).
