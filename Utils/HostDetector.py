import ipaddress
import ssl
import urllib.request
import urllib.error
import time
import socket
import subprocess
import re
from scapy.all import ARP, Ether, srp, IP, TCP
from mac_vendor_lookup import MacLookup
from mac_vendor_lookup import VendorNotFoundError
from Utils.ui import (
    print_header, print_success, print_error, print_warning, 
    print_info, print_progress, print_table_header, print_table_row, 
    print_table_footer, print_separator, Colors
)

#maclookup uma vez para melhor performance
mac_lookup = None
use_online_api = False

def get_vendor_from_api(mac):
    """Busca vendor usando múltiplas APIs online como fallback"""
    #normaliza o MAC address
    mac_normalized = mac.replace('-', ':').upper()
    oui = ':'.join(mac_normalized.split(':')[:3])
    oui_no_colon = oui.replace(':', '')
    
    #lista de api e formatos para tentar
    apis = [
        f"https://api.macvendors.com/{mac_normalized}",
        f"https://api.macvendors.com/{oui}",
        f"https://macvendors.com/api/vendorname/{mac_normalized}",
        f"https://macvendors.com/api/vendorname/{oui}",
    ]
    
    #contexto ssl que não verifica certificados (para resolver o problema de ssl)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for url in apis:
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                vendor = response.read().decode('utf-8', errors='ignore').strip()
                #remove possíveis tags HTML ou caracteres especiais
                vendor = vendor.replace('<', '').replace('>', '').replace('&nbsp;', ' ').strip()
                
                if vendor and len(vendor) > 0:
                    #verifica se não é uma resposta de erro
                    vendor_lower = vendor.lower()
                    if (vendor_lower != "not found" and 
                        not vendor_lower.startswith("error") and
                        not vendor_lower.startswith("invalid") and
                        not vendor_lower.startswith("no results") and
                        len(vendor) > 2 and
                        len(vendor) < 200):  #evita respostas muito longas (provavelmente HTML)
                        return vendor
        except urllib.error.HTTPError as e:
            #se for 404, tenta próxima API
            if e.code == 404:
                continue
            #se for rate limit (429), espera um pouco mais
            elif e.code == 429:
                time.sleep(0.5)
                continue
        except urllib.error.URLError:
            #erro de URL, tenta próxima
            continue
        except Exception:
            #tenta próxima API em caso de erro
            continue
        #pequeno delay para evitar rate limiting
        time.sleep(0.15)
    
    #tenta uma última vez com uma API alternativa usando OUI
    try:
        #tenta buscar direto do IEEE OUI database (formato alternativo)
        url = f"https://standards-oui.ieee.org/oui/{oui_no_colon}.txt"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, context=ssl_context, timeout=8) as response:
            content = response.read().decode('utf-8', errors='ignore')
            #procura por padrões comuns no formato IEEE OUI
            for line in content.split('\n'):
                if '(base 16)' in line or 'Organization' in line:
                    parts = line.split('\t')
                    if len(parts) > 1:
                        vendor = parts[-1].strip()
                        if vendor and len(vendor) > 2:
                            return vendor
    except Exception:
        pass
    
    return None

def init_mac_lookup():
    """inicializa o MacLookup e atualiza o banco de dados se necessário"""
    global mac_lookup, use_online_api
    if mac_lookup is None:
        try:
            mac_lookup = MacLookup()
            #tenta atualizar o banco de dados de vendors
            try:
                print_info("Atualizando banco de dados de vendors MAC (isso pode levar um momento na primeira execução)...")
                mac_lookup.update_vendors()
                print_success("Banco de dados de vendors MAC atualizado com sucesso.")
                use_online_api = False
            except Exception as update_error:
                #se falhar ao atualizar, usa API online como fallback
                error_msg = str(update_error)
                if "SSL" in error_msg or "certificate" in error_msg.lower():
                    print_warning("Problema de certificado SSL detectado. Usando API online como alternativa.")
                    use_online_api = True
                else:
                    print_warning(f"Não foi possível atualizar o banco de dados de vendors, tentando API online: {update_error}")
                    use_online_api = True
        except Exception as e:
            print_warning(f"Não foi possível inicializar a busca de vendors MAC: {e}")
            print_info("Usando API online como alternativa.")
            mac_lookup = None
            use_online_api = True
    return mac_lookup

def is_private_mac(mac):
    """verifica se o MAC é privado/local (não tem vendor registrado)"""
    mac_normalized = mac.replace('-', ':').upper()
    parts = mac_normalized.split(':')
    if len(parts) < 3:
        return False
    
    #se o segundo bit menos significativo do primeiro octeto está definido
    #isso indica um MAC localmente administrado
    first_octet = int(parts[0], 16)
    if (first_octet & 0x02) != 0:
        return True
    
    #verifica alguns padrões conhecidos de macs privados
    oui = ':'.join(parts[:3])
    private_ouis = [
        '02:00:00',  #Locally administered
        '00:50:56',  #VMware (pode ter vendor)
        '00:0C:29',  #VMware
        '00:05:69',  #VMware
    ]
    
    return oui in private_ouis

def detect_device_type(vendor, mac, ip):
    """Tenta identificar o tipo específico de dispositivo baseado no vendor e padrões conhecidos"""
    vendor_lower = vendor.lower() if vendor else ""
    mac_normalized = mac.replace('-', ':').upper()
    oui = ':'.join(mac_normalized.split(':')[:3])
    
    #verifica se é provavelmente um gateway/router (geralmente .1 ou .254)
    ip_parts = ip.split('.')
    last_octet = None
    if len(ip_parts) == 4:
        last_octet = ip_parts[-1]
        if last_octet in ['1', '254']:
            # Provavelmente é um router/gateway
            if not vendor_lower or 'unknown' in vendor_lower:
                return "Router/Gateway (likely)"
    
    #base de dados de padrões conhecidos de dispositivos
    device_patterns = {
        #apple devices
        'apple': {
            'macbook': ['8c:85:90', 'a4:c7:3d', 'f0:db:e2', 'c8:bc:c8', 'f8:1e:df', 'a0:99:9b'],
            'iphone': ['00:0e:c6', '00:23:df', '00:25:4b', '00:26:4a', '00:26:bb', 'f0:db:e2'],
            'ipad': ['00:23:12', '00:25:00', '00:26:08'],
            'airpods': ['dc:a6:32', 'f8:ff:c2'],
            'apple tv': ['00:25:00', '00:26:08'],
            'homepod': ['70:48:0f'],
        },
        #routers/gateways
        'd-link': {
            'router': ['58:d5:6e', '00:1b:11', '00:1e:58'],
            'access point': ['00:1b:11', '00:1e:58'],
        },
        'zte': {
            'router': ['c0:b1:01', '00:15:eb'],
            'modem': ['c0:b1:01'],
        },
        'asus': {
            'router': ['ac:9e:17', '00:1d:60', '00:1e:8c'],
            'laptop': ['ac:9e:17'],
        },
        'hon hai': {
            'router': ['68:94:23'],
            'access point': ['68:94:23'],
        },
        'proware': {
            'router': ['6c:fd:b9'],
            'access point': ['6c:fd:b9'],
        },
    }
    
    #verifica padrões específicos
    device_type = None
    
    #verifica Apple (precisa ser mais específico para não pegar outros "Inc.")
    if vendor_lower.startswith('apple') or (vendor_lower == 'apple, inc.' or 'apple inc' in vendor_lower):
        for device, macs in device_patterns.get('apple', {}).items():
            if any(oui.startswith(m) for m in macs):
                device_type = device.replace('_', ' ').title()
                break
        if not device_type:
            #tenta identificar pelo OUI específico
            if oui.startswith('8c:85:90'):
                device_type = "MacBook/Apple Computer"
            else:
                device_type = "Apple Device"
    
    elif 'd-link' in vendor_lower or 'dlink' in vendor_lower:
        for device, macs in device_patterns.get('d-link', {}).items():
            if any(oui.startswith(m) for m in macs):
                device_type = f"D-Link {device.title()}"
                break
        if not device_type:
            device_type = "D-Link Router/Device"
    
    elif 'zte' in vendor_lower:
        for device, macs in device_patterns.get('zte', {}).items():
            if any(oui.startswith(m) for m in macs):
                device_type = f"ZTE {device.title()}"
                break
        if not device_type:
            if last_octet in ['1', '254']:
                device_type = "ZTE Router/Modem"
            else:
                device_type = "ZTE Device"
    
    elif 'asus' in vendor_lower or 'asustek' in vendor_lower:
        for device, macs in device_patterns.get('asus', {}).items():
            if any(oui.startswith(m) for m in macs):
                device_type = f"ASUS {device.title()}"
                break
        if not device_type:
            if last_octet in ['1', '254']:
                device_type = "ASUS Router"
            else:
                device_type = "ASUS Computer/Device"
    
    elif 'hon hai' in vendor_lower or 'foxconn' in vendor_lower:
        device_type = "Router/Access Point"
    
    elif 'proware' in vendor_lower:
        device_type = "Router/Network Device"
    
    if not device_type:
        device_type = try_identify_via_http(ip)
    
    #se ainda não identificou e está em IP comum de gateway
    if not device_type and last_octet and last_octet in ['1', '254']:
        device_type = "Router/Gateway (likely)"
    
    return device_type

def get_hostname_from_arp(ip):
    """tenta obter hostname da tabela ARP do sistema"""
    try:
        #no macOS/Linux, usa arp -a
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            #procura o IP na saída do arp
            for line in result.stdout.split('\n'):
                if ip in line:
                    # macOS formato: hostname (ip) at mac [ether] on interface
                    # Linux formato: hostname (ip) at mac [ether] on interface
                    # Tenta múltiplos padrões
                    patterns = [
                        r'([^\s\(]+)\s*\(',  # hostname (ip)
                        r'\(([^\)]+)\)',     # (ip) - se não tiver hostname antes
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            hostname = match.group(1).strip()
                            #pegou o IP, pula
                            if hostname == ip:
                                continue
                            #remove dominio se presente
                            if '.' in hostname:
                                hostname = hostname.split('.')[0]
                            #verifica se não é apenas números (provavelmente IP)
                            if not re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname):
                                return hostname
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, Exception):
        pass
    return None

def get_hostname_via_mdns(ip):
    """Tenta resolver hostname via mDNS/Bonjour usando dns-sd"""
    try:
        #usa dns-sd para resolver via mDNS (Bonjour)
        #formato: dns-sd -G v4 <hostname> ou dns-sd -Q <ip>
        result = subprocess.run(['dns-sd', '-Q', ip], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                #procura por linhas com informações de nome
                if 'name' in line.lower() or 'canonical' in line.lower():
                    #extrai o hostname
                    parts = line.split()
                    for part in parts:
                        if '.' in part and ip not in part and not part.startswith('in-addr'):
                            hostname = part.rstrip('.')
                            if '.' in hostname:
                                hostname = hostname.split('.')[0]
                            if hostname and hostname != '?' and len(hostname) > 1:
                                return hostname
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, Exception):
        pass
    return None

def get_hostname(ip):
    """tenta resolver o hostname do IP usando múltiplos métodos"""
    #método 1: tenta obter da tabela ARP (mais rápido e confiável em redes locais)
    hostname = get_hostname_from_arp(ip)
    if hostname and hostname != '?':
        return hostname
    
    #método 2: tenta mDNS/Bonjour (muito comum no macOS/iOS)
    hostname = get_hostname_via_mdns(ip)
    if hostname:
        return hostname
    
    #método 3: tenta reverse DNS usando comando host
    try:
        result = subprocess.run(['host', ip], capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            #formato: ip.in-addr.arpa domain name pointer hostname.
            for line in result.stdout.split('\n'):
                if 'pointer' in line.lower() or 'name' in line.lower():
                    #extrai o hostname
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'pointer' in part.lower() or 'name' in part.lower():
                            if i + 1 < len(parts):
                                hostname = parts[i + 1].rstrip('.')
                                if '.' in hostname:
                                    hostname = hostname.split('.')[0]
                                if hostname and hostname != '?':
                                    return hostname
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, Exception):
        pass
    
    #método 4: tenta resolução DNS reversa via socket
    try:
        socket.setdefaulttimeout(1.0)
        hostname = socket.gethostbyaddr(ip)[0]
        if '.' in hostname:
            hostname = hostname.split('.')[0]
        if hostname and hostname != '?':
            return hostname
    except (socket.herror, socket.gaierror, OSError, socket.timeout, Exception):
        pass
    finally:
        socket.setdefaulttimeout(None)
    
    return None

def try_identify_via_http(ip):
    """tenta identificar o dispositivo através de uma verificação HTTP rápida"""
    common_ports = [80, 8080, 443, 8443]
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                #porta aberta, tenta fazer uma requisição HTTP
                try:
                    url = f"http://{ip}:{port}" if port != 80 else f"http://{ip}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    with urllib.request.urlopen(req, context=ssl_context, timeout=2) as response:
                        server_header = response.headers.get('Server', '')
                        if server_header:
                            #tenta identificar pelo header Server
                            server_lower = server_header.lower()
                            if 'router' in server_lower or 'gateway' in server_lower:
                                return "Router/Gateway"
                            elif 'apache' in server_lower:
                                return "Web Server"
                            elif 'nginx' in server_lower:
                                return "Web Server/Proxy"
                except:
                    pass
        except:
            continue
    
    return None

def get_mac_vendor(mac):   
    global use_online_api
    
    #verifica se é um MAC privado/local
    if is_private_mac(mac):
        #ainda tenta buscar, mas pode não encontrar
        pass
    
    #se a biblioteca local não está disponível ou falhou, usa API online
    if use_online_api or mac_lookup is None:
        vendor = get_vendor_from_api(mac)
        if vendor:
            if vendor == "PCS Systemtechnik GmbH" or vendor == "Oracle Corp":
                vendor = "Virtual Box"
            return vendor
        #se não encontrou e é MAC privado, retorna informação mais específica
        if is_private_mac(mac):
            return "Private/Local MAC"
        return "Unknown"
    
    try:
        lookup = init_mac_lookup()
        if lookup is None:
            vendor = get_vendor_from_api(mac)
            if vendor:
                return vendor
            if is_private_mac(mac):
                return "Private/Local MAC"
            return "Unknown"
        
        vendor = lookup.lookup(mac)
        if not vendor or vendor.strip() == "":
            vendor = get_vendor_from_api(mac)
            if vendor:
                return vendor
            if is_private_mac(mac):
                return "Private/Local MAC"
            return "Unknown"
        
        if vendor == "PCS Systemtechnik GmbH" or vendor == "Oracle Corp":
            vendor = "Virtual Box"
        return vendor
    except VendorNotFoundError:
        #vendor não encontrado no banco de dados local, tenta API online
        vendor = get_vendor_from_api(mac)
        if vendor:
            return vendor
        if is_private_mac(mac):
            return "Private/Local MAC"
        return "Unknown"
    except Exception as e:
        #outros erros, tenta API online como fallback
        vendor = get_vendor_from_api(mac)
        if vendor:
            return vendor
        if is_private_mac(mac):
            return "Private/Local MAC"
        return "Unknown"

def detect_live_hosts(local_ip, interface=None):
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    print_info(f"Seu IP: {Colors.BRIGHT_WHITE}{local_ip}{Colors.RESET}")
    print_info(f"Faixa de Rede: {Colors.BRIGHT_WHITE}{network}{Colors.RESET}\n")
    
    print_info("Inicializando busca de vendors MAC...")
    init_mac_lookup()
    
    target_ip = f"{network.network_address}/24"
    ethernet = Ether(dst="ff:ff:ff:ff:ff:ff") # send to all devices 
    arp = ARP(pdst=target_ip)
    packet = ethernet/arp
    
    if interface:
        print_info(f"Escaneando rede em busca de hosts vivos na interface {Colors.BRIGHT_WHITE}{interface}{Colors.RESET}...")
    else:
        print_info("Escaneando rede em busca de hosts vivos...")
    
    try:
        # Se interface foi especificada, usa ela, senão deixa o Scapy escolher
        if interface:
            result = srp(packet, timeout=15, verbose=False, retry=3, iface=interface)[0]
        else:
            result = srp(packet, timeout=15, verbose=False, retry=3)[0]
    except Exception as e:
        print_error(f"Erro durante o escaneamento da rede: {e}")
        if interface:
            print_warning(f"Tentando sem especificar a interface {interface}...")
        try:
            result = srp(packet, timeout=15, verbose=False, retry=3)[0]
        except Exception as e2:
            print_error(f"Erro: {e2}")
            result = []
    
    live_hosts = []
    
    if not result:
        print_warning("Nenhum host respondeu ao escaneamento ARP. Isso pode ser devido a:")
        print(f"  {Colors.YELLOW}•{Colors.RESET} Firewall de rede bloqueando requisições ARP")
        print(f"  {Colors.YELLOW}•{Colors.RESET} Dispositivos não respondendo a ARP")
        print(f"  {Colors.YELLOW}•{Colors.RESET} Problema com a interface de rede")
        print(f"  {Colors.YELLOW}•{Colors.RESET} Tente executar com sudo se ainda não o fez")
        return

    if use_online_api:
        print_info("Buscando vendors MAC usando API online (isso pode levar um momento)...")
    else:
        print_info("Buscando vendors MAC...")
    
    total_hosts = len(result)
    print_success(f"Encontrado(s) {Colors.BRIGHT_WHITE}{total_hosts}{Colors.RESET} host(s), analisando dispositivos...\n")
    
    for idx, (sent, received) in enumerate(result, 1):
        if use_online_api and total_hosts > 1:
            print_progress(idx, total_hosts, f"Analisando {received.psrc}")
        
        vendor = get_mac_vendor(received.hwsrc)
        device_type = detect_device_type(vendor, received.hwsrc, received.psrc)
        hostname = get_hostname(received.psrc)
        
        #n encontrou hostname e é o IP local, tenta obter do sistema
        if not hostname and received.psrc == local_ip:
            try:
                #no macOS, tenta usar scutil primeiro (mais confiável)
                try:
                    result = subprocess.run(['scutil', '--get', 'ComputerName'], 
                                          capture_output=True, text=True, timeout=0.5)
                    if result.returncode == 0 and result.stdout.strip():
                        hostname = result.stdout.strip()
                except:
                    #fallback para socket.gethostname()
                    hostname = socket.gethostname()
                    if '.' in hostname:
                        hostname = hostname.split('.')[0]
            except:
                pass
        
        host_info = {
            "ip": received.psrc,
            "mac": received.hwsrc,
            "vendor": vendor,
            "device_type": device_type,
            "hostname": hostname
        }
        live_hosts.append(host_info)
    
    if use_online_api and total_hosts > 1:
        print() 
    
    if live_hosts:
        print() 
        print_header("HOSTS VIVOS DETECTADOS", Colors.BRIGHT_GREEN)
        
        live_hosts.sort(key=lambda x: ipaddress.IPv4Address(x['ip']))
        
        widths = [18, 20, 25, 35, 20]
        headers = ["IP Address", "MAC Address", "Hostname", "Vendor", "Device Type"]
        
        print_table_header(headers, widths, Colors.RED)
        
        for host in live_hosts:
            ip = host['ip']
            mac = host['mac']
            hostname = host['hostname'] if host['hostname'] else f"{Colors.DIM}-{Colors.RESET}"
            
            vendor_info = host['vendor'] if host['vendor'] != "Unknown" else f"{Colors.DIM}Unknown{Colors.RESET}"
            device_type = host['device_type'] if host['device_type'] else f"{Colors.DIM}-{Colors.RESET}"
            
            #trunca vendor se muito longo
            if len(vendor_info.replace(Colors.DIM, '').replace(Colors.RESET, '')) > 33:
                vendor_info = vendor_info[:30] + "..."
            
            #trunca device_type se muito longo
            if len(device_type.replace(Colors.DIM, '').replace(Colors.RESET, '')) > 18:
                device_type = device_type[:15] + "..."
            
            #trunca hostname se muito longo
            if len(str(hostname).replace(Colors.DIM, '').replace(Colors.RESET, '')) > 23:
                hostname = str(hostname)[:20] + "..."
            
            row_color = Colors.WHITE
            if 'router' in device_type.lower() or 'gateway' in device_type.lower():
                row_color = Colors.BRIGHT_YELLOW
            elif 'apple' in vendor_info.lower():
                row_color = Colors.BRIGHT_GREEN
            elif 'unknown' in vendor_info.lower():
                row_color = Colors.DIM
            
            print_table_row([ip, mac, hostname, vendor_info, device_type], widths, row_color)
        
        print_table_footer(widths, Colors.RED)
        
        print(f"\n{Colors.RED}{Colors.BOLD}Total:{Colors.RESET} {Colors.BRIGHT_WHITE}{len(live_hosts)}{Colors.RESET} dispositivo(s) encontrado(s)\n")
        
        #conta quantos hostnames foram encontrados
        hostnames_found = sum(1 for h in live_hosts if h['hostname'] and h['hostname'] != '-')
        if hostnames_found == 0:
            print_warning("Nenhum hostname resolvido. Isso é normal para:")
            print(f"  {Colors.YELLOW}•{Colors.RESET} Routers e dispositivos de rede (geralmente não anunciam hostnames)")
            print(f"  {Colors.YELLOW}•{Colors.RESET} Dispositivos IoT")
            print(f"  {Colors.YELLOW}•{Colors.RESET} Dispositivos sem mDNS/Bonjour configurado")
            print(f"  {Colors.YELLOW}•{Colors.RESET} Dispositivos em redes sem DNS reverso\n")
        
        #estatísticas adicionais
        routers = sum(1 for h in live_hosts if h['device_type'] and ('router' in h['device_type'].lower() or 'gateway' in h['device_type'].lower()))
        apple_devices = sum(1 for h in live_hosts if 'apple' in h['vendor'].lower())
        unknown = sum(1 for h in live_hosts if h['vendor'] == "Unknown" or h['vendor'] == "Unknown Vendor")
        computers = sum(1 for h in live_hosts if h['device_type'] and ('computer' in h['device_type'].lower() or 'laptop' in h['device_type'].lower() or 'macbook' in h['device_type'].lower()))
        
        if routers > 0 or apple_devices > 0 or unknown > 0 or computers > 0:
            print_header("RESUMO DA REDE", Colors.BRIGHT_MAGENTA)
            if routers > 0:
                print(f"  {Colors.BRIGHT_YELLOW}{Colors.RESET} {Colors.BRIGHT_WHITE}Routers/Gateways:{Colors.RESET} {Colors.BRIGHT_GREEN}{routers}{Colors.RESET}")
            if computers > 0:
                print(f"  {Colors.RED}{Colors.RESET} {Colors.BRIGHT_WHITE}Computadores/Notebooks:{Colors.RESET} {Colors.BRIGHT_GREEN}{computers}{Colors.RESET}")
            if apple_devices > 0:
                print(f"  {Colors.BRIGHT_GREEN}{Colors.RESET} {Colors.BRIGHT_WHITE}Dispositivos Apple:{Colors.RESET} {Colors.BRIGHT_GREEN}{apple_devices}{Colors.RESET}")
            if unknown > 0:
                print(f"  {Colors.BRIGHT_YELLOW}{Colors.RESET} {Colors.BRIGHT_WHITE}Dispositivos Desconhecidos:{Colors.RESET} {Colors.BRIGHT_YELLOW}{unknown}{Colors.RESET}")
            print()
    else:
        print_error("Nenhum host vivo encontrado.")


