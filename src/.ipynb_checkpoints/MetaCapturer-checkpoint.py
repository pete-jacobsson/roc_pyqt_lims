import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QTextEdit, QPushButton, QDialog, 
                             QDialogButtonBox, QMessageBox)

import json
with open("src/MetaCapturer_config.json", "r") as f:
    config = json.load(f)
    print(config)
### Custom widgets supporting the page-----------------------------------------



### Visible Widget supporting the page-----------------------------------------
class MetaCapturer(QWidget):
    """
    This class covers the window that does the metadata capture.
    Ultimately it will take in the info from an SQLite DB and send added info to the ROC creator module.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        dropdowns_to_print = config["dropdowns"]
        self.dropdowns = {}
        for key, value in dropdowns_to_print.items():
            hbox = QHBoxLayout()
            label = QLabel(key)
            dropdown = QComboBox()
            dropdown.addItem("")  # Empty option
            dropdown.addItems(value)
            hbox.addWidget(label)
            hbox.addWidget(dropdown)
            layout.addLayout(hbox)
            self.dropdowns[key] = dropdown             

        ### Comments box
        self.comments = QTextEdit()
        layout.addWidget(QLabel("Comments"))
        layout.addWidget(self.comments)


        ### Stage button
        self.stage_button = QPushButton("Stage")
        self.stage_button.clicked.connect(self.stage_dialog)
        layout.addWidget(self.stage_button)
        

        self.setLayout(layout)
    
        # Set some default size
        self.setWindowTitle('MetaCapturer')

    def NamedDropdownLayout(self, name, combobox_inputs):
        return NamedDropdown(name, combobox_inputs)

    
    def stage_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm ROC generation")
        
        layout = QVBoxLayout()
        
        for name, dropdown in self.dropdowns.items():
            layout.addWidget(QLabel(f"{name}: {dropdown.currentText()}"))
        
        layout.addWidget(QLabel(f"Comments: {self.comments.toPlainText()}"))
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(lambda: self.final_confirm(dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()

    
    def final_confirm(self, dialog):
        if any(dropdown.currentText() == "" for dropdown in self.dropdowns.values()):
            QMessageBox.warning(self, "Warning", "All fields must be filled!")
        else:
            QMessageBox.information(self, "Success", "Information confirmed!")
            dialog.accept()








if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = MetaCapturer()
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")