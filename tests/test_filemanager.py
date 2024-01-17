import unittest
import hashlib
import tempfile
import os
import uuid

from py_openai_assistant.Assistant import Assistant
from py_openai_assistant.FileManager import FileManager


class TestFileManager(unittest.TestCase):
    env_file = None
    assistant = None
    file_manager = None

    @classmethod
    def setUpClass(cls):

        # Initialize Assistant and FileManager with the path to the temporary .env file
        cls.assistant = Assistant()
        cls.assistant.create_assistant("Test Assistant")
        cls.file_manager = FileManager(cls.assistant)

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary .env file
        cls.file_manager.file_db.clear()
        cls.file_manager.file_db.close()
        cls.assistant.delete_assistant_by_id(cls.assistant.assistant_id)

    def test_upload_file(self):
        # Create a temporary file to upload
        file_id = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp_file:
                tmp_file.write(str(uuid.uuid4()))
                tmp_file_name = tmp_file.name

            # Generate a key based on the file name
            key = os.path.basename(tmp_file_name)

            # Upload the file using FileManager and get the file_id
            file_id = self.file_manager.upload_file(tmp_file_name, key)

            # Get the uploaded file IDs from the assistant
            uploaded_file_ids = self.file_manager.get_uploaded_file_ids()

            # Assertions
            self.assertIn(file_id, uploaded_file_ids, "Uploaded file ID should be in the list of uploaded file IDs")
        finally:
            os.remove(tmp_file_name)
            if file_id is not None:
                self.file_manager.delete_file(file_id)

    def test_calculate_file_hash(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"Test data")
            tmp_file_name = tmp_file.name

        expected_hash = hashlib.sha256(b"Test data").hexdigest()
        calculated_hash = self.file_manager.calculate_file_hash(tmp_file_name)
        os.remove(tmp_file_name)

        self.assertEqual(calculated_hash, expected_hash)

    def test_has_file_changed(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"Test data")
            tmp_file_name = tmp_file.name

        # Calculate the hash of the temporary file
        new_hash = self.file_manager.calculate_file_hash(tmp_file_name)

        # Read the last hash from db
        last_hash = 0

        # Check if the file has changed
        file_changed, calculated_hash = self.file_manager.has_file_changed(tmp_file_name, last_hash)

        # Test assertions
        self.assertTrue(file_changed)
        self.assertEqual(calculated_hash, new_hash)

        # Cleanup: Remove the temporary file
        os.remove(tmp_file_name)

    def test_delete_all_files(self):
        test_files = ['test_file1.txt', 'test_file2.txt']
        try:
            # Create and upload multiple mock files for testing
            for file_name in test_files:
                with open(file_name, 'w') as file:
                    file.write('Test content for ' + file_name)
                self.assertIsNotNone(self.file_manager.upload_file(file_name, file_name))

            # Call delete_all_files
            self.assertTrue(self.file_manager.delete_all_files())

            # Verify that no files are left associated with the assistant
            remaining_files = self.file_manager.get_uploaded_file_ids()
            self.assertEqual(len(remaining_files), 0)

        finally:
            # Clean up the created test files
            for file_name in test_files:
                if os.path.exists(file_name):
                    os.remove(file_name)


if __name__ == '__main__':
    unittest.main()
