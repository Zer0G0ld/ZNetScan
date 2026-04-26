# 🚀 Como o ZNetScan Funciona

## Visão Geral

O ZNetScan é uma ferramenta modular que descobre dispositivos na rede e analisa seus MAC addresses para determinar confiabilidade.

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                      ZNetScan                           │
├─────────────────────────────────────────────────────────┤
│  main.py          → Ponto de entrada                    │
│  scanners/        → Métodos de descoberta (ARP/Ping)    │
│  network/         → Análise de MAC e IP                 │
│  output/          → Formatação e exportação             │
│  utils/           → Logging e validações                │
└─────────────────────────────────────────────────────────┘
```

## Fluxo de Execução

### 1. Descoberta de Dispositivos
```python
# O scanner envia requisições ARP ou ping
scanner.scan(network) → Lista de dispositivos
```

### 2. Análise de MAC
```python
# Cada MAC é analisado individualmente
mac_utils.get_vendor_info(mac) → {
    'is_randomized': True/False,
    'reliability': 'ALTA'/'BAIXA',
    'explanation': '...'
}
```

### 3. Classificação
```python
if is_randomized:
    manufacturer = "🔄 Mobile Device (MAC Randomizado)"
    reliability = "BAIXA"
else:
    manufacturer = get_manufacturer_from_oui(mac)
    reliability = "ALTA"
```

### 4. Apresentação
- Tabela colorida no console
- Estatísticas de randomização
- Exportação em múltiplos formatos

## Métodos de Detecção

### 1. Análise do Bit U/L (Primário)
```python
# Verifica o segundo caractere do MAC
if second_char in ['2','6','A','E']:
    return "RANDOMIZADO"
```

### 2. Consulta a Banco OUI (Secundário)
```python
# Busca fabricante pelo prefixo
oui = mac[:8]  # 3C:58:5D
manufacturer = oui_database.get(oui)
```

### 3. API Online (Fallback)
```python
# Consulta API pública se não encontrou
response = requests.get(f"https://api.macvendors.com/{mac}")
```

### 4. Aprendizado Manual
```python
# Usuário pode ensinar novos dispositivos
mac_utils.learn_device(mac, "Meu Notebook", "computer")
```

## Exemplos de Identificação

### Dispositivo Confiável (MAC Fábrica)
```bash
$ python main.py --mac-info 3C:58:5D:78:AD:DE

🔍 ANÁLISE DE CONFIABILIDADE:
   📌 MAC de Fábrica (Universal) - Bit U/L=0
   🎯 Confiabilidade: ALTA
   💡 Pode usar como identificador confiável
```

### Dispositivo Não Confiável (MAC Randomizado)
```bash
$ python main.py --mac-info 26:BC:9C:38:81:57

🔍 ANÁLISE DE CONFIABILIDADE:
   📌 MAC Randomizado (Local) - Bit U/L=1
   🎯 Confiabilidade: BAIXA
   💡 Não use como ID único
```

## Performance

### Método ARP (Recomendado)
- **Velocidade:** ~2 segundos para rede /24
- **Precisão:** 100% (dispositivos ativos)
- **Requer:** sudo

### Método ICMP (Fallback)
- **Velocidade:** ~30-60 segundos
- **Precisão:** 70-80% (bloqueios de firewall)
- **Requer:** Permissão normal

## Saídas Suportadas

| Formato | Comando | Uso |
|---------|---------|-----|
| Console | `--output console` | Visualização rápida |
| JSON | `--output json` | Integração com APIs |
| CSV | `--output csv` | Planilhas |
| HTML | `--output html` | Relatórios visuais |
| TXT | `--output txt` | Logs simples |

## Integração com Outros Sistemas

### Exportando para Splunk/ELK
```bash
python main.py --method arp --output json -f scan.json
# Agora envie scan.json para seu sistema de logs
```

### Monitoramento Contínuo
```bash
#!/bin/bash
while true; do
    python main.py --method arp --output json -f "scan_$(date +%Y%m%d_%H%M%S).json"
    sleep 300  # A cada 5 minutos
done
```

### Alertas de Novos Dispositivos
```python
# Script para detectar dispositivos desconhecidos
previous_macs = load_previous_scan()
current_macs = get_current_macs()

new_devices = current_macs - previous_macs
if new_devices:
    send_alert(f"Novos dispositivos: {new_devices}")
```

## Boas Práticas

1. **Execute com sudo para melhor performance**
   ```bash
   sudo python main.py --method arp
   ```

2. **Use rede específica para escanear**
   ```bash
   python main.py --network 192.168.0.0/24
   ```

3. **Exporte resultados para análise posterior**
   ```bash
   python main.py --output json -f "scan_$(date +%Y%m%d).json"
   ```

4. **Limpe logs antigos periodicamente**
   ```bash
   find . -name "scanner_*.log" -mtime +30 -delete
   ```

## Troubleshooting

### Scan ARP não encontra dispositivos
```bash
# Verifique se arp-scan está instalado
which arp-scan

# Execute com sudo
sudo python main.py --method arp
```

### MACs randomizados não identificados
```bash
# Verifique a lógica manualmente
python -c "
from network.mac_utils import MACUtils
m = MACUtils()
print(m.is_randomized_mac('26:BC:9C:38:81:57'))  # Deve ser True
"
```

### Exportação falha
```bash
# Verifique permissões de escrita
touch test.json && rm test.json
```

## Próximos Passos

- [ ] Adicionar detecção de SO por fingerprint
- [ ] Implementar scan de vulnerabilidades
- [ ] Criar interface gráfica
- [ ] Adicionar alertas em tempo real