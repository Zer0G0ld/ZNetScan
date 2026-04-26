# 📚 Documentação do ZNetScan

Bem-vindo à documentação completa do ZNetScan!

## 📖 Guias

1. **[Entendendo MAC Address](01_MAC_ADDRESS_EXPLAINED.md)**
   - O que é MAC Address
   - Como funciona a randomização
   - Bit U/L e identificação
   - Impacto na privacidade

2. **[Como o ZNetScan Funciona](02_HOW_ZNETSCAN_WORKS.md)**
   - Arquitetura do sistema
   - Fluxo de execução
   - Métodos de detecção
   - Integração com outros sistemas

## 🚀 Quick Links

- [Voltar ao README principal](../README.md)
- [Reportar Bug](https://github.com/Zer0G0ld/ZNetScan/issues)
- [Ver Changelog](../CHANGELOG.md)

## 📊 Exemplos de Uso

### Básico
```bash
# Scan rápido
sudo python main.py --method arp

# Análise de MAC
python main.py --mac-info AA:BB:CC:DD:EE:FF
```

### Avançado
```bash
# Scan com exportação
python main.py --method arp --output json -f rede.json

# Scan de portas específicas
python main.py --port-scan 192.168.1.1 --ports 22,80,443
```

## 🔧 Desenvolvimento

### Setup de desenvolvimento
```bash
git clone https://github.com/Zer0G0ld/ZNetScan.git
cd ZNetScan
python3 setup_venv.py
source venv/bin/activate
```

### Executando testes
```bash
pytest tests/
python -m doctest -v network/mac_utils.py
```

## 📝 Licença

Este projeto está sob licença GPLv3 - veja o arquivo [LICENSE](../LICENSE)

## 🤝 Contribuindo

Leia nosso [Guia de Contribuição](../README.md#-contribuindo)

---

**Dúvidas?** Abra uma [Issue](https://github.com/Zer0G0ld/ZNetScan/issues)