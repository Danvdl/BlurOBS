import cv2
import numpy as np
import pyvirtualcam
import logging
from ultralytics import YOLO
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from src.utils.settings import settings_manager

class VideoWorker(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    status_signal = pyqtSignal(str) # Emits status updates to the UI
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.auto_blur_enabled = settings_manager.get("auto_blur")
        self.show_output = settings_manager.get("show_preview")
        self.target_classes = settings_manager.get("target_classes")
        self.conf_threshold = settings_manager.get("confidence_threshold")
        self.use_custom_model = settings_manager.get("use_custom_model")
        self.custom_classes = settings_manager.get("custom_classes")
        self.model = None 
        self.model_type = None # 'standard' or 'world'

    def update_settings(self):
        self.target_classes = settings_manager.get("target_classes")
        self.conf_threshold = settings_manager.get("confidence_threshold")
        
        # Check if model needs reloading
        new_use_custom = settings_manager.get("use_custom_model")
        new_custom_classes = settings_manager.get("custom_classes")
        
        if new_use_custom != self.use_custom_model:
            self.use_custom_model = new_use_custom
            self.model = None # Force reload
        elif self.use_custom_model and new_custom_classes != self.custom_classes:
            self.custom_classes = new_custom_classes
            if self.model:
                self.model.set_classes(self.custom_classes)

    def load_model(self):
        if self.use_custom_model:
            if self.model_type != 'world':
                self.status_signal.emit("Loading YOLO-World v2 (Security Mode)...")
                logging.info("Loading YOLOv8 World v2...")
                self.model = YOLO('yolov8s-worldv2.pt')
                self.model_type = 'world'
            
            # Set custom classes
            logging.info(f"Setting custom classes: {self.custom_classes}")
            self.model.set_classes(self.custom_classes)
            # World models often need lower confidence for custom prompts
            if self.conf_threshold > 0.3:
                logging.info("Lowering confidence threshold for World model to 0.2")
                self.conf_threshold = 0.2
        else:
            if self.model_type != 'standard':
                self.status_signal.emit("Loading Standard AI Model...")
                logging.info("Loading YOLOv8 Nano...")
                self.model = YOLO('yolov8n.pt')
                self.model_type = 'standard'

    def run(self):
        width = settings_manager.get("obs_width")
        height = settings_manager.get("obs_height")
        fps = settings_manager.get("fps")

        # 1. Load YOLO Model
        if self.model is None:
            self.load_model()

        # 2. Open Camera
        self.status_signal.emit("Connecting to Camera...")
        logging.info("Opening camera...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            logging.error("Error: Could not open video device.")
            self.status_signal.emit("Error: Camera Not Found")
            return
        logging.info("Camera opened successfully.")

        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # 3. Initialize Virtual Camera
        self.status_signal.emit("Starting Virtual Camera...")
        try:
            cam = pyvirtualcam.Camera(width=width, height=height, fps=fps, fmt=pyvirtualcam.PixelFormat.BGR)
            logging.info(f"Virtual Camera Active: {cam.device}")
            self.status_signal.emit(f"Active: {cam.device}")
        except Exception as e:
            logging.error(f"Virtual Camera Error: {e}")
            logging.warning("Running in GUI-only mode (no OBS output).")
            self.status_signal.emit("Warning: Virtual Cam Failed (GUI Only)")
            cam = None

        logging.info("Starting video loop...")
        
        while self.running:
            ret, img = cap.read()
            if not ret:
                logging.error("Failed to read frame from camera.")
                self.status_signal.emit("Error: Camera Disconnected")
                break
            
            # Resize to ensure it matches OBS/VirtualCam config
            img = cv2.resize(img, (width, height))
            display_img = img.copy() 

            # 4. Detection & Blur Logic
            if self.auto_blur_enabled:
                # Reload model if needed (e.g. settings changed and model was set to None)
                if self.model is None:
                    self.load_model()

                # Run YOLO inference
                results = self.model(img, verbose=False, conf=self.conf_threshold)
                
                for result in results:
                    for box in result.boxes:
                        cls_id = int(box.cls[0])
                        
                        # Logic for Standard vs World
                        should_blur = False
                        if self.use_custom_model:
                            # In World mode, we blur EVERYTHING detected because we only set specific classes
                            should_blur = True
                        else:
                            # In Standard mode, we check against the target list
                            if cls_id in self.target_classes:
                                should_blur = True
                        
                        if should_blur:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            
                            # Ensure bounds
                            y1, y2 = max(0, y1), min(height, y2)
                            x1, x2 = max(0, x1), min(width, x2)
                            
                            if x2 > x1 and y2 > y1:
                                # Apply Heavy Gaussian Blur to the Box
                                roi = img[y1:y2, x1:x2]
                                roi = cv2.GaussianBlur(roi, (51, 51), 0) 
                                img[y1:y2, x1:x2] = roi
                                
                                # Draw Red Box for Director View (GUI)
                                cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                label = "BLURRED"
                                if self.use_custom_model and result.names:
                                    label = result.names[cls_id]
                                cv2.putText(display_img, label, (x1, y1-10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

            # 5. Output to OBS Virtual Camera
            if cam:
                cam.send(img)
                cam.sleep_until_next_frame()
            else:
                QThread.msleep(int(1000/fps)) 

            # 6. Output to GUI
            final_display = img if self.show_output else display_img
            rgb_image = cv2.cvtColor(final_display, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
            self.change_pixmap_signal.emit(qt_image)
        
        if cam:
            cam.close()
        cap.release()

    def stop(self):
        self.running = False
