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
            

        ### Some sample input boxes:  TODO: CONVERT TO A BUNCH OF STUFF LOADED FROM A JSON DICT!
        # self.research_group = self.NamedDropdownLayout(name="Research Group: ", combobox_inputs=["Smith", "Kowalski", "Forgeron"])
        # layout.addWidget(self.research_group)

        # self.sample_identifier = self.NamedDropdownLayout(name="Sample ID: ", combobox_inputs=["Animal 1", "Mineral 2", "Vegetable 3"])
        # layout.addWidget(self.sample_identifier)

        # self.instrument = self.NamedDropdownLayout(name="Instrument ID: ", combobox_inputs=["SEM 1", "CT 2", "Mass Spec 3"])
        # layout.addWidget(self.instrument)

        # self.operator = self.NamedDropdownLayout(name="Operator: ", combobox_inputs=["Jane Smith", "John Doe"])
        # layout.addWidget(self.operator)

        # self.measurement_type = self.NamedDropdownLayout(name="Observation Type: ", combobox_inputs=["ImageObject", "Dataset"])
        # layout.addWidget(self.measurement_type)

        # self.sensitivity = self.NamedDropdownLayout(name="Sensitivity: ", combobox_inputs=["Public repo", "Shareable", "Internal"])
        # layout.addWidget(self.sensitivity)

        # self.roc = self.NamedDropdownLayout(name="Research Crate: ", combobox_inputs=["Project 1", "Project 2", "Method development"])
        # layout.addWidget(self.roc)  

        ### Comments box
        self.comments = QTextEdit()
        layout.addWidget(QLabel("Comments"))
        layout.addWidget(self.comments)


        ### Stage button
        self.stage_button = QPushButton("Stage")
        # self.stage_button.clicked.connect(self.stage_dialog)
        layout.addWidget(self.stage_button)
        

        self.setLayout(layout)
    
        # Set some default size
        self.setWindowTitle('MetaCapturer')

    def NamedDropdownLayout(self, name, combobox_inputs):
        return NamedDropdown(name, combobox_inputs)










if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = MetaCapturer()
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")