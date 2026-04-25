#!/usr/bin/env python3
"""
run_with_venv.py - Executa o scanner garantindo uso do venv
"""

import os
import sys
import subprocess
from pathlib import Path

def get_venv_python():
    """Retorna o caminho do Python no venv"""
    venv_python = None
    
    if sys.platform == "win32":
        venv_python = Path("venv/Scripts/python.exe")
    else:
        venv_python = Path("venv/bin/python")
    
    if venv_python.exists():
        return str(venv_python)
    return None

def main():
    # Verifica se venv existe
    venv_python = get_venv_python()
    
    if not venv_python:
        print("❌ Ambiente virtual não encontrado!")
        print("Execute primeiro: python3 setup_venv.py")
        sys.exit(1)
    
    # Prepara comando
    args = sys.argv[1:]
    cmd = [venv_python, "main.py"] + args
    
    # Verifica se precisa de sudo (apenas para ARP scan)
    if "--method" in args and "arp" in args[args.index("--method") + 1]:
        cmd = ["sudo"] + cmd
        print("⚠️  Scan ARP requer privilégios de root (sudo)")
    
    print(f"🚀 Executando: {' '.join(cmd)}")
    
    # Executa
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n⏹️  Scan interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()