"""
Módulo especializado em escaneamento ARP
"""

import subprocess
import re
from typing import List, Dict
from utils.logger import setup_logger

class ARPScanner:
    """Scanner usando protocolo ARP"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.devices = []
        
    def scan(self, network: str = "192.168.1.0/24") -> List[Dict]:
        """
        Escaneia rede usando arp-scan
        
        Args:
            network: Rede no formato CIDR (ex: 192.168.1.0/24)
            
        Returns:
            Lista de dicionários com dispositivos encontrados
        """
        self.logger.info(f"Iniciando ARP scan na rede {network}")
        
        try:
            # Comando arp-scan
            cmd = ['sudo', 'arp-scan', '--localnet']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"ARP scan failed: {result.stderr}")
                return []
            
            # Processa resultados
            self.devices = self._parse_output(result.stdout)
            self.logger.info(f"ARP scan completado. {len(self.devices)} dispositivos encontrados")
            
            return self.devices
            
        except subprocess.TimeoutExpired:
            self.logger.error("ARP scan timeout")
            return []
        except FileNotFoundError:
            self.logger.error("arp-scan não instalado. Instale com: sudo apt install arp-scan")
            return []
    
    def _parse_output(self, output: str) -> List[Dict]:
        """Parseia a saída do arp-scan"""
        devices = []
        lines = output.split('\n')
        
        for line in lines:
            # Padrão: IP \t MAC \t Manufacturer
            pattern = r'(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]{17})\s+(.+)'
            match = re.search(pattern, line)
            
            if match:
                device = {
                    'ip': match.group(1),
                    'mac': match.group(2).upper(),
                    'manufacturer': match.group(3).strip(),
                    'status': 'active'
                }
                devices.append(device)
                
        return devices
    
    def get_device_by_ip(self, ip: str) -> Dict:
        """Busca dispositivo por IP"""
        for device in self.devices:
            if device['ip'] == ip:
                return device
        return None
    
    def get_devices_by_manufacturer(self, manufacturer: str) -> List[Dict]:
        """Filtra dispositivos por fabricante"""
        return [d for d in self.devices if manufacturer.lower() in d['manufacturer'].lower()]