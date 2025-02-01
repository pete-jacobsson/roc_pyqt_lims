import sys
import os
import json
import tempfile
import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from MetaCapturer import MetaCapturer  # Now this import will work

import unittest
from PyQt6.QtWidgets import QApplication, QDialog, QDialogButtonBox
from unittest.mock import patch
from MetaCapturer import MetaCapturer

# Initialize the QApplication once for all tests
app = QApplication([])


### Single fail on predicting population. 


class TestMetaCapturer(unittest.TestCase):
    """
    Unit tests for the MetaCapturer class.
    """

    def setUp(self):
        """
        Set up the MetaCapturer instance before each test.
        """
        # Load test configuration from JSON file
        test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.json')
        with open(test_config_path, 'r') as config_file:
            self.test_config = json.load(config_file)

        # Mock the collate_dropdowns function
        # We'll create a simple mock that returns a dictionary based on dropdown_inputs
        def mock_collate_dropdowns(dropdown_inputs, db_keys):
            return {item[2]: [f"value{i}" for i in range(1, 4)] for item in dropdown_inputs}

        # Patch the config and collate_dropdowns
        patcher1 = patch("MetaCapturer.config", self.test_config)
        patcher2 = patch("MetaCapturer.collate_dropdowns", side_effect=mock_collate_dropdowns)

        self.mock_config_patch = patcher1.start()
        self.mock_collate_patch = patcher2.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)

        # Reinitialize the widget after patching
        self.widget = MetaCapturer()

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.widget.close()

    def test_dropdown_population(self):
        """
        Test that dropdowns are dynamically populated with the correct items.
        """
        # Get the expected dropdown keys from the test_config
        expected_keys = [item[2] for item in self.test_config['dropdown_inputs']]
        actual_keys = list(self.widget.dropdowns.keys())
        self.assertListEqual(expected_keys, actual_keys)
    
        # Verify dropdown items match the values from our mock collate_dropdowns
        for key, dropdown in self.widget.dropdowns.items():
            expected_items = [""] + [f"value{i}" for i in range(1, 4)]  # Include the empty option
            actual_items = [dropdown.itemText(i) for i in range(dropdown.count())]
            self.assertListEqual(expected_items, actual_items)
    
        # Verify collate_dropdowns was called with the correct arguments
        self.mock_collate_patch.assert_called_once_with(
            self.test_config['dropdown_inputs'],
            self.test_config['db_keys']
        )

    def test_comments_section(self):
        """
        Test that the comments section exists and can accept text.
        """
        self.assertIsNotNone(self.widget.comments)
        test_text = "Test comment"
        self.widget.comments.setText(test_text)
        self.assertEqual(self.widget.comments.toPlainText(), test_text)

    def test_stage_dialog_all_fields_filled(self):
        """
        Test that the stage dialog works when all fields are filled.
        """
        for dropdown in self.widget.dropdowns.values():
            dropdown.setCurrentIndex(1)  # Select the first non-empty item
        
        self.widget.comments.setText("This is a test comment")

        with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
            self.widget.stage_dialog()
            dialog = self.widget.findChild(QDialog)
            buttons = dialog.findChild(QDialogButtonBox)
            buttons.button(QDialogButtonBox.StandardButton.Ok).click()

            # Verify success message is shown
            mock_info.assert_called_once_with(self.widget, "Success", "Information confirmed!")

    def test_stage_dialog_all_fields_filled(self):
        """
        Test that the stage dialog works when all fields are filled.
        """
        for dropdown in self.widget.dropdowns.values():
            dropdown.setCurrentIndex(1)  # Select valid items
        
        with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
            dialog = QDialog()
            self.widget.final_confirm(dialog)
            
            self.assertTrue(dialog.result() == QDialog.DialogCode.Accepted)
            mock_info.assert_called_once_with(self.widget, "Success", "Information confirmed!")


    def test_final_confirm_all_fields_filled(self):
        """
        Test final confirmation with all fields filled.
        """
        for dropdown in self.widget.dropdowns.values():
            dropdown.setCurrentIndex(1)  # Select valid items
        
        with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
            dialog = QDialog()
            self.widget.final_confirm(dialog)
            
            # Verify dialog acceptance and success message
            self.assertTrue(dialog.result() == QDialog.DialogCode.Accepted)
            mock_info.assert_called_once_with(self.widget, "Success", "Information confirmed!")

    def test_stage_dialog_missing_field(self):
        """
        Test that the stage dialog shows a warning if any field is missing.
        """
        for i, dropdown in enumerate(self.widget.dropdowns.values()):
            if i == 0:
                dropdown.setCurrentIndex(0)  # Leave one field blank
            else:
                dropdown.setCurrentIndex(1)  # Select valid items
        
        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            dialog = QDialog()
            self.widget.final_confirm(dialog)
            
            self.assertTrue(dialog.result() != QDialog.DialogCode.Accepted)
            mock_warning.assert_called_once_with(self.widget, "Warning", "All fields must be filled!")


    def test_src_and_dst_dirs(self):
        self.assertEqual(self.widget.src_dir, self.test_config['src_dir'])
        self.assertEqual(self.widget.dst_dir, self.test_config['dst_dir'])

    
    def test_move_files(self):
        # Create some test files in the src_dir
        for i in range(3):
            with open(os.path.join(self.test_config['src_dir'], f'test_file_{i}.txt'), 'w') as f:
                f.write(f'Test content {i}')
    
        self.widget.move_files()
    
        # Check that files have been moved to dst_dir
        for i in range(3):
            self.assertTrue(os.path.exists(os.path.join(self.test_config['dst_dir'], f'test_file_{i}.txt')))

    def test_file_renaming(self):
        """
        Test that files are renamed correctly after moving.
        """
        # Create a temporary source directory
        with tempfile.TemporaryDirectory() as temp_src_dir:
            self.widget.src_dir = temp_src_dir
            
            # Create a temporary destination directory
            with tempfile.TemporaryDirectory() as temp_dst_dir:
                self.widget.dst_dir = temp_dst_dir
                
                # Create a test file
                test_filename = "test_file.txt"
                test_filepath = os.path.join(temp_src_dir, test_filename)
                with open(test_filepath, 'w') as f:
                    f.write("Test content")
                
                # Set creation time to a known value
                test_creation_time = datetime.datetime(2023, 6, 15, 14, 30, 0).timestamp()
                os.utime(test_filepath, (test_creation_time, test_creation_time))
                
                # Mock the naming requirements and dictionary
                self.widget.naming_reqs = ["user", "instrument"]
                self.widget.naming_dict = {"user": "john", "instrument": "microscope"}
                
                # Move and rename the file
                self.widget.move_files()
                
                # Check if the file was renamed correctly
                expected_filename = "20230615_143000_john_microscope.txt"
                self.assertTrue(os.path.exists(os.path.join(temp_dst_dir, expected_filename)))
                
                # Check that the original file no longer exists in the source directory
                self.assertFalse(os.path.exists(test_filepath))

if __name__ == "__main__":
    unittest.main()
