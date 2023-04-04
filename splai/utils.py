import os

def find_project_root(start_path="."):
    current_path = os.path.abspath(start_path)
    while current_path != os.path.abspath(os.sep):
        if os.path.exists(os.path.join(current_path, ".splai.yml")):
            return current_path
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError("No .splai.yml file found in the directory hierarchy.")
