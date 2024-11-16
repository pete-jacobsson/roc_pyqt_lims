import sys
from sqlalchemy import create_engine, inspect, text



from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QTextEdit, QPushButton, QDialog, 
                             QDialogButtonBox, QMessageBox)

import json
with open("src/MetaCapturer_config.json", "r") as f:  ### THIS WILL WANT TO BE ULTIMATELY REPLACED BY SOMETHING COMING DOWN THROUGH A LOGIN PAGE CONNECTED TO THE USER
    config = json.load(f)


### Custom functions, methods and widgets supporting the page-----------------------------------------


def return_one_column(column, table, db_keys, dict_name = None):
    """
    This function searches a postgres DB using SQLAlchemy and returns a single column as a python dictionary.
    TODO: extend to allow filtering.

    *Arguments*
    - column (str): name of column to be selected
    - table (str): name of the table to be selected
    - db_keys (str): path to .json file containing the DB keys
    - dict_name (str): name to be attributer to the dictionary, e.g. if it is "Sample", the dictionary returned by the function will be: {"Sample": [value_1, value_2, value_3]}

    Returns:
    - dictionary: a dictionary containing of dictionary name and column values   
    
    """
    # Set the end dict name
    if dict_name is None:
        dict_name = column

    # Get the leys
    with open(db_keys, "r") as f:
        keys_dict = json.load(f)

    db_username = keys_dict["db_username"]
    db_password = keys_dict["db_password"]
    db_name = keys_dict["db_name"]
    db_host = keys_dict["db_host"]
    db_port = keys_dict["db_port"]

    connection_string = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    engine = create_engine(connection_string)

    query = text(f"SELECT {column} FROM {table};")

    values = []
    with engine.connect() as connection:
        result = connection.execute(query)
        # Extract the values from the result and return as a list
        for row in result.fetchall():
            values.append(row[0])

    outcome_dict = {dict_name: values}
    return outcome_dict


def collate_dropdowns()







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
        self.db_keys = config["db_keys"]


    
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
        print(dropdowns_to_print)
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


        ### Re-introduce "Sensitive data" as a tick box


        ### Stage button
        self.stage_button = QPushButton("Stage")
        self.stage_button.clicked.connect(self.stage_dialog)
        layout.addWidget(self.stage_button)
        

        self.setLayout(layout)
    
        # Set some default size
        self.setWindowTitle('MetaCapturer')

    
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
            dialog.done(QDialog.DialogCode.Accepted)











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