"""
Manipulação de interfaces de rede
"""

import subprocess
import re
import sys
from typing import List, Dict, Optional
from utils.logger import setup_logger
from utils.validators import Validators

class NetworkInterface:
    """Classe para gerenciar interfaces de rede"""
    
    def __init__(self, interface_name: str = None):
        self.logger = setup_logger()
        self.interface_name = interface_name
        self.info = {}
        
        if interface_name:
            self.load_interface_info()
    
    def list_interfaces(self) -> List[str]:
        """
        Lista todas as interfaces de rede disponíveis
        
        Returns:
            Lista de nomes das interfaces
        """
        interfaces = []
        
        if sys.platform.startswith('linux'):
            # Linux
            try:
                result = subprocess.run(
                    ['ip', 'link', 'show'],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'\d+: (\w+):'
                interfaces = re.findall(pattern, result.stdout)
                
            except:
                # Fallback para /proc/net/dev
                with open('/proc/net/dev', 'r') as f:
                    for line in f:
                        if ':' in line:
                            name = line.split(':')[0].strip()
                            if name not in ['lo', 'sit0']:
                                interfaces.append(name)
                                
        elif sys.platform == 'win32':
            # Windows
            try:
                result = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'Adaptador (?:Ethernet|Wi-Fi) ([\w\s]+):'
                interfaces = re.findall(pattern, result.stdout)
                
            except:
                pass
        else:
            # macOS
            try:
                result = subprocess.run(
                    ['ifconfig', '-l'],
                    capture_output=True,
                    text=True
                )
                interfaces = result.stdout.strip().split()
                interfaces = [i for i in interfaces if i != 'lo0']
            except:
                pass
        
        return interfaces
    
    def load_interface_info(self) -> Dict:
        """
        Carrega informações da interface
        
        Returns:
            Dicionário com informações da interface
        """
        if not self.interface_name:
            return {}
        
        info = {
            'name': self.interface_name,
            'mac': self.get_mac_address(),
            'ipv4': self.get_ipv4_address(),
            'ipv6': self.get_ipv6_address(),
            'status': self.get_status(),
            'speed': self.get_speed(),
            'mtu': self.get_mtu()
        }
        
        self.info = info
        return info
    
    def get_mac_address(self) -> Optional[str]:
        """Obtém MAC address da interface"""
        try:
            if sys.platform.startswith('linux'):
                result = subprocess.run(
                    ['ip', 'link', 'show', self.interface_name],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'link/ether ([0-9a-f:]{17})'
                match = re.search(pattern, result.stdout)
                if match:
                    return match.group(1)
                    
            elif sys.platform == 'win32':
                result = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True,
                    text=True
                )
                
                pattern = rf'{self.interface_name}.*?Endereço Físico[.\s]+:\s+([0-9A-F-]+)'
                match = re.search(pattern, result.stdout, re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).replace('-', ':')
                    
            else:  # macOS
                result = subprocess.run(
                    ['ifconfig', self.interface_name],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'ether ([0-9a-f:]{17})'
                match = re.search(pattern, result.stdout)
                if match:
                    return match.group(1)
                    
        except Exception as e:
            self.logger.error(f"Erro ao obter MAC: {e}")
            
        return None
    
    def get_ipv4_address(self) -> Optional[str]:
        """Obtém endereço IPv4 da interface"""
        try:
            if sys.platform.startswith('linux'):
                result = subprocess.run(
                    ['ip', '-4', 'addr', 'show', self.interface_name],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'inet (\d+\.\d+\.\d+\.\d+)/'
                match = re.search(pattern, result.stdout)
                if match:
                    return match.group(1)
                    
            else:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
                
        except Exception as e:
            self.logger.error(f"Erro ao obter IPv4: {e}")
            
        return None
    
    def get_ipv6_address(self) -> Optional[str]:
        """Obtém endereço IPv6 da interface"""
        try:
            if sys.platform.startswith('linux'):
                result = subprocess.run(
                    ['ip', '-6', 'addr', 'show', self.interface_name],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'inet6 ([0-9a-f:]+)/'
                match = re.search(pattern, result.stdout)
                if match:
                    return match.group(1)
                    
        except:
            pass
            
        return None
    
    def get_status(self) -> str:
        """Verifica status da interface (up/down)"""
        try:
            if sys.platform.startswith('linux'):
                result = subprocess.run(
                    ['ip', 'link', 'show', self.interface_name],
                    capture_output=True,
                    text=True
                )
                
                if 'UP' in result.stdout:
                    return 'up'
                else:
                    return 'down'
                    
        except:
            pass
            
        return 'unknown'
    
    def get_speed(self) -> Optional[int]:
        """Obtém velocidade da interface em Mbps"""
        try:
            if sys.platform.startswith('linux'):
                # Lê velocidade do arquivo sysfs
                speed_file = f'/sys/class/net/{self.interface_name}/speed'
                with open(speed_file, 'r') as f:
                    speed = int(f.read().strip())
                    return speed
        except:
            pass
        
        return None
    
    def get_mtu(self) -> Optional[int]:
        """Obtém MTU da interface"""
        try:
            if sys.platform.startswith('linux'):
                result = subprocess.run(
                    ['ip', 'link', 'show', self.interface_name],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'mtu (\d+)'
                match = re.search(pattern, result.stdout)
                if match:
                    return int(match.group(1))
                    
        except:
            pass
            
        return None
    
    def set_interface_up(self) -> bool:
        """Ativa a interface"""
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(
                    ['sudo', 'ip', 'link', 'set', self.interface_name, 'up'],
                    check=True
                )
                return True
        except:
            pass
        return False
    
    def set_interface_down(self) -> bool:
        """Desativa a interface"""
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(
                    ['sudo', 'ip', 'link', 'set', self.interface_name, 'down'],
                    check=True
                )
                return True
        except:
            pass
        return False
    
    def change_mac(self, new_mac: str) -> bool:
        """
        Altera MAC address da interface (requer sudo)
        
        Args:
            new_mac: Novo MAC address
            
        Returns:
            True se sucesso
        """
        if not Validators.validate_mac(new_mac):
            self.logger.error(f"MAC inválido: {new_mac}")
            return False
        
        try:
            if sys.platform.startswith('linux'):
                # Desativa interface
                self.set_interface_down()
                
                # Altera MAC
                subprocess.run(
                    ['sudo', 'ip', 'link', 'set', self.interface_name, 'address', new_mac],
                    check=True
                )
                
                # Reativa interface
                self.set_interface_up()
                
                self.logger.info(f"MAC alterado para {new_mac}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao alterar MAC: {e}")
            
        return False
    
    def get_network_info(self) -> Dict:
        """
        Obtém informações completas da rede
        
        Returns:
            Dicionário com informações da rede
        """
        return {
            'interface': self.info,
            'gateway': self._get_gateway(),
            'dns_servers': self._get_dns_servers(),
            'network_cidr': self._get_network_cidr()
        }
    
    def _get_gateway(self) -> Optional[str]:
        """Obtém gateway padrão"""
        try:
            if sys.platform.startswith('linux'):
                result = subprocess.run(
                    ['ip', 'route', 'show', 'default'],
                    capture_output=True,
                    text=True
                )
                
                pattern = r'default via (\d+\.\d+\.\d+\.\d+)'
                match = re.search(pattern, result.stdout)
                if match:
                    return match.group(1)
                    
        except:
            pass
            
        return None
    
    def _get_dns_servers(self) -> List[str]:
        """Obtém servidores DNS"""
        dns_servers = []
        
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns_servers.append(line.split()[1])
        except:
            pass
            
        return dns_servers
    
    def _get_network_cidr(self) -> Optional[str]:
        """Obtém rede no formato CIDR"""
        if self.info.get('ipv4'):
            parts = self.info['ipv4'].split('.')
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        return None
    
    def scan_available_interfaces(self) -> List[Dict]:
        """
        Escaneia e retorna informações de todas interfaces
        
        Returns:
            Lista de dicionários com informações das interfaces
        """
        interfaces_info = []
        
        for iface in self.list_interfaces():
            iface_obj = NetworkInterface(iface)
            info = iface_obj.load_interface_info()
            interfaces_info.append(info)
            
        return interfaces_info
    
    def print_info(self):
        """Imprime informações formatadas da interface"""
        if not self.info:
            self.load_interface_info()
        
        print("\n" + "=" * 50)
        print(f"INTERFACE: {self.interface_name}")
        print("=" * 50)
        print(f"Status: {self.info.get('status', 'N/A')}")
        print(f"MAC Address: {self.info.get('mac', 'N/A')}")
        print(f"IPv4 Address: {self.info.get('ipv4', 'N/A')}")
        print(f"IPv6 Address: {self.info.get('ipv6', 'N/A')}")
        print(f"MTU: {self.info.get('mtu', 'N/A')}")
        print(f"Speed: {self.info.get('speed', 'N/A')} Mbps")
        
        # Informações da rede
        gateway = self._get_gateway()
        if gateway:
            print(f"Gateway: {gateway}")
        
        dns = self._get_dns_servers()
        if dns:
            print(f"DNS Servers: {', '.join(dns)}")
        
        print("=" * 50 + "\n")