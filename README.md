# 🌐 ZNetScan - Scanner de Rede Inteligente

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-red.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)]()

**ZNetScan** é uma ferramenta que descobre todos os dispositivos na sua rede e identifica quais MAC addresses são **reais** (de fábrica) e quais são **falsos** (randomizados por privacidade).

> 🔥 **Diferencial**: Enquanto outros scanners só mostram o MAC, o ZNetScan te diz se você pode confiar nele ou não!

## 📸 Demonstração

```bash
$ sudo python main.py --method arp

====================================================================================================
| IP           | MAC Address       | Fabricante                         | Confiança |
----------------------------------------------------------------------------------------------------
| 192.168.10.1  | 3C:55:5D:78:AD:DE | Sagemcom (roteador)                | ✅ ALTA   |
| 192.168.10.10 | EC:6G:9A:9E:9A:62 | Arcadyan (computador)              | ✅ ALTA   |
| 192.168.10.34 | 26:BT:9C:38:81:57 | 🔄 iPhone (MAC randomizado)        | ⚠️ BAIXA  |
| 192.168.10.38 | 9A:B3:C5:2C:39:7F | 🔄 Android (MAC randomizado)       | ⚠️ BAIXA  |
====================================================================================================

✅ Dispositivos confiáveis: 2
⚠️  Dispositivos com MAC falso: 2

💡 Dica: MACs randomizados mudam a cada rede. Não use como identificador único!
```

## 🎯 O que este scanner faz?

| Recurso | O que significa | Para que serve |
|---------|----------------|----------------|
| **Scan ARP** | Descobre dispositivos em segundos | Mapear sua rede rapidamente |
| **Scan Ping** | Alternativa sem sudo | Quando não tem permissão de root |
| **Detecta MAC falso** | Identifica iPhones/Androids | Saber se o MAC é confiável |
| **Scan de portas** | Verifica portas abertas | Auditoria de segurança |
| **Exporta resultados** | JSON, CSV, HTML, TXT | Relatórios e integrações |

## 🚀 Instalação (3 passos)

```bash
# 1. Instalar arp-scan (necessário para scan rápido)
sudo apt install arp-scan  # Linux
brew install arp-scan      # macOS

# 2. Clonar e entrar no projeto
git clone https://github.com/Zer0G0ld/ZNetScan.git
cd ZNetScan

# 3. Setup automático
python3 setup_venv.py
source venv/bin/activate
```

## 📖 Comandos principais

```bash
# Scan rápido (recomendado) - mostra confiabilidade dos MACs
sudo python main.py --method arp

# Scan alternativo (sem sudo)
python main.py --method ping

# Analisar um MAC específico
python main.py --mac-info AA:BB:CC:DD:EE:FF

# Escanear portas de um IP
python main.py --port-scan 192.168.1.1

# Salvar resultado em JSON
sudo python main.py --method arp --output json -f minha_rede.json
```

## 🔍 Entendendo a saída

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
→ Este MAC é CRIADO POR SOFTWARE. Muda a cada rede. Não confie!
```

### Por que isso acontece?

- **iPhone/Android**: Criaram MACs falsos em 2017 para proteger sua privacidade
- **Resultado**: Uma pessoa com o mesmo celular aparece como dispositivos diferentes em redes diferentes
- **Solução**: O ZNetScan identifica esses MACs falsos e avisa você

## 📁 Estrutura do projeto

```
ZNetScan/
├── main.py              # 👉 Comece aqui
├── network/
│   └── mac_utils.py     # 🔥 Lógica que detecta MAC falso
├── scanners/            # Métodos de descoberta
├── output/              # Formatadores e exportadores
├── docs/                # Documentação técnica
└── config/              # Configurações
```

## 🛠️ Para desenvolvedores

```bash
# Instalar ferramentas extras
pip install black flake8 pytest

# Formatar código
black .

# Verificar estilo
flake8 .
```

## 🐛 Problemas comuns

| Problema | Solução |
|----------|---------|
| `arp-scan: command not found` | `sudo apt install arp-scan` |
| `Permission denied` | Use `sudo` no scan ARP |
| Scan muito lento | Use `--method arp` (mais rápido) |

## 📊 Comparação com outras ferramentas

| Ferramenta | Velocidade | Detecta MAC falso | Exporta JSON |
|------------|------------|-------------------|--------------|
| **ZNetScan** | ⚡ Rápido | ✅ **SIM** | ✅ Sim |
| nmap | 🐌 Lento | ❌ Não | ✅ Sim |
| arp-scan | ⚡ Rápido | ❌ Não | ❌ Não |
| netdiscover | ⚡ Rápido | ❌ Não | ❌ Não |

## 🎓 Aprenda mais

- [Como funciona a detecção de MAC randomizado?](docs/01_MAC_ADDRESS_EXPLAINED.md)
- [Arquitetura do ZNetScan](docs/02_HOW_ZNETSCAN_WORKS.md)

## 🤝 Contribuir

1. Fork o projeto
2. Crie uma branch: `git checkout -b minha-feature`
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
