import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


import unittest
from unittest.mock import patch, MagicMock
from MetaCapturer import return_one_column
import json

class TestReturnOneColumn(unittest.TestCase):
    @patch("MetaCapturer.create_engine")  # Mock SQLAlchemy's create_engine
    @patch("MetaCapturer.inspect")       # Mock SQLAlchemy's inspect
    def test_return_one_column(self, mock_inspect, mock_create_engine):
        """
        Test the `return_one_column` function for correct database querying and dictionary creation.
        """
        # Mock database keys
        mock_db_keys = {
            "db_host": "localhost",
            "db_name": "testdb",
            "db_username": "testuser",
            "db_password": "testpass",
            "db_port": "54321"
        }
        
        # Mock the db_keys JSON file
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(mock_db_keys))):
            
            # Mock the SQLAlchemy engine and connection
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            mock_connection = mock_engine.connect.return_value.__enter__.return_value
            
            # Mock the SQLAlchemy inspector
            mock_inspector = MagicMock()
            mock_inspect.return_value = mock_inspector
            
            # Mock table data
            column_name = "column_name"
            table_name = "table_name"
            mock_query_result = [
                ("value1",),
                ("value2",),
                ("value3",),
            ]
            
            # Mock execution of SQL query
            mock_connection.execute.return_value.fetchall.return_value = mock_query_result
            
            # Call the function
            result = return_one_column(
                column=column_name,
                table=table_name,
                db_keys="mock_db_keys.json",
                dict_name="Sample"
            )
            
            # Assertions
            mock_create_engine.assert_called_once_with(
                f"postgresql://{mock_db_keys['db_username']}:{mock_db_keys['db_password']}@{mock_db_keys['db_host']}:{mock_db_keys['db_port']}/{mock_db_keys['db_name']}"
            )
            # mock_connection.execute.assert_called_once_with(f"SELECT {column_name} FROM {table_name}")
            self.assertEqual(result, {"Sample": ["value1", "value2", "value3"]})

if __name__ == "__main__":
    unittest.main()
