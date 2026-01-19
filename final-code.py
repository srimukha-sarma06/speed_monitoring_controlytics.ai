import cv2
from datetime import datetime
import os
import time
import threading
import serial
import subprocess
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageDraw, ImageFont

# ====================== Simulated Speeds ======================
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

# ====================== Configurations ======================
RTSP_URL = 'rtsp://admin:admin12345@192.168.1.250:554/cam/realmonitor?channel=1&subtype=0'
SETTINGS_FILE = "/home/pi/flask-webpage/settings.txt"

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

# ====================== Panel Mapping ======================
def get_panel_offset(panel_name):
    mapping = {
        'top_left': 0,
        'top_right': 32,
        'mid_left': 64,
        'mid_right': 96,
        'bot_left': 128,
        'bot_right': 160
    }
    return mapping[panel_name]

# ====================== Draw Speed Split ======================
def draw_large_split_text(canvas, text, color, top_left_x, top_left_y, mid_left_x, mid_left_y):
    image = Image.new("RGB", (32, 32), "black")
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=pil_font, fill=(color.red, color.green, color.blue))

    top_half = image.crop((0, 0, 32, 16))
    bottom_half = image.crop((0, 16, 32, 32))

    for y in range(top_half.size[1]):
        for x in range(top_half.size[0]):
            r, g, b = top_half.getpixel((x, y))
            canvas.SetPixel(top_left_x + x, top_left_y + y, r, g, b)

    for y in range(bottom_half.size[1]):
        for x in range(bottom_half.size[0]):
            r, g, b = bottom_half.getpixel((x, y))
            canvas.SetPixel(mid_left_x + x, mid_left_y + y, r, g, b)

# ====================== Helper Functions ======================
def get_speed_limit():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return int(f.read().strip())
    except Exception as e:
        print(f"Settings error: {e}")
        return 70

def update_display(speed, speed_limit):
    canvas.Clear()

    # Choose color and alert message
    if speed <= speed_limit - 10:
        color = color_safe
        alert = "Safe Speed"
    elif speed_limit - 10 < speed <= speed_limit:
        color = color_warn
        alert = "Warning"
    else:
        color = color_alert
        alert = "SLOW DOWN!"

    # ==== Draw SPEED across top_left and mid_left ====
    speed_text = str(speed)
    draw_large_split_text(
        canvas,
        speed_text,
        color,
        get_panel_offset('top_left'),
        0,
        get_panel_offset('mid_left'),
        0
    )

    # ==== Draw 'km/h' on mid_right ====
    x_kmh = get_panel_offset('mid_right') + 2
    graphics.DrawText(canvas, font_small, x_kmh, 12, color, "km/h")

    # ==== Draw alert message across bot panels ====
    # Measure alert width
    alert_width = graphics.DrawText(canvas, font_small, 0, 0, graphics.Color(0, 0, 0), alert)
    x_alert = get_panel_offset('bot_left') + 64 - (alert_width // 2)
    graphics.DrawText(canvas, font_small, x_alert, 12, color, alert)

    matrix.SwapOnVSync(canvas)

def read_speed():
    data = ser.read(4)
    if len(data) < 4:
        speed = 0
    if data[0] == 0xFC and data[1] == 0xFA and data[3] == 0x00:
        speed = data[2]
    return speed
    time.sleep(0.1)

def overlay_speed_info(frame, radar_speed, speed_limit):
    text = f"Speed: {radar_speed} km/h | Limit: {speed_limit} km/h"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_thickness = 2
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
    x, y = 20, 40
    cv2.rectangle(frame, (x - 10, y - text_height - 10), (x + text_width + 10, y + 10), (255, 255, 255), -1)
    cv2.putText(frame, text, (x, y), font, font_scale, (0, 0, 0), font_thickness)
    return frame

def capture_screenshot(speed, speed_limit):
    timestamp = datetime.now().strftime('%H%M%S')
    date_str = datetime.now().strftime('%Y%m%d')
    folder_name = f"/home/pi/{date_str}"
    os.makedirs(folder_name, exist_ok=True)
    filename = f"{timestamp}.jpg"
    save_path = os.path.join(folder_name, filename)

    try:
        cap = cv2.VideoCapture(RTSP_URL)
        if not cap.isOpened():
            print("? Failed to connect to camera")
            return

        start_time = time.time()
        ret = False
        while time.time() - start_time < 5:
            ret, frame = cap.read()
            if ret:
                break
            time.sleep(0.1)

        if not ret:
            print("? Frame capture failed")
            return

        annotated_frame = overlay_speed_info(frame, speed, speed_limit)
        cv2.imwrite(save_path, annotated_frame)
        print(f"? Saved violation: {save_path}")
    except Exception as e:
        print(f"?? Capture error: {e}")
    finally:
        if 'cap' in locals():
            cap.release()

def record_hourly_stream():
    while True:
        current_time = datetime.now()
        date_str = current_time.strftime('%Y%m%d')
        hour_str = current_time.strftime('%H')
        folder_path = f"/home/pi/{date_str}/videos"
        os.makedirs(folder_path, exist_ok=True)

        output_filename = f"{date_str}_{hour_str}.mp4"
        output_path = os.path.join(folder_path, output_filename)

        ffmpeg_command = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', RTSP_URL,
            '-t', '3600',
            '-vcodec', 'copy',
            '-acodec', 'copy',
            output_path
        ]

        print(f"?? Starting FFmpeg recording: {output_path}")
        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"? Finished recording: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"?? FFmpeg failed: {e}")
            time.sleep(5)

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
                      
