"""
Formatadores para saída de dados com identificação de MAC randomizado
"""

from typing import List, Dict

class ConsoleFormatter:
    """Formata saída para console"""
    
    @staticmethod
    def print_table(devices: List[Dict], mac_utils=None):
        """
        Imprime tabela formatada no console com detecção de MAC randomizado
        
        Args:
            devices: Lista de dispositivos
            mac_utils: Instância de MACUtils para análise (opcional)
        """
        if not devices:
            print("Nenhum dispositivo encontrado")
            return
        
        # Enriquece dados com análise de randomização
        if mac_utils:
            for device in devices:
                if 'mac' in device and device['mac']:
                    reliability = mac_utils.get_mac_reliability(device['mac'])
                    device['is_randomized'] = reliability['is_randomized']
                    device['reliability'] = reliability['reliability']
                    
                    # Se for randomizado, adiciona explicação
                    if reliability['is_randomized']:
                        device['manufacturer'] = f"🔄 {device.get('manufacturer', 'Unknown')} (Randomizado)"
        
        # Define cabeçalhos
        headers = ['IP Address', 'MAC Address', 'Manufacturer', 'Reliability', 'Status']
        
        # Calcula larguras
        widths = [len(h) for h in headers]
        for device in devices:
            widths[0] = max(widths[0], len(device.get('ip', '')))
            widths[1] = max(widths[1], len(device.get('mac', '')))
            widths[2] = max(widths[2], len(device.get('manufacturer', '')))
            widths[3] = max(widths[3], len(device.get('reliability', '')))
            widths[4] = max(widths[4], len(device.get('status', '')))
        
        # Imprime cabeçalho
        print("\n" + "=" * (sum(widths) + 9))
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {header:<{widths[i]}} |"
        print(header_line)
        print("-" * (sum(widths) + 9))
        
        # Imprime dispositivos
        randomized_count = 0
        for device in devices:
            line = "|"
            line += f" {device.get('ip', 'N/A'):<{widths[0]}} |"
            line += f" {device.get('mac', 'N/A'):<{widths[1]}} |"
            
            # Manufacturer com indicador visual
            manufacturer = device.get('manufacturer', 'N/A')
            if device.get('is_randomized', False):
                manufacturer = f"⚠️ {manufacturer}"
                randomized_count += 1
            
            line += f" {manufacturer:<{widths[2]}} |"
            line += f" {device.get('reliability', 'N/A'):<{widths[3]}} |"
            line += f" {device.get('status', 'N/A'):<{widths[4]}} |"
            print(line)
        
        print("=" * (sum(widths) + 9))
        print(f"\n📊 Total de dispositivos: {len(devices)}")
        
        if randomized_count > 0:
            print(f"⚠️  Dispositivos com MAC Randomizado: {randomized_count}")
            print("💡 Estes dispositivos usam MACs temporários (Android/iOS). Não são confiáveis como ID único.")
        
        # Estatísticas adicionais
        if mac_utils:
            high_reliability = sum(1 for d in devices if d.get('reliability') == 'ALTA')
            low_reliability = sum(1 for d in devices if d.get('reliability') == 'BAIXA')
            
            print(f"\n🔒 Confiabilidade dos MACs:")
            print(f"   ✅ Alta (Hardware/Fábrica): {high_reliability}")
            print(f"   ⚠️  Baixa (Randomizado/Software): {low_reliability}")
    
    @staticmethod
    def print_detailed(device: Dict, mac_utils=None):
        """
        Imprime informações detalhadas de um dispositivo específico
        
        Args:
            device: Dicionário do dispositivo
            mac_utils: Instância de MACUtils para análise
        """
        print("\n" + "=" * 60)
        print("📡 INFORMAÇÕES DETALHADAS DO DISPOSITIVO")
        print("=" * 60)
        
        print(f"\n🌐 IP Address: {device.get('ip', 'N/A')}")
        print(f"🔢 MAC Address: {device.get('mac', 'N/A')}")
        
        if mac_utils and 'mac' in device:
            reliability = mac_utils.get_mac_reliability(device['mac'])
            print(f"\n🔍 Análise do MAC:")
            print(f"   📌 {reliability['explanation']}")
            print(f"   🎯 Confiabilidade: {reliability['reliability']}")
            print(f"   💡 Recomendação: {reliability['recommendation']}")
        
        print(f"\n🏭 Fabricante: {device.get('manufacturer', 'N/A')}")
        print(f"📊 Status: {device.get('status', 'N/A')}")
        
        # Informações adicionais se disponíveis
        if 'type' in device:
            print(f"📱 Tipo: {device['type']}")
        if 'certainty' in device:
            print(f"🎲 Certeza: {device['certainty']}")
        
        print("\n" + "=" * 60)
    
    @staticmethod
    def print_simple(devices: List[Dict]):
        """Imprime formato simples"""
        for device in devices:
            mac_info = ""
            if 'is_randomized' in device:
                mac_info = " [RANDOMIZADO]" if device['is_randomized'] else " [FÁBRICA]"
            print(f"IP: {device['ip']} | MAC: {device['mac']}{mac_info} | {device.get('manufacturer', 'N/A')}")