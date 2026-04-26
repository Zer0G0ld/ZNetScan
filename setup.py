#!/usr/bin/env python3
"""
Setup para instalar ZNetScan como comando global
"""

from setuptools import setup, find_packages
import os

# Lê o README para usar como descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="znetscan",
    version="1.1.0",
    author="Zer0G0ld",
    author_email="seu-email@example.com",
    description="ZNetScan - Scanner de Rede Inteligente com detecção de MAC randomizado",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zer0G0ld/ZNetScan",
    project_urls={
        "Bug Reports": "https://github.com/Zer0G0ld/ZNetScan/issues",
        "Source": "https://github.com/Zer0G0ld/ZNetScan",
    },
    packages=find_packages(),
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
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.7",
    keywords="network scanner, arp, mac randomizer, fingerprint, network monitoring",
)
