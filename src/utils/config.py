import logging

# Camera Settings
OBS_WIDTH = 1280
OBS_HEIGHT = 720
FPS = 30

# AI Settings
CONFIDENCE_THRESHOLD = 0.5
# YOLO classes to automatically censor (e.g., 67=cell phone)
TARGET_CLASSES = [67] 

# Logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
