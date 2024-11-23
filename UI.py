import os
import sys
from pwshConfig import Automatic_installation_And_Config 

sys.stdout.reconfigure(encoding='utf-8')

class Handle_Input:
    def __init__(self) -> None:
        self.banner: str = """                   _       ___             __ _       
 _ ____      _____| |__   / __\\___  _ __  / _(_) __ _ 
| '_ \\ \\ /\\ / / __| '_ \\ / /  / _ \\| '_ \\| |_| |/ _` |
| |_) \\ V  V /\\__ \\ | | / /__| (_) | | | |  _| | (_| |
| .__/ \\_/\\_/ |___/_| |_\\____/\\___/|_| |_|_| |_|\\__, |
|_|                                             |___/ 
           ╔════════════════════════════╗
           ╠════════Version 2.1═════════╣
           ╠═════════ @ PUXY ═══════════╣
           ╚════════════════════════════╝"""
        self.options: str = """
║
╠═╗
║[1] Automatic installation
║ ╚╗
║ [2] Manual installation
║  ╚╗
║  [3] Exit
╚ ?> """
        self.success: str = """                          
 ___ _   _  ___ ___ ___  ___ ___ 
/ __| | | |/ __/ __/ _ \\/ __/ __|
\\__ \\ |_| | (_| (_|  __/\\__ \\__ \\
|___/\\__,_|\\___\\___\\___||___/___/ 
"""
        self.installer = Automatic_installation_And_Config()
        
    def cls(self) -> None:
        os.system("cls")
    
    def Print_banner(self) -> None:
        print(self.banner)
    
    def Print_options(self) -> str:
        user_input: str = input(self.options) 
        return user_input
        
    def Handle(self, user_input: str) -> None:
        if user_input == "1":
            os.system("cls")
            print("Automatic installation")
            if self.installer.setup_environment() == True:
                print(self.success)
            
        elif user_input == "2":
            os.system("cls")
            print("Manual installation")
            
        elif user_input == "3":
            os.system("cls")
            while True:
                exit_user_input: str = input("Are you sure you want to exit? (y/n): ").strip().lower()
                if exit_user_input == 'y':
                    exit()
                elif exit_user_input == 'n':
                    break
                else:
                    os.system("cls")
                    print("Invalid input. Please enter 'y' or 'n'.")
            
        else:
            os.system("cls")
            print("Invalid input. Please select 1, 2, or 3.")