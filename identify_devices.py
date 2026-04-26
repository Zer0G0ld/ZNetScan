#!/usr/bin/env python3
"""
Identifica dispositivos mesmo com MAC randomizado
Usa impressão digital para evitar falsos positivos
"""

import subprocess
import re
from network.mac_utils import MACUtils
from network.device_fingerprint import DeviceFingerprinter
from utils.logger import setup_logger

def scan_network():
    """Escaneia rede atual"""
    result = subprocess.run(
        ['sudo', 'arp-scan', '--localnet'],
        capture_output=True,
        text=True
    )
    
    devices = []
    for line in result.stdout.split('\n'):
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]{17})', line, re.IGNORECASE)
        if match:
            devices.append({
                'ip': match.group(1),
                'mac': match.group(2).upper()
            })
    
    return devices

def main():
    logger = setup_logger()
    mac_utils = MACUtils()
    fingerprinter = DeviceFingerprinter()
    
    print("\n" + "=" * 80)
    print("🔍 ZNetScan - Identificação Inteligente de Dispositivos")
    print("=" * 80)
    
    # Escaneia rede
    print("\n📡 Escaneando rede...")
    devices = scan_network()
    
    if not devices:
        print("❌ Nenhum dispositivo encontrado")
        return
    
    # Identifica cada dispositivo
    identified_devices = []
    
    for device in devices:
        # 1. Análise do MAC (randomizado ou não)
        mac_info = mac_utils.get_vendor_info(device['mac'], include_reliability=True)
        
        # 2. Identificação por impressão digital
        fingerprint = fingerprinter.identify_device(device)
        
        device_info = {
            'ip': device['ip'],
            'mac': device['mac'],
            'mac_reliability': mac_info['reliability'],
            'is_randomized': mac_info.get('is_randomized', False),
            'manufacturer': mac_info['manufacturer'],
            'device_id': fingerprint['device_id'],
            'device_name': fingerprint['device_info'].get('name', 'Unknown'),
            'confidence': fingerprint['confidence'],
            'is_new': fingerprint['is_new'],
            'matched_by': fingerprint['matched_by'],
            'seen_count': fingerprint['device_info'].get('seen_count', 1)
        }
        
        identified_devices.append(device_info)
    
    # Mostra resultados
    print("\n" + "=" * 80)
    print("📊 RESULTADO DA IDENTIFICAÇÃO")
    print("=" * 80)
    
    print(f"\n{'IP':<18} {'MAC':<20} {'Dispositivo':<20} {'Confiança':<10} {'Visto'}")
    print("-" * 80)
    
    for device in identified_devices:
        # Nome do dispositivo
        name = device['device_name']
        if name == 'Unknown':
            if device['is_randomized']:
                name = "📱 Smartphone (desconhecido)"
            else:
                name = f"🖥️ {device['manufacturer'][:20]}"
        
        # Indicador de confiança
        confidence_icon = {
            'high': '✅ ALTA',
            'medium': '⚠️ MÉDIA',
            'low': '❌ BAIXA'
        }.get(device['confidence'], '❓')
        
        print(f"{device['ip']:<18} {device['mac']:<20} {name:<20} {confidence_icon:<10} {device['seen_count']}")
    
    # Estatísticas
    print("\n" + "=" * 80)
    print("📈 ESTATÍSTICAS")
    print("-" * 80)
    
    new_devices = [d for d in identified_devices if d['is_new']]
    known_devices = [d for d in identified_devices if not d['is_new']]
    randomized = [d for d in identified_devices if d['is_randomized']]
    
    print(f"✅ Dispositivos conhecidos: {len(known_devices)}")
    print(f"🆕 Novos dispositivos: {len(new_devices)}")
    print(f"🔄 MACs randomizados: {len(randomized)}")
    
    # Dispositivos conhecidos (aprendidos)
    print("\n" + "=" * 80)
    print("📚 DISPOSITIVOS APRENDIDOS (Banco de dados)")
    print("-" * 80)
    
    learned = fingerprinter.list_devices()
    if learned:
        for dev in learned[:10]:  # Mostra últimos 10
            print(f"  • {dev['name']} - Visto {dev['seen_count']}x - Último: {dev['last_ip']}")
    else:
        print("  (Nenhum dispositivo aprendido ainda)")
    
    print("\n💡 Dica: Use 'python device_fingerprint.py learn <ID> <NOME>' para nomear dispositivos")
    print("   Ex: python network/device_fingerprint.py learn dev_20260425_123456 'Celular João'")

if __name__ == "__main__":
    main()
