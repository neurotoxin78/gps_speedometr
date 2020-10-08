import time
from gc import collect, mem_free
import adafruit_bme280
import board
import busio
from ui import UI
import digitalio
import adafruit_gps

# BME
i2c = busio.I2C(board.B6, board.B7)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
bme280.sea_level_pressure = 1011.92
bme280.mode = adafruit_bme280.MODE_NORMAL
bme280.standby_period = adafruit_bme280.STANDBY_TC_500
bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2
time.sleep(1)
# Button
btn = digitalio.DigitalInOut(board.B0)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.DOWN
# GPS
uart = busio.UART(board.A2, board.A3, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

# UI
fg_color = 0x00ffbf
bg_color = 0x252525
ui = UI()
ui.main_screen(fg_color, bg_color)

last_print = time.monotonic()
collect()
# Main Loop
while KeyboardInterrupt:
    # BME
    try:
        ui.set_bme_values(bme280.temperature, bme280.humidity, bme280.pressure)
        ui.set_altitude(bme280.altitude)
    except ValueError:
        pass
    # GPS
    try:
        gps.update()
    except:
        pass
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            continue
    collect()
    # Speed
    if gps.speed_knots is not None:
        ui.set_speed_value(gps.speed_knots)
    # Coordinates
    if gps.latitude is not None:
        ui.set_coord_stat(gps.latitude, gps.longitude)
    else:
        ui.set_coord_stat(0, 0)
    # Satellites
    if gps.satellites is not None:
        ui.set_sat_num(gps.satellites)
    if gps.fix_quality is not None:
        ui.set_fix_quality(gps.fix_quality)
    # Time
    if gps.timestamp_utc is not None:
        ui.set_time(gps.timestamp_utc.tm_hour + 3, gps.timestamp_utc.tm_min)
    ui.set_counter(9856)
    ui.set_sys_stat("RAM:" + str(mem_free()) + "B")
    time.sleep(1)
