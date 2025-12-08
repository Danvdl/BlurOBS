from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel, 
    QGridLayout, QGroupBox, QDialogButtonBox, QRadioButton, QButtonGroup,
    QLineEdit, QWidget, QSlider
)
from PyQt6.QtCore import Qt
from src.utils.settings import settings_manager, AVAILABLE_CLASSES

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 600)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        
        layout = QVBoxLayout(self)
        
        # --- Model Selection ---
        model_group = QGroupBox("Detection Mode")
        model_layout = QVBoxLayout()
        
        self.mode_group = QButtonGroup(self)
        self.radio_standard = QRadioButton("Standard (Fast - Predefined Objects)")
        self.radio_custom = QRadioButton("Security / Custom (Slower - Custom Prompts)")
        
        self.mode_group.addButton(self.radio_standard)
        self.mode_group.addButton(self.radio_custom)
        
        if settings_manager.get("use_custom_model"):
            self.radio_custom.setChecked(True)
        else:
            self.radio_standard.setChecked(True)
            
        self.radio_standard.toggled.connect(self.toggle_mode_ui)
        
        model_layout.addWidget(self.radio_standard)
        model_layout.addWidget(self.radio_custom)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # --- Sensitivity (Confidence) ---
        sens_group = QGroupBox("Sensitivity")
        sens_layout = QVBoxLayout()
        
        self.conf_label = QLabel()
        current_conf = settings_manager.get("confidence_threshold")
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setRange(1, 99)
        self.conf_slider.setValue(int(current_conf * 100))
        self.conf_slider.valueChanged.connect(self.update_conf_label)
        self.update_conf_label(self.conf_slider.value())
        
        sens_layout.addWidget(self.conf_label)
        sens_layout.addWidget(self.conf_slider)
        sens_group.setLayout(sens_layout)
        layout.addWidget(sens_group)

        # --- Standard Object Detection Settings ---
        self.obj_group = QGroupBox("Standard Objects")
        obj_layout = QGridLayout()
        
        self.checkboxes = {}
        current_targets = settings_manager.get("target_classes")
        
        row, col = 0, 0
        for cls_id, name in AVAILABLE_CLASSES.items():
            cb = QCheckBox(name)
            cb.setChecked(cls_id in current_targets)
            self.checkboxes[cls_id] = cb
            obj_layout.addWidget(cb, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        self.obj_group.setLayout(obj_layout)
        layout.addWidget(self.obj_group)
        
        # --- Custom / Security Settings ---
        self.custom_group = QGroupBox("Custom Security Prompts")
        custom_layout = QVBoxLayout()
        
        custom_layout.addWidget(QLabel("Enter objects to detect (comma separated):"))
        custom_layout.addWidget(QLabel("Examples: credit card, id card, passport, document with text"))
        
        self.custom_input = QLineEdit()
        current_custom = settings_manager.get("custom_classes")
        self.custom_input.setText(", ".join(current_custom))
        custom_layout.addWidget(self.custom_input)
        
        self.custom_group.setLayout(custom_layout)
        layout.addWidget(self.custom_group)
        
        # Initial UI State
        self.toggle_mode_ui()

        # --- Buttons ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def update_conf_label(self, value):
        self.conf_label.setText(f"Confidence Threshold: {value}% (Lower = More Sensitive)")

    def toggle_mode_ui(self):
        is_standard = self.radio_standard.isChecked()
        self.obj_group.setVisible(is_standard)
        self.custom_group.setVisible(not is_standard)

    def accept(self):
        # Save settings
        
        # 1. Mode
        use_custom = self.radio_custom.isChecked()
        settings_manager.set("use_custom_model", use_custom)
        
        # 2. Confidence
        conf = self.conf_slider.value() / 100.0
        settings_manager.set("confidence_threshold", conf)
        
        # 3. Standard Targets
        new_targets = []
        for cls_id, cb in self.checkboxes.items():
            if cb.isChecked():
                new_targets.append(cls_id)
        settings_manager.set("target_classes", new_targets)
        
        # 4. Custom Prompts
        raw_text = self.custom_input.text()
        custom_list = [x.strip() for x in raw_text.split(",") if x.strip()]
        if not custom_list:
            custom_list = ["credit card"] # Fallback
        settings_manager.set("custom_classes", custom_list)
        
        super().accept()
        
        settings_manager.set("target_classes", new_targets)
        super().accept()
