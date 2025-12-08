DARK_THEME = """
QMainWindow {
    background-color: #121212;
    color: #ffffff;
}
QWidget {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
    padding: 5px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #555;
    background: #2d2d2d;
}
QCheckBox::indicator:checked {
    background-color: #6200ee;
    border-color: #6200ee;
    image: url(none); /* You can add a checkmark icon here if you have resources */
}
QCheckBox::indicator:hover {
    border-color: #888;
}
QLabel {
    color: #ffffff;
}
QGroupBox {
    border: 1px solid #333333;
    border-radius: 6px;
    margin-top: 20px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #bbbbbb;
}
QStatusBar {
    background-color: #1e1e1e;
    color: #aaaaaa;
    border-top: 1px solid #333;
}
QPushButton {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 6px 12px;
    color: white;
}
QPushButton:hover {
    background-color: #444444;
}
QPushButton:pressed {
    background-color: #222222;
}
"""
