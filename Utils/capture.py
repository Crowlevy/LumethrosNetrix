from scapy.all import sniff
from Utils.filters import packet_filter

def packet_callback(packet, filter_criteria, captured_packets):
    if packet_filter(packet, filter_criteria):
        captured_packets.append(packet)
        print(packet.summary())

def start_capture(interface, packet_count=10, filter_criteria=None):
    captured_packets = []
    print(f"Iniciando captura de pacotes na interface {interface}...")
    try:
        sniff(iface=interface, prn=lambda pkt: packet_callback(pkt, filter_criteria, captured_packets), count=packet_count, store=0)
        print("Captura de pacotes completa...")
        return captured_packets
    except PermissionError:
        print(f"Erro: Permissão negada para captura na interface {interface}.")
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None
