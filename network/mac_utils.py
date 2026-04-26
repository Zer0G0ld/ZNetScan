"""
Utilitários para manipulação de MAC addresses
Com detecção de MAC Randomizado baseado no bit U/L
"""

import re
import requests
from typing import Dict, Optional, List, Tuple
from utils.validators import Validators
from config.settings import OUI_DATABASE

class MACUtils:
    """Classe com funções para manipular MAC addresses"""
    
    def __init__(self):
        self.oui_cache = OUI_DATABASE.copy()
        self.cache_file = "oui_cache.json"
        self.known_devices_file = "known_devices.json"
        self._load_cache()
        self._load_known_devices()
    
    def _load_cache(self):
        """Carrega cache de fabricantes"""
        try:
            import json
            from pathlib import Path
            
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    loaded = json.load(f)
                    self.oui_cache.update(loaded)
        except:
            pass
    
    def _save_cache(self):
        """Salva cache de fabricantes"""
        try:
            import json
            from pathlib import Path
            
            with open(self.cache_file, 'w') as f:
                json.dump(self.oui_cache, f)
        except:
            pass
    
    def _load_known_devices(self):
        """Carrega banco de dispositivos conhecidos"""
        try:
            import json
            from pathlib import Path
            
            devices_path = Path(self.known_devices_file)
            if devices_path.exists():
                with open(devices_path, 'r') as f:
                    self.known_devices = json.load(f)
            else:
                self.known_devices = {}
        except:
            self.known_devices = {}
    
    def _save_known_devices(self):
        """Salva banco de dispositivos conhecidos"""
        try:
            import json
            from pathlib import Path
            
            with open(self.known_devices_file, 'w') as f:
                json.dump(self.known_devices, f, indent=2)
        except:
            pass
    
    def get_oui(self, mac: str) -> str:
        """
        Obtém OUI (Organizationally Unique Identifier) do MAC
        
        Args:
            mac: MAC address
            
        Returns:
            Prefixo OUI (3 primeiros bytes)
        """
        normalized = Validators.normalize_mac(mac, 'colon')
        return normalized[:8]  # AA:BB:CC
    
    def is_randomized_mac(self, mac: str) -> Tuple[bool, str]:
        """
        Detecta se o MAC é randomizado baseado no bit U/L
        
        A lógica é baseada no segundo caractere do MAC:
        - Se o segundo caractere for 0,4,8,C → MAC Universal (Fábrica)
        - Se o segundo caractere for 2,6,A,E → MAC Local (Randomizado)
        
        Args:
            mac: MAC address
            
        Returns:
            Tupla (é_randomizado, explicação)
        """
        if not Validators.validate_mac(mac):
            return False, "MAC inválido"
        
        normalized = Validators.normalize_mac(mac, 'colon')
        first_byte = normalized.split(':')[0]  # Ex: "AA"
        
        # Pega o segundo caractere do primeiro byte
        second_char = first_byte[1].upper()  # Ex: "A" em "AA"
        
        # MACs randomizados (Localmente Administrados)
        randomized_chars = ['2', '6', 'A', 'E']
        # MACs de fábrica (Universalmente Administrados)
        factory_chars = ['0', '4', '8', 'C']
        
        if second_char in randomized_chars:
            return True, f"MAC Randomizado (Local) - Bit U/L=1 - Segundo caractere '{second_char}' indica MAC gerado por software"
        elif second_char in factory_chars:
            return False, f"MAC de Fábrica (Universal) - Bit U/L=0 - Segundo caractere '{second_char}' indica MAC único de hardware"
        else:
            # Caso raro, faz análise binária
            first_int = int(first_byte, 16)
            is_local = (first_int & 0x02) != 0
            if is_local:
                return True, f"MAC Randomizado detectado via análise binária (bit U/L=1)"
            else:
                return False, f"MAC de Fábrica detectado via análise binária (bit U/L=0)"
    
    def get_mac_reliability(self, mac: str) -> Dict:
        """
        Avalia a confiabilidade do MAC como identificador único
        
        Args:
            mac: MAC address
            
        Returns:
            Dicionário com análise de confiabilidade
        """
        is_random, explanation = self.is_randomized_mac(mac)
        
        return {
            'mac': mac,
            'normalized': Validators.normalize_mac(mac),
            'is_randomized': is_random,
            'explanation': explanation,
            'reliability': 'BAIXA' if is_random else 'ALTA',
            'recommendation': 'Não use como ID único - use autenticação adicional' if is_random else 'Pode usar como identificador confiável',
            'type': 'Local (Software)' if is_random else 'Universal (Hardware)'
        }
    
    def get_manufacturer(self, mac: str, check_reliability: bool = True) -> str:
        """
        Identifica fabricante pelo MAC address com análise de confiabilidade
        
        Args:
            mac: MAC address
            check_reliability: Se deve incluir informação de randomização
            
        Returns:
            Nome do fabricante com indicação de randomização se aplicável
        """
        if not Validators.validate_mac(mac):
            return "Invalid MAC"
        
        # Verifica se é randomizado
        if check_reliability:
            is_random, _ = self.is_randomized_mac(mac)
            if is_random:
                # Tenta identificar padrão de randomização
                return self._identify_randomized_device(mac)
        
        oui = self.get_oui(mac)
        
        # Primeiro verifica no cache local
        if oui in self.oui_cache:
            return self.oui_cache[oui]
        
        # Tenta consultar API online
        manufacturer = self._query_api(mac)
        if manufacturer:
            self.oui_cache[oui] = manufacturer
            self._save_cache()
            return manufacturer
        
        return "Unknown Manufacturer"
    
    def _identify_randomized_device(self, mac: str) -> str:
        """
        Identifica possível dispositivo baseado em padrões de MAC randomizado
        
        Args:
            mac: MAC address
            
        Returns:
            Descrição do tipo provável de dispositivo
        """
        normalized = Validators.normalize_mac(mac, 'colon')
        first_byte = normalized.split(':')[0]
        
        # Padrões conhecidos de randomização
        patterns = {
            '02:42': 'Docker Container',
            '02:44': 'Docker Container',
            '02:45': 'Docker Container',
            '08:00:27': 'VirtualBox VM',
            '00:0C:29': 'VMware VM',
            '00:50:56': 'VMware VM',
            '02:00:00': 'Virtual Machine',
            '06:00:00': 'Virtual Machine',
            '0A:00:00': 'Virtual Machine',
        }
        
        for pattern, device_type in patterns.items():
            if normalized.startswith(pattern):
                return f"{device_type} (MAC Randomizado)"
        
        # Detecta por prefixo
        second_char = first_byte[1].upper()
        
        if second_char in ['2', '6', 'A', 'E']:
            return f"Mobile Device (MAC Randomizado - Android/iOS)"
        
        return "Unknown Device (MAC Randomizado)"
    
    def _query_api(self, mac: str) -> Optional[str]:
        """
        Consulta API externa para identificar fabricante
        
        Args:
            mac: MAC address
            
        Returns:
            Nome do fabricante ou None
        """
        try:
            # API gratuita para consulta de MAC
            url = f"https://api.macvendors.com/{mac}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        
        return None
    
    def is_multicast(self, mac: str) -> bool:
        """
        Verifica se MAC é multicast
        
        Args:
            mac: MAC address
            
        Returns:
            True se multicast
        """
        first_byte = mac.split(':')[0]
        return int(first_byte, 16) & 1 == 1
    
    def is_broadcast(self, mac: str) -> bool:
        """Verifica se é broadcast (FF:FF:FF:FF:FF:FF)"""
        return Validators.normalize_mac(mac) == "FF:FF:FF:FF:FF:FF"
    
    def is_unicast(self, mac: str) -> bool:
        """Verifica se é unicast (não multicast)"""
        return not self.is_multicast(mac)
    
    def get_mac_type(self, mac: str) -> str:
        """
        Classifica o tipo de MAC
        
        Returns:
            Tipo: 'unicast', 'multicast', 'broadcast'
        """
        normalized = Validators.normalize_mac(mac)
        
        if self.is_broadcast(normalized):
            return 'broadcast'
        elif self.is_multicast(normalized):
            return 'multicast'
        else:
            return 'unicast'
    
    def generate_random_mac(self, manufacturer: str = None) -> str:
        """
        Gera MAC address aleatório (respeitando bit U/L=1)
        
        Args:
            manufacturer: Fabricante específico (opcional)
            
        Returns:
            MAC address aleatório
        """
        import random
        
        if manufacturer:
            # Busca OUI do fabricante
            for oui, name in self.oui_cache.items():
                if manufacturer.lower() in name.lower():
                    prefix = oui
                    break
            else:
                prefix = "02:00:00"
        else:
            # Gera OUI aleatório com bit local (x2:xx:xx)
            # O primeiro byte deve ter o segundo bit = 1 (randomizado)
            first_byte = random.choice(['02', '06', '0A', '12', '16', '1A', '22', '26', '2A', '32', '36', '3A'])
            prefix = f"{first_byte}:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
        
        # Gera sufixo
        suffix = f":{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
        
        return prefix + suffix
    
    def get_vendor_info(self, mac: str, include_reliability: bool = True) -> Dict:
        """
        Obtém informações detalhadas do fabricante
        
        Args:
            mac: MAC address
            include_reliability: Se deve incluir análise de randomização
            
        Returns:
            Dicionário com informações do fabricante
        """
        result = {
            'mac': mac,
            'normalized': Validators.normalize_mac(mac),
            'oui': self.get_oui(mac),
            'manufacturer': self.get_manufacturer(mac),
            'type': self.get_mac_type(mac),
            'is_multicast': self.is_multicast(mac),
            'is_broadcast': self.is_broadcast(mac),
            'is_unicast': self.is_unicast(mac)
        }
        
        if include_reliability:
            reliability = self.get_mac_reliability(mac)
            result['is_randomized'] = reliability['is_randomized']
            result['reliability'] = reliability['reliability']
            result['mac_explanation'] = reliability['explanation']
            result['recommendation'] = reliability['recommendation']
        
        return result
    
    def compare_macs(self, mac1: str, mac2: str) -> bool:
        """
        Compara dois MAC addresses (case insensitive)
        
        Args:
            mac1: Primeiro MAC
            mac2: Segundo MAC
            
        Returns:
            True se iguais
        """
        norm1 = Validators.normalize_mac(mac1)
        norm2 = Validators.normalize_mac(mac2)
        return norm1 == norm2
    
    def learn_device(self, mac: str, device_name: str, device_type: str = None):
        """
        Aprende um novo dispositivo manualmente
        
        Args:
            mac: MAC address
            device_name: Nome/descrição do dispositivo
            device_type: Tipo (computer, mobile, iot, etc)
        """
        normalized = Validators.normalize_mac(mac)
        is_random, _ = self.is_randomized_mac(mac)
        
        self.known_devices[normalized] = {
            'name': device_name,
            'type': device_type or 'unknown',
            'is_randomized': is_random,
            'learned_at': str(__import__('datetime').datetime.now())
        }
        
        self._save_known_devices()
        print(f"✅ Dispositivo aprendido: {device_name} - {mac}")
    
    def get_learned_device(self, mac: str) -> Optional[Dict]:
        """Recupera dispositivo aprendido anteriormente"""
        normalized = Validators.normalize_mac(mac)
        return self.known_devices.get(normalized)