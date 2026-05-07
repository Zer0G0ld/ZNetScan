#!/usr/bin/env python3
"""
Setup para instalar ZNetScan como comando global
Com suporte a compilação nativa para x86_64 e ARM64
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import subprocess
import os
import sys
import platform

# Função para compilar o core C/ASM
def build_native_core():
    """Compila o motor C/ASM usando o Makefile"""
    arch = platform.machine()
    print(f"🔧 Detectada arquitetura: {arch}")
    print("🔧 Compilando motor C/ASM do ZNetScan...")
    
    try:
        # Limpa compilações anteriores
        subprocess.check_call(['make', '-C', 'core', 'clean'], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        
        # Compila
        subprocess.check_call(['make', '-C', 'core', 'all'])
        
        # Instala a lib na raiz
        subprocess.check_call(['make', '-C', 'core', 'install'])
        
        print("✅ Motor C/ASM compilado com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Falha na compilação nativa: {e}")
        print("   O ZNetScan usará fallback em Python (mais lento)")
        return False
    except FileNotFoundError:
        print("⚠️ 'make' não encontrado. Instale build-essential ou binutils")
        print("   Ubuntu/Debian: sudo apt install build-essential")
        print("   Termux: pkg install binutils make clang")
        return False

# Comando personalizado para instalação
class CustomInstallCommand(install):
    def run(self):
        build_native_core()
        install.run(self)

# Comando personalizado para desenvolvimento
class CustomDevelopCommand(develop):
    def run(self):
        build_native_core()
        develop.run(self)

# Lê o README para usar como descrição longa
def read_long_description():
    """Lê o README.md para usar como descrição no PyPI"""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return """
# ZNetScan - Scanner de Rede Inteligente

**ZNetScan** é uma ferramenta que descobre dispositivos na rede e identifica MACs randomizados (iPhone/Android).

## 🔥 Diferencial
- 🔍 Detecta MACs falsos (randomizados por privacidade)
- 🆔 Fingerprint para identificar mesmo com MAC mudando
- 📊 Gerenciamento de dispositivos com histórico
- ⚡ Motor C/ASM otimizado para x86_64 e ARM64

## Instalação
```bash
pip install znetscan
```

## Uso
```bash
znet --method arp
znet help
```

## Links
- GitHub: https://github.com/Zer0G0ld/ZNetScan
"""

setup(
    name="znetscan",
    version="2.0.0",  # Versão Release Candidate
    author="Zer0G0ld",
    author_email="zer0g0ld@proton.me",
    description="🔍 ZNetScan - Scanner de Rede Inteligente com detecção de MAC randomizado e fingerprint",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zer0G0ld/ZNetScan",
    project_urls={
        "Bug Reports": "https://github.com/Zer0G0ld/ZNetScan/issues",
        "Source": "https://github.com/Zer0G0ld/ZNetScan",
        "Documentation": "https://github.com/Zer0G0ld/ZNetScan#readme",
        "Changelog": "https://github.com/Zer0G0ld/ZNetScan/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["docs", "tests", "venv", "__pycache__"]),
    py_modules=["main", "scan_all_networks", "identify_devices"],
    entry_points={
        "console_scripts": [
            "znet=main:main",
            "znetscan=main:main",
        ],
    },
    install_requires=[
        "colorama>=0.4.6",
        "requests>=2.31.0",
        "ipaddress>=1.0.23",
    ],
    # Dependências para compilação (opcionais)
    extras_require={
        "core": ["setuptools>=42.0.0"],
    },
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
    },
    # Inclui a biblioteca compilada
    package_data={
        'core': ['*.so', '*.dylib'],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Android",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C",
        "Programming Language :: Assembly",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    keywords="network scanner, arp, mac randomizer, fingerprint, network monitoring, security, termux",
    license="GPL-3.0",
    zip_safe=False,  # Necessário para ctypes carregar .so
)
