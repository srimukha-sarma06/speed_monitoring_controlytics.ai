import cv2
from datetime import datetime
import os
import time
import threading
import serial
import subprocess
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from services.get_speed_limit import get_speed_limit
from services.panel_config import update_display, get_panel_offset, draw_large_split_text
from services.read_speed import read_speed
from services.record_hourly_stream import record_hourly_stream
from services.screenshots_annotations import capture_screenshot, overlay_speed_info

load_dotenv()

# ====================== Simulated Speeds ======================
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

# ====================== Config =====================
RTSP_URL = os.getenv("RTSP_URL")
SETTINGS_FILE = os.getenv("SETTINGS_FILE")

# ====================== RGB Matrix Setup ======================
options = RGBMatrixOptions()
options.rows = 16
options.cols = 32
options.chain_length = 6
options.parallel = 1
options.hardware_mapping = 'classic-pi1'
options.pwm_bits = 11
options.brightness = 80
options.show_refresh_rate = 0
options.scan_mode = 1
options.gpio_slowdown = 3
options.disable_hardware_pulsing = True

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

# ====================== Fonts & Colors ======================
font = graphics.Font()
font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/9x15.bdf")

font_small = graphics.Font()
font_small.LoadFont('/home/pi/rpi-rgb-led-matrix/fonts/6x9.bdf')

font_large = graphics.Font()
font_large.LoadFont('/home/pi/rpi-rgb-led-matrix/fonts/9x13.bdf')

color_safe = graphics.Color(0, 255, 0)
color_warn = graphics.Color(255, 165, 0)
color_alert = graphics.Color(255, 0, 0)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_size = 24
pil_font = ImageFont.truetype(font_path, font_size)

# ====================== MAIN ======================
if __name__ == "__main__":
    try:
        threading.Thread(target=record_hourly_stream, daemon=True).start()
        while True:
            speed = read_speed()
            speed_limit = get_speed_limit()

            update_display(speed, speed_limit)

            if speed > speed_limit:
                print(f"?? Violation: {speed} km/h")
                capture_screenshot(speed, speed_limit)
            else:
                print(f"? Safe speed: {speed} km/h")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n?? System stopped")
                      
