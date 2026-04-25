"""
Validações para dados de rede
"""

import re
from typing import Union, List, Optional

class Validators:
    """Classe com funções de validação"""
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """
        Valida formato de IP
        
        Args:
            ip: String do IP (ex: 192.168.1.1)
            
        Returns:
            True se IP válido, False caso contrário
        """
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))
    
    @staticmethod
    def validate_mac(mac: str) -> bool:
        """
        Valida formato de MAC address
        
        Args:
            mac: String do MAC (ex: AA:BB:CC:DD:EE:FF)
            
        Returns:
            True se MAC válido, False caso contrário
        """
        # Aceita formatos: AA:BB:CC:DD:EE:FF, AA-BB-CC-DD-EE-FF, AABBCCDDEEFF
        patterns = [
            r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',  # Com separadores
            r'^[0-9A-Fa-f]{12}$'  # Sem separadores
        ]
        
        return any(re.match(pattern, mac) for pattern in patterns)
    
    @staticmethod
    def validate_cidr(cidr: str) -> bool:
        """
        Valida formato CIDR
        
        Args:
            cidr: String no formato CIDR (ex: 192.168.1.0/24)
            
        Returns:
            True se CIDR válido, False caso contrário
        """
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(3[0-2]|[12]?[0-9])$'
        return bool(re.match(pattern, cidr))
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """
        Valida número de porta
        
        Args:
            port: Número da porta
            
        Returns:
            True se porta válida (1-65535)
        """
        return 1 <= port <= 65535
    
    @staticmethod
    def validate_port_range(port_range: str) -> Optional[tuple]:
        """
        Valida intervalo de portas (ex: 20-80)
        
        Args:
            port_range: String no formato "inicio-fim"
            
        Returns:
            Tupla (inicio, fim) ou None se inválido
        """
        try:
            if '-' in port_range:
                start, end = map(int, port_range.split('-'))
                if Validators.validate_port(start) and Validators.validate_port(end) and start <= end:
                    return (start, end)
            else:
                port = int(port_range)
                if Validators.validate_port(port):
                    return (port, port)
        except:
            pass
        return None
    
    @staticmethod
    def normalize_mac(mac: str, format: str = 'colon') -> str:
        """
        Normaliza MAC para formato padrão
        
        Args:
            mac: MAC address em qualquer formato
            format: 'colon' (AA:BB:CC:DD:EE:FF) ou 'dash' (AA-BB-CC-DD-EE-FF)
            
        Returns:
            MAC normalizado
        """
        # Remove caracteres não hexadecimais
        clean_mac = re.sub(r'[^0-9A-Fa-f]', '', mac)
        
        if len(clean_mac) != 12:
            return mac
        
        # Divide em pares
        pairs = [clean_mac[i:i+2] for i in range(0, 12, 2)]
        
        if format == 'colon':
            return ':'.join(pairs).upper()
        elif format == 'dash':
            return '-'.join(pairs).upper()
        else:
            return clean_mac.upper()
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """
        Verifica se IP é privado
        
        Args:
            ip: Endereço IP
            
        Returns:
            True se IP privado
        """
        private_ranges = [
            r'^10\.',  # 10.0.0.0/8
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # 172.16.0.0/12
            r'^192\.168\.',  # 192.168.0.0/16
            r'^127\.',  # Loopback
        ]
        
        return any(re.match(pattern, ip) for pattern in private_ranges)
    
    @staticmethod
    def validate_network_interface(interface: str) -> bool:
        """
        Valida nome de interface de rede
        
        Args:
            interface: Nome da interface (eth0, wlan0, etc)
            
        Returns:
            True se nome válido
        """
        # Padrões comuns de interfaces Linux/Windows
        patterns = [
            r'^eth\d+$',  # eth0, eth1
            r'^wlan\d+$',  # wlan0, wlan1
            r'^enp\ds\d+$',  # enp0s3 (predictable names)
            r'^enx[0-9a-f]{12}$',  # enxMAC
            r'^Ethernet\d+$',  # Windows
            r'^Wi-Fi\d*$',  # Windows
            r'^en\d+$',  # macOS
        ]
        
        return any(re.match(pattern, interface) for pattern in patterns)