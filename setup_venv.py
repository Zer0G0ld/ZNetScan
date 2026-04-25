#!/usr/bin/env python3
"""
setup_venv.py - Script Python para configurar o ambiente virtual
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Executa comando com feedback"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        print(f"Output: {e.output}")
        return False

def main():
    print("=" * 50)
    print("Network Scanner - Setup Automático")
    print("=" * 50)
    
    # Verifica Python
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ é necessário")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Cria venv
    venv_path = Path("venv")
    if not venv_path.exists():
        print("\n📦 Criando ambiente virtual...")
        if sys.platform == "win32":
            run_command("python -m venv venv", "Criando venv")
        else:
            run_command("python3 -m venv venv", "Criando venv")
    else:
        print("✅ Ambiente virtual já existe")
    
    # Define caminho do pip no venv
    if sys.platform == "win32":
        pip_path = "venv/Scripts/pip"
        python_path = "venv/Scripts/python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Atualiza pip
    print("\n⬆️  Atualizando pip...")
    run_command(f"{python_path} -m pip install --upgrade pip", "Atualizando pip")
    
    # Instala dependências
    if Path("requirements.txt").exists():
        print("\n📥 Instalando dependências...")
        run_command(f"{pip_path} install -r requirements.txt", "Instalando dependências")
    else:
        print("⚠️  requirements.txt não encontrado")
    
    # Instala ferramentas extras
    print("\n🛠️  Instalando ferramentas de desenvolvimento...")
    run_command(f"{pip_path} install ipython pytest black flake8", "Instalando ferramentas")
    
    # Verifica instalação
    print("\n🔍 Verificando instalação...")
    run_command(f"{python_path} check_installation.py", "Verificação")
    
    print("\n" + "=" * 50)
    print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print("\nPara ATIVAR o ambiente virtual:")
    if sys.platform == "win32":
        print("  venv\\Scripts\\activate.bat")
        print("\nPara executar o scanner:")
        print("  venv\\Scripts\\python main.py --method ping")
        print("  sudo venv\\Scripts\\python main.py --method arp")
    else:
        print("  source venv/bin/activate")
        print("\nPara executar o scanner:")
        print("  venv/bin/python main.py --method ping")
        print("  sudo venv/bin/python main.py --method arp")
    print("\nPara DESATIVAR:")
    print("  deactivate")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()