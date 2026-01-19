from flask import Flask, request, render_template, send_from_directory, send_file
from waitress import serve
from datetime import datetime
import os
import zipfile
import socket
import re

app = Flask(__name__)

# Use a dedicated violations directory
base_dir = "/home/pi"
SETTINGS_FILE = "settings.txt"

# Ensure base_dir exists
os.makedirs(base_dir, exist_ok=True)

def get_speed_limit():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 70

def set_speed_limit(limit):
    with open(SETTINGS_FILE, "w") as f:
        f.write(str(limit))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        new_limit = request.form.get("speed_limit")
        if new_limit and new_limit.isdigit():
            set_speed_limit(int(new_limit))

    speed_limit = get_speed_limit()

    # Only include folders that match YYYYMMDD format
    folders = sorted([
        f for f in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, f)) and re.fullmatch(r"\d{8}", f)
    ], reverse=True)

    violation_data = []
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        images = sorted(os.listdir(folder_path), reverse=True)
        violation_data.append((folder, images))

    return render_template("index.html", speed_limit=speed_limit, violation_data=violation_data)

@app.route("/violations/<date>/<filename>")
def download_file(date, filename):
    folder_path = os.path.join(base_dir, date)
    return send_from_directory(folder_path, filename, as_attachment=True)

@app.route("/download_day/<date>")
def download_day(date):
    folder_path = os.path.join(base_dir, date)
    zip_filename = f"{date}.zip"
    zip_path = os.path.join("static", zip_filename)

    os.makedirs("static", exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir)
                    zipf.write(file_path, arcname=arcname)
    except Exception as e:
        return f"Error creating zip: {str(e)}", 500

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Server running at: http://{ip_address}:8000")
    serve(app, host="0.0.0.0", port=8000)
