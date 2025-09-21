import os
import json

def openJson(path: str):
    """Open a JSON file

    Args:
        path (str): JSON path

    Returns:
        dict or list: JSON content
    """
    with open(path, 'r') as file:
        content = json.load(file)
    return content

def createJsonIfNot(path, content):
    """Create a file if a JSON does not exists

    Args:
        path (str): file path
        content (): Content to add in the JSON
    """
    if not os.path.exists(path):
        with open(path, 'w') as file:
            json.dump(content, file)
