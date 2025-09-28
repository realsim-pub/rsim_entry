def print_green(print_content:str)-> str:
     print(f"\033[32m{print_content}\033[0m")
     return print_content + "\n"

def print_red(print_content:str)-> str:
     print(f"\033[31m{print_content}\033[0m")
     return print_content + "\n"
    
def print_blue(print_content:str)-> str:
     print(f"\033[34m{print_content}\033[0m")
     return print_content + "\n"