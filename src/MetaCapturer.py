import sys
import os
import shutil
import hashlib
from sqlalchemy import create_engine, inspect, text



from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QTextEdit, QPushButton, QDialog, 
                             QDialogButtonBox, QMessageBox, QCheckBox)

import json
with open("src/MetaCapturer_config.json", "r") as f:  ### THIS WILL WANT TO BE ULTIMATELY REPLACED BY SOMETHING COMING DOWN THROUGH A LOGIN PAGE CONNECTED TO THE USER
    config = json.load(f)


### Custom functions, methods and widgets supporting the page-----------------------------------------

def calculate_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def return_one_column(db_keys, table, column):
    """
    This function searches a postgres DB using SQLAlchemy and returns a single column as a python dictionary.
    TODO: extend to allow filtering.

    *Arguments*
    - column (str): name of column to be selected
    - table (str): name of the table to be selected
    - db_keys (str): path to .json file containing the DB keys
    - dict_name (str): name to be attributer to the dictionary, e.g. if it is "Sample", the dictionary returned by the function will be: {"Sample": [value_1, value_2, value_3]}

    Returns:
    - list: a list of column values   
    
    """

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

    return values


def collate_dropdowns(dropdown_inputs, db_keys):
    """
    This method runs the return_one_column method to generate dictionary inputs for creating dropdowns
    
    *Args:*
    - dropdown_inputs(list): a list of lists containing inputs for the return_one_column ordered as (table, column, dict_name)
    - db_keys (str): path to the db keys used by the return_one_column

    *Returns*
    - dictionary: a dictionary consisting of each of the lists returned by return_one_column (e.g. {"item1": ["value1", "value2"], "item2: ["value1", "value2"]}
    """

    dropdown_config = {}
    
    for dropdown_input in dropdown_inputs:
        values = return_one_column(db_keys, dropdown_input[0], dropdown_input[1])
        dropdown_config[dropdown_input[2]] = values

    # print(dropdown_config)
    return dropdown_config






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
        self.db_keys = config["db_keys"] ## Has to go before initUI
        self.src_dir = config["src_dir"]
        self.dst_dir = config["dst_dir"]
        # self.renaming_convention = config["renaming_convention"]
        print(self.src_dir)
        print(self.dst_dir)
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

        dropdown_inputs = config["dropdown_inputs"]  # List of (table, column, dict_name) tuples
        dropdowns_to_print = collate_dropdowns(dropdown_inputs, self.db_keys)
        print(dropdowns_to_print)

        src_dir = config["src_dir"]
        dst_dir = config["dst_dir"]

        # print(src_dir)
        # print(dst_dir)
        
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
        layout.addWidget(QLabel("Comments:"))
        layout.addWidget(self.comments)

        ### "Sensitive data" as a tick box
        self.sensitive_checkbox = QCheckBox("Sensitive Data")  # Set the label for the checkbox
        self.sensitive_checkbox.setChecked(False)
        layout.addWidget(self.sensitive_checkbox)



        ### Stage button
        self.stage_button = QPushButton("Stage")
        self.stage_button.clicked.connect(self.stage_dialog)
        layout.addWidget(self.stage_button)
        

        self.setLayout(layout)
    
        # Set some default size
        self.setWindowTitle('MetaCapturer')


    def move_files(self):
        try:
            for filename in os.listdir(self.src_dir):
                src_file = os.path.join(self.src_dir, filename)
                dst_file = os.path.join(self.dst_dir, filename)
                
                if os.path.isfile(src_file):
                    # Calculate checksum of source file
                    src_checksum = calculate_checksum(src_file)
                    creation_time = os.path.getctime(src_file)
                    
                    # Copy the file, preserving as much metadata as possible
                    shutil.copy2(src_file, dst_file)
                    
                    # Set the creation time on the destination file
                    if os.name == 'nt':  # Windows -- Should be redundant if shipped with Docker :)
                        import win32_setctime
                        win32_setctime.setctime(dst_file, creation_time)
                    else:  # Unix-like systems
                        os.utime(dst_file, (creation_time, os.path.getmtime(dst_file)))
                    
                    # Calculate checksum of destination file
                    dst_checksum = calculate_checksum(dst_file)
                    
                    # Compare checksums
                    if src_checksum == dst_checksum:
                        # Remove the original file only if checksums match
                        os.remove(src_file)
                    else:
                        # If checksums don't match, remove the copied file and raise an error
                        os.remove(dst_file)
                        raise ValueError(f"Checksum mismatch for file: {filename}")
            
            QMessageBox.information(self, "Success", "All files have been moved successfully!")
        except (OSError, shutil.Error, ValueError) as e:
            QMessageBox.critical(self, "Error", f"An error occurred while moving files: {str(e)}")

    
    def rename_files(self):
        """
        Rename a file based on its creation time and user-defined naming requirements.
    
        This function generates a new filename for the given file. The new name consists of:
        1. The file's creation timestamp in 'yyyymmdd_hhmmss' format.
        2. Additional components as specified in the naming_reqs list, with values drawn from naming_dict.
        3. The original file extension.
    
        The naming convention is configurable through the config file, allowing users to easily
        customize the filename structure to their needs.
    
        Args:
        filepath (str): The full path to the original file.
        naming_reqs (list): A list of strings specifying additional components to include in the filename.
                            These components are defined in the config file.
        naming_dict (dict): A dictionary mapping naming requirement keys to their corresponding values.
    
        Returns:
        str: The new filename, including the file extension.
    
        Example:
        If filepath is '/path/to/image.jpg', naming_reqs is ['user', 'instrument'],
        and naming_dict is {'user': 'john', 'instrument': 'microscope'},
        the function might return '20230615_142230_john_microscope.jpg'.
    
        Note:
        - The first component of the new filename will always be the file creation time.
        - The function assumes that all keys in naming_reqs are present in naming_dict.
        - The original file extension is preserved.
        """
        pass



    
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
            layout.addWidget(QLabel(f"{name} {dropdown.currentText()}"))
        
        layout.addWidget(QLabel(f"Comments: {self.comments.toPlainText()}"))

        sensitive_state = "Yes" if self.sensitive_checkbox.isChecked() else "No"
        layout.addWidget(QLabel(f"Sensitive Data: {sensitive_state}"))
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(lambda: self.final_confirm(dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.move_files()  # Only move files if the dialog was accepted
            self.rename_files() # Rename files in the dst_dir after this gets triggered.

    
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