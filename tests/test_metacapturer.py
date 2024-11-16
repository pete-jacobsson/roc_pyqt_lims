import sys
import os
import json
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
        # Mock dropdown inputs and config
        self.mock_dropdown_inputs = [
            ("table1", "column1", "Dropdown1"),
            ("table2", "column2", "Dropdown2"),
        ]
        self.mock_config = {
            "db_keys": "mock_db_keys.json",
            "dropdown_inputs": self.mock_dropdown_inputs,
        }

        # Mock dropdown results returned by collate_dropdowns
        self.mock_dropdown_data = {
            "Dropdown1": ["value1", "value2", "value3"],
            "Dropdown2": ["valueA", "valueB", "valueC"],
        }

        # Patch the config and collate_dropdowns
        patcher1 = patch("MetaCapturer.config", self.mock_config)
        patcher2 = patch("MetaCapturer.collate_dropdowns", return_value=self.mock_dropdown_data)

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
        # Verify dropdown keys match the dictionary keys from collate_dropdowns
        expected_keys = list(self.mock_dropdown_data.keys())
        actual_keys = list(self.widget.dropdowns.keys())
        self.assertListEqual(expected_keys, actual_keys)

        # Verify dropdown items match the values from collate_dropdowns
        for key, dropdown in self.widget.dropdowns.items():
            expected_items = [""] + self.mock_dropdown_data[key]  # Include the empty option
            actual_items = [dropdown.itemText(i) for i in range(dropdown.count())]
            self.assertListEqual(expected_items, actual_items)

        # Verify collate_dropdowns was called with the correct arguments
        self.mock_collate_patch.assert_called_once_with(self.mock_dropdown_inputs, "mock_db_keys.json")

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


if __name__ == "__main__":
    unittest.main()
