# Lumethros Netrix

<div align="center">

**Advanced Network Analysis & Security Tool**

*by Crowlevy for TCC (Trabalho de Conclusão de Curso)*

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

</div>

---

## Índice

- [Visão Geral](#-visão-geral)
- [Características Principais](#-características-principais)
- [Requisitos do Sistema](#-requisitos-do-sistema)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Exemplos Práticos](#-exemplos-práticos)
- [Segurança e Privacidade](#-segurança-e-privacidade)
- [Solução de Problemas](#-solução-de-problemas)
- [Aviso Legal](#-aviso-legal)
- [Licença](#-licença)
- [Contato](#-contato)

---

## Visão Geral

**Lumethros Netrix** é uma ferramenta avançada de análise de rede desenvolvida em Python, projetada para profissionais de segurança cibernética, administradores de rede e testadores de penetração. A ferramenta oferece capacidades poderosas de monitoramento de tráfego de rede, detecção de dispositivos em tempo real e análise de vulnerabilidades.

### O que esta ferramenta faz?

**Captura e analisa** pacotes de rede em tempo real  
**Detecta dispositivos** ativos na sua rede local  
**Identifica fabricantes** de dispositivos através de endereços MAC  
**Classifica dispositivos** por tipo (routers, computadores, IoT, etc.)  
**Escaneia portas** TCP com detecção de serviços e banner grabbing  
**Gera relatórios HTML** profissionais dos escaneamentos  
**Exporta dados** em formatos PCAP, TXT e HTML para análise posterior  
**Autenticação segura** com hash SHA-256 para proteger o acesso  

---

## Características Principais

### Captura e Análise de Pacotes
- Capture tráfego de rede de qualquer interface de rede
- Filtros BPF (Berkeley Packet Filter) personalizados
- Análise em tempo real de protocolos (TCP, UDP, ICMP, IPv6)
- Extração de informações detalhadas: IPs, portas, protocolos e payloads

### Detecção de Hosts Vivos
- Varredura de rede usando requisições ARP
- Mapeamento completo: IP, MAC, fabricante e tipo de dispositivo
- Identificação automática de tipos de dispositivos (routers, computadores, etc.)
- Resolução de hostnames quando disponível
- Estatísticas detalhadas da rede

### Escaneamento de Portas
- Escaneamento TCP SYN (stealth scan) e Connect scan
- Detecção automática de serviços comuns (HTTP, SSH, FTP, etc.)
- Banner grabbing para identificar versões de serviços
- Escaneamento paralelo com múltiplas threads
- Suporte para portas comuns, ranges e listas personalizadas
- Estatísticas detalhadas (abertas, fechadas, filtradas)

### Geração de Relatórios HTML
- Relatórios HTML profissionais e responsivos
- Design moderno com tema escuro
- Tabelas formatadas de hosts e portas
- Estatísticas visuais com badges e cards
- Informações completas do escaneamento
- Pronto para impressão e compartilhamento

### Segurança
- Autenticação com senha protegida por SHA-256
- Armazenamento seguro de credenciais
- Proteção contra acesso não autorizado

### Exportação de Dados
- Formato **PCAP** (compatível com Wireshark)
- Formato **TXT** (análise textual)
- Formato **HTML** (relatórios profissionais)
- Facilita análise posterior e compartilhamento

---

## Requisitos do Sistema

### Software Necessário
- **Python 3.7 ou superior**
- **Biblioteca Scapy** (instalada automaticamente)
- **Biblioteca mac-vendor-lookup** (instalada automaticamente)
- **Biblioteca colorama** (instalada automaticamente)

### Permissões
⚠️ **IMPORTANTE**: A ferramenta requer privilégios de administrador para acessar interfaces de rede.

- **Linux/macOS**: Execute com `sudo`
- **Windows**: Execute como Administrador

---

## Instalação

### Passo 1: Clonar o Repositório

   ```bash
   git clone https://github.com/Pawar-Tushar/SecureNet-Analyzer.git
    cd SecureNet-Analyzer
    ```

### Passo 2: Instalar Dependências

    ```bash
    pip install -r requirements.txt
    ```

Ou usando pip3:

```bash
pip3 install -r requirements.txt
```

### Passo 3: Verificar Instalação

    ```bash
python3 Main.py --help
```

Se tudo estiver correto, você verá o banner do **Lumethros Netrix** e as opções de ajuda.

---

## Como Usar

### Estrutura de Comandos

    ```bash
sudo python3 Main.py [modo] [opções]
```

### Modos de Operação

| Modo | Descrição | Uso |
|------|-----------|-----|
| `c` | **Capture Mode** - Captura pacotes de rede | `python3 Main.py c --i en0 --pc 100` |
| `lh` | **Live Host Detection** - Detecta dispositivos na rede | `python3 Main.py lh --ip 192.168.1.1` |
| `ps` | **Port Scanner** - Escaneia portas TCP de um host | `python3 Main.py ps --ip 192.168.1.1` |

### Opções Disponíveis

#### Para Captura de Pacotes (`c`)

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `--i` | Interface de rede | `--i en0` ou `--i eth0` |
| `--pc` | Número de pacotes a capturar | `--pc 100` |
| `--f` | Filtro BPF (opcional) | `--f "tcp and port 80"` |
| `--a` | Analisar pacotes capturados | `--a` |
| `--s` | Salvar pacotes capturados | `--s` |
| `--p` | Salvar em formato PCAP | `--p capture.pcap` |
| `--t` | Salvar em formato TXT | `--t capture.txt` |

#### Para Detecção de Hosts (`lh`)

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `--ip` | Seu endereço IP na rede | `--ip 192.168.1.100` |
| `--i` | Interface de rede (opcional) | `--i en0` |
| `--report` | Gerar relatório HTML | `--report network_report.html` |

#### Para Escaneamento de Portas (`ps`)

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `--ip` | Endereço IP alvo | `--ip 192.168.1.1` |
| `--ports` | Portas para escanear | `--ports common` ou `--ports 1-1000` ou `--ports 80,443,8080` |
| `--scan-type` | Tipo de escaneamento | `--scan-type syn` ou `--scan-type connect` |
| `--threads` | Número de threads paralelas | `--threads 100` (padrão: 100) |
| `--timeout` | Timeout por porta (segundos) | `--timeout 1` (padrão: 1) |
| `--banner` | Tentar obter banners dos serviços | `--banner` |
| `--report` | Gerar relatório HTML | `--report port_scan.html` |

---

## Exemplos Práticos

### Exemplo 1: Capturar e Analisar Pacotes

```bash
sudo python3 Main.py c --i en0 --pc 50 --a --s --p my_capture.pcap
```

**O que faz:**
- Captura 50 pacotes da interface `en0`
- Analisa os pacotes em tempo real (`--a`)
- Salva em formato PCAP (`--p my_capture.pcap`)

### Exemplo 2: Capturar Apenas Tráfego HTTP

```bash
sudo python3 Main.py c --i en0 --pc 100 --f "tcp and port 80" --a
```

**O que faz:**
- Captura 100 pacotes
- Filtra apenas tráfego TCP na porta 80 (HTTP)
- Analisa os pacotes

### Exemplo 3: Detectar Todos os Dispositivos na Rede

```bash
sudo python3 Main.py lh --ip 192.168.1.100 --i en0
```

**O que faz:**
- Escaneia a rede 192.168.1.0/24
- Detecta todos os dispositivos ativos
- Mostra IP, MAC, fabricante e tipo de cada dispositivo

### Exemplo 4: Captura Completa com Análise

```bash
sudo python3 Main.py c --i Wi-Fi --pc 200 --f "src host 192.168.1.1" --a --s --t analysis.txt
```

**O que faz:**
- Captura 200 pacotes da interface Wi-Fi
- Filtra apenas tráfego do IP 192.168.1.1
- Analisa e salva em formato TXT

### Exemplo 5: Escanear Portas Comuns

```bash
sudo python3 Main.py ps --ip 192.168.1.1 --ports common
```

**O que faz:**
- Escaneia portas comuns (21, 22, 23, 25, 53, 80, 443, etc.)
- Detecta serviços rodando
- Mostra portas abertas e seus serviços

### Exemplo 6: Escaneamento Completo com Banner Grabbing

```bash
sudo python3 Main.py ps --ip 192.168.1.1 --ports 1-1000 --scan-type syn --banner --report scan_report.html
```

**O que faz:**
- Escaneia portas de 1 a 1000
- Usa escaneamento SYN (stealth)
- Tenta obter banners dos serviços
- Gera relatório HTML completo

### Exemplo 7: Detecção de Hosts com Relatório

```bash
sudo python3 Main.py lh --ip 192.168.1.100 --i en0 --report network_report.html
```

**O que faz:**
- Detecta todos os hosts vivos na rede
- Identifica vendors e tipos de dispositivos
- Gera relatório HTML profissional com todas as informações

### Exemplo 8: Escaneamento Rápido de Portas Específicas

```bash
sudo python3 Main.py ps --ip 192.168.1.1 --ports 80,443,8080,8443 --banner
```

**O que faz:**
- Escaneia apenas portas HTTP/HTTPS comuns
- Obtém banners dos serviços
- Execução rápida e focada

---

## Segurança e Privacidade

### Autenticação
- **Primeira execução**: Você será solicitado a criar uma senha mestre
- **Senhas**: Armazenadas com hash SHA-256 (nunca em texto plano)
- **Tentativas**: Máximo de 3 tentativas de login

### Boas Práticas
Use apenas em redes que você possui ou tem permissão explícita  
Mantenha suas credenciais seguras 
Não compartilhe arquivos de captura com dados sensíveis  
Use em ambientes controlados para testes  

### ⚠️ Avisos Importantes
- **ARP Spoofing**: A detecção de hosts usa requisições ARP que podem acionar alertas em alguns sistemas
- **Monitoramento**: Capturar tráfego de rede pode ser ilegal sem autorização
- **Dados Sensíveis**: Pacotes capturados podem conter informações confidenciais

---

## Solução de Problemas

### Problema: "Permission denied" ou "No packets captured"

**Solução:**
```bash
# Certifique-se de executar com sudo
sudo python3 Main.py lh --ip 192.168.1.100
```

### Problema: Interface de rede não encontrada

**Solução:**
```bash
# Liste interfaces disponíveis
# Linux/macOS:
ifconfig

# Windows:
ipconfig

# Use o nome correto da interface no comando
```

### Problema: Dependências faltando

**Solução:**
```bash
# Reinstale as dependências
pip3 install --upgrade -r requirements.txt
```

### Problema: Erro de SSL ao atualizar banco de dados MAC

**Solução:**
- Isso é normal! A ferramenta automaticamente usa uma API online como alternativa
- Não afeta a funcionalidade principal

### Problema: Nenhum host encontrado

**Possíveis causas:**
- Firewall bloqueando requisições ARP
- Dispositivos não respondendo a ARP
- Interface de rede incorreta
- Problemas de permissão

**Solução:**
- Verifique se está usando `sudo`
- Tente uma interface de rede diferente
- Verifique se há firewall ativo

### Problema: Port Scanner não encontra portas abertas

**Possíveis causas:**
- Firewall bloqueando conexões
- Host não está acessível
- Timeout muito curto
- Portas realmente fechadas

**Solução:**
- Aumente o timeout: `--timeout 3`
- Tente escaneamento Connect: `--scan-type connect`
- Verifique conectividade: `ping <ip>`
- Verifique se o host está na mesma rede

### Problema: Relatório HTML não é gerado

**Solução:**
- Verifique se o nome do arquivo termina com `.html`
- Verifique permissões de escrita no diretório
- Certifique-se de que há dados para gerar o relatório (hosts ou portas detectadas)

---

## ⚖️ Aviso Legal

### ⚠️ USO RESPONSÁVEL OBRIGATÓRIO

O uso deste código, seja parcial ou completo, para interagir com alvos **sem consentimento prévio e explícito** é **ILEGAL**. É **responsabilidade do usuário final** cumprir todas as **leis locais, estaduais e federais** aplicáveis.

### Responsabilidades

Os desenvolvedores **não assumem responsabilidade** e **não são responsáveis** por qualquer uso indevido ou danos causados pelo uso deste código. Isso se aplica em qualquer circunstância, seja **acidental** ou **intencional**, se o código for utilizado por um atacante ou entidade não autorizada para **comprometer** a segurança, privacidade, confidencialidade, integridade e/ou disponibilidade de sistemas ou recursos associados.

### Uso Autorizado

Os desenvolvedores endossam explicitamente o uso deste código **apenas** em:

**Ambientes educacionais** para aprendizado de conceitos de segurança cibernética  
**Testes de penetração autorizados**, onde o proprietário do sistema deu **consentimento explícito**  

O objetivo deve ser identificar e mitigar vulnerabilidades, protegendo sistemas contra exploração por agentes maliciosos.

### ⚠️ ANTES DE USAR

Certifique-se de ter **autorização por escrito** e aderir a todas as leis e diretrizes éticas relevantes.

**É crucial que esta ferramenta seja usada de forma ética e legal. O uso não autorizado pode resultar em consequências graves sob a lei.**

---

## Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **Scapy**: Por fornecer funcionalidade poderosa para criação e envio de pacotes
- **Python 3.x**: Pela simplicidade e flexibilidade para programação de rede
- **mac-vendor-lookup**: Por fornecer identificação de fabricantes via MAC
- **Wireshark**: Por ser uma ferramenta confiável para análise de arquivos PCAP
- Aos nossos professores que tornaram isso possível. Tmj rapaziada do TI!

---

## Contato

Para dúvidas, problemas ou sugestões:

- **GitHub Issues**: [Abrir uma issue](https://github.com/Crowlevy/LumethrosNetrix)
- **Email**: crowlevt@gmail.com

---

## Conclusão

**Lumethros Netrix** é uma ferramenta robusta e versátil projetada para monitoramento de segurança de rede, análise de pacotes, detecção de hosts vivos, escaneamento de portas e geração de relatórios profissionais. 

Com funcionalidades avançadas como:
- **Detecção de hosts** com identificação de vendors e tipos de dispositivos
- **Escaneamento de portas** TCP com banner grabbing
- **Geração de relatórios HTML** profissionais
- **Interface visual** moderna com ASCII art
- **Autenticação segura** para proteção de acesso

Seja você um administrador de rede, um profissional de segurança cibernética ou um testador de penetração, esta ferramenta fornecerá insights valiosos sobre o comportamento da rede, melhorará o monitoramento de segurança e ajudará a identificar potenciais ameaças e vulnerabilidades.

**Lembre-se: Use com responsabilidade e sempre com autorização adequada!**

---

<div align="center">

**Desenvolvido como um trabalho de TCC**

*2.0v Lumethros Netrix*

</div>
