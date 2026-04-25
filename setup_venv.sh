#!/bin/bash
# setup_venv.sh - Configuração completa com venv

echo "========================================="
echo "Network Scanner - Setup com VirtualEnv"
echo "========================================="

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 não encontrado. Instale primeiro."
    exit 1
fi

# Cria venv
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativa venv
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instala dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Instala ferramentas de desenvolvimento
echo "🛠️  Instalando ferramentas de desenvolvimento..."
pip install ipython  # Shell interativo melhorado

# Verifica instalação
echo "✅ Verificando instalação..."
python check_installation.py

echo ""
echo "🎉 Setup concluído!"
echo ""
echo "Para ativar o ambiente:"
echo "  source venv/bin/activate"
echo ""
echo "Para executar o scanner:"
echo "  sudo venv/bin/python main.py --method arp"
echo ""
echo "Para sair do ambiente:"
echo "  deactivate"