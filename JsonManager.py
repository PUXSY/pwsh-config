import json
from typing import List

class JsonManager:
    def __init__(self):
        self.applications_data: dict
        self.load_applications_data()

    def load_applications_data(self) -> None:
        """
        Loads the applications data from JSON file, handling different encodings.
        Falls back to empty dict if file is not found or cannot be decoded.
        """
        try:
            # Try UTF-8 encoding first
            with open('./packages.json', 'r', encoding='utf-8') as f:
                self.applications_data = json.load(f)
        except UnicodeDecodeError:
            # If UTF-8 fails, try with 'cp1252' encoding
            try:
                with open('./applications.json', 'r', encoding='cp1252') as f:
                    self.applications_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                self.applications_data = {}
        except FileNotFoundError:
            print("applications.json not found. Please ensure the file exists.")
            self.applications_data = {}

    def print_applications_data(self) -> None:
        """
        Prints the applications data in a formatted JSON structure.
        """
        print(json.dumps(self.applications_data, indent=4))

    def get_necessary_package_commands(self) -> List[str]:
        """
        Returns a list of winget installation commands for necessary packages.
        
        Returns:
            List[str]: A list of winget commands to install necessary packages.
                      Each command is ready to be executed in PowerShell/Command Prompt.
        """
        if not self.applications_data or 'Necessary_packages' not in self.applications_data:
            return []
        
        return [
            command for command in self.applications_data['Necessary_packages'].values()
        ]

    def get_python_package_commands(self) -> List[str]:
        """
        Returns a list of pip installation commands for Python packages.
        
        Returns:
            List[str]: A list of pip install commands for required Python packages.
                      Each command is ready to be executed in terminal.
        """
        if not self.applications_data or 'Py_packages' not in self.applications_data:
            return []
        
        return [
            command for command in self.applications_data['Py_packages'].values()
        ]

    def get_formatted_necessary_packages(self) -> List[tuple]:
        """
        Returns a list of tuples containing package names and their installation commands.
        
        Returns:
            List[tuple]: A list of (package_name, install_command) tuples for necessary packages.
        """
        if not self.applications_data or 'Necessary_packages' not in self.applications_data:
            return []
        
        return [
            (package, command) 
            for package, command in self.applications_data['Necessary_packages'].items()
        ]

    def get_formatted_python_packages(self) -> List[tuple]:
        """
        Returns a list of tuples containing Python package names and their pip commands.
        
        Returns:
            List[tuple]: A list of (package_name, pip_command) tuples for Python packages.
        """
        if not self.applications_data or 'Py_packages' not in self.applications_data:
            return []
        
        return [
            (package, command) 
            for package, command in self.applications_data['Py_packages'].items()
        ]