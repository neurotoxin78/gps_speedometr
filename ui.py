import board
import busio
import displayio
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text import label


class UI(object):
    def __init__(self):
        # Fonts
        self.font_mini = terminalio.FONT
        self.font_middle = bitmap_font.load_font("fonts/dseg-10.bdf")
        self.font_spd = bitmap_font.load_font("fonts/dseg-32.bdf")
        displayio.release_displays()
        # Display init
        spi = busio.SPI(clock=board.B10, MOSI=board.B15, MISO=board.B14)
        while not spi.try_lock():
            pass
        spi.configure(baudrate=25000000, phase=0, polarity=0)
        spi.unlock()
        init_sequence = (
            b"\x01\x80\x32"  # _SWRESET and Delay 50ms
            b"\x11\x80\xFF"  # _SLPOUT
            b"\x3A\x81\x05\x0A"  # _COLMOD
            b"\xB1\x83\x00\x06\x03\x0A"  # _FRMCTR1
            b"\x36\x01\x08"  # _MADCTL
            b"\xB6\x02\x15\x02"  # _DISSET5
            b"\xC0\x82\x02\x70\x0A"  # _PWCTR1 GVDD = 4.7V, 1.0uA, 10 ms delay
            b"\xC1\x01\x05"  # _PWCTR2 VGH = 14.7V, VGL = -7.35V
            b"\xC2\x02\x01\x02"  # _PWCTR3 Opamp current small, Boost frequency
            b"\xC5\x82\x3C\x38\x0A"  # _VMCTR1
            b"\xFC\x02\x11\x15"  # _PWCTR6
            b"\xE0\x10\x09\x16\x09\x20\x21\x1B\x13\x19\x17\x15\x1E\x2B\x04\x05\x02\x0E"  # _GMCTRP1 Gamma
            b"\xE1\x90\x0B\x14\x08\x1E\x22\x1D\x18\x1E\x1B\x1A\x24\x2B\x06\x06\x02\x0F\x0A"  # _GMCTRN1
            b"\x13\x80\x0a"  # _NORON
            b"\x29\x80\xFF"  # _DISPON
        )
        display_bus = displayio.FourWire(
            spi, command=board.B8, chip_select=board.B9, reset=board.B5)
        self.display = displayio.Display(
            display_bus, init_sequence, width=128, height=160)
        self.display.rotation = 90

    def main_screen(self, fg_color, bg_color):
        # UI
        self.main_group = displayio.Group(max_size=25)
        # background
        bg_bitmap = displayio.Bitmap(160, 128, 2)
        bg_palette = displayio.Palette(1)
        bg_palette[0] = fg_color  # Bright Green
        bg_sprite = displayio.TileGrid(
            bg_bitmap, pixel_shader=bg_palette, x=0, y=0)
        self.main_group.append(bg_sprite)
        # Main Screen Round rectangle
        roundrect = RoundRect(
            2, 2, 156, 124, 5, fill=bg_color, outline=bg_color, stroke=1)
        self.main_group.append(roundrect)
        # Show display
        self.display.show(self.main_group)
        self.display.auto_refresh = True
        self._speed_labels(fg_color)
        self._bme_labels(fg_color, bg_color)
        self._status_bar(fg_color, bg_color)
        self._counter(0xffffff)
        self._datetime_labels(fg_color)

    def _speed_labels(self, color):
        # SPEED Value
        self.speed_value = label.Label(self.font_spd, text="00", color=color)
        self.speed_value.x = 48
        self.speed_value.y = 49
        self.speed_value.scale = 1
        self.main_group.append(self.speed_value)
        # Speed Unit
        speed_unit = label.Label(self.font_mini, text='km/h', color=0xffffff)
        speed_unit.x = 124
        speed_unit.y = 10
        speed_unit.scale = 1
        self.main_group.append(speed_unit)

    def _bme_labels(self, fill_color, outline_color):
        # Shapes
        frame_1 = RoundRect(3, 3, 44, 30, 5, fill=fill_color,
                            outline=outline_color, stroke=1)
        self.main_group.append(frame_1)
        frame_2 = RoundRect(3, 34, 44, 30, 5, fill=fill_color,
                            outline=outline_color, stroke=1)
        self.main_group.append(frame_2)
        frame_3 = RoundRect(3, 65, 44, 30, 5, fill=fill_color,
                            outline=outline_color, stroke=1)
        self.main_group.append(frame_3)
        # Temperature Label
        temp_label = label.Label(
            self.font_mini, text='TEMP', color=outline_color)
        temp_label.x = 12
        temp_label.y = 8
        self.main_group.append(temp_label)
        # Humidity Label
        humi_label = label.Label(
            self.font_mini, text='HUMI', color=outline_color)
        humi_label.x = 12
        humi_label.y = 39
        self.main_group.append(humi_label)
        # Pressure label
        press_label = label.Label(
            self.font_mini, text='P.mmHg', color=outline_color)
        press_label.x = 6
        press_label.y = 71
        self.main_group.append(press_label)
        # Values Labels
        # Temp Value
        self.temp_value = label.Label(self.font_middle, text='00' + chr(0176), color=outline_color)
        self.temp_value.x = 5
        self.temp_value.y = 24
        self.temp_value.scale = 1
        self.main_group.append(self.temp_value)
        # Humidity Value
        self.humi_value = label.Label(
            self.font_middle, text="00" + chr(0x25), color=outline_color)
        self.humi_value.x = 5
        self.humi_value.y = 55
        self.main_group.append(self.humi_value)
        # Pressure Value
        self.press_value = label.Label(
            self.font_middle, text="00" + chr(0x25), color=outline_color)
        self.press_value.x = 5
        self.press_value.y = 86
        self.press_value.scale = 1
        self.main_group.append(self.press_value)

    def _counter(self, fill_color):
        self.counter = label.Label(
            self.font_middle, text="000000  ", color=fill_color)
        self.counter.x = 73
        self.counter.y = 84
        self.main_group.append(self.counter)

    def set_counter(self, count_value):
        self.counter._update_text("{:0>6}".format(count_value))

    def _datetime_labels(self, fill_color):
        self.time_label = label.Label(
            self.font_middle, text="00:00", color=fill_color)
        self.time_label.x = 95
        self.time_label.y = 65
        self.main_group.append(self.time_label)

    def set_time(self, hours, minutes):
        self.time_label._update_text(
            "{:0>2}".format(hours) + ":{:0>2}".format(minutes))

    def set_bme_values(self, temp, humi, press):
        self.temp_value._update_text("{}".format(str(round(temp))) + chr(0176))
        self.humi_value._update_text("{}".format(round(humi)) + "%")
        self.press_value._update_text("{}".format(round(press * 0.75)))

    def set_speed_value(self, speed):
        self.speed_value._update_text("{:0>2}".format(round(speed * 1.852)))

    def _status_bar(self, fill_color, outline_color):
        # Shapes
        frame = RoundRect(3, 96, 154, 28, 5, fill=fill_color,
                          outline=outline_color, stroke=1)
        self.main_group.append(frame)
        line = Rect(8, 110, 144, 1, fill=0x0)
        self.main_group.append(line)
        # Free resources
        self.sys_stat_label = label.Label(
            self.font_mini, text='Wait for status ...', color=outline_color)
        self.sys_stat_label.x = 92
        self.sys_stat_label.y = 116
        self.main_group.append(self.sys_stat_label)
        # Coordinates
        self.lat_label = label.Label(
            self.font_mini, text='LAT: wait            ', color=outline_color)
        self.lat_label.x = 7
        self.lat_label.y = 103
        self.main_group.append(self.lat_label)
        self.lon_label = label.Label(
            self.font_mini, text='LON: wait            ', color=outline_color)
        self.lon_label.x = 7
        self.lon_label.y = 115
        self.main_group.append(self.lon_label)
        # Satellites
        self.sat_label = label.Label(
            self.font_mini, text='SAT:0', color=fill_color)
        self.sat_label.x = 122
        self.sat_label.y = 25
        self.main_group.append(self.sat_label)
        # Fix Quality
        self.fq_label = label.Label(
            self.font_mini, text='FQU:0', color=fill_color)
        self.fq_label.x = 122
        self.fq_label.y = 35
        self.main_group.append(self.fq_label)
        # Altitude
        self.alt_label = label.Label(
            self.font_mini, text='ALT:0      ', color=outline_color)
        self.alt_label.x = 92
        self.alt_label.y = 103
        self.main_group.append(self.alt_label)

    def set_sys_stat(self, sys_stat):
        self.sys_stat_label._update_text(sys_stat)

    def set_coord_stat(self, latitude, longitude):
        self.lat_label._update_text("LAT:{0:.6f}".format(latitude) + chr(0176))
        self.lon_label._update_text("LON:{0:.6f}".format(longitude) + chr(0176))

    def set_sat_num(self, sattelites):
        self.sat_label._update_text("SAT:{}".format(sattelites))

    def set_fix_quality(self, fix_quality):
        self.fq_label._update_text("FQU:{}".format(fix_quality))

    def set_altitude(self, altitude):
        self.alt_label._update_text("ALT:{0:.1f}".format(altitude))
