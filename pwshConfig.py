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

    def install_nerd_fonts(self) -> bool:
        """
        Install Nerd Fonts using PowerShell commands.
        
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            # Create a PowerShell script to download and install Nerd Fonts
            install_fonts_command = """
            $webClient = New-Object System.Net.WebClient
            $fontsUrl = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1"
            $fonts = @("Hack", "HeavyData")
            
            foreach ($font in $fonts) {
                try {
                    Write-Host "Downloading $font Nerd Font..."
                    $zipFile = "$env:TEMP\\$font.zip"
                    $fontUrl = "$fontsUrl/$font.zip"
                    $webClient.DownloadFile($fontUrl, $zipFile)
                    
                    Write-Host "Installing $font Nerd Font..."
                    Expand-Archive -Path $zipFile -DestinationPath "$env:TEMP\\$font" -Force
                    
                    $fontFiles = Get-ChildItem -Path "$env:TEMP\\$font" -Include '*.ttf','*.otf' -Recurse
                    foreach ($fontFile in $fontFiles) {
                        $destination = Join-Path $env:LOCALAPPDATA 'Microsoft\\Windows\\Fonts' $fontFile.Name
                        Copy-Item -Path $fontFile.FullName -Destination $destination -Force
                        
                        # Add font to registry
                        $regValue = Join-Path $env:LOCALAPPDATA "Microsoft\\Windows\\Fonts\\$($fontFile.Name)"
                        New-ItemProperty -Path "HKCU:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts" -Name $fontFile.Name -Value $regValue -Force
                    }
                    
                    Remove-Item -Path $zipFile -Force
                    Remove-Item -Path "$env:TEMP\\$font" -Recurse -Force
                    Write-Host "$font Nerd Font installed successfully."
                }
                catch {
                    Write-Error "Failed to install $font Nerd Font: $_"
                    exit 1
                }
            }
            """
            
            # Execute the PowerShell script
            result = subprocess.run(
                ['pwsh', '-Command', install_fonts_command],
                capture_output=True,
                text=True,
                check=True
            )
            print("Nerd Fonts installed successfully.")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error installing Nerd Fonts: {e}")
            print(f"Command output: {e.stdout}")
            print(f"Error output: {e.stderr}")
            input("Press any key to continue...")
            return False

    def install_necessary_packages(self) -> bool:
        """
        Install necessary packages using winget commands.
        
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            for command in self.necessary_package_commands:
                # Skip the Nerd Fonts installation command from winget
                if "Install-NerdFont.ps1" in command:
                    continue
                    
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                print(f"Executed: {command}")
                print(result.stdout)
                # Continue even if package is already installed
                if result.returncode != 0 and ("No available upgrade found" in result.stdout or 
                                            "already installed" in result.stdout):
                    continue
                elif result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, command)
            
            # Install Nerd Fonts separately
            if not self.install_nerd_fonts():
                return False
                
            print("Necessary packages installed successfully.")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error installing necessary packages: {e}")
            print(f"Command output: {e.output}")
            input("Press any to continue...")
            return False

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
                input("Press any to continue...")
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
            input("Press any to continue...")
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
            # Read existing profile content
            existing_content = self.profile_path.read_text()
            
            commands = [
                "Invoke-Expression (& { (zoxide init --cmd cd powershell | Out-String) })",
                "oh-my-posh init pwsh --config '~\.config\ohmyposh\zen.toml' | Invoke-Expression"
            ]
            
            # Check if all commands are already in the profile
            all_commands_present = all(command in existing_content for command in commands)
            
            if all_commands_present:
                print("PowerShell profile already configured.")
                return True
            
            # Join commands with newlines
            commands_text = "\n".join(commands)
            
            add_content_command = f'''
Add-Content -Path $PROFILE -Value @"

# Added by PowerShell Configuration Script
{commands_text}
"@
'''
            
            result = subprocess.run(['pwsh', '-Command', add_content_command],
                                 check=True, capture_output=True, text=True)
            print("PowerShell profile configured successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error configuring PowerShell profile: {e}")
            print(f"Command output: {e.output}")
            input("Press any to continue...")
            return False

    def install_oh_my_posh_config(self) -> bool:
        """
        Install Oh My Posh configuration.

        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            # Define paths
            oh_my_posh_config_path = Path.home() / ".config" / "ohmyposh"
            zen_toml_source = Path.cwd() / "zen.toml"
            zen_toml_dest = oh_my_posh_config_path / "zen.toml"

            # Create config directory if it doesn't exist
            print(f"Creating Oh-My-Posh configuration directory at: {oh_my_posh_config_path}")
            oh_my_posh_config_path.mkdir(parents=True, exist_ok=True)

            # Check if source file exists
            if not zen_toml_source.exists():
                print(f"Error: zen.toml not found in current directory: {zen_toml_source}")
                print("Please ensure zen.toml is in the same directory as the script.")
                return False

            # Try to copy using Python's Path
            try:
                print(f"Copying {zen_toml_source} to {zen_toml_dest}")
                import shutil
                shutil.copy2(zen_toml_source, zen_toml_dest)
            except PermissionError:
                print("Permission denied. Attempting to copy using PowerShell with elevated privileges...")
                # Fallback to PowerShell with explicit error handling
                copy_command = f"""
                $source = '{zen_toml_source}'
                $destination = '{zen_toml_dest}'
                try {{
                    Copy-Item -Path $source -Destination $destination -Force -ErrorAction Stop
                    Write-Output "File copied successfully using PowerShell"
                }} catch {{
                    Write-Error "PowerShell copy failed: $_"
                    exit 1
                }}
                """
                result = subprocess.run(
                    ['pwsh', '-Command', copy_command],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"PowerShell copy failed with error: {result.stderr}")
                    return False

            # Verify the file was copied successfully
            if zen_toml_dest.exists():
                print("Oh My Posh configuration installed successfully.")
                print(f"Configuration file location: {zen_toml_dest}")
                return True
            else:
                print(f"Error: Configuration file was not copied to {zen_toml_dest}")
                return False

        except Exception as e:
            print(f"Error installing Oh My Posh configuration: {str(e)}")
            print("Stack trace:")
            import traceback
            print(traceback.format_exc())
            input("Press any key to continue...")
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