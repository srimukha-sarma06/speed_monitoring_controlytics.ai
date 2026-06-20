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
├── app.py                  # Flask web server application and API routes
├── main_edge_pipeline.py   # Core sensor fusion, synchronization, and event loop
├── modules/
│   ├── radar_interface.py  # RS485 communication, byte parsing, and threshold logic
│   ├── vision_capture.py   # OpenCV RTSP buffer management and frame capture
│   └── logger.py           # Handles saving violation metadata and images
├── static/                 # CSS, HTML, and saved violation images for the dashboard
├── templates/              # HTML templates for the Flask dashboard UI
└── requirements.txt        # Python dependencies