import subprocess
import sys
from typing import List
from pathlib import Path
from JsonManager import JsonManager

class Automatic_installation_And_Config:
    """
    Handles automatic installation and configuration of PowerShell environment.
    """
    def __init__(self):
        """
        Initialize the installation manager with package commands from JsonManager.
        """
        self.json_manager = JsonManager()
        self.necessary_package_commands = self.json_manager.get_necessary_package_commands()
        self.python_package_commands = self.json_manager.get_python_package_commands()
        
        # Set up correct PowerShell Core profile path
        self.powershell_dir = Path.home() / "Documents" / "PowerShell"
        self.profile_path = self.powershell_dir / "Microsoft.PowerShell_profile.ps1"

    def install_python_packages(self) -> bool:
        """
        Install Python packages using pip commands.
        
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            for command in self.python_package_commands:
                result = subprocess.run(command, shell=True, check=True, 
                                     capture_output=True, text=True)
                print(f"Executed: {command}")
                print(result.stdout)
            print("Python packages installed successfully.")
            return True
        except ImportError:
            
            try:
                for package_name in self.json_manager.get_python_package_names():
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                return True
            
            except subprocess.CalledProcessError as e:
                print(f"Error installing Python packages: {e}")
                print(f"Command output: {e.output}")
                return False
        

        
    def install_necessary_packages(self) -> bool:
        """
        Install necessary packages using winget commands.
        
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            for command in self.necessary_package_commands:
                result = subprocess.run(command, shell=True, check=True, 
                                     capture_output=True, text=True)
                print(f"Executed: {command}")
                print(result.stdout)
            print("Necessary packages installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing necessary packages: {e}")
            print(f"Command output: {e.output}")
            return False

    def install_pwsh_profile(self) -> bool:
        """
        Create PowerShell profile if it doesn't exist.
        
        Returns:
            bool: True if profile was created successfully, False otherwise.
        """
        try:
            # Create PowerShell directory if it doesn't exist
            self.powershell_dir.mkdir(parents=True, exist_ok=True)
            
            # Create profile using PowerShell Core specific path
            create_profile_command = f"""
$ProfileDir = Split-Path -Parent $PROFILE
if (!(Test-Path -Path $ProfileDir)) {{
    New-Item -ItemType Directory -Path $ProfileDir -Force
}}
if (!(Test-Path -Path $PROFILE)) {{
    New-Item -ItemType File -Path $PROFILE -Force
}}
"""
            result = subprocess.run(['pwsh', '-Command', create_profile_command],
                                 check=True, capture_output=True, text=True)
            print("PowerShell profile created successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating PowerShell profile: {e}")
            print(f"Command output: {e.output}")
            return False

    def configure_pwsh_profile(self) -> bool:
        """
        Configure PowerShell profile with required commands.
        
        Returns:
            bool: True if profile was configured successfully, False otherwise.
        """
        if not self.profile_path.exists():
            print(f"Error: Profile file not found at {self.profile_path}")
            return False

        try:
            commands = [
                "Invoke-Expression (& { (zoxide init powershell | Out-String) })",
                "oh-my-posh init pwsh --config '~\\.config\\ohmyposh\\base.json' | Invoke-Expression"
            ]
            
            add_content_command = f"""
            Add-Content -Path $PROFILE -Value @'
            {chr(10).join(commands)}
'@
            """
            
            result = subprocess.run(['pwsh', '-Command', add_content_command],
                                 check=True, capture_output=True, text=True)
            print("PowerShell profile configured successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error configuring PowerShell profile: {e}")
            print(f"Command output: {e.output}")
            return False


    def install_oh_my_posh_config(self) -> bool:
        """
        Install Oh My Posh configuration.

        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            oh_my_posh_config_path = Path.home() / ".config" / "ohmyposh"
            oh_my_posh_config_path.mkdir(parents=True, exist_ok=True)

            Copy_base_json:str = "Copy-Item "r"./base.json" f"-Destination {oh_my_posh_config_path}"
            subprocess.run(Copy_base_json, check=True, capture_output=True, text=True)

            print("Oh My Posh configuration installed successfully.")
            return True
        except Exception as e:
            print(f"Error installing Oh My Posh configuration: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """
        Complete setup of the environment by running all installation and configuration steps.
        
        Returns:
            bool: True if all steps completed successfully, False otherwise.
        """
        steps = [
            (self.install_python_packages, "Installing Python packages"),
            (self.install_necessary_packages, "Installing necessary packages"),
            (self.install_pwsh_profile, "Creating PowerShell profile"),
            (self.configure_pwsh_profile, "Configuring PowerShell profile"),
            (self.install_oh_my_posh_config, "Installing Oh My Posh configuration")
        ]
        
        success = True
        for step_func, step_name in steps:
            print(f"\nStarting: {step_name}...")
            if not step_func():
                print(f"Failed: {step_name}")
                success = False
                break
            print(f"Completed: {step_name}")
            
        return success