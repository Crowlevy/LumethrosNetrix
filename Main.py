import argparse
import hashlib
import os
import sys
from getpass import getpass
from Utils.capture import start_capture
from Utils.filters import parse_filter_string
from Utils.analysis import analyze_packet
from Utils.save import save_to_txt, save_to_pcap
from Utils.HostDetector import detect_live_hosts
from Utils.PortScanner import scan_host
from Utils.ReportGenerator import create_report_from_hosts, create_report_from_ports, create_combined_report
from Utils.ArpSpoofDetector import ArpSpoofDetector
from Web.app import start_web_server
from Utils.ui import (
    print_banner, print_header, print_success, print_error, 
    print_warning, print_info, print_login_screen, Colors
)

PASSWORD_FILE = "password_hash.txt"  #nunca toque nesse arquivo para mudar, se tiver algum problema dele o projeto e rode novamente
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password):
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            stored_hash = f.read().strip()
            return stored_hash == hash_password(input_password)
    return False

def set_password():
    print(f"\n{Colors.BRIGHT_YELLOW}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}║{Colors.BRIGHT_WHITE}  Configuração Inicial - Crie Sua Senha Mestra{Colors.BRIGHT_YELLOW}              ║{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    password = getpass(f"{Colors.BRIGHT_CYAN}[?]{Colors.RESET} {Colors.CYAN}Defina uma nova senha: {Colors.RESET}")
    confirm_password = getpass(f"{Colors.BRIGHT_CYAN}[?]{Colors.RESET} {Colors.CYAN}Confirme a senha: {Colors.RESET}")
    
    if password != confirm_password:
        print_error("As senhas não coincidem. Por favor, tente novamente.")
        sys.exit(1)
    
    with open(PASSWORD_FILE, 'w') as f:
        f.write(hash_password(password))
    print_success("Senha definida com sucesso!")

def login():
    print_login_screen()
    
    if not os.path.exists(PASSWORD_FILE):
        print_warning("Nenhuma senha definida. Por favor, defina uma nova senha.")
        set_password()
        print_login_screen()
    
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        password = getpass(f"{Colors.BRIGHT_CYAN}[?]{Colors.RESET} {Colors.CYAN}Digite a senha: {Colors.RESET}")
        if verify_password(password):
            print_success("Autenticação bem-sucedida!")
            print(f"{Colors.BRIGHT_GREEN}Bem-vindo ao Lumethros Netrix{Colors.RESET}\n")
            break
        else:
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                print_error(f"Senha incorreta. {remaining} tentativa(s) restante(s).")
            else:
                print_error("Número máximo de tentativas excedido. Acesso negado.")
                sys.exit(1)

def start_application(args):
    if args.option == "c":
        print_header("MODO DE CAPTURA DE PACOTES", Colors.BRIGHT_MAGENTA)
        print_info(f"Interface: {Colors.BRIGHT_WHITE}{args.i}{Colors.RESET}")
        print_info(f"Pacotes para capturar: {Colors.BRIGHT_WHITE}{args.pc}{Colors.RESET}")
        print_info(f"Filtro: {Colors.BRIGHT_WHITE}{args.f}{Colors.RESET}\n")
        
        filter_criteria = parse_filter_string(args.f)
        captured_packets = start_capture(args.i, args.pc, filter_criteria)

        if not captured_packets:
            print_error("Nenhum pacote capturado.")
            return

        if args.a:
            print_header("ANALISANDO PACOTES", Colors.BRIGHT_YELLOW)
            print_info(f"Analisando {args.pc} pacotes...\n")
            for packet in captured_packets:
                analyze_packet(packet)

        if args.s:
            if args.p:
                save_to_pcap(captured_packets, args.p)
                print_success(f"Pacotes salvos em {args.p}")
            elif args.t:
                save_to_txt(captured_packets, args.t)
                print_success(f"Pacotes salvos em {args.t}")
            else:
                print_error("Nenhuma opção de salvamento selecionada. Por favor, escolha salvar os pacotes como arquivo .PCAP ou .TXT.")

    elif args.option == "lh":
        if args.ip:
            print_header("MODO DE DETECÇÃO DE HOSTS VIVOS", Colors.BRIGHT_GREEN)
            hosts_data = detect_live_hosts(args.ip, args.i)
            
            # Gerar relatório se solicitado
            if args.report:
                print_info("Gerando relatório HTML...")
                network_info = {
                    'network': f"{args.ip}/24",
                    'interface': args.i if args.i else 'N/A',
                    'duration': 'N/A'
                }
                report_file = args.report if args.report.endswith('.html') else f"{args.report}.html"
                create_report_from_hosts(hosts_data if hosts_data else [], network_info, report_file)
        else:
            print_error("Para detecção de hosts vivos, forneça um endereço IP usando --ip")
            sys.exit(1)

    elif args.option == "ps":
        if args.ip:
            ports = args.ports if args.ports else "common"
            scan_type = args.scan_type if args.scan_type else "syn"
            threads = args.threads if args.threads else 100
            timeout = args.timeout if args.timeout else 1
            grab_banners = args.banner if args.banner else False
            
            ports_data = scan_host(
                args.ip, 
                ports=ports,
                scan_type=scan_type,
                threads=threads,
                timeout=timeout,
                grab_banners=grab_banners
            )
            
            # Gerar relatório se solicitado
            if args.report:
                print_info("Gerando relatório HTML...")
                report_file = args.report if args.report.endswith('.html') else f"{args.report}.html"
                create_report_from_ports(ports_data, args.ip, report_file)
        else:
            print_error("Para escaneamento de portas, forneça um endereço IP usando --ip")
            sys.exit(1)

    elif args.option == "asd":
        print_header("MODO DE DETECÇÃO DE ARP SPOOFING", Colors.BRIGHT_RED)
        detector = ArpSpoofDetector()
        detector.start_monitoring(args.i)

    elif args.option == "web":
        print_header("MODO WEB DASHBOARD", Colors.BRIGHT_CYAN)
        start_web_server(args.i)

    else:
        print_error("Opção inválida. Use 'c', 'lh', 'ps', 'asd' ou 'web'.")
        sys.exit(1)

def main():
    #print banner on startup
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Lumethros Netrix - Advanced Network Analysis & Security Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BRIGHT_CYAN}Exemplos:{Colors.RESET}
  {Colors.BRIGHT_WHITE}Captura de Pacotes:{Colors.RESET}
    sudo python3 Main.py c --i en0 --pc 100 --a --s --p capture.pcap
    
  {Colors.BRIGHT_WHITE}Detecção de Hosts Vivos:{Colors.RESET}
    sudo python3 Main.py lh --ip 192.168.1.1 --i en0
    
  {Colors.BRIGHT_WHITE}Escaneamento de Portas:{Colors.RESET}
    sudo python3 Main.py ps --ip 192.168.1.1 --ports common
    sudo python3 Main.py ps --ip 192.168.1.1 --ports 1-1000 --scan-type syn --banner --report scan_report.html
    
    sudo python3 Main.py ps --ip 192.168.1.1 --ports 1-1000 --scan-type syn --banner --report scan_report.html

  {Colors.BRIGHT_WHITE}Detecção de ARP Spoofing:{Colors.RESET}
    sudo python3 Main.py asd --i en0
    
  {Colors.BRIGHT_WHITE}Web Dashboard:{Colors.RESET}
    sudo python3 Main.py web --i en0

  {Colors.BRIGHT_WHITE}Gerar Relatório:{Colors.RESET}
    sudo python3 Main.py lh --ip 192.168.1.1 --report network_report.html
    sudo python3 Main.py ps --ip 192.168.1.1 --report port_scan.html

{Colors.BRIGHT_YELLOW}⚠️  AVISO: Use apenas em redes que você possui ou tem permissão explícita para testar!{Colors.RESET}
        """
    )

    parser.add_argument("option", choices=["c", "lh", "ps", "asd", "web"], 
                       help="Modo de operação: 'c', 'lh', 'ps', 'asd', 'web'")
    parser.add_argument("--i", help="Interface de rede (ex: en0, eth0, Wi-Fi)", required=False)
    parser.add_argument("--f", help="Filtro BPF (ex: 'src host 192.168.1.1 and tcp')", default="all")
    parser.add_argument("--pc", help="Número de pacotes para capturar", type=int, required=False)
    parser.add_argument("--a", help="Analisar pacotes capturados", action="store_true")
    parser.add_argument("--s", help="Salvar pacotes capturados", action="store_true")
    parser.add_argument("--t", help="Salvar em formato TXT (forneça o nome do arquivo)", type=str)
    parser.add_argument("--p", help="Salvar em formato PCAP (forneça o nome do arquivo)", type=str)
    parser.add_argument("--ip", help="Endereço IP alvo", required=False)
    parser.add_argument("--ports", help="Portas para escanear: 'common', range (ex: '1-1000') ou lista (ex: '80,443,8080')", default="common")
    parser.add_argument("--scan-type", choices=["syn", "connect"], help="Tipo de escaneamento: 'syn' (stealth) ou 'connect'", default="syn")
    parser.add_argument("--threads", help="Número de threads paralelas (padrão: 100)", type=int, default=100)
    parser.add_argument("--timeout", help="Timeout por porta em segundos (padrão: 1)", type=float, default=1.0)
    parser.add_argument("--banner", help="Tentar obter banners dos serviços", action="store_true")
    parser.add_argument("--report", help="Gerar relatório HTML (forneça o nome do arquivo)", type=str)

    args = parser.parse_args()
    if args.option == "c":
        if not args.i or not args.pc:
            print_error("Para captura de pacotes, são necessários '--i' (interface) e '--pc' (quantidade de pacotes).")
            sys.exit(1)

    login()
    start_application(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}[!]{Colors.RESET} {Colors.YELLOW}Operação cancelada pelo usuário{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Ocorreu um erro: {e}")
        sys.exit(1)


