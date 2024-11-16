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


class TestMetaCapturer(unittest.TestCase):
    """
    Unit tests for the MetaCapturer class.
    """

    def setUp(self):
        """
        Set up the MetaCapturer instance before each test.
        """
        self.widget = MetaCapturer()
        # Load the config from the JSON file
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/MetaCapturer_config.json'))
        with open(config_path, "r") as f:
            self.config = json.load(f)

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.widget.close()

    def test_dropdown_population(self):
        """
        Test that dropdowns are populated with the correct items from the config.
        """
        # Test if dropdowns were created for all keys in the config
        expected_keys = list(self.widget.dropdowns.keys())
        actual_keys = list(self.config["dropdowns"].keys())
        self.assertListEqual(expected_keys, actual_keys)

        # Test if each dropdown contains the correct items
        for key, dropdown in self.widget.dropdowns.items():
            expected_items = [""] + self.config["dropdowns"][key]  # Include the empty option
            actual_items = [dropdown.itemText(i) for i in range(dropdown.count())]
            self.assertListEqual(expected_items, actual_items)

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

    def test_stage_dialog_missing_field(self):
        """
        Test that the stage dialog shows a warning if any field is missing.
        """
        # Leave one dropdown empty
        for i, dropdown in enumerate(self.widget.dropdowns.values()):
            if i == 0:  # Leave the first dropdown empty
                dropdown.setCurrentIndex(0)
            else:
                dropdown.setCurrentIndex(1)  # Select valid items for other dropdowns
        
        self.widget.comments.setText("This is a test comment")

        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            self.widget.stage_dialog()
            dialog = self.widget.findChild(QDialog)
            buttons = dialog.findChild(QDialogButtonBox)
            buttons.button(QDialogButtonBox.StandardButton.Ok).click()

            # Verify warning message is shown
            mock_warning.assert_called_once_with(self.widget, "Warning", "All fields must be filled!")

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
            self.assertTrue(dialog.result() == QDialog.Accepted)
            mock_info.assert_called_once_with(self.widget, "Success", "Information confirmed!")

    def test_final_confirm_missing_field(self):
        """
        Test final confirmation with a missing field.
        """
        for i, dropdown in enumerate(self.widget.dropdowns.values()):
            if i == 0:  # Leave the first dropdown empty
                dropdown.setCurrentIndex(0)
            else:
                dropdown.setCurrentIndex(1)  # Select valid items for other dropdowns

        with patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warning:
            dialog = QDialog()
            self.widget.final_confirm(dialog)
            
            # Verify dialog rejection and warning message
            self.assertFalse(dialog.result() == QDialog.Accepted)
            mock_warning.assert_called_once_with(self.widget, "Warning", "All fields must be filled!")


if __name__ == "__main__":
    unittest.main()
