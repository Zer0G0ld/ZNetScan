#!/usr/bin/env python3
"""
Network Scanner - Ferramenta modular para escaneamento de rede
Versão completa com todos os módulos, análise de MAC randomizado e fingerprint
"""

import sys
import argparse
from typing import List, Dict
from scanners.arp_scanner import ARPScanner
from scanners.ping_scanner import PingScanner
from scanners.port_scanner import PortScanner
from output.formatters import ConsoleFormatter
from output.exporters import JSONExporter, CSVExporter, TXTExporter, HTMLExporter
from utils.logger import setup_logger
from network.interface import NetworkInterface
from network.mac_utils import MACUtils
from network.device_fingerprint import DeviceFingerprinter

def main():
    # VERIFICAÇÃO DE HELP ANTES DO PARSE (CRÍTICO)
    if len(sys.argv) > 1 and sys.argv[1] == 'help':
        from utils.help import HelpSystem
        if len(sys.argv) > 2:
            HelpSystem.show_help(sys.argv[2])
        else:
            HelpSystem.show_help()
        return
    
    parser = argparse.ArgumentParser(
        description='Network Scanner Tool - Scan IPs, MACs and Ports with Device Fingerprinting',
        epilog='Examples:\n'
               '  znet --method arp\n'
               '  znet --method ping --output json\n'
               '  znet --port-scan 192.168.1.1\n'
               '  znet --interfaces\n'
               '  znet --list-devices\n'
               '  znet --learn-device dev_xxx "Meu Celular"\n'
               '  znet --version'
    )
    
    # Opções de scan
    parser.add_argument('-n', '--network', default='192.168.1.0/24',
                       help='Network range (ex: 192.168.1.0/24)')
    parser.add_argument('-m', '--method', choices=['arp', 'ping'], 
                       default='arp', help='Scan method')
    
    # Opções de port scan
    parser.add_argument('-p', '--port-scan', metavar='IP',
                       help='Scan ports on specific IP')
    parser.add_argument('--ports', default='common',
                       help='Ports to scan: "common", "range:1-1024", or comma list "22,80,443"')
    
    # Opções de saída
    parser.add_argument('-o', '--output', choices=['console', 'json', 'csv', 'txt', 'html'],
                       default='console', help='Output format')
    parser.add_argument('-f', '--filename', help='Output filename')
    
    # Informações do sistema
    parser.add_argument('-i', '--interfaces', action='store_true',
                       help='Show network interfaces')
    parser.add_argument('--mac-info', metavar='MAC',
                       help='Get info about a MAC address')
    
    # Opções de fingerprint
    parser.add_argument('--list-devices', action='store_true',
                       help='List all known devices (fingerprint database)')
    parser.add_argument('--learn-device', nargs=2, metavar=('DEVICE_ID', 'NAME'),
                       help='Learn a device name manually (ex: --learn-device dev_xxx "João iPhone")')
    parser.add_argument('--forget-device', metavar='DEVICE_ID',
                       help='Forget/remove a device from database')
    parser.add_argument('--device-history', metavar='DEVICE_ID',
                       help='Show history of a specific device')
    
    # Versão
    parser.add_argument('-v', '--version', action='version', version='ZNetScan v1.2.2')
    
    args = parser.parse_args()
    
    logger = setup_logger()
    
    # Lista dispositivos conhecidos
    if args.list_devices:
        list_known_devices()
        return
    
    # Aprende dispositivo
    if args.learn_device:
        learn_device_name(args.learn_device[0], args.learn_device[1])
        return
    
    # Esquece dispositivo
    if args.forget_device:
        forget_device(args.forget_device)
        return
    
    # Histórico do dispositivo
    if args.device_history:
        show_device_history(args.device_history)
        return
    
    # Mostra interfaces de rede
    if args.interfaces:
        print_network_interfaces()
        return
    
    # Informações de MAC
    if args.mac_info:
        get_mac_info(args.mac_info)
        return
    
    # Port scan
    if args.port_scan:
        port_scan(args.port_scan, args.ports, args.output, args.filename)
        return
    
    # Network scan (IPs e MACs) com fingerprint
    network_scan(args.network, args.method, args.output, args.filename)

def list_known_devices():
    """Lista todos os dispositivos conhecidos no banco de fingerprints"""
    fp = DeviceFingerprinter()
    devices = fp.list_devices()
    
    if not devices:
        print("\n📭 Nenhum dispositivo conhecido ainda.")
        print("   Execute um scan primeiro: znet --method arp")
        return
    
    print("\n" + "=" * 80)
    print("📱 DISPOSITIVOS CONHECIDOS (Banco de Fingerprints)")
    print("=" * 80)
    
    for device in devices:
        print(f"\n🆔 ID: {device['id']}")
        print(f"   📛 Nome: {device['name']}")
        print(f"   📱 Tipo: {device['type']}")
        print(f"   👁️  Visto: {device['seen_count']} vezes")
        print(f"   🔢 Último MAC: {device['last_mac']}")
        print(f"   🌐 Último IP: {device['last_ip']}")
        print(f"   📅 Primeira vez: {device['first_seen'][:19] if device['first_seen'] else 'N/A'}")
        print(f"   🕒 Última vez: {device['last_seen'][:19] if device['last_seen'] else 'N/A'}")
    
    print("\n" + "=" * 80)
    print(f"📊 Total: {len(devices)} dispositivos")
    print("\n💡 Dica: Use --learn-device <ID> \"Nome\" para nomear um dispositivo")

def learn_device_name(device_id: str, name: str):
    """Aprende o nome de um dispositivo manualmente"""
    fp = DeviceFingerprinter()
    
    if fp.learn_device(device_id, name, 'manual'):
        print(f"✅ Dispositivo {device_id} agora se chama '{name}'")
    else:
        print(f"❌ Dispositivo {device_id} não encontrado")
        print("   Use --list-devices para ver os IDs disponíveis")

def forget_device(device_id: str):
    """Remove um dispositivo do banco de dados"""
    fp = DeviceFingerprinter()
    
    if device_id in fp.devices:
        confirm = input(f"⚠️ Tem certeza que quer esquecer '{fp.devices[device_id].get('name', device_id)}'? (s/N): ")
        if confirm.lower() == 's':
            del fp.devices[device_id]
            to_remove = [mac for mac, did in fp.sessions.items() if did == device_id]
            for mac in to_remove:
                del fp.sessions[mac]
            fp.save_database()
            print(f"✅ Dispositivo removido")
    else:
        print(f"❌ Dispositivo {device_id} não encontrado")

def show_device_history(device_id: str):
    """Mostra histórico completo de um dispositivo"""
    fp = DeviceFingerprinter()
    history = fp.get_device_history(device_id)
    
    if not history:
        print(f"❌ Dispositivo {device_id} não encontrado")
        return
    
    print("\n" + "=" * 80)
    print(f"📜 HISTÓRICO DO DISPOSITIVO: {history.get('name', device_id)}")
    print("=" * 80)
    
    print(f"\n📋 Informações gerais:")
    print(f"   🆔 ID: {device_id}")
    print(f"   📛 Nome: {history.get('name', 'Unknown')}")
    print(f"   📱 Tipo: {history.get('type', 'unknown')}")
    print(f"   👁️  Visto: {history.get('seen_count', 0)} vezes")
    print(f"   📅 Primeira aparição: {history.get('first_seen', 'N/A')[:19]}")
    print(f"   🕒 Última aparição: {history.get('last_seen', 'N/A')[:19]}")
    
    print(f"\n🔢 MACs já utilizados:")
    for mac in history.get('macs_seen', []):
        print(f"   • {mac}")
    
    print(f"\n🌐 IPs já utilizados:")
    for ip in history.get('ips_seen', []):
        print(f"   • {ip}")
    
    print(f"\n⏰ Horários mais ativos:")
    for hour in sorted(history.get('active_hours', [])):
        print(f"   • {hour}:00 - {hour+1}:00")
    
    print("\n" + "=" * 80)

def print_network_interfaces():
    """Mostra informações das interfaces de rede"""
    print("\n" + "=" * 60)
    print("INTERFACES DE REDE")
    print("=" * 60)
    
    iface = NetworkInterface()
    interfaces = iface.scan_available_interfaces()
    
    for info in interfaces:
        print(f"\nInterface: {info.get('name', 'N/A')}")
        print(f"  Status: {info.get('status', 'N/A')}")
        print(f"  IP: {info.get('ipv4', 'N/A')}")
        print(f"  MAC: {info.get('mac', 'N/A')}")
        print(f"  MTU: {info.get('mtu', 'N/A')}")
        if info.get('speed'):
            print(f"  Speed: {info.get('speed')} Mbps")

def get_mac_info(mac_address: str):
    """Mostra informações detalhadas de um MAC com análise de randomização"""
    mac_utils = MACUtils()
    fp = DeviceFingerprinter()
    
    info = mac_utils.get_vendor_info(mac_address, include_reliability=True)
    
    print("\n" + "=" * 60)
    print("📡 INFORMAÇÕES DO MAC ADDRESS")
    print("=" * 60)
    print(f"\n🔢 MAC Original: {info['mac']}")
    print(f"📝 MAC Normalizado: {info['normalized']}")
    print(f"🔑 OUI: {info['oui']}")
    
    device_id = fp.sessions.get(mac_address.upper())
    if device_id and device_id in fp.devices:
        print(f"\n🔗 Este MAC pertence ao dispositivo:")
        print(f"   🆔 ID: {device_id}")
        print(f"   📛 Nome: {fp.devices[device_id].get('name', 'Unknown')}")
        print(f"   👁️  Visto {fp.devices[device_id].get('seen_count', 0)} vezes")
    
    if 'is_randomized' in info:
        print(f"\n🔍 ANÁLISE DE CONFIABILIDADE:")
        print(f"   📌 {info['mac_explanation']}")
        print(f"   🎯 Confiabilidade: {info['reliability']}")
        print(f"   💡 Recomendação: {info['recommendation']}")
        print(f"   📱 Tipo: {info['type']}")
    
    print("\n" + "=" * 60)

def port_scan(ip: str, ports_option: str, output_format: str, filename: str):
    """Executa scan de portas"""
    scanner = PortScanner()
    
    if ports_option == 'common':
        results = scanner.scan_common_ports(ip, 'tcp')
    elif ports_option.startswith('range:'):
        _, range_str = ports_option.split(':')
        start, end = map(int, range_str.split('-'))
        results = scanner.scan_range(ip, start, end, 'tcp')
    else:
        ports = [int(p.strip()) for p in ports_option.split(',')]
        results = scanner.scan_ports_tcp(ip, ports)
    
    report = scanner.generate_report(results)
    print(report)
    
    if output_format != 'console':
        export_results(results, output_format, filename or f'port_scan_{ip}.{output_format}')

def network_scan(network: str, method: str, output_format: str, filename: str):
    """Executa scan de rede com análise de MAC randomizado e fingerprint"""
    
    mac_utils = MACUtils()
    fp = DeviceFingerprinter()
    
    if method == 'arp':
        scanner = ARPScanner()
    else:
        scanner = PingScanner()
    
    print(f"Escaneando rede {network} usando {method}...")
    devices = scanner.scan(network)
    
    for device in devices:
        if 'mac' in device and device['mac']:
            mac_info = mac_utils.get_vendor_info(device['mac'], include_reliability=True)
            fingerprint = fp.identify_device(device)
            
            if mac_info.get('is_randomized', False):
                randomized_type = mac_utils._identify_randomized_device(device['mac'])
                device['manufacturer'] = f"🔄 {randomized_type}"
                device['reliability'] = mac_info['reliability']
                device['is_randomized'] = True
            else:
                device['manufacturer'] = mac_info['manufacturer']
                device['reliability'] = mac_info['reliability']
                device['is_randomized'] = False
            
            device['device_id'] = fingerprint['device_id']
            device['device_name'] = fingerprint['device_info'].get('name', 'Unknown')
            device['fingerprint_confidence'] = fingerprint['confidence']
            device['is_new_device'] = fingerprint['is_new']
            device['seen_count'] = fingerprint['device_info'].get('seen_count', 1)
    
    print_enhanced_results(devices, mac_utils, fp)
    
    if output_format != 'console':
        export_devices = []
        for device in devices:
            export_devices.append({
                'ip': device.get('ip', 'N/A'),
                'mac': device.get('mac', 'N/A'),
                'manufacturer': device.get('manufacturer', 'N/A'),
                'reliability': device.get('reliability', 'N/A'),
                'is_randomized': device.get('is_randomized', False),
                'device_id': device.get('device_id', 'N/A'),
                'device_name': device.get('device_name', 'N/A'),
                'confidence': device.get('fingerprint_confidence', 'N/A'),
                'seen_count': device.get('seen_count', 0),
                'status': device.get('status', 'N/A')
            })
        export_results(export_devices, output_format, filename or f'scan_{network.replace("/", "_")}.{output_format}')

def print_enhanced_results(devices: List[Dict], mac_utils, fp):
    """Imprime resultados enriquecidos com fingerprint"""
    if not devices:
        print("Nenhum dispositivo encontrado")
        return
    
    print("\n" + "=" * 110)
    print(f"{'IP':<16} {'MAC':<20} {'Dispositivo Identificado':<35} {'Confiança':<12} {'Visto'}")
    print("-" * 110)
    
    new_count = 0
    for device in devices:
        if device.get('device_name') and device['device_name'] != 'Unknown':
            name = device['device_name'][:33]
        elif device.get('is_randomized', False):
            name = "📱 Smartphone (desconhecido)"[:33]
        else:
            name = device.get('manufacturer', 'Unknown')[:33]
        
        conf_icon = {
            'high': '✅ ALTA',
            'medium': '⚠️ MÉDIA',
            'low': '❌ BAIXA'
        }.get(device.get('fingerprint_confidence', 'low'), '❓')
        
        if device.get('is_new_device', False):
            name = f"🆕 {name}"
            new_count += 1
        
        print(f"{device.get('ip', 'N/A'):<16} {device.get('mac', 'N/A'):<20} {name:<35} {conf_icon:<12} {device.get('seen_count', 1)}")
    
    print("=" * 110)
    
    randomized = sum(1 for d in devices if d.get('is_randomized', False))
    known = sum(1 for d in devices if not d.get('is_new_device', True))
    
    print(f"\n📊 Total de dispositivos: {len(devices)}")
    print(f"   ✅ Dispositivos conhecidos: {known}")
    print(f"   🆕 Novos dispositivos: {new_count}")
    print(f"   🔄 MACs randomizados: {randomized}")
    
    if new_count > 0:
        print(f"\n💡 Dica: Use --list-devices para ver todos os dispositivos conhecidos")
        print(f"   Use --learn-device <ID> \"Nome\" para nomear um dispositivo")
    
    fp.cleanup_old_sessions()

def export_results(data, format_type: str, filename: str):
    """Exporta resultados para diferentes formatos"""
    exporters = {
        'json': JSONExporter(),
        'csv': CSVExporter(),
        'txt': TXTExporter(),
        'html': HTMLExporter()
    }
    
    exporter = exporters.get(format_type)
    if exporter:
        exporter.export(data, filename)

if __name__ == "__main__":
    main()
