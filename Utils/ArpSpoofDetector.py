import time
import sys
from scapy.all import sniff, ARP
from Utils.ui import print_error, print_warning, print_info, print_success, Colors

class ArpSpoofDetector:
    def __init__(self):
        self.ip_mac_map = {}
        self.alerts = []

    def process_packet(self, packet):
        if packet.haslayer(ARP) and packet[ARP].op == 2:  # ARP Reply (is-at)
            src_ip = packet[ARP].psrc
            src_mac = packet[ARP].hwsrc

            try:
                #se já conhecemos este ip
                if src_ip in self.ip_mac_map:
                    #se o mac mudou para o mesmo ip
                    if self.ip_mac_map[src_ip] != src_mac:
                        old_mac = self.ip_mac_map[src_ip]
                        message = f"ALERTA: Possível ARP Spoofing detectado!\nIP {src_ip} mudou de MAC: {old_mac} -> {src_mac}"
                        print_warning(f"\n{message}")
                        
                        #log do alerta
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        self.alerts.append(f"[{timestamp}] {message}")
                        
                        #atualiza para o novo mac (para evitar flood de alertas, mas mantém monitorando)
                        #em um cenário real, poderíamos não atualizar para manter o alerta constante
                        # self.ip_mac_map[src_ip] = src_mac 
                else:
                    #novo mapeamento
                    self.ip_mac_map[src_ip] = src_mac
                    # print_info(f"Mapeado: {src_ip} -> {src_mac}") # Verbose demais para produção

            except Exception as e:
                print_error(f"Erro ao processar pacote: {e}")

    def start_monitoring(self, interface=None):
        print_info(f"Iniciando detecção de ARP Spoofing...")
        if interface:
            print_info(f"Interface: {Colors.BRIGHT_WHITE}{interface}{Colors.RESET}")
        
        print_info("Pressione Ctrl+C para parar.")
        print_success("Monitoramento Ativo! 🛡️")
        
        try:
            if interface:
                sniff(iface=interface, store=False, prn=self.process_packet, filter="arp")
            else:
                sniff(store=False, prn=self.process_packet, filter="arp")
        except KeyboardInterrupt:
            print_info("\nMonitoramento interrompido pelo usuário.")
        except Exception as e:
            print_error(f"Erro no monitoramento: {e}")
