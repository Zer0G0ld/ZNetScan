#!/usr/bin/env python3
"""
Setup para instalar ZNetScan como comando global
"""

from setuptools import setup, find_packages
import os

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
    version="1.2.2",  # Atualizado para nova versão
    author="Zer0G0ld",
    author_email="zer0g0ld@proton.me",  # Coloque um email real se quiser
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
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    keywords="network scanner, arp, mac randomizer, fingerprint, network monitoring, security",
    license="GPL-3.0",
    include_package_data=True,
    zip_safe=False,
)
