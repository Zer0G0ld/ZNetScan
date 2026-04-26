# Changelog

Todos os cambios notáveis neste projeto serão documentados aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.1.0] - 2026-04-25

### Adicionado
- 🆔 **Sistema de Fingerprint** - Identifica dispositivos mesmo quando mudam de MAC
  - Reconhece iPhones/Androids que randomizam o MAC
  - Múltiplas características: padrão do chip, horários, histórico de IPs
  - Níveis de confiança: ALTA (70%+), MÉDIA (50-70%), BAIXA (<50%)
- 📚 **Sistema de ajuda interativo** - Documentação integrada
  - `python main.py help` - Menu principal
  - `python main.py help scan` - Ajuda específica para scan
  - `python main.py help devices` - Gerenciamento de dispositivos
  - `python main.py help ports` - Scan de portas
  - `python main.py help export` - Exportação de resultados
  - `python main.py help fingerprint` - Explicação do fingerprint
  - `python main.py help mac` - Análise de MAC
  - `python main.py help troubleshoot` - Solução de problemas
- 📊 **Gerenciamento de dispositivos**
  - `--list-devices` - Lista todos os dispositivos conhecidos
  - `--learn-device` - Nomeia dispositivos manualmente
  - `--device-history` - Mostra histórico completo (MACs, IPs, horários)
  - `--forget-device` - Remove dispositivos do banco
- 🔍 **Detecção avançada de MAC randomizado**
  - Identificação pelo bit U/L (segundo caractere do MAC)
  - Classificação: 0,4,8,C = Fábrica (confiável) / 2,6,A,E = Randomizado (não confiável)
  - Identificação de padrões: Docker, VMs, dispositivos móveis
- 📁 **Logs organizados**
  - Pasta `logs/` dedicada
  - Rotação automática de arquivos (10MB / 5 backups)
  - Arquivo separado para erros
  - Cores no terminal por nível (verde=INFO, amarelo=WARNING, vermelho=ERROR)
- 🗄️ **Banco de dados persistente**
  - `device_fingerprints.json` - Armazena dispositivos conhecidos
  - `oui_cache.json` - Cache de fabricantes MAC
- 🔧 **Utilitários**
  - `scan_all_networks.py` - Escaneia todas as interfaces de rede
  - `identify_devices.py` - Script dedicado para identificação
  - `utils/help.py` - Módulo de ajuda centralizado

### Melhorado
- 🎨 **Interface do console**
  - Cores para identificar níveis de confiança
  - Indicadores visuais (✅ ⚠️ 🔄 🆕)
  - Estatísticas detalhadas ao final do scan
- 📊 **Tabela de resultados**
  - Nova coluna "Confiança" (ALTA/BAIXA)
  - Nova coluna "Visto" (contagem de aparições)
  - Identificação de dispositivos novos (🆕)
- 📝 **Logging profissional**
  - Cores no terminal usando colorama
  - Formato consistente com timestamp
  - Contexto adicional para operações
- 🐍 **Código modular**
  - Separação clara de responsabilidades
  - Tipagem com `typing`
  - Documentação de funções

### Corrigido
- 🐛 Importação do `List` e `Dict` do typing
- 🐛 Permissões do arquivo `device_fingerprints.json`
- 🐛 Compatibilidade com sudo no ambiente virtual
- 🐛 Tratamento de exceções no logger
- 🐛 Fallback quando não consegue criar arquivo de log

### Documentação
- 📚 README atualizado com fingerprint e sistema de ajuda
- 📖 Documentação técnica na pasta `docs/`
  - `01_MAC_ADDRESS_EXPLAINED.md` - Teoria do MAC randomizado
  - `02_HOW_ZNETSCAN_WORKS.md` - Arquitetura e funcionamento
- 💡 Exemplos práticos de uso
- 🔧 Guia de solução de problemas

## [1.0.0] - 2024-01-15

### Adicionado
- 🔍 Scan ARP para descoberta de dispositivos
- 📡 Scan ICMP (ping) como alternativa
- 🏭 Identificação de fabricantes por MAC
- 🔌 Scan de portas TCP
- 📊 Múltiplos formatos de exportação (JSON, CSV, TXT, HTML)
- 📝 Sistema de logs completo
- 🎮 Menu interativo (run.py)
- 🐍 Setup automático com venv
- ✅ Validação de dados

### Corrigido
- 🐛 Bugs de threading no scan de portas
- 🐛 Memory leak no scan de rede grande
- 🐛 Compatibilidade com Windows no método ping

### Melhorado
- ⚡ Performance do scan ARP
- 🎨 Interface do console com cores
- 📚 Documentação e exemplos

## [0.9.0] - 2024-01-01

### Adicionado
- 🎉 Versão inicial do projeto
- 📡 Funcionalidade básica de scan
- 🔍 Descoberta de dispositivos via ARP

---

## 🚀 Roadmap para próximas versões

### [1.2.0] - Planejado
- [ ] Interface gráfica (GUI)
- [ ] Scan de rede wireless (Wi-Fi)
- [ ] Detecção de sistema operacional
- [ ] Mapeamento de topologia de rede

### [1.3.0] - Planejado
- [ ] Alertas em tempo real
- [ ] Integração com APIs de threat intelligence
- [ ] Versão Docker otimizada
- [ ] Suporte a IPv6 completo

---

**Legenda:**
- ✨ Nova funcionalidade
- 🐛 Correção de bug
- 📚 Documentação
- 🎨 Melhoria visual
- ⚡ Performance
- 🔒 Segurança
