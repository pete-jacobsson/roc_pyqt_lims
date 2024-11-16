import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QTextEdit, QPushButton, QDialog, 
                             QDialogButtonBox, QMessageBox)

import json
with open("src/MetaCapturer_config.json", "r") as f:  ### THIS WILL WANT TO BE ULTIMATELY REPLACED BY SOMETHING COMING DOWN THROUGH A LOGIN PAGE CONNECTED TO THE USER
    config = json.load(f)
    print(config)
### Custom widgets supporting the page-----------------------------------------



### Visible Widget supporting the page-----------------------------------------
class MetaCapturer(QWidget):
    """
    A PyQt6-based GUI application for capturing metadata.
    
    This widget represents the main interface for capturing metadata 
    by selecting options from dropdown menus and adding comments. The 
    information is displayed in a confirmation dialog before it is 
    staged for further processing, such as sending to the ROC creator module.
    """
    
    def __init__(self):
        """
        Initialize the MetaCapturer widget and its user interface.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Set up the user interface layout and elements.

        The UI includes:
        - Dropdowns for metadata categories defined in the configuration file.
        - A comments section for free-form input.
        - A "Stage" button to confirm and stage the entered data.
        """
        
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
        """
        Display a dialog to confirm the staged metadata.

        The dialog shows the selected values from dropdown menus and the
        comments entered. The user can confirm or cancel the staging.
        """
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
        """
        Handle the final confirmation of staged metadata.

        This method checks if all dropdown fields are filled and displays
        an appropriate message. If all fields are valid, it confirms the staging.

        Parameters:
            dialog (QDialog): The dialog instance to close after confirmation.
        """

        if any(dropdown.currentText() == "" for dropdown in self.dropdowns.values()):
            QMessageBox.warning(self, "Warning", "All fields must be filled!")
        else:
            QMessageBox.information(self, "Success", "Information confirmed!")
            dialog.accept()








if __name__ == '__main__':
    """
    Entry point of the application. Initializes the QApplication and displays
    the MetaCapturer widget.
    """
    try:
        app = QApplication(sys.argv)
        ex = MetaCapturer()
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")