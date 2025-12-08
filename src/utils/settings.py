import json
import os
import logging

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "obs_width": 1280,
    "obs_height": 720,
    "fps": 30,
    "confidence_threshold": 0.5,
    "target_classes": [67],  # Default: Cell Phone
    "auto_blur": True,
    "show_preview": False,
    "use_custom_model": False, # False = Standard COCO, True = YOLO-World
    "custom_classes": ["credit card", "debit card", "id card", "passport", "driver license", "holding a credit card"], # Default custom prompts
    "confidence_threshold": 0.25 # Lower default for better detection
}

# Common COCO Classes for the UI
AVAILABLE_CLASSES = {
    0: "Person",
    67: "Cell Phone",
    63: "Laptop",
    64: "Mouse",
    66: "Keyboard",
    39: "Bottle",
    41: "Cup",
    73: "Book",
    24: "Backpack",
    26: "Handbag",
    77: "Teddy Bear"
}

class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                logging.error(f"Failed to load settings: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()

# Global instance
settings_manager = SettingsManager()
