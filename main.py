#!/usr/bin/env python3
"""
Network Scanner - Ferramenta modular para escaneamento de rede
Versão completa com todos os módulos
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
    """Mostra informações detalhadas de um MAC"""
    mac_utils = MACUtils()
    info = mac_utils.get_vendor_info(mac_address)
    
    print("\n" + "=" * 50)
    print("INFORMAÇÕES DO MAC ADDRESS")
    print("=" * 50)
    print(f"Original: {info['mac']}")
    print(f"Normalizado: {info['normalized']}")
    print(f"OUI: {info['oui']}")
    print(f"Fabricante: {info['manufacturer']}")
    print(f"Tipo: {info['type']}")
    print(f"Multicast: {info['is_multicast']}")
    print(f"Broadcast: {info['is_broadcast']}")
    print(f"Unicast: {info['is_unicast']}")

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
    """Executa scan de rede"""
    # Escolhe o scanner
    if method == 'arp':
        scanner = ARPScanner()
    else:
        scanner = PingScanner()
    
    # Executa o scan
    print(f"Escaneando rede {network} usando {method}...")
    devices = scanner.scan(network)
    
    # Saída no console
    if output_format == 'console':
        formatter = ConsoleFormatter()
        formatter.print_table(devices)
    
    # Exporta resultados
    if output_format != 'console':
        export_results(devices, output_format, filename or f'scan_{network.replace("/", "_")}.{output_format}')

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