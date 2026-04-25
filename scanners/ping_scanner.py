"""
Módulo especializado em escaneamento ICMP (ping)
"""

import subprocess
import threading
import ipaddress
from typing import List, Dict
from utils.logger import setup_logger

class PingScanner:
    """Scanner usando ICMP ping"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.active_hosts = []
        self.devices = []
        self.max_threads = 100
        
    def scan(self, network: str = "192.168.1.0/24") -> List[Dict]:
        """
        Escaneia rede usando ping
        
        Args:
            network: Rede no formato CIDR
            
        Returns:
            Lista de dispositivos ativos
        """
        self.logger.info(f"Iniciando ping scan na rede {network}")
        
        # Converte rede para lista de IPs
        network_obj = ipaddress.ip_network(network, strict=False)
        hosts = list(network_obj.hosts())
        
        print(f"Escaneando {len(hosts)} hosts... (pode levar alguns minutos)")
        
        # Executa ping em paralelo
        self._ping_all_hosts(hosts)
        
        # Obtém MACs dos hosts ativos
        self._get_macs()
        
        self.logger.info(f"Ping scan completado. {len(self.devices)} dispositivos encontrados")
        return self.devices
    
    def _ping_all_hosts(self, hosts: List):
        """Pinga todos os hosts usando threads"""
        threads = []
        
        for ip in hosts:
            ip_str = str(ip)
            thread = threading.Thread(
                target=self._ping_host,
                args=(ip_str,)
            )
            thread.start()
            threads.append(thread)
            
            # Limita threads simultâneas
            if len(threads) >= self.max_threads:
                for t in threads:
                    t.join()
                threads = []
        
        # Aguarda threads restantes
        for t in threads:
            t.join()
    
    def _ping_host(self, ip: str):
        """Ping de um host específico"""
        try:
            # Linux/Unix
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                capture_output=True,
                timeout=2
            )
            
            if result.returncode == 0:
                self.active_hosts.append(ip)
                print(f"✓ Host ativo: {ip}")
                
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            self.logger.debug(f"Erro ao pingar {ip}: {e}")
    
    def _get_macs(self):
        """Obtém MACs do cache ARP"""
        for ip in self.active_hosts:
            mac = self._get_mac_from_arp(ip)
            if mac:
                device = {
                    'ip': ip,
                    'mac': mac.upper(),
                    'manufacturer': self._get_manufacturer(mac),
                    'status': 'active'
                }
                self.devices.append(device)
    
    def _get_mac_from_arp(self, ip: str) -> str:
        """Obtém MAC do cache ARP"""
        try:
            result = subprocess.run(
                ['arp', '-n', ip],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ether' in line:
                    parts = line.split()
                    return parts[2]  # MAC address
                    
        except Exception as e:
            self.logger.debug(f"Erro ao obter MAC de {ip}: {e}")
            
        return None
    
    def _get_manufacturer(self, mac: str) -> str:
        """Identifica fabricante pelo MAC (simplificado)"""
        # Dicionário de prefixos MAC conhecidos
        vendors = {
            '00:11:22': 'Cisco',
            'AA:BB:CC': 'Dell',
            '88:88:88': 'Apple',
            # Adicione mais conforme necessário
        }
        
        prefix = mac[:8]  # Primeiros 3 bytes
        return vendors.get(prefix, 'Unknown')