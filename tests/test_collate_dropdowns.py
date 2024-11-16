import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import unittest
from unittest.mock import patch, MagicMock
from MetaCapturer import collate_dropdowns, return_one_column

class TestCollateDropdowns(unittest.TestCase):
    @patch("MetaCapturer.return_one_column")  # Mock the return_one_column function
    def test_collate_dropdowns(self, mock_return_one_column):
        """
        Test the collate_dropdowns function for correctly collating dropdown inputs into a dictionary.
        """
        # Mock inputs
        dropdown_inputs = [
            ["table1", "column1", "Dropdown1"],
            ["table2", "column2", "Dropdown2"],
        ]
        db_keys = "mock_db_keys.json"

        # Mock the return values of return_one_column
        mock_return_one_column.side_effect = [
            ["value1", "value2", "value3"],  # For the first call
            ["valueA", "valueB", "valueC"],  # For the second call
        ]

        # Call the collate_dropdowns function
        result = collate_dropdowns(dropdown_inputs, db_keys)

        # Expected output
        expected_result = {
            "Dropdown1": ["value1", "value2", "value3"],
            "Dropdown2": ["valueA", "valueB", "valueC"],
        }

        # Assertions
        self.assertEqual(result, expected_result)

        # Check that return_one_column was called with the correct arguments
        mock_return_one_column.assert_any_call(db_keys, "table1", "column1")
        mock_return_one_column.assert_any_call(db_keys, "table2", "column2")
        self.assertEqual(mock_return_one_column.call_count, len(dropdown_inputs))

if __name__ == "__main__":
    unittest.main()
