
# BlurOBS Live: Intelligent Privacy Shield for Streamers

BlurOBS Live is a real-time "active defense" system for live streamers. It acts as a secure middleware between your webcam and OBS Studio, automatically detecting and blurring sensitive objects (smartphones, credit cards, ID documents) before they are broadcast to your audience.

## Product Vision
A desktop middleware that sits between a Webcam and OBS. It automatically detects sensitive objects (phones, credit cards, faces) and blurs them in real-time.

## The Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Language** | Python 3.11 | High-performance logic. |
| **Input/Output** | PyAV & PyVirtualCam | Low-latency video capture and Virtual Camera output. |
| **Detector** | YOLOv8 Nano (Local) | Runs on CPU. Instantly spots where the object is. |
| **Segmenter** | SAM 2 (Replicate API) | Runs in Cloud. Refines the "Box" into a "Perfect Shape." |
| **Tracker** | OpenCV CSRT | Runs on CPU. Tracks the perfect shape locally between cloud calls. |
| **GUI** | PyQt6 | Modern, hardware-accelerated user interface. |

## Roadmap

### Phase 1: The "Fast & Rough" MVP (Local Only)
**Goal:** A working app that automatically blurs objects using a simple bounding box. No cloud integration yet. This ensures the app is "usable" even if the internet drops.

**The Video Pipeline:**
*   Implement QThread with PyAV to capture webcam frames at 30fps.
*   Push frames to pyvirtualcam so they appear in OBS.

**The "Spotter" (YOLO Integration):**
*   Load `yolov8n.pt` (Nano model) locally.
*   Run inference on every 3rd frame (to save CPU).
*   If `class_id == 67` (Cell Phone), draw a Gaussian Blur over the detection box.

**The GUI:**
*   Show the "Red Box" overlay in the app window (Director View) so the user knows protection is active.

### Phase 2: The "Cloud Refiner" (Adding Replicate)
**Goal:** Fix the "ugly box" problem. Use the Cloud API to turn the rough square blur into a precise object mask.

**The Async API Call:**
*   When YOLO detects a new object (stable for >10 frames), take a snapshot.
*   Send this snapshot + the YOLO box coordinates to Replicate (Meta SAM 2).
*   **Critical:** Do this in a separate thread so the video feed doesn't freeze.

**The Handoff:**
*   While waiting for the Cloud (approx. 1-2s), keep using the Local YOLO Box.
*   When Replicate returns the High-Res Mask:
    *   Stop using the YOLO Box.
    *   Initialize a local OpenCV Tracker (CSRT) with the new high-res mask.
*   Now the blur perfectly hugs the shape of the phone.

### Phase 3: The "Streamer Experience" (UX) - **Implemented**
**Goal:** Features that make the app safe and trustworthy for live broadcasting.

**The "Confidence" Switch:**
*   Add a logic check: If the Local Tracker confidence drops below 50% (object moves too fast), instantly revert to the YOLO Box (safety fallback).

**Class Selector:**
*   Add a simple "Settings" menu in PyQt6 allowing the user to toggle what to blur: [x] Cell Phones, [ ] Faces, [ ] Credit Cards (Custom trained YOLO model required for cards).

**The Panic Button:**
*   Global Hotkey (F12): Instantly blurs the entire screen and pauses the camera.

### Phase 4: Packaging & Release
**Goal:** A distributable .exe file.

**Dependency Handling:**
*   Create a `requirements.txt` locking exact versions of `ultralytics` and `pyqt6`.

**Compilation:**
*   Use Nuitka to compile the Python source into a standalone executable.
*   Command: `nuitka --standalone --enable-plugin=pyqt6 --follow-imports main.py`

## Prerequisites
Before running the application, ensure you have the following installed:
*   OBS Studio (Version 26.0+): Required for the generic "OBS Virtual Camera" driver.
*   Python 3.10 or 3.11.
*   A Webcam.
*   **Replicate API Token**: You need a Replicate account and API token for the cloud masking feature.

## Installation
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set your Replicate API Token (Optional, for precise masking):
    *   Edit `main.py` and replace the token, or set the environment variable `REPLICATE_API_TOKEN`.
3.  Run the application:
    ```bash
    python main.py
    ```