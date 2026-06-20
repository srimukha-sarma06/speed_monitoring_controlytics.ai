# Radar-Assisted Edge Speed Enforcement System

> **Note:** This repository serves as a portfolio showcase of the embedded systems and sensor fusion architecture developed during my internship at Controlytics.AI. Because the system is deeply integrated with specific edge hardware (Raspberry Pi, TSR20 Radar via RS485, and RTSP IP Cameras), the code cannot be executed locally without the physical hardware setup. 

An end-to-end, hardware-integrated traffic monitoring solution deployed entirely on edge hardware. This system fuses radar telemetry with live video streams to accurately detect overspeeding vehicles in real-time, securely log violations, and serve the data to a remote web dashboard.

## 🚀 System Overview

The core objective of this project was to build a localized, high-performance edge pipeline that did not rely on cloud compute for real-time hazard detection. The workflow is divided into three main stages:

1. **Sensor Fusion (Perception):** Synchronizes continuous TSR20 radar data (received via RS485 serial protocols) with live RTSP IP camera streams.
2. **Edge-Optimized Processing (Logic):** Continuously evaluates the velocity metrics against defined speed limits. The processing pipeline was heavily optimized to run locally on resource-constrained Raspberry Pi hardware without thermal throttling or frame drops.
3. **Automated Event Logging & Dashboard (Storage & UI):** The moment a speed threshold is breached, the system captures time-stamped frames and velocity data. This is stored locally and served via a custom Flask-based web dashboard, allowing remote operators to review violations without needing physical access to the edge device.

## 🛠️ Tech Stack & Hardware

**Software & Frameworks:**
* **Language:** Python 3.x
* **Computer Vision:** OpenCV (for RTSP stream handling and frame capture)
* **Backend/Dashboard:** Flask, HTML/CSS
* **Communication:** RS485 Serial protocols

**Hardware Architecture:**
* Raspberry Pi (Edge Linux target)
* TSR20 Radar Module
* IP Camera (RTSP streaming)
* RS485 to USB converter

## 🧠 Key Engineering Challenges Solved

* **Asynchronous Data Synchronization:** Solved the timing mismatch between the high-frequency radar telemetry (serial) and the lower-frequency IP camera frame rate (network), ensuring the captured image perfectly matched the radar's speed reading.
* **Resource Optimization:** Designed the OpenCV pipeline to only write to disk and trigger heavy processing when the radar interrupt signaled a violation, keeping baseline CPU and RAM usage minimal during idle traffic periods.

## 📁 Directory Structure

```text
├── services/                       # Core logic and helper modules
│   ├── get_speed_limit.py          # Retrieves configured speed thresholds
│   ├── panel_config.py             # Handles system configuration settings
│   ├── read_speed.py               # Radar telemetry extraction and parsing
│   ├── record_hourly_stream.py     # Manages continuous video/data recording
│   └── screenshots_annotations.py  # Handles frame capture and bounding box overlays
├── static/                         # Frontend assets for the dashboard
│   ├── logo.jpg
│   └── main.css
├── templates/                      # HTML templates for the Flask UI
│   └── index.html
├── .gitignore                      # Git ignore rules
├── DOCUMENTATION.docx              # Detailed project documentation (Word)
├── DOCUMENTATION.pdf               # Detailed project documentation (PDF)
├── README.md                       # Project overview and setup instructions
├── RestAPI.py                      # API endpoints for remote data retrieval
├── app.py                          # Main Flask server application
├── final-code.py                   # Primary execution script/entry point
└── settings.txt                    # Configuration parameters
