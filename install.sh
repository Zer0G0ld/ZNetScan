#!/bin/bash
# install.sh - Script de instalação automática do ZNetScan

echo "🚀 Instalando ZNetScan..."

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale primeiro."
    exit 1
fi

# Instala dependências do sistema
echo "📦 Instalando dependências do sistema..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y arp-scan
elif command -v brew &> /dev/null; then
    brew install arp-scan
fi

# Instala via pip
echo "📦 Instalando ZNetScan..."
pip install znetscan

# Verifica instalação
if command -v znet &> /dev/null; then
    echo "✅ ZNetScan instalado com sucesso!"
    echo ""
    echo "🎯 Comandos disponíveis:"
    echo "   znet --method arp     # Scan rápido"
    echo "   znet help             # Ajuda"
    echo "   znet --list-devices   # Dispositivos conhecidos"
else
    echo "❌ Falha na instalação. Tente: pip install -e ."
fi
