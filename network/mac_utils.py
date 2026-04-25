"""
Utilitários para manipulação de MAC addresses
"""

import re
import requests
from typing import Dict, Optional, List
from utils.validators import Validators
from config.settings import OUI_DATABASE

class MACUtils:
    """Classe com funções para manipular MAC addresses"""
    
    def __init__(self):
        self.oui_cache = OUI_DATABASE.copy()
        self.cache_file = "oui_cache.json"
        self._load_cache()
    
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
    
    def get_manufacturer(self, mac: str) -> str:
        """
        Identifica fabricante pelo MAC address
        
        Args:
            mac: MAC address
            
        Returns:
            Nome do fabricante
        """
        if not Validators.validate_mac(mac):
            return "Invalid MAC"
        
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
        
        Args:
            mac: MAC address
            
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
        Gera MAC address aleatório
        
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
                prefix = "00:00:00"
        else:
            # Gera OUI aleatório local (x2:xx:xx)
            prefix = f"02:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
        
        # Gera sufixo
        suffix = f":{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
        
        return prefix + suffix
    
    def get_vendor_info(self, mac: str) -> Dict:
        """
        Obtém informações detalhadas do fabricante
        
        Args:
            mac: MAC address
            
        Returns:
            Dicionário com informações do fabricante
        """
        return {
            'mac': mac,
            'normalized': Validators.normalize_mac(mac),
            'oui': self.get_oui(mac),
            'manufacturer': self.get_manufacturer(mac),
            'type': self.get_mac_type(mac),
            'is_multicast': self.is_multicast(mac),
            'is_broadcast': self.is_broadcast(mac),
            'is_unicast': self.is_unicast(mac)
        }
    
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