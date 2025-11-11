"""
Lumethros Netrix - Advanced Network Analysis Tool
UI/UX Module with ASCII Art and Terminal Styling
"""

import sys
import time
import re
from typing import Optional

# Cores ANSI para terminal
class Colors:
    """ANSI color codes for terminal output"""
    # Cores básicas
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Cores de texto
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Cores brilhantes
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

def print_banner():
    """Print the main ASCII art banner"""
    banner = f"""
{Colors.RED}
██╗     ██╗   ██╗███╗   ███╗███████╗████████╗██╗  ██╗██████╗  ██████╗ ███████╗
██║     ██║   ██║████╗ ████║██╔════╝╚══██╔══╝██║  ██║██╔══██╗██╔═══██╗██╔════╝
██║     ██║   ██║██╔████╔██║█████╗     ██║   ███████║██████╔╝██║   ██║███████╗
██║     ██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██╔══██╗██║   ██║╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║██║  ██║╚██████╔╝███████║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
{Colors.RED}
███╗   ██╗███████╗████████╗██████╗ ██╗██╗  ██╗
████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║╚██╗██╔╝
██╔██╗ ██║█████╗     ██║   ██████╔╝██║ ╚███╔╝ 
██║╚██╗██║██╔══╝     ██║   ██╔══██╗██║ ██╔██╗ 
██║ ╚████║███████╗   ██║   ██║  ██║██║██╔╝ ██╗
╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
{Colors.RESET}
{Colors.DIM}
        ────────────────────────────────────────────────────────────────
{Colors.BRIGHT_WHITE}        Lumethros Netrix - Advanced Network Analysis Tool v2.0{Colors.RESET}
{Colors.RED}        by Crowlevy for TCC (Trabalho de Conclusão de Curso){Colors.RESET}
{Colors.DIM}        ────────────────────────────────────────────────────────────────{Colors.RESET}
"""
    print(banner)

def print_header(text: str, color: str = Colors.RED):
    """Print a formatted header"""
    width = 80
    border = "═" * width
    print(f"\n{color}{Colors.BOLD}{border}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{text.center(width)}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{border}{Colors.RESET}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.YELLOW}[✓]{Colors.RESET} {Colors.YELLOW}{message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.BRIGHT_RED}[✗]{Colors.RESET} {Colors.RED}{message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.BRIGHT_YELLOW}[!]{Colors.RESET} {Colors.YELLOW}{message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}[i]{Colors.RESET} {Colors.RED}{message}{Colors.RESET}")

def print_progress(current: int, total: int, prefix: str = "Progress"):
    """Print progress bar"""
    percent = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r{Colors.RED}[{prefix}]{Colors.RESET} [{bar}] {percent:.1f}% ({current}/{total})", end='', flush=True)

def print_table_header(headers: list, widths: list, color: str = Colors.RED):
    """Print formatted table header"""
    header_line = " │ ".join(f"{h:<{w}}" for h, w in zip(headers, widths))
    total_width = sum(widths) + (len(headers) - 1) * 3
    border = "═" * total_width
    print(f"{color}{Colors.BOLD}╔{border}╗{Colors.RESET}")
    print(f"{color}{Colors.BOLD}║ {header_line} ║{Colors.RESET}")
    print(f"{color}{Colors.BOLD}╠{border.replace('═', '═')}╣{Colors.RESET}")

def print_table_row(data: list, widths: list, color: str = Colors.WHITE):
    """Print formatted table row"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    #formata cada coluna, considerando códigos ANSI
    formatted_cols = []
    for d, w in zip(data, widths):
        d_str = str(d)
        #remove códigos ANSI para calcular largura real
        clean_d = ansi_escape.sub('', d_str)
        #padding baseado na largura real
        padding = max(0, w - len(clean_d))
        formatted_cols.append(d_str + ' ' * padding)
    
    row_line = " │ ".join(formatted_cols)
    print(f"{color}║ {row_line} ║{Colors.RESET}")

def print_table_footer(widths: list, color: str = Colors.RED):
    """Print formatted table footer"""
    total_width = sum(widths) + (len(widths) - 1) * 3
    border = "═" * total_width
    print(f"{color}{Colors.BOLD}╚{border}╝{Colors.RESET}")

def print_box(content: list, title: Optional[str] = None, color: str = Colors.RED):
    """Print content in a box"""
    if content:
        max_width = max(len(str(line)) for line in content)
        if title:
            max_width = max(max_width, len(title))
        max_width += 4
        
        border_top = "╔" + "═" * (max_width - 2) + "╗"
        border_bottom = "╚" + "═" * (max_width - 2) + "╝"
        border_side = "║"
        
        print(f"{color}{Colors.BOLD}{border_top}{Colors.RESET}")
        if title:
            print(f"{color}{Colors.BOLD}{border_side} {title.center(max_width - 4)} {border_side}{Colors.RESET}")
            print(f"{color}{Colors.BOLD}{border_side.replace('║', '╠')}{'═' * (max_width - 2)}{border_side.replace('║', '╣')}{Colors.RESET}")
        
        for line in content:
            print(f"{color}{border_side} {str(line).ljust(max_width - 4)} {border_side}{Colors.RESET}")
        
        print(f"{color}{Colors.BOLD}{border_bottom}{Colors.RESET}")

def print_separator(char: str = "─", length: int = 80, color: str = Colors.RED):
    """Print a separator line"""
    print(f"{color}{char * length}{Colors.RESET}")

def animate_text(text: str, delay: float = 0.05):
    """Animate text printing"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def clear_screen():
    """Clear terminal screen"""
    print("\033[2J\033[H", end='')

def print_login_screen():
    """Print login screen"""
    clear_screen()
    print_banner()
    print_header("AUTENTICAÇÃO NECESSÁRIA", Colors.BRIGHT_YELLOW)
    print(f"{Colors.BRIGHT_WHITE}Por favor, digite suas credenciais para acessar o Lumethros Netrix{Colors.RESET}\n")

def print_main_menu():
    """Print main menu options"""
    menu = [
        f"{Colors.RED}[1]{Colors.RESET} Packet Capture & Analysis",
        f"{Colors.RED}[2]{Colors.RESET} Live Host Detection",
        f"{Colors.RED}[3]{Colors.RESET} Exit"
    ]
    print_box(menu, "MAIN MENU", Colors.RED)

