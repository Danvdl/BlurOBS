from ultralytics import YOLO
import cv2
import time

try:
    print("Loading YOLO-World model...")
    model = YOLO('yolov8s-world.pt')  # or yolov8s-worldv2.pt
    print("Model loaded.")

    # Define custom classes
    model.set_classes(["credit card", "id card", "passport"])
    print("Classes set.")

    # Dummy inference
    img = cv2.imread("test.jpg") # Need a dummy image, or just zeros
    if img is None:
        import numpy as np
        img = np.zeros((720, 1280, 3), dtype=np.uint8)

    print("Running inference...")
    start = time.time()
    results = model.predict(img)
    end = time.time()
    print(f"Inference time: {end - start:.4f}s")
    
    print("Success!")

except Exception as e:
    print(f"Error: {e}")
