import os
import unittest
import openai
from py_openai_assistant.Assistant import Assistant


class TestAssistant(unittest.TestCase):
    assistant = None

    @classmethod
    def setUpClass(cls):
        # Initialize the Assistant class
        cls.assistant = Assistant(api_key=os.getenv("OPENAI_API_KEY"))

    @classmethod
    def tearDownClass(cls):
        cls.assistant.delete_by_id(cls.assistant.assistant_id)

    def test_create_assistant(self):
        # Create an assistant and test its creation
        response = self.assistant.create("Test Assistant")
        # Assuming a method to verify if an assistant exists
        self.assertTrue(self.assistant.client.beta.assistants.retrieve(assistant_id=self.assistant.assistant_id))
        self.assistant.delete_by_id(self.assistant.assistant_id)

    def test_delete_all_assistants(self):
        # Create a few assistants
        for i in range(3):
            self.assistant.create(f"Test Assistant {i}")

        # Test the delete_all_assistants method
        self.assistant.delete_all_assistants()
        # Assuming a method to get all assistants
        assistants = self.assistant.client.beta.assistants.list()
        self.assertEqual(len(self.assistant.client.beta.assistants.list().data), 0)

    def test_delete_assistant_by_id(self):
        # Create an assistant to delete
        self.assistant.create("Test Assistant for Deletion by ID")

        # Test the delete_assistant_by_id method
        self.assistant.delete_by_id(self.assistant.assistant_id)
        with self.assertRaises(openai.NotFoundError):
            self.assistant.client.beta.assistants.retrieve(assistant_id=self.assistant.assistant_id)

    def test_delete_assistant_by_name(self):
        # Create an assistant to delete
        name = "Test Assistant for Deletion by Name"
        self.assistant.create(name)

        # Test the delete_assistant_by_name method
        self.assistant.delete_by_name(name)
        self.assertFalse(self.assistant.get_by_name(name))


if __name__ == '__main__':
    unittest.main()
