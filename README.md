# 🌐 ZNetScan - Scanner de Rede Inteligente

[![PyPI version](https://badge.fury.io/py/znetscan.svg)](https://badge.fury.io/py/znetscan)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-red.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)]()
[![Downloads](https://pepy.tech/badge/znetscan)](https://pepy.tech/project/znetscan)

**ZNetScan** é uma ferramenta que descobre todos os dispositivos na sua rede e identifica quais MAC addresses são **reais** (de fábrica) e quais são **falsos** (randomizados por privacidade). Além disso, usa **fingerprint** para reconhecer o mesmo dispositivo mesmo quando ele muda de MAC!

> 🔥 **Diferencial**: Enquanto outros scanners só mostram o MAC, o ZNetScan te diz se você pode confiar nele e identifica dispositivos que se escondem atrás de MACs falsos!

## 📦 Instalação Rápida

```bash
# Via pip (recomendado)
pip install znetscan

# Agora use em qualquer lugar!
znet --method arp
```

## 📸 Demonstração

```bash
$ znet --method arp

================================================================================================================
IP               MAC                  Dispositivo Identificado            Confiança    Visto
----------------------------------------------------------------------------------------------------------------
192.168.0.1      3C:58:5D:78:AD:DE    Roteador Sagemcom                   ✅ ALTA      45
192.168.0.6      EC:6C:9A:9E:9A:62    Computador João                     ✅ ALTA      23
192.168.0.37     02:F6:E8:0E:1C:3D    iPhone Maria                        ✅ ALTA      12
192.168.0.38     9A:B2:C5:2C:39:7F    📱 Smartphone (desconhecido)        ⚠️ MÉDIA     3
192.168.0.42     96:2F:8A:09:02:6A    🆕 📱 Smartphone (desconhecido)      ❌ BAIXA     1
================================================================================================================

📊 Total de dispositivos: 5
   ✅ Dispositivos conhecidos: 4
   🆕 Novos dispositivos: 1
   🔄 MACs randomizados: 3
```

## 🎯 O que este scanner faz?

| Recurso | O que significa | Para que serve |
|---------|----------------|----------------|
| **Scan ARP** | Descobre dispositivos em segundos | Mapear sua rede rapidamente |
| **Scan Ping** | Alternativa sem sudo | Quando não tem permissão de root |
| **Detecta MAC falso** | Identifica iPhones/Androids | Saber se o MAC é confiável |
| **Fingerprint** | Reconhece dispositivos mesmo com MAC diferente | Identificar o mesmo celular em redes diferentes |
| **Gerencia dispositivos** | Nomeia, lista e vê histórico | Organizar e identificar dispositivos |
| **Scan de portas** | Verifica portas abertas | Auditoria de segurança |
| **Exporta resultados** | JSON, CSV, HTML, TXT | Relatórios e integrações |

## 🚀 Instalação detalhada

### Via pip (recomendado para usuários)
```bash
# Instalar
pip install znetscan

# Usar
znet --method arp
znet help
```

### Via git (para desenvolvedores)
```bash
# Clonar e entrar no projeto
git clone https://github.com/Zer0G0ld/ZNetScan.git
cd ZNetScan

# Setup automático
python3 setup_venv.py
source venv/bin/activate

# Instalar dependência do sistema (para scan ARP)
sudo apt install arp-scan  # Linux
brew install arp-scan      # macOS
```

## 📖 Comandos principais

### 🔍 Scan de Rede
```bash
# Scan rápido (recomendado) - mostra confiabilidade dos MACs
sudo znet --method arp

# Scan alternativo (sem sudo)
znet --method ping

# Escanear rede específica
znet --network 192.168.0.0/24 --method arp
```

### 📊 Gerenciamento de Dispositivos (Fingerprint)
```bash
# Listar todos os dispositivos conhecidos
znet --list-devices

# Nomear um dispositivo (aprender quem é)
znet --learn-device dev_20260425_123456 "Celular da Maria"

# Ver histórico completo de um dispositivo
znet --device-history dev_20260425_123456

# Remover um dispositivo do banco
znet --forget-device dev_20260425_123456
```

### 🔌 Scan de Portas
```bash
# Escanear portas de um IP
znet --port-scan 192.168.1.1

# Portas específicas
znet --port-scan 192.168.1.1 --ports 22,80,443,3306

# Intervalo de portas
znet --port-scan 192.168.1.1 --ports range:1-1000
```

### ℹ️ Informações e Ajuda
```bash
# Sistema de ajuda interativo
znet help
znet help scan
znet help devices
znet help ports

# Analisar um MAC específico
znet --mac-info AA:BB:CC:DD:EE:FF

# Mostrar interfaces de rede
znet --interfaces
```

### 📤 Exportação
```bash
# Salvar resultado em JSON
znet --method arp --output json -f minha_rede.json

# Salvar em CSV (planilha)
znet --method arp --output csv -f minha_rede.csv

# Gerar relatório HTML
znet --method arp --output html -f relatorio.html
```

## 🔍 Entendendo o Fingerprint

### O problema: dispositivos que escondem o MAC
Smartphones modernos (iPhone, Android) **randomizam o MAC** a cada rede que se conectam para proteger sua privacidade.

### A solução: identificação por múltiplas características
O ZNetScan identifica o mesmo dispositivo por:
- **Padrão do chip Wi-Fi** (mesmo com MAC falso)
- **Comportamento de horários** (quando costuma aparecer)
- **Histórico de IPs** (que rede usa)

### Níveis de confiança do fingerprint
| Nível | Significado | O que fazer |
|-------|-------------|-------------|
| **✅ ALTA** | Mesmo dispositivo com certeza | Pode confiar, nomeie o dispositivo |
| **⚠️ MÉDIA** | Provavelmente o mesmo | Observe mais alguns dias |
| **❌ BAIXA** | Dispositivo novo ou inconclusivo | Ainda aprendendo |

### Exemplo prático
```bash
# Primeiro scan: iPhone aparece com MAC aleatório
znet --method arp
# Mostra: "📱 Smartphone (desconhecido)"

# Nomeie o dispositivo
znet --learn-device dev_xxx "iPhone da Ana"

# Segundo scan (dias depois): iPhone com MAC diferente
znet --method arp
# Agora mostra: "iPhone da Ana" ✅ reconhecido!
```

## 🔍 Entendendo a detecção de MAC falso

### ✅ Confiança ALTA (MAC verdadeiro)
```
MAC: 3C:58:5D:78:AD:DE
Segundo caractere: 'C' (0,4,8,C)
→ Este MAC é GRAVADO no hardware. Não muda. Confiável!
```

### ⚠️ Confiança BAIXA (MAC falso/randomizado)
```
MAC: 26:BC:9C:38:81:57
Segundo caractere: '6' (2,6,A,E)
→ Este MAC é CRIADO POR SOFTWARE. Muda a cada rede. Não confie como ID único!
```

### Por que isso acontece?

- **iPhone/Android**: Criaram MACs falsos em 2017 para proteger sua privacidade
- **Resultado**: Uma pessoa com o mesmo celular aparece como dispositivos diferentes
- **Solução**: Use o **sistema de fingerprint** do ZNetScan para identificar!

## 📁 Estrutura do projeto

```
ZNetScan/
├── main.py                    # 👉 Ponto de entrada principal
├── network/
│   ├── mac_utils.py          # 🔥 Detecta MAC falso (bit U/L)
│   └── device_fingerprint.py # 🆔 Identifica dispositivos que mudam de MAC
├── scanners/                  # Métodos de descoberta (ARP, Ping, Portas)
├── output/                    # Formatadores e exportadores
├── utils/
│   ├── logger.py             # Sistema de logs com cores
│   └── help.py               # 📚 Sistema de ajuda interativo
├── docs/                      # Documentação técnica completa
└── config/                    # Configurações
```

## 🎓 Aprenda mais

- [Como funciona a detecção de MAC randomizado?](docs/01_MAC_ADDRESS_EXPLAINED.md)
- [Arquitetura do ZNetScan](docs/02_HOW_ZNETSCAN_WORKS.md)

## 🛠️ Para desenvolvedores

```bash
# Instalar ferramentas extras
pip install black flake8 pytest

# Formatar código
black .

# Verificar estilo
flake8 .

# Executar testes
pytest tests/
```

## 🐛 Problemas comuns

| Problema | Solução |
|----------|---------|
| `arp-scan: command not found` | `sudo apt install arp-scan` |
| `Permission denied` no scan ARP | Use `sudo` ou método ping |
| Scan muito lento | Use `--method arp` (mais rápido) |
| Dispositivo desconhecido aparece sempre | Nomeie com `--learn-device` |
| MACs randomizados não identificados | Já são identificados automaticamente! |

## 📊 Comparação com outras ferramentas

| Ferramenta | Velocidade | Detecta MAC falso | Fingerprint | Exporta JSON | Ajuda interativa |
|------------|------------|-------------------|-------------|--------------|------------------|
| **ZNetScan** | ⚡ Rápido | ✅ SIM | ✅ SIM | ✅ Sim | ✅ Sim |
| nmap | 🐌 Lento | ❌ Não | ❌ Não | ✅ Sim | ❌ Não |
| arp-scan | ⚡ Rápido | ❌ Não | ❌ Não | ❌ Não | ❌ Não |
| netdiscover | ⚡ Rápido | ❌ Não | ❌ Não | ❌ Não | ❌ Não |

## 🤝 Contribuir

1. Fork o projeto
2. Crie sua branch: `git checkout -b minha-feature`
3. Commit: `git commit -m 'Adiciona feature'`
4. Push: `git push origin minha-feature`
5. Abra um Pull Request

## 📄 Licença

**GNU General Public License v3.0** - Use, modifique e distribua livremente.

## 👤 Autor

**Zer0G0ld** - [GitHub](https://github.com/Zer0G0ld)

---

⭐ **Gostou? Dê uma estrela no GitHub!**  
🐛 **Encontrou um bug?** [Abra uma issue](https://github.com/Zer0G0ld/ZNetScan/issues)

---

Desenvolvido com 🐍 por **Zer0G0ld**