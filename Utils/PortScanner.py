"""
Lumethros Netrix - Port Scanner Module
Escaneamento de portas TCP/UDP com detecção de serviços
"""

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from scapy.all import IP, TCP, sr1, RandShort
from Utils.ui import (
    print_header, print_success, print_error, print_warning,
    print_info, print_progress, print_table_header, print_table_row,
    print_table_footer, Colors
)

# portas comuns e seus serviços
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt"
}

def get_service_name(port):
    """Retorna o nome do serviço conhecido para uma porta"""
    return COMMON_PORTS.get(port, "Unknown")

def grab_banner(ip, port, timeout=2):
    """Tenta obter banner do serviço na porta"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            try:
                # Tenta receber banner
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                if banner:
                    return banner[:100]  # Limita tamanho
            except:
                pass
        sock.close()
    except:
        pass
    return None

def scan_port_tcp_syn(ip, port, timeout=1):
    """Escaneamento TCP SYN (stealth scan)"""
    try:
        src_port = RandShort()
        packet = IP(dst=ip) / TCP(sport=src_port, dport=port, flags="S")
        response = sr1(packet, timeout=timeout, verbose=False)
        
        if response is None:
            return "filtered"  # Porta filtrada ou não respondeu
        elif response.haslayer(TCP):
            if response.getlayer(TCP).flags == 0x12:  # SYN-ACK
                # Envia RST para fechar conexão
                sr1(IP(dst=ip) / TCP(sport=src_port, dport=port, flags="R"), 
                    timeout=timeout, verbose=False)
                return "open"
            elif response.getlayer(TCP).flags == 0x14:  # RST-ACK
                return "closed"
        return "filtered"
    except Exception as e:
        return "error"

def scan_port_tcp_connect(ip, port, timeout=1):
    """Escaneamento TCP Connect (mais lento mas mais confiável)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            return "open"
        else:
            return "closed"
    except socket.timeout:
        return "filtered"
    except Exception:
        return "error"

def scan_ports(ip, ports, scan_type="syn", threads=100, timeout=1, grab_banners=False):
    """
    Escaneia múltiplas portas em um IP
    
    Args:
        ip: Endereço IP alvo
        ports: Lista de portas ou range (ex: [80, 443] ou "1-1000")
        scan_type: "syn" ou "connect"
        threads: Número de threads paralelas
        timeout: Timeout por porta
        grab_banners: Se deve tentar obter banners
    """
    # Parse ports
    port_list = []
    if isinstance(ports, str):
        if '-' in ports:
            # Range de portas
            start, end = map(int, ports.split('-'))
            port_list = list(range(start, end + 1))
        elif ',' in ports:
            # Lista de portas separadas por vírgula
            port_list = [int(p.strip()) for p in ports.split(',')]
        else:
            # Porta única
            port_list = [int(ports)]
    else:
        port_list = ports
    
    print_info(f"Escaneando {len(port_list)} porta(s) em {Colors.BRIGHT_WHITE}{ip}{Colors.RESET}...")
    print_info(f"Tipo de escaneamento: {Colors.BRIGHT_WHITE}{scan_type.upper()}{Colors.RESET}")
    print_info(f"Threads: {Colors.BRIGHT_WHITE}{threads}{Colors.RESET}\n")
    
    open_ports = []
    closed_ports = []
    filtered_ports = []
    error_ports = []
    
    start_time = time.time()
    
    def scan_single_port(port):
        """Função para escanear uma porta"""
        if scan_type.lower() == "syn":
            status = scan_port_tcp_syn(ip, port, timeout)
        else:
            status = scan_port_tcp_connect(ip, port, timeout)
        
        banner = None
        if status == "open" and grab_banners:
            banner = grab_banner(ip, port, timeout=2)
        
        return port, status, banner
    
    # executa escaneamento em paralelo
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_single_port, port): port for port in port_list}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            try:
                port, status, banner = future.result()
                
                if status == "open":
                    open_ports.append((port, banner))
                elif status == "closed":
                    closed_ports.append(port)
                elif status == "filtered":
                    filtered_ports.append(port)
                else:
                    error_ports.append(port)
                
                # Progresso
                if len(port_list) > 10:
                    print_progress(completed, len(port_list), "Escaneando portas")
            except Exception as e:
                error_ports.append(futures[future])
    
    if len(port_list) > 10:
        print()  # Nova linha após progresso
    
    elapsed_time = time.time() - start_time
    
    return {
        "ip": ip,
        "open": open_ports,
        "closed": closed_ports,
        "filtered": filtered_ports,
        "errors": error_ports,
        "total_scanned": len(port_list),
        "time_elapsed": elapsed_time
    }

def scan_common_ports(ip, scan_type="syn", threads=100, timeout=1, grab_banners=False):
    """Escaneia apenas portas comuns"""
    common_port_list = list(COMMON_PORTS.keys())
    return scan_ports(ip, common_port_list, scan_type, threads, timeout, grab_banners)

def display_results(results):
    """Exibe os resultados do escaneamento de forma formatada"""
    ip = results["ip"]
    open_ports = results["open"]
    closed_ports = results["closed"]
    filtered_ports = results["filtered"]
    error_ports = results["errors"]
    total_scanned = results["total_scanned"]
    elapsed_time = results["time_elapsed"]
    
    print_header("RESULTADOS DO ESCANEAMENTO DE PORTAS", Colors.BRIGHT_GREEN)
    
    if open_ports:
        print_success(f"Portas abertas encontradas: {Colors.BRIGHT_WHITE}{len(open_ports)}{Colors.RESET}")
        
        # tabela de portas abertas
        widths = [12, 20, 15, 50]
        headers = ["Porta", "Serviço", "Status", "Banner"]
        
        print_table_header(headers, widths, Colors.RED)
        
        for port, banner in sorted(open_ports, key=lambda x: x[0]):
            service = get_service_name(port)
            banner_str = banner if banner else f"{Colors.DIM}-{Colors.RESET}"
            
            # trunca banner se muito longo
            if banner and len(banner) > 48:
                banner_str = banner[:45] + "..."
            
            print_table_row([
                str(port),
                service,
                f"{Colors.BRIGHT_GREEN}OPEN{Colors.RESET}",
                banner_str
            ], widths, Colors.WHITE)
        
        print_table_footer(widths, Colors.RED)
    else:
        print_warning("Nenhuma porta aberta encontrada.")
    
    print(f"\n{Colors.BRIGHT_CYAN}Estatísticas:{Colors.RESET}")
    print(f"  {Colors.BRIGHT_WHITE}Total escaneado:{Colors.RESET} {total_scanned}")
    print(f"  {Colors.BRIGHT_GREEN}Abertas:{Colors.RESET} {len(open_ports)}")
    print(f"  {Colors.YELLOW}Fechadas:{Colors.RESET} {len(closed_ports)}")
    print(f"  {Colors.DIM}Filtradas:{Colors.RESET} {len(filtered_ports)}")
    if error_ports:
        print(f"  {Colors.BRIGHT_RED}Erros:{Colors.RESET} {len(error_ports)}")
    print(f"  {Colors.BRIGHT_CYAN}Tempo decorrido:{Colors.RESET} {elapsed_time:.2f}s")
    print()

def scan_host(ip, ports="common", scan_type="syn", threads=100, timeout=1, grab_banners=False):
    """
    Função principal para escanear um host
    
    Args:
        ip: Endereço IP alvo
        ports: "common" para portas comuns, ou lista/range de portas
        scan_type: "syn" ou "connect"
        threads: Número de threads
        timeout: Timeout por porta
        grab_banners: Se deve obter banners
    """
    print_header("MODO DE ESCANEAMENTO DE PORTAS", Colors.BRIGHT_MAGENTA)
    print_info(f"Alvo: {Colors.BRIGHT_WHITE}{ip}{Colors.RESET}")
    
    if ports == "common":
        print_info("Escaneando portas comuns...")
        results = scan_common_ports(ip, scan_type, threads, timeout, grab_banners)
    else:
        results = scan_ports(ip, ports, scan_type, threads, timeout, grab_banners)
    
    display_results(results)
    
    return results

