import hashlib
import shelve
from openai.types.beta import Assistant


class FileManager:
    def __init__(self, assistant: Assistant, folder="./text_data"):
        self.assistant = assistant
        self.folder = folder
        self.file_db = shelve.open("files", writeback=True, flag = "n")

    def calculate_file_hash(self, filepath):
        hash_sha256 = hashlib.sha256()
        with open(filepath, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def has_file_changed(self, filepath, last_hash):
        """Check if the file has changed since the last hash."""
        current_hash = self.calculate_file_hash(filepath)
        return current_hash != last_hash, current_hash

    def upload_file(self, file_path, key):
        """Upload the file if it has changed."""
        try:
            last_uploaded_hash = self.file_db[key]
        except KeyError:
            last_uploaded_hash = 0

        changed, new_hash = self.has_file_changed(file_path, last_uploaded_hash)

        if changed:  # File has changed, upload it
            file = self.assistant.client.files.create(
                file=open(file_path, "rb"),
                purpose="assistants",
            )
            self.file_db[key] = new_hash

            file_ids = self.get_uploaded_file_ids()
            file_ids.append(file.id)

            # Update the assistant with the new file
            response = self.assistant.client.beta.assistants.update(
                self.assistant.assistant_id,
                tools=[{"type": "retrieval"}],
                file_ids=file_ids,
            )
            if file.id not in response.file_ids:
                raise Exception(f"File with ID {file.id} could not attached to assistant")
            print(f"Assistant updated successfully with file {file_path}.")
            return file.id
        else:
            print(f"File {file_path} hasn't changed, no need to upload.")
            return None

    def get_uploaded_file_ids(self):
        assistant = self.assistant.client.beta.assistants.retrieve(assistant_id=self.assistant.assistant_id)
        return assistant.file_ids

    def delete_file(self, file_id):
        """Delete a file from the assistant."""
        file_ids = self.get_uploaded_file_ids()
        file_ids.remove(file_id)
        try:
            response = self.assistant.client.beta.assistants.update(
                self.assistant.assistant_id,
                tools=[{"type": "retrieval"}],
                file_ids=file_ids,
            )
            if file_id not in response.file_ids:
                print(f"File {file_id} has been deleted.")
                return True
            else:
                return False
        except Exception as e:
            print("Error:", e)

    def delete_all_files(self):
        """Delete all files from the assistant."""

        # And therein lies the magic, we just need to wipe teh file_ids list
        try:
            response = self.assistant.client.beta.assistants.update(
                self.assistant.assistant_id,
                tools=[{"type": "retrieval"}],
                file_ids=[],
            )
            if len(response.file_ids) == 0:
                print("All files have been deleted.")
                return True
            else:
                return False
        except Exception as e:
            print("Error:", e)
