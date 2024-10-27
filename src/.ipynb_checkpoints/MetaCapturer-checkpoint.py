import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QTextEdit, QPushButton, QDialog, 
                             QDialogButtonBox, QMessageBox)

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

        ### Some sample input boxes:
        research_group = self.NamedDropdownLayout(name = "Research Group: ", combobox_inputs = ["Smith", "Kowalski", "Forgeron"])
        layout.addLayout(research_group)


        self.setLayout(layout)
    
        # Set some default size
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('MetaCapturer')





    def NamedDropdownLayout(self, name, combobox_inputs):
        """
        A named dropdown widget. Takes on a name of a combo box, a list of options, adds an empty option.
        """
        hbox = QHBoxLayout()
        label = QLabel(name)
        dropdown = QComboBox()
        dropdown.addItem("")
        dropdown.addItems(combobox_inputs)
        hbox.addWidget(label)
        hbox.addWidget(dropdown)
        return hbox


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = MetaCapturer()
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")