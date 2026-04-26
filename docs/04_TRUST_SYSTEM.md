# 🔒 Sistema de Confiança do ZNetScan

## Visão Geral

O ZNetScan possui um **sistema inteligente de confiança** que avalia a confiabilidade dos dispositivos na sua rede. Este sistema combina **análise de MAC address** (hardware vs randomizado) com **histórico de aparições** (fingerprint) para determinar o nível de confiança de cada dispositivo.

## 📊 Níveis de Confiança

### 1. ✅ ALTA (High Confidence)
**Significado:** Dispositivo altamente confiável e identificado com certeza.

| Critério | Valor |
|----------|-------|
| Visto | 5+ vezes |
| MAC | De fábrica (Universal) |
| Identificação | Múltiplas características combinadas |
| Recomendação | Pode usar como identificador único |

**Exemplo:**
```
192.168.0.1 | 3C:58:5D:78:AD:DE | Roteador | ✅ ALTA | 45
```

### 2. ⚠️ MÉDIA (Medium Confidence)
**Significado:** Provavelmente confiável, mas requer mais observação.

| Critério | Valor |
|----------|-------|
| Visto | 2-4 vezes |
| MAC | De fábrica OU randomizado com padrão |
| Identificação | Algumas características coincidem |
| Recomendação | Observe por mais tempo antes de confiar |

**Exemplo:**
```
192.168.0.38 | 9A:B2:C5:2C:39:7F | Smartphone | ⚠️ MÉDIA | 3
```

### 3. 🆕/❌ BAIXA (Low Confidence)
**Significado:** Dispositivo novo ou inconclusivo. Não confie como ID único.

| Critério | Valor |
|----------|-------|
| Visto | 1 vez (novo) |
| MAC | Randomizado (Local) |
| Identificação | Poucas características |
| Recomendação | Não use como identificador único |

**Exemplo:**
```
192.168.0.31 | B2:74:A8:3E:B4:4D | Novo Dispositivo | ❌ BAIXA | 1
```

## 🔍 Como a Confiança é Calculada

### Fórmula de Confiança

```
Confiança = (Pontuação_Hardware + Pontuação_Histórico + Pontuação_Comportamento) / 3
```

### Pontuação por Categoria

#### 1. Hardware (Análise do MAC)
| Tipo de MAC | Pontos | Confiabilidade |
|-------------|--------|----------------|
| Universal (Fábrica) - 0,4,8,C | 50 | ✅ Alta |
| Local (Randomizado) - 2,6,A,E | 10 | ⚠️ Baixa |

#### 2. Histórico (Fingerprint)
| Visto | Pontos | Status |
|-------|--------|--------|
| 1 vez | 10 | 🆕 Novo |
| 2-4 vezes | 30 | 🔄 Aprendendo |
| 5+ vezes | 50 | ✅ Estável |

#### 3. Comportamento (Padrões)
| Característica | Pontos |
|----------------|--------|
| Mesmo horário de aparição | +10 |
| Mesma faixa de IP | +10 |
| Mesmo padrão OUI | +20 |
| Múltiplos MACs associados | +30 |

### Tabela de Níveis

| Pontuação Total | Nível | Cor | Ícone |
|-----------------|-------|-----|-------|
| 70 - 100 | ALTA | Verde | ✅ |
| 40 - 69 | MÉDIA | Amarelo | ⚠️ |
| 0 - 39 | BAIXA | Vermelho | ❌/🆕 |

## 📈 Evolução da Confiança

### Linha do Tempo de um Dispositivo

```
Scan 1: 🆕 BAIXA (10 pontos)
         ↓
Scan 2: 🔄 MÉDIA (40 pontos) - Mesmo MAC
         ↓
Scan 3: 🔄 MÉDIA (55 pontos) - Mesmo padrão
         ↓
Scan 4: ✅ ALTA (70 pontos) - Confirmado
         ↓
Scan 5+: ✅ ALTA (85+ pontos) - Totalmente confiável
```

### Exemplo Prático: Smartphone com MAC Randomizado

```python
# Scan 1: Primeira aparição
{
    'mac': '02:F6:E8:0E:1C:3D',
    'tipo_mac': 'randomizado',  # 10 pontos
    'seen_count': 1,             # 10 pontos
    'total': 20,                 # BAIXA ❌
    'status': '🆕 Novo'
}

# Scan 2: Mesmo padrão, horário similar
{
    'mac': '9A:B2:C5:2C:39:7F',  # MAC diferente!
    'tipo_mac': 'randomizado',   # 10 pontos
    'seen_count': 2,              # 30 pontos
    'padrao_horario': True,      # +10 pontos
    'mesmo_oui_pattern': True,   # +20 pontos
    'total': 70,                 # ALTA ✅
    'status': '✅ Reconhecido!'
}
```

## 🎯 Casos de Uso por Nível de Confiança

### ✅ ALTA - Pode confiar
```bash
# Use como identificador único
znet --learn-device dev_001 "Servidor Web"

# Configure monitoramento
znet --device-history dev_001

# Exporte para segurança
znet --method arp --output json -f rede.confiavel.json
```

### ⚠️ MÉDIA - Observe mais
```bash
# Acompanhe por alguns dias
znet --list-devices

# Verifique histórico
znet --device-history dev_002

# Aguarde mais 2-3 scans antes de confiar
```

### ❌ BAIXA - Não confie
```bash
# Não use como identificador
# Espere o dispositivo aparecer mais vezes
# O sistema vai aprender automaticamente

# Se for um dispositivo conhecido, ensine manualmente:
znet --learn-device dev_003 "Celular do João"
```

## 🔧 Como Melhorar a Confiança

### Automático (Recomendado)
O sistema aprende sozinho com o tempo:
1. Execute scans periódicos
2. O fingerprint acumula dados
3. A confiança aumenta naturalmente

### Manual
Você pode ensinar o sistema:
```bash
# Nomear um dispositivo acelera o aprendizado
znet --learn-device dev_003 "Impressora do Escritório"

# Ver histórico para confirmar
znet --device-history dev_003
```

## 📊 Exemplos Reais

### Exemplo 1: Roteador (MAC Fixo)
```
MAC: 3C:58:5D:78:AD:DE
Tipo: Universal (Fábrica)
Visto: 45 vezes
Confiança: ALTA ✅
Motivo: MAC fixo + muitas aparições
```

### Exemplo 2: iPhone (MAC Randomizado)
```
MAC: 02:F6:E8:0E:1C:3D (Scan 1)
MAC: 9A:B2:C5:2C:39:7F (Scan 2)
Tipo: Local (Randomizado)
Visto: 12 vezes (como mesmo dispositivo)
Confiança: ALTA ✅
Motivo: Fingerprint reconheceu padrões
```

### Exemplo 3: Dispositivo Novo
```
MAC: B2:74:A8:3E:B4:4D
Tipo: Universal
Visto: 1 vez
Confiança: BAIXA ❌
Motivo: Apareceu agora, aguardando confirmação
```

## 🎓 Boas Práticas

### Para Administradores de Rede
1. **Execute scans regulares** - Quanto mais dados, melhor a confiança
2. **Nomeie dispositivos importantes** - Acelera o aprendizado
3. **Monitore mudanças** - Confiança cai se padrões mudarem

### Para Desenvolvedores
1. **Use `--list-devices`** para ver a confiança de cada dispositivo
2. **Exporte JSON** para análise programática
3. **Integre com sistemas de monitoramento**

## 🔍 Debug da Confiança

### Ver detalhes de um dispositivo
```bash
znet --device-history dev_003
```

**Saída:**
```
📜 HISTÓRICO DO DISPOSITIVO: Unknown Device 3
================================================================================

📋 Informações gerais:
   🆔 ID: dev_20260425_222407_2
   📛 Nome: Unknown Device 3
   👁️  Visto: 6 vezes
   📅 Primeira aparição: 2026-04-25 22:24:07
   🕒 Última aparição: 2026-04-26 13:45:08

🔢 MACs já utilizados:
   • 78:DD:12:38:66:CC (Sempre o mesmo - MAC fixo)

🌐 IPs já utilizados:
   • 192.168.0.22
   • 192.168.0.25

⏰ Horários mais ativos:
   • 13:00 - 14:00
   • 22:00 - 23:00
```

## 📈 Métricas de Qualidade

| Métrica | Valor Ideal | Significado |
|---------|-------------|-------------|
| Dispositivos ALTA | >80% | Rede bem mapeada |
| Dispositivos MÉDIA | <15% | Em aprendizado |
| Dispositivos BAIXA | <5% | Novos ou esporádicos |

## 🚀 Conclusão

O sistema de confiança do ZNetScan é **inteligente e adaptativo**:
- 🔄 Aprende com o tempo
- 🎯 Combina múltiplos fatores
- ✅ Evolui de BAIXA → MÉDIA → ALTA
- 🆔 Reconhece dispositivos mesmo com MAC randomizado

**Use a confiança como guia, não como regra absoluta!**

---

🔗 **Links relacionados:**
- [Sistema de Fingerprint](02_HOW_ZNETSCAN_WORKS.md)
- [Entendendo MAC Randomizado](01_MAC_ADDRESS_EXPLAINED.md)
- [Comandos de Gerenciamento](../README.md#-gerenciamento-de-dispositivos)

**Versão da documentação:** 1.0  
**Última atualização:** 2026-04-26