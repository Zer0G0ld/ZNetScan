#!/usr/bin/env python3
"""
Scan All Networks - Descobre dispositivos em todas as interfaces de rede ativas
"""

import subprocess
import re
from network.mac_utils import MACUtils
from output.formatters import ConsoleFormatter
from utils.logger import setup_logger

def get_all_networks():
    """Descobre todas as redes ativas no sistema"""
    networks = []
    
    # Executa ip address
    result = subprocess.run(['ip', 'address'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    current_interface = None
    
    for line in lines:
        # Detecta interface
        interface_match = re.match(r'\d+:\s+(\w+):', line)
        if interface_match:
            current_interface = interface_match.group(1)
        
        # Detecta IP
        ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', line)
        if ip_match and current_interface:
            ip = ip_match.group(1)
            mask = int(ip_match.group(2))
            
            # Ignora localhost e interfaces sem IP válido
            if ip != '127.0.0.1' and mask < 32 and mask > 0:
                # Ignora interfaces Docker/Tailscale por padrão (opcional)
                if current_interface not in ['docker0', 'tailscale0', 'veth'] and not current_interface.startswith('veth'):
                    network = f"{ip.rsplit('.', 1)[0]}.0/{mask}"
                    networks.append({
                        'interface': current_interface,
                        'ip': ip,
                        'network': network,
                        'mask': mask
                    })
    
    return networks

def scan_network_arp(network, interface=None):
    """Escaneia uma rede específica com ARP"""
    try:
        cmd = ['sudo', 'arp-scan', network]
        if interface:
            cmd.extend(['--interface', interface])
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        devices = []
        for line in result.stdout.split('\n'):
            # Padrão: IP \t MAC
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]{17})', line, re.IGNORECASE)
            if match:
                devices.append({
                    'ip': match.group(1),
                    'mac': match.group(2).upper()
                })
        
        return devices
    except subprocess.TimeoutExpired:
        print(f"  ⏰ Timeout no scan da rede {network}")
        return []
    except Exception as e:
        print(f"  ❌ Erro ao escanear {network}: {e}")
        return []

def main():
    print("\n" + "=" * 70)
    print("🔍 ZNetScan - Scan Completo de Todas as Redes")
    print("=" * 70)
    
    # Configura logger
    logger = setup_logger()
    
    # Descobre todas as redes
    networks = get_all_networks()
    
    if not networks:
        print("\n❌ Nenhuma rede ativa encontrada!")
        print("   Verifique se você está conectado a alguma rede.")
        return
    
    print(f"\n📡 Redes encontradas:")
    for net in networks:
        print(f"   • {net['interface']}: {net['network']} (IP: {net['ip']})")
    
    mac_utils = MACUtils()
    all_devices = []
    all_networks_data = []
    
    # Escaneia cada rede
    for net in networks:
        print(f"\n{'='*70}")
        print(f"🌐 Escaneando rede: {net['network']}")
        print(f"   Interface: {net['interface']}")
        print(f"   Seu IP: {net['ip']}")
        print(f"{'='*70}")
        
        devices = scan_network_arp(net['network'], net['interface'])
        
        if devices:
            print(f"✅ Encontrados {len(devices)} dispositivos")
            
            # Enriquece com análise de MAC
            for device in devices:
                mac_info = mac_utils.get_vendor_info(device['mac'], include_reliability=True)
                device['manufacturer'] = mac_info['manufacturer']
                device['reliability'] = mac_info['reliability']
                device['is_randomized'] = mac_info.get('is_randomized', False)
                device['interface'] = net['interface']
                device['network'] = net['network']
                all_devices.append(device)
            
            all_networks_data.append({
                'network': net['network'],
                'interface': net['interface'],
                'devices': devices
            })
        else:
            print(f"⚠️  Nenhum dispositivo encontrado")
            print(f"   Dica: Certifique-se que o arp-scan está instalado e você tem permissão")
    
    # Mostra resultados consolidados
    print("\n" + "=" * 70)
    print("📊 RESULTADO CONSOLIDADO")
    print("=" * 70)
    
    if not all_devices:
        print("\n❌ Nenhum dispositivo encontrado em nenhuma rede!")
        print("\n🔧 Possíveis soluções:")
        print("   1. Execute com sudo: sudo python3 scan_all_networks.py")
        print("   2. Instale arp-scan: sudo apt install arp-scan")
        print("   3. Verifique sua conexão de rede")
        return
    
    # Separa por tipo
    physical_devices = [d for d in all_devices if not d.get('is_randomized', False)]
    randomized_devices = [d for d in all_devices if d.get('is_randomized', False)]
    
    print(f"\n📈 Estatísticas:")
    print(f"   • Total de dispositivos: {len(all_devices)}")
    print(f"   • Dispositivos físicos (MAC fábrica): {len(physical_devices)}")
    print(f"   • Dispositivos com MAC randomizado: {len(randomized_devices)}")
    print(f"   • Redes escaneadas: {len(networks)}")
    
    # Tabela detalhada
    print(f"\n{'='*110}")
    print(f"{'Interface':<15} {'Rede':<20} {'IP Address':<18} {'MAC Address':<20} {'Fabricante'}")
    print(f"{'-'*110}")
    
    for device in all_devices:
        iface = device.get('interface', 'N/A')[:15]
        network = device.get('network', 'N/A')[:20]
        ip = device.get('ip', 'N/A')[:18]
        mac = device.get('mac', 'N/A')[:20]
        manufacturer = device.get('manufacturer', 'N/A')
        
        # Adiciona indicador visual para MAC randomizado
        if device.get('is_randomized', False):
            manufacturer = f"🔄 {manufacturer}"
        
        print(f"{iface:<15} {network:<20} {ip:<18} {mac:<20} {manufacturer}")
    
    print(f"{'='*110}\n")
    
    # Identifica seu próprio IP
    for net in networks:
        if 'wlp' in net['interface'] or 'eth' in net['interface']:
            print(f"📍 Seu IP na rede principal: {net['ip']}")
            print(f"   (Você não aparece no scan porque é a origem)\n")
            break
    
    # Recomendações
    if randomized_devices:
        print(f"💡 Dica: {len(randomized_devices)} dispositivo(s) com MAC randomizado")
        print("   Estes são provavelmente smartphones/tablets (Android/iOS)")
        print("   Não use MAC como identificador único para estes dispositivos\n")
    
    # Pergunta se quer salvar
    save = input("💾 Salvar resultados em JSON? (s/N): ").lower()
    if save == 's':
        import json
        from datetime import datetime
        
        filename = f"scan_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(all_devices, f, indent=2)
        print(f"✅ Resultados salvos em: {filename}")

if __name__ == "__main__":
    main()
