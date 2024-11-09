from UI import Handle_Input  


def main():
    """
    Main function to run the automatic installation and configuration process.
    """
    ui = Handle_Input()  
    ui.cls()
    while True:
        ui.Print_banner()  
        user_input = ui.Print_options() 
        ui.Handle(user_input)  

if __name__ == "__main__":
    main()
