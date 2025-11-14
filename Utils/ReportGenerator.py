"""
Lumethros Netrix - Report Generator Module
Gera relatórios HTML dos escaneamentos
"""

import os
from datetime import datetime
from Utils.ui import print_success, print_error, print_info, Colors

def generate_html_report(report_data, output_file="report.html"):
    """
    Gera relatório HTML completo
    
    Args:
        report_data: Dicionário com dados do relatório
        output_file: Nome do arquivo de saída
    """
    try:
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lumethros Netrix - Relatório de Análise de Rede</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #e0e0e0;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #2a2a3e;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #dc143c 0%, #8b0000 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            background: #1e1e2e;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            border-left: 4px solid #dc143c;
        }}
        
        .section h2 {{
            color: #dc143c;
            font-size: 1.8em;
            margin-bottom: 20px;
            border-bottom: 2px solid #dc143c;
            padding-bottom: 10px;
        }}
        
        .section h3 {{
            color: #ff6b6b;
            font-size: 1.3em;
            margin-top: 20px;
            margin-bottom: 15px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .info-card {{
            background: #2a2a3e;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #3a3a4e;
        }}
        
        .info-card strong {{
            color: #ff6b6b;
            display: block;
            margin-bottom: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: #2a2a3e;
        }}
        
        th {{
            background: #dc143c;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            padding: 10px;
            border-bottom: 1px solid #3a3a4e;
        }}
        
        tr:hover {{
            background: #3a3a4e;
        }}
        
        .status-open {{
            color: #4ade80;
            font-weight: bold;
        }}
        
        .status-closed {{
            color: #f87171;
        }}
        
        .status-filtered {{
            color: #94a3b8;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
            margin: 2px;
        }}
        
        .badge-router {{
            background: #fbbf24;
            color: #1e1e2e;
        }}
        
        .badge-computer {{
            background: #60a5fa;
            color: white;
        }}
        
        .badge-apple {{
            background: #34d399;
            color: #1e1e2e;
        }}
        
        .badge-unknown {{
            background: #94a3b8;
            color: #1e1e2e;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin: 20px 0;
        }}
        
        .stat-box {{
            background: #2a2a3e;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            min-width: 150px;
            margin: 10px;
            border: 2px solid #dc143c;
        }}
        
        .stat-box .number {{
            font-size: 2.5em;
            color: #dc143c;
            font-weight: bold;
        }}
        
        .stat-box .label {{
            color: #94a3b8;
            margin-top: 5px;
        }}
        
        .footer {{
            background: #1e1e2e;
            padding: 20px;
            text-align: center;
            color: #94a3b8;
            border-top: 1px solid #3a3a4e;
        }}
        
        .timestamp {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .banner {{
            font-family: 'Courier New', monospace;
            background: #1e1e2e;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #dc143c;
            margin: 5px 0;
            font-size: 0.9em;
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Lumethros Netrix</h1>
            <p>Relatório de Análise de Rede e Segurança</p>
            <div class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        </div>
        
        <div class="content">
"""
        
        #seção de Informações Gerais
        if 'general' in report_data:
            general = report_data['general']
            html_content += f"""
            <div class="section">
                <h2>Informações Gerais</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <strong>Data do Escaneamento</strong>
                        {general.get('scan_date', 'N/A')}
                    </div>
                    <div class="info-card">
                        <strong>Rede Analisada</strong>
                        {general.get('network', 'N/A')}
                    </div>
                    <div class="info-card">
                        <strong>Interface Utilizada</strong>
                        {general.get('interface', 'N/A')}
                    </div>
                    <div class="info-card">
                        <strong>Tempo de Execução</strong>
                        {general.get('duration', 'N/A')}
                    </div>
                </div>
            </div>
"""
        
        #seção de Hosts Detectados
        if 'hosts' in report_data and report_data['hosts']:
            hosts = report_data['hosts']
            html_content += f"""
            <div class="section">
                <h2>🖥️ Hosts Vivos Detectados</h2>
                <div class="stats">
                    <div class="stat-box">
                        <div class="number">{len(hosts)}</div>
                        <div class="label">Dispositivos</div>
                    </div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Endereço IP</th>
                            <th>Endereço MAC</th>
                            <th>Hostname</th>
                            <th>Vendor</th>
                            <th>Tipo de Dispositivo</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for host in hosts:
                device_type = host.get('device_type') or '-'
                vendor = host.get('vendor') or ''
                badge_class = 'badge-unknown'
                device_type_str = str(device_type).lower()
                vendor_str = str(vendor).lower()
                if device_type and ('router' in device_type_str or 'gateway' in device_type_str):
                    badge_class = 'badge-router'
                elif vendor and 'apple' in vendor_str:
                    badge_class = 'badge-apple'
                elif device_type and ('computer' in device_type_str or 'laptop' in device_type_str):
                    badge_class = 'badge-computer'
                
                html_content += f"""
                        <tr>
                            <td><strong>{host.get('ip', '-')}</strong></td>
                            <td>{host.get('mac', '-')}</td>
                            <td>{host.get('hostname', '-')}</td>
                            <td>{host.get('vendor', 'Unknown')}</td>
                            <td><span class="badge {badge_class}">{device_type}</span></td>
                        </tr>
"""
            html_content += """
                    </tbody>
                </table>
            </div>
"""
        
        #seção de Portas Escaneadas
        if 'ports' in report_data and report_data['ports']:
            ports_data = report_data['ports']
            open_ports = ports_data.get('open', [])
            
            html_content += f"""
            <div class="section">
                <h2>🔌 Portas Escaneadas</h2>
                <div class="stats">
                    <div class="stat-box">
                        <div class="number">{ports_data.get('total_scanned', 0)}</div>
                        <div class="label">Total Escaneado</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">{len(open_ports)}</div>
                        <div class="label">Portas Abertas</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">{ports_data.get('closed', 0)}</div>
                        <div class="label">Portas Fechadas</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">{ports_data.get('filtered', 0)}</div>
                        <div class="label">Portas Filtradas</div>
                    </div>
                </div>
"""
            
            if open_ports:
                html_content += """
                <h3>Portas Abertas</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Porta</th>
                            <th>Serviço</th>
                            <th>Status</th>
                            <th>Banner</th>
                        </tr>
                    </thead>
                    <tbody>
"""
                for port_info in open_ports:
                    if isinstance(port_info, tuple):
                        port, banner = port_info
                    else:
                        port = port_info
                        banner = None
                    
                    service = get_service_name(port)
                    banner_html = f'<div class="banner">{banner}</div>' if banner else '-'
                    
                    html_content += f"""
                        <tr>
                            <td><strong>{port}</strong></td>
                            <td>{service}</td>
                            <td><span class="status-open">OPEN</span></td>
                            <td>{banner_html}</td>
                        </tr>
"""
                html_content += """
                    </tbody>
                </table>
"""
            html_content += """
            </div>
"""
        
        # Seção de Estatísticas da Rede
        if 'statistics' in report_data:
            stats = report_data['statistics']
            html_content += f"""
            <div class="section">
                <h2>Estatísticas da Rede</h2>
                <div class="stats">
"""
            if stats.get('routers', 0) > 0:
                html_content += f"""
                    <div class="stat-box">
                        <div class="number">{stats.get('routers', 0)}</div>
                        <div class="label">📡 Routers/Gateways</div>
                    </div>
"""
            if stats.get('computers', 0) > 0:
                html_content += f"""
                    <div class="stat-box">
                        <div class="number">{stats.get('computers', 0)}</div>
                        <div class="label">Computadores</div>
                    </div>
"""
            if stats.get('apple_devices', 0) > 0:
                html_content += f"""
                    <div class="stat-box">
                        <div class="number">{stats.get('apple_devices', 0)}</div>
                        <div class="label">Dispositivos Apple</div>
                    </div>
"""
            if stats.get('unknown', 0) > 0:
                html_content += f"""
                    <div class="stat-box">
                        <div class="number">{stats.get('unknown', 0)}</div>
                        <div class="label">Desconhecidos</div>
                    </div>
"""
            html_content += """
                </div>
            </div>
"""
        
        # footer
        html_content += f"""
        </div>
        
        <div class="footer">
            <p><strong>Lumethros Netrix</strong> - Advanced Network Analysis & Security Tool v2.0</p>
            <p>by Crowlevy for TCC (Trabalho de Conclusão de Curso)</p>
            <p class="timestamp">⚠️ Este relatório contém informações sensíveis. Use com responsabilidade.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Salva o arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print_success(f"Relatório HTML gerado: {Colors.BRIGHT_WHITE}{output_file}{Colors.RESET}")
        return output_file
        
    except Exception as e:
        print_error(f"Erro ao gerar relatório: {e}")
        return None

def get_service_name(port):
    """Retorna o nome do serviço para uma porta"""
    common_ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt"
    }
    return common_ports.get(port, "Unknown")

def create_report_from_hosts(hosts_data, network_info=None, output_file="report.html"):
    """
    Cria relatório a partir de dados de hosts detectados
    
    Args:
        hosts_data: Lista de hosts detectados
        network_info: Informações da rede
        output_file: Nome do arquivo de saída
    """
    report_data = {
        'general': {
            'scan_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'network': network_info.get('network', 'N/A') if network_info else 'N/A',
            'interface': network_info.get('interface', 'N/A') if network_info else 'N/A',
            'duration': network_info.get('duration', 'N/A') if network_info else 'N/A'
        },
        'hosts': hosts_data,
        'statistics': {
            'routers': sum(1 for h in hosts_data if h.get('device_type') and ('router' in str(h.get('device_type', '')).lower() or 'gateway' in str(h.get('device_type', '')).lower())),
            'computers': sum(1 for h in hosts_data if h.get('device_type') and ('computer' in str(h.get('device_type', '')).lower() or 'laptop' in str(h.get('device_type', '')).lower())),
            'apple_devices': sum(1 for h in hosts_data if h.get('vendor') and 'apple' in str(h.get('vendor', '')).lower()),
            'unknown': sum(1 for h in hosts_data if h.get('vendor') == "Unknown" or h.get('vendor') == "Unknown Vendor")
        }
    }
    
    return generate_html_report(report_data, output_file)

def create_report_from_ports(ports_data, ip, output_file="report.html"):
    """
    Cria relatório a partir de dados de escaneamento de portas
    
    Args:
        ports_data: Dados do escaneamento de portas
        ip: IP escaneado
        output_file: Nome do arquivo de saída
    """
    report_data = {
        'general': {
            'scan_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'network': f"Escaneamento de {ip}",
            'interface': 'N/A',
            'duration': f"{ports_data.get('time_elapsed', 0):.2f}s"
        },
        'ports': {
            'open': ports_data.get('open', []),
            'closed': len(ports_data.get('closed', [])),
            'filtered': len(ports_data.get('filtered', [])),
            'total_scanned': ports_data.get('total_scanned', 0)
        }
    }
    
    return generate_html_report(report_data, output_file)

def create_combined_report(hosts_data, ports_data, network_info=None, output_file="report.html"):
    """
    Cria relatório combinado com hosts e portas
    
    Args:
        hosts_data: Lista de hosts detectados
        ports_data: Dados do escaneamento de portas
        network_info: Informações da rede
        output_file: Nome do arquivo de saída
    """
    report_data = {
        'general': {
            'scan_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'network': network_info.get('network', 'N/A') if network_info else 'N/A',
            'interface': network_info.get('interface', 'N/A') if network_info else 'N/A',
            'duration': network_info.get('duration', 'N/A') if network_info else 'N/A'
        },
        'hosts': hosts_data if hosts_data else [],
        'ports': {
            'open': ports_data.get('open', []) if ports_data else [],
            'closed': len(ports_data.get('closed', [])) if ports_data else 0,
            'filtered': len(ports_data.get('filtered', [])) if ports_data else 0,
            'total_scanned': ports_data.get('total_scanned', 0) if ports_data else 0
        },
        'statistics': {
            'routers': sum(1 for h in hosts_data if h.get('device_type') and ('router' in str(h.get('device_type', '')).lower() or 'gateway' in str(h.get('device_type', '')).lower())) if hosts_data else 0,
            'computers': sum(1 for h in hosts_data if h.get('device_type') and ('computer' in str(h.get('device_type', '')).lower() or 'laptop' in str(h.get('device_type', '')).lower())) if hosts_data else 0,
            'apple_devices': sum(1 for h in hosts_data if h.get('vendor') and 'apple' in str(h.get('vendor', '')).lower()) if hosts_data else 0,
            'unknown': sum(1 for h in hosts_data if h.get('vendor') == "Unknown" or h.get('vendor') == "Unknown Vendor") if hosts_data else 0
        }
    }
    
    return generate_html_report(report_data, output_file)

