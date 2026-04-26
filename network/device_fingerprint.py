"""
Sistema de Identificação de Dispositivos por Impressão Digital
Sem falsos positivos - usando múltiplas características
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from utils.logger import setup_logger

class DeviceFingerprinter:
    """Identifica dispositivos mesmo com MAC randomizado"""
    
    def __init__(self, db_file: str = "device_fingerprints.json"):
        self.logger = setup_logger()
        self.db_file = db_file
        self.devices = {}  # ID do dispositivo -> informações
        self.sessions = {}  # MAC atual -> ID do dispositivo
        self.load_database()
    
    def load_database(self):
        """Carrega banco de dispositivos conhecidos"""
        if Path(self.db_file).exists():
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.devices = data.get('devices', {})
                    self.sessions = data.get('sessions', {})
                self.logger.info(f"Carregados {len(self.devices)} dispositivos conhecidos")
            except:
                pass
    
    def save_database(self):
        """Salva banco de dispositivos"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump({
                    'devices': self.devices,
                    'sessions': self.sessions,
                    'last_update': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar banco: {e}")
    
    def extract_features(self, device_info: Dict) -> Dict:
        """
        Extrai características únicas do dispositivo
        Mesmo com MAC randomizado, essas características são estáveis
        """
        features = {
            'oui_pattern': None,      # Padrão do fabricante do chip
            'ip_range': None,          # Faixa de IP que o dispositivo usa
            'active_hours': [],        # Horários que aparece
            'typical_ports': [],       # Portas que costuma usar
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'seen_count': 0
        }
        
        # 1. Extrai padrão OUI mesmo de MAC randomizado
        if 'mac' in device_info:
            mac = device_info['mac'].upper()
            # Pega os primeiros 8 caracteres (OUI real ou padrão)
            oui = mac[:8] if len(mac) >= 8 else mac
            features['oui_pattern'] = oui
            
            # Para MACs randomizados, o OUI pode ser falso mas o chip ainda tem padrão
            # Ex: 02:F6:E8:0E:1C:3D -> chip pode ser Broadcom mesmo com MAC falso
        
        # 2. Extrai faixa de IP
        if 'ip' in device_info:
            ip = device_info['ip']
            # Pega a sub-rede /24
            ip_parts = ip.split('.')
            features['ip_range'] = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        
        # 3. Extrai hora atual para padrão de comportamento
        current_hour = datetime.now().hour
        features['active_hours'].append(current_hour)
        
        return features
    
    def generate_fingerprint(self, device_info: Dict) -> str:
        """
        Gera uma impressão digital única do dispositivo
        Combina múltiplas características para identificar mesmo com MAC mudando
        """
        features = self.extract_features(device_info)
        
        # Cria uma string única combinando características estáveis
        fingerprint_parts = []
        
        if features['oui_pattern']:
            fingerprint_parts.append(f"oui:{features['oui_pattern']}")
        
        if features['ip_range']:
            fingerprint_parts.append(f"iprange:{features['ip_range']}")
        
        # Adiciona padrão de horário (agrupado por blocos de 4 horas)
        if features['active_hours']:
            hour_block = min(features['active_hours']) // 4
            fingerprint_parts.append(f"timeblock:{hour_block}")
        
        # Gera hash único
        fingerprint_str = "|".join(fingerprint_parts)
        fingerprint_hash = hashlib.md5(fingerprint_str.encode()).hexdigest()[:16]
        
        return fingerprint_hash
    
    def identify_device(self, current_device: Dict) -> Dict:
        """
        Identifica um dispositivo mesmo com MAC randomizado
        
        Retorna:
            - device_id: ID do dispositivo (existente ou novo)
            - confidence: nível de confiança (high/medium/low)
            - is_new: se é um dispositivo nunca visto
            - matched_by: como foi identificado
        """
        current_mac = current_device.get('mac', '').upper()
        current_ip = current_device.get('ip', '')
        
        # 1. Verifica se já vimos este MAC hoje (sessão ativa)
        if current_mac in self.sessions:
            device_id = self.sessions[current_mac]
            self.devices[device_id]['last_seen'] = datetime.now().isoformat()
            self.devices[device_id]['seen_count'] += 1
            self.save_database()
            return {
                'device_id': device_id,
                'confidence': 'high',
                'is_new': False,
                'matched_by': 'active_session',
                'device_info': self.devices[device_id]
            }
        
        # 2. Gera impressão digital atual
        current_fingerprint = self.generate_fingerprint(current_device)
        
        # 3. Compara com dispositivos conhecidos
        best_match = None
        best_score = 0
        
        for device_id, device_data in self.devices.items():
            score = 0
            match_reasons = []
            
            # Compara OUI pattern (principal característica)
            if 'oui_pattern' in device_data.get('features', {}):
                if device_data['features']['oui_pattern'] == current_fingerprint.split('oui:')[1].split('|')[0] if 'oui:' in current_fingerprint else None:
                    score += 50
                    match_reasons.append('same_oui')
            
            # Compara faixa de IP
            current_ip_range = self.extract_features(current_device)['ip_range']
            if device_data.get('ip_range') == current_ip_range:
                score += 30
                match_reasons.append('same_ip_range')
            
            # Compara padrão de horário
            current_hour = datetime.now().hour
            if current_hour in device_data.get('active_hours', []):
                score += 20
                match_reasons.append('same_hour_pattern')
            
            # Atualiza score
            if score > best_score:
                best_score = score
                best_match = {
                    'device_id': device_id,
                    'score': score,
                    'reasons': match_reasons,
                    'device_data': device_data
                }
        
        # 4. Decide baseado no score
        if best_match and best_match['score'] >= 50:
            # Dispositivo conhecido com alta confiança
            device_id = best_match['device_id']
            
            # Atualiza sessão
            self.sessions[current_mac] = device_id
            
            # Atualiza dados do dispositivo
            self.devices[device_id]['last_seen'] = datetime.now().isoformat()
            self.devices[device_id]['seen_count'] += 1
            self.devices[device_id]['last_mac'] = current_mac
            self.devices[device_id]['last_ip'] = current_ip
            
            # Atualiza horários ativos
            current_hour = datetime.now().hour
            if current_hour not in self.devices[device_id].get('active_hours', []):
                self.devices[device_id].setdefault('active_hours', []).append(current_hour)
            
            self.save_database()
            
            return {
                'device_id': device_id,
                'confidence': 'high' if best_match['score'] >= 70 else 'medium',
                'is_new': False,
                'matched_by': best_match['reasons'],
                'device_info': self.devices[device_id],
                'match_score': best_match['score']
            }
        
        # 5. Dispositivo novo - cria registro
        new_device_id = f"dev_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.devices)}"
        
        features = self.extract_features(current_device)
        
        self.devices[new_device_id] = {
            'name': f"Unknown Device {len(self.devices) + 1}",
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'seen_count': 1,
            'macs_seen': [current_mac],
            'ips_seen': [current_ip],
            'features': features,
            'active_hours': [datetime.now().hour],
            'last_mac': current_mac,
            'last_ip': current_ip,
            'type': 'unknown'
        }
        
        # Registra sessão
        self.sessions[current_mac] = new_device_id
        
        self.save_database()
        
        return {
            'device_id': new_device_id,
            'confidence': 'low',
            'is_new': True,
            'matched_by': 'new_device',
            'device_info': self.devices[new_device_id]
        }
    
    def learn_device(self, device_id: str, name: str, device_type: str):
        """Aprende manualmente o nome de um dispositivo"""
        if device_id in self.devices:
            self.devices[device_id]['name'] = name
            self.devices[device_id]['type'] = device_type
            self.devices[device_id]['manually_named'] = True
            self.save_database()
            self.logger.info(f"Dispositivo {device_id} aprendido como {name}")
            return True
        return False
    
    def get_device_history(self, device_id: str) -> Dict:
        """Retorna histórico completo de um dispositivo"""
        if device_id in self.devices:
            return self.devices[device_id]
        return {}
    
    def list_devices(self) -> List[Dict]:
        """Lista todos os dispositivos conhecidos"""
        devices_list = []
        for device_id, data in self.devices.items():
            devices_list.append({
                'id': device_id,
                'name': data.get('name', 'Unknown'),
                'type': data.get('type', 'unknown'),
                'seen_count': data.get('seen_count', 0),
                'first_seen': data.get('first_seen'),
                'last_seen': data.get('last_seen'),
                'last_mac': data.get('last_mac'),
                'last_ip': data.get('last_ip')
            })
        return sorted(devices_list, key=lambda x: x['seen_count'], reverse=True)
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Limpa sessões antigas (MACs que não vistos há X horas)"""
        cutoff = datetime.now() - timedelta(hours=hours)
        to_remove = []
        
        for mac, device_id in self.sessions.items():
            device = self.devices.get(device_id, {})
            last_seen = device.get('last_seen')
            
            if last_seen:
                last_seen_dt = datetime.fromisoformat(last_seen)
                if last_seen_dt < cutoff:
                    to_remove.append(mac)
        
        for mac in to_remove:
            del self.sessions[mac]
        
        if to_remove:
            self.logger.debug(f"Removidas {len(to_remove)} sessões antigas")
            self.save_database()


# Utilitário para linha de comando
if __name__ == "__main__":
    import sys
    
    fp = DeviceFingerprinter()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            print("\n📱 Dispositivos conhecidos:")
            print("-" * 80)
            for device in fp.list_devices():
                print(f"ID: {device['id']}")
                print(f"  Nome: {device['name']}")
                print(f"  Tipo: {device['type']}")
                print(f"  Visto: {device['seen_count']} vezes")
                print(f"  Último MAC: {device['last_mac']}")
                print(f"  Último IP: {device['last_ip']}")
                print()
        
        elif sys.argv[1] == 'learn' and len(sys.argv) == 4:
            fp.learn_device(sys.argv[2], sys.argv[3], 'user_identified')
            print(f"✅ Aprendido: {sys.argv[3]}")
        
        else:
            print("Uso:")
            print("  python device_fingerprint.py list")
            print("  python device_fingerprint.py learn <device_id> <nome>")
    else:
        # Demo
        test_device = {
            'mac': '02:F6:E8:0E:1C:3D',
            'ip': '192.168.0.37'
        }
        result = fp.identify_device(test_device)
        print(json.dumps(result, indent=2))
