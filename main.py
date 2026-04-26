#!/usr/bin/env python3
"""
Network Scanner - Ferramenta modular para escaneamento de rede
Versão completa com todos os módulos e análise de MAC randomizado
"""

import sys
import argparse
from scanners.arp_scanner import ARPScanner
from scanners.ping_scanner import PingScanner
from scanners.port_scanner import PortScanner
from output.formatters import ConsoleFormatter
from output.exporters import JSONExporter, CSVExporter, TXTExporter, HTMLExporter
from utils.logger import setup_logger
from network.interface import NetworkInterface
from network.mac_utils import MACUtils

def main():
    parser = argparse.ArgumentParser(
        description='Network Scanner Tool - Scan IPs, MACs and Ports',
        epilog='Examples:\n'
               '  python main.py --method arp\n'
               '  python main.py --method ping --output json\n'
               '  python main.py --port-scan 192.168.1.1\n'
               '  python main.py --interfaces'
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
    
    args = parser.parse_args()
    
    logger = setup_logger()
    
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
    
    # Network scan (IPs e MACs)
    network_scan(args.network, args.method, args.output, args.filename)

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
    
    # Obtém análise completa incluindo randomização
    info = mac_utils.get_vendor_info(mac_address, include_reliability=True)
    
    print("\n" + "=" * 60)
    print("📡 INFORMAÇÕES DO MAC ADDRESS")
    print("=" * 60)
    print(f"\n🔢 MAC Original: {info['mac']}")
    print(f"📝 MAC Normalizado: {info['normalized']}")
    print(f"🔑 OUI: {info['oui']}")
    
    # Análise de randomização (se disponível)
    if 'is_randomized' in info:
        print(f"\n🔍 ANÁLISE DE CONFIABILIDADE:")
        print(f"   📌 {info['mac_explanation']}")
        print(f"   🎯 Confiabilidade: {info['reliability']}")
        print(f"   💡 Recomendação: {info['recommendation']}")
        print(f"   📱 Tipo: {info['type']}")
    else:
        print(f"\n🏭 Fabricante: {info['manufacturer']}")
        print(f"📊 Tipo MAC: {info['type']}")
        print(f"📡 Multicast: {info['is_multicast']}")
        print(f"📢 Broadcast: {info['is_broadcast']}")
        print(f"🔗 Unicast: {info['is_unicast']}")
    
    print("\n" + "=" * 60)

def port_scan(ip: str, ports_option: str, output_format: str, filename: str):
    """Executa scan de portas"""
    scanner = PortScanner()
    
    # Define portas a escanear
    if ports_option == 'common':
        results = scanner.scan_common_ports(ip)
    elif ports_option.startswith('range:'):
        _, range_str = ports_option.split(':')
        start, end = map(int, range_str.split('-'))
        results = scanner.scan_range(ip, start, end)
    else:
        ports = [int(p.strip()) for p in ports_option.split(',')]
        results = scanner.scan_ports(ip, ports)
    
    # Gera relatório
    report = scanner.generate_report(results)
    print(report)
    
    # Exporta se necessário
    if output_format != 'console':
        export_results(results, output_format, filename or f'port_scan_{ip}.{output_format}')

def network_scan(network: str, method: str, output_format: str, filename: str):
    """Executa scan de rede com análise de MAC randomizado"""
    
    # Inicializa o MACUtils para análise de randomização
    mac_utils = MACUtils()
    
    # Escolhe o scanner
    if method == 'arp':
        scanner = ARPScanner()
    else:
        scanner = PingScanner()
    
    # Executa o scan
    print(f"Escaneando rede {network} usando {method}...")
    devices = scanner.scan(network)
    
    # Enriquece os dispositivos com análise de MAC
    for device in devices:
        if 'mac' in device and device['mac']:
            # Obtém análise completa do MAC
            mac_info = mac_utils.get_vendor_info(device['mac'], include_reliability=True)
            
            # Para MACs randomizados, mostra o tipo identificado
            if mac_info.get('is_randomized', False):
                # Tenta identificar o tipo de dispositivo randomizado
                randomized_type = mac_utils._identify_randomized_device(device['mac'])
                device['manufacturer'] = f"🔄 {randomized_type}"
                device['reliability'] = mac_info['reliability']
                device['is_randomized'] = True
                device['mac_analysis'] = mac_info['mac_explanation']
                device['type'] = mac_info.get('type', 'randomized')
            else:
                # Para MACs de fábrica, mostra o fabricante real
                device['manufacturer'] = mac_info['manufacturer']
                device['reliability'] = mac_info['reliability']
                device['is_randomized'] = False
                device['mac_analysis'] = mac_info['mac_explanation']
                device['type'] = mac_info.get('type', 'hardware')
    
    # Saída no console usando o formatter com análise
    if output_format == 'console':
        formatter = ConsoleFormatter()
        # Passa o mac_utils para o formatter
        formatter.print_table(devices, mac_utils)
    else:
        # Para outros formatos, também mostra no console
        formatter = ConsoleFormatter()
        formatter.print_table(devices, mac_utils)
    
    # Exporta resultados se necessário
    if output_format != 'console':
        # Prepara dados para exportação (remove campos complexos)
        export_devices = []
        for device in devices:
            export_devices.append({
                'ip': device.get('ip', 'N/A'),
                'mac': device.get('mac', 'N/A'),
                'manufacturer': device.get('manufacturer', 'N/A'),
                'reliability': device.get('reliability', 'N/A'),
                'is_randomized': device.get('is_randomized', False),
                'type': device.get('type', 'unknown'),
                'status': device.get('status', 'N/A')
            })
        export_results(export_devices, output_format, filename or f'scan_{network.replace("/", "_")}.{output_format}')

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