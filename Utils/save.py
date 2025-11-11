#crowlevy@gmail.com
from scapy.all import wrpcap

captured_packets = []

def save_to_txt(captured_packets, filename):
    try:
        with open(filename, 'w') as f:
            for packet in captured_packets:
                f.write(packet.summary() + '\n')
        print(f"Pacotes salvos em {filename}")
    except Exception as e:
        print(f"Erro ao salvar pacotes em TXT: {e}")

def save_to_pcap(captured_packets, filename):
    try:
        wrpcap(filename, captured_packets)
        print(f"Pacotes salvos em {filename}")
    except Exception as e:
        print(f"Erro ao salvar pacotes em PCAP: {e}")
