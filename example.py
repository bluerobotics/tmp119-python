#!/usr/bin/env python3
import tmp119
from time import sleep

# Optional constructor parameters: TMP119(bus, address)
#   bus     - I2C bus number (default 1; busses are listed as /dev/i2c*)
#   address - I2C address set by the ADD0 pin (default 0x48):
#             0x48 (GND), 0x49 (V+), 0x4A (SDA), 0x4B (SCL)
sensor = tmp119.TMP119()

if not sensor.init():
    print("Error initializing sensor")
    exit(1)

# init() configures the fastest update rate. Override it here with low-noise
# settings: average 64 conversions and update roughly once per second.
#
# Averaging options (set_averaging) and the time each takes per result:
#   TMP119_AVERAGE_1X  -> 15.5 ms
#   TMP119_AVERAGE_8X  -> 125 ms
#   TMP119_AVERAGE_32X -> 500 ms
#   TMP119_AVERAGE_64X -> 1 s
#
# Minimum standby delay options (set_read_delay):
#   TMP119_DELAY_NONE, TMP119_DELAY_125_MS, TMP119_DELAY_250_MS,
#   TMP119_DELAY_500_MS, TMP119_DELAY_1000_MS, TMP119_DELAY_4000_MS,
#   TMP119_DELAY_8000_MS, TMP119_DELAY_16000_MS
#
# The actual time between readings is the greater of the averaging time above
# and the standby delay (datasheet Table 8-6). So 64x averaging with
# TMP119_DELAY_1000_MS gives ~1 s, but 64x with TMP119_DELAY_NONE is also ~1 s
# since the averaging itself takes 1 s.
sensor.set_averaging(tmp119.TMP119_AVERAGE_64X)
sensor.set_read_delay(tmp119.TMP119_DELAY_1000_MS)

while True:
    if not sensor.read():
        print("Error reading sensor")
        exit(1)
    print("Temperature: %.2f C\t%.2f F" % (
        sensor.temperature(),
        sensor.temperature(tmp119.UNITS_Fahrenheit)))
    sleep(1)
