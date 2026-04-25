# Changelog

## [1.0.0] - 2024-01-15

### Adicionado
- Scan ARP para descoberta de dispositivos
- Scan ICMP (ping) como alternativa
- Identificação de fabricantes por MAC
- Scan de portas TCP
- Múltiplos formatos de exportação (JSON, CSV, TXT, HTML)
- Sistema de logs completo
- Menu interativo (run.py)
- Setup automático com venv
- Validação de dados

### Corrigido
- Bugs de threading no scan de portas
- Memory leak no scan de rede grande
- Compatibilidade com Windows no método ping

### Melhorado
- Performance do scan ARP
- Interface do console com cores
- Documentação e exemplos

## [0.9.0] - 2024-01-01

### Adicionado
- Versão inicial do projeto
- Funcionalidade básica de scan