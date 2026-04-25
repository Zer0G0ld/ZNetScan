"""
Utilitários para manipulação de IPs
"""

import ipaddress
import socket
from typing import List, Optional

class IPUtils:
    """Classe com funções utilitárias para IP"""
    
    @staticmethod
    def get_local_ip() -> str:
        """Obtém IP local da máquina"""
        try:
            # Conecta a um IP externo para descobrir interface ativa
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def get_network_cidr(ip: str = None) -> str:
        """Obtém a rede local no formato CIDR"""
        if not ip:
            ip = IPUtils.get_local_ip()
        
        # Assume máscara /24 (comum em redes locais)
        ip_parts = ip.split('.')
        network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return network
    
    @staticmethod
    def ip_to_int(ip: str) -> int:
        """Converte IP para número inteiro"""
        parts = ip.split('.')
        return (int(parts[0]) << 24) + (int(parts[1]) << 16) + \
               (int(parts[2]) << 8) + int(parts[3])
    
    @staticmethod
    def int_to_ip(ip_int: int) -> str:
        """Converte número inteiro para IP"""
        return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}." \
               f"{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Valida se string é um IP válido"""
        try:
            ipaddress.ip_address(ip)
            return True
        except:
            return False
    
    @staticmethod
    def get_hosts_in_network(network: str) -> List[str]:
        """Retorna todos os IPs de uma rede"""
        try:
            network_obj = ipaddress.ip_network(network, strict=False)
            return [str(ip) for ip in network_obj.hosts()]
        except:
            return []