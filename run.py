import sys
import logging
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.config import LOG_LEVEL, LOG_FORMAT

def main():
    # Configure Logging
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    app = QApplication(sys.argv)
    
    # Set Application Metadata
    app.setApplicationName("BlurOBS")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
