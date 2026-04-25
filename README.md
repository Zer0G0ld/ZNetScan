# 🌐 ZNetScan - Ferramenta de Escaneamento de Rede

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-red.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)]()

Uma ferramenta modular e profissional para escaneamento de rede, desenvolvida em Python. Permite descobrir dispositivos na rede local, identificar MAC addresses, fabricantes e realizar escaneamento de portas.

## ✨ Funcionalidades

- 🔍 **Descoberta de dispositivos** - Encontre todos os dispositivos na sua rede local
- 📡 **Múltiplos métodos de scan** - ARP (rápido) e ICMP/Ping (compatível)
- 🏭 **Identificação de fabricantes** - Descubra qual empresa fabricou o dispositivo pelo MAC
- 🔌 **Escaneamento de portas** - Detecte portas abertas e serviços em execução
- 📊 **Múltiplos formatos de saída** - Console, JSON, CSV, TXT, HTML
- 🎯 **Alta performance** - Scan multi-thread para resultados rápidos
- 📝 **Logging completo** - Registro detalhado de todas as operações
- 🐍 **Totalmente modular** - Código organizado e fácil de entender

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Pip (gerenciador de pacotes Python)
- Git (opcional, para clonar o repositório)

### Dependências do Sistema

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install arp-scan -y
```

**macOS:**
```bash
brew install arp-scan
```

**Windows:**
- O método ARP pode não funcionar nativamente
- Use o método ping: `--method ping`
- Ou instale [Wireshark](https://www.wireshark.org/) para ferramentas adicionais

## 🚀 Instalação Rápida

### 1. Clone o repositório
```bash
git clone https://github.com/Zer0G0ld/ZNetScan.git
cd ZNetScan
```

### 2. Execute o setup automático
```bash
# Linux/macOS
chmod +x setup_venv.sh
./setup_venv.sh

# Windows
setup_venv.bat
```

### 3. Ative o ambiente virtual
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate.bat
```

### 4. Verifique a instalação
```bash
python check_installation.py
```

## 📖 Como Usar

### Comandos Básicos

```bash
# Ajuda completa
python main.py --help

# Scan ARP (mais rápido - requer sudo)
sudo python main.py --method arp

# Scan Ping (mais lento - não requer sudo)
python main.py --method ping

# Escanear rede específica
python main.py --network 192.168.0.0/24

# Scan com saída em JSON
python main.py --output json -f resultados.json
```

### Escaneamento de Portas

```bash
# Scan rápido das portas mais comuns
python main.py --port-scan 192.168.1.1

# Scan em intervalo de portas
python main.py --port-scan 192.168.1.1 --ports range:1-1000

# Scan em portas específicas
python main.py --port-scan 192.168.1.1 --ports 22,80,443,3306

# Scan com relatório HTML
python main.py --port-scan 192.168.1.1 --output html -f relatorio.html
```

### Utilitários

```bash
# Mostrar interfaces de rede disponíveis
python main.py --interfaces

# Obter informações de um MAC address
python main.py --mac-info AA:BB:CC:DD:EE:FF
```

## 📁 Estrutura do Projeto

```
ZNetScan/
│
├── main.py                 # Ponto de entrada principal
├── run_with_venv.py        # Executor com venv
├── setup_venv.py          # Setup automático
├── requirements.txt       # Dependências Python
├── README.md             # Documentação
├── LICENSE               # Licença GPLv3
├── CHANGELOG.md          # Histórico de versões
│
├── scanners/             # Módulos de escaneamento
│   ├── arp_scanner.py    # Scanner ARP
│   ├── ping_scanner.py   # Scanner ICMP
│   └── port_scanner.py   # Scanner de portas
│
├── network/              # Funções de rede
│   ├── ip_utils.py       # Manipulação de IPs
│   ├── mac_utils.py      # Manipulação de MACs
│   └── interface.py      # Interfaces de rede
│
├── output/               # Saída dos resultados
│   ├── formatters.py     # Formatadores de saída
│   └── exporters.py      # Exportadores (JSON, CSV, etc)
│
├── utils/                # Utilitários gerais
│   ├── logger.py         # Sistema de logs
│   └── validators.py     # Validações
│
└── config/               # Configurações
    └── settings.py       # Parâmetros configuráveis
```

## 🎯 Exemplos de Uso

### Exemplo 1: Scan Rápido da Rede Local

```bash
sudo python main.py --method arp
```

**Saída:**
```
================================================================================
| IP Address    | MAC Address         | Manufacturer        | Status |
--------------------------------------------------------------------------------
| 192.168.1.1   | 00:11:22:33:44:55   | TP-Link             | active |
| 192.168.1.10  | AA:BB:CC:DD:EE:FF   | Apple Inc.          | active |
| 192.168.1.15  | 11:22:33:44:55:66   | Samsung Electronics | active |
================================================================================

Total de dispositivos: 3
```

### Exemplo 2: Scan de Portas em um Servidor

```bash
python main.py --port-scan 192.168.1.100 --ports 22,80,443
```

**Saída:**
```
Escaneando 3 portas em 192.168.1.100...
  ✓ Porta 22 aberta - SSH
  ✓ Porta 80 aberta - HTTP
  ✓ Porta 443 aberta - HTTPS

RELATÓRIO DE SCAN DE PORTAS
================================================================================
PORTA    STATUS     SERVIÇO         BANNER
--------------------------------------------------------------------------------
22       open       SSH             SSH-2.0-OpenSSH_8.2p1
80       open       HTTP            HTTP/1.1 200 OK
443      open       HTTPS           -
================================================================================
```

### Exemplo 3: Exportar Resultados para JSON

```bash
sudo python main.py --method arp --output json -f scan_$(date +%Y%m%d).json
```

## 🛠️ Desenvolvimento

### Configuração do Ambiente de Desenvolvimento

```bash
# Instalar ferramentas de desenvolvimento
pip install black flake8 pytest mypy

# Formatar código
black .

# Verificar estilo
flake8 .

# Executar testes
pytest tests/

# Type checking
mypy .
```

## 🐛 Troubleshooting

### Problema: "arp-scan: command not found"
```bash
# Solução: instalar arp-scan
sudo apt install arp-scan  # Linux
brew install arp-scan      # macOS
```

### Problema: "Permission denied" no scan ARP
```bash
# Solução: executar com sudo
sudo python main.py --method arp
```

### Problema: Módulo não encontrado
```bash
# Solução: instalar dependências no venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problema: Scan muito lento
```bash
# Solução: usar método ARP (mais rápido)
sudo python main.py --method arp

# Ou reduzir timeout no código (config/settings.py)
TIMEOUT = 1  # Reduzir de 2 para 1 segundo
```

### Problema: MACs não aparecem no scan ping
```bash
# Solução: Limpar cache ARP e tentar novamente
sudo ip neigh flush all  # Linux
arp -d  # Windows (como admin)
```

## 📊 Performance

| Método | Velocidade | Precisão | Requer Sudo |
|--------|-----------|----------|-------------|
| ARP    | ⚡ Muito rápido (segundos) | ✅ Alta | ✅ Sim |
| Ping   | 🐌 Lento (minutos) | ⚠️ Média | ❌ Não |

## 🔒 Segurança

- O scanner apenas **descobre** dispositivos, não os ataca
- Use apenas em redes que você possui autorização
- O método ARP requer `sudo` por questões de segurança do sistema
- Logs são salvos localmente, não enviam dados para internet

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga estes passos:

1. Fork o projeto
2. Crie sua branch: `git checkout -b feature/nova-feature`
3. Commit suas mudanças: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

### Guidelines de Contribuição

- Mantenha o código modular e documentado
- Adicione testes para novas funcionalidades
- Siga o estilo de código PEP 8
- Atualize o README se necessário

## 📄 Licença

Este projeto está sob a licença **GNU General Public License v3.0**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autor

- **Zer0G0ld** - *Desenvolvimento inicial* - [Zer0G0ld](https://github.com/Zer0G0ld)

## 🙏 Agradecimentos

- Comunidade Python pelas bibliotecas incríveis
- Desenvolvedores do `arp-scan` pela ferramenta
- Todos os contribuidores e testadores

## 📞 Suporte

- 🐛 Issues: [GitHub Issues](https://github.com/Zer0G0ld/ZNetScan/issues)

## 🗺️ Roadmap

- [ ] Interface gráfica (GUI)
- [ ] Scan de rede wireless (Wi-Fi)
- [ ] Detecção de sistema operacional
- [ ] Mapeamento de topologia de rede
- [ ] Alertas em tempo real
- [ ] Integração com APIs de threat intelligence
- [ ] Versão Docker otimizada
- [ ] Suporte a IPv6 completo

## ⚡ Quick Start (Resumo)

```bash
# 1. Clone e entre na pasta
git clone https://github.com/Zer0G0ld/ZNetScan.git
cd ZNetScan

# 2. Setup automático
python3 setup_venv.py

# 3. Ativar ambiente
source venv/bin/activate  # Linux/macOS
# OU
venv\Scripts\activate.bat  # Windows

# 4. Executar!
sudo python main.py --method arp  # Scan rápido
# OU
python main.py --method ping       # Scan sem sudo
```

---

⭐ **Se este projeto ajudou você, considere dar uma estrela no GitHub!**

🔗 **Links úteis:**
- [Documentação Python](https://docs.python.org/3/)
- [ARP Scan Documentation](https://github.com/royhills/arp-scan)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

Desenvolvido com 🐍 por **Zer0G0ld**