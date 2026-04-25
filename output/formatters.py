"""
Formatadores para saída de dados
"""

from typing import List, Dict

class ConsoleFormatter:
    """Formata saída para console"""
    
    @staticmethod
    def print_table(devices: List[Dict]):
        """Imprime tabela formatada no console"""
        if not devices:
            print("Nenhum dispositivo encontrado")
            return
        
        # Define cabeçalhos
        headers = ['IP Address', 'MAC Address', 'Manufacturer', 'Status']
        
        # Calcula larguras
        widths = [len(h) for h in headers]
        for device in devices:
            widths[0] = max(widths[0], len(device.get('ip', '')))
            widths[1] = max(widths[1], len(device.get('mac', '')))
            widths[2] = max(widths[2], len(device.get('manufacturer', '')))
            widths[3] = max(widths[3], len(device.get('status', '')))
        
        # Imprime cabeçalho
        print("\n" + "=" * (sum(widths) + 9))
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {header:<{widths[i]}} |"
        print(header_line)
        print("-" * (sum(widths) + 9))
        
        # Imprime dispositivos
        for device in devices:
            line = "|"
            line += f" {device.get('ip', 'N/A'):<{widths[0]}} |"
            line += f" {device.get('mac', 'N/A'):<{widths[1]}} |"
            line += f" {device.get('manufacturer', 'N/A'):<{widths[2]}} |"
            line += f" {device.get('status', 'N/A'):<{widths[3]}} |"
            print(line)
        
        print("=" * (sum(widths) + 9))
        print(f"\nTotal de dispositivos: {len(devices)}")
    
    @staticmethod
    def print_simple(devices: List[Dict]):
        """Imprime formato simples"""
        for device in devices:
            print(f"IP: {device['ip']} | MAC: {device['mac']}")