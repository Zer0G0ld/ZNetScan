"""
Módulos para exportar resultados em diferentes formatos
"""

import json
import csv
from typing import List, Dict
from datetime import datetime
from pathlib import Path

class JSONExporter:
    """Exporta resultados para formato JSON"""
    
    def __init__(self):
        self.format = 'json'
    
    def export(self, data: List[Dict], filename: str = None) -> str:
        """
        Exporta dados para arquivo JSON
        
        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo criado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scan_export_{timestamp}.json"
        
        # Prepara dados com metadados
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_devices': len(data),
                'format': self.format
            },
            'devices': data
        }
        
        # Salva arquivo
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Dados exportados para: {filepath.absolute()}")
        return str(filepath)
    
    def export_simple(self, data: List[Dict], filename: str = None) -> str:
        """Exporta versão simplificada (apenas dados brutos)"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scan_simple_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Dados exportados para: {filename}")
        return filename

class CSVExporter:
    """Exporta resultados para formato CSV"""
    
    def __init__(self):
        self.format = 'csv'
    
    def export(self, data: List[Dict], filename: str = None) -> str:
        """
        Exporta dados para arquivo CSV
        
        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo criado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scan_export_{timestamp}.csv"
        
        if not data:
            print("Nenhum dado para exportar")
            return ""
        
        # Obtém todas as chaves possíveis
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        # Escreve CSV
        filepath = Path(filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✓ Dados exportados para: {filepath.absolute()}")
        return str(filepath)
    
    def export_with_metadata(self, data: List[Dict], filename: str = None) -> str:
        """Exporta CSV com metadados em linhas separadas"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scan_metadata_{timestamp}.csv"
        
        filepath = Path(filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Metadados
            writer.writerow(['# Export Date:', datetime.now().isoformat()])
            writer.writerow(['# Total Devices:', len(data)])
            writer.writerow(['#'] * 5)
            writer.writerow([])
            
            # Dados
            if data:
                fieldnames = list(data[0].keys())
                writer.writerow(fieldnames)
                for item in data:
                    writer.writerow([item.get(field, '') for field in fieldnames])
        
        print(f"✓ Dados exportados para: {filepath.absolute()}")
        return str(filepath)

class TXTExporter:
    """Exporta resultados para formato TXT legível"""
    
    def __init__(self):
        self.format = 'txt'
    
    def export(self, data: List[Dict], filename: str = None) -> str:
        """
        Exporta dados para arquivo TXT formatado
        
        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo criado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scan_export_{timestamp}.txt"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE SCAN DE REDE\n")
            f.write("=" * 80 + "\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de dispositivos: {len(data)}\n")
            f.write("-" * 80 + "\n\n")
            
            # Dispositivos
            for i, device in enumerate(data, 1):
                f.write(f"Dispositivo {i}:\n")
                for key, value in device.items():
                    f.write(f"  {key.upper()}: {value}\n")
                f.write("\n" + "-" * 40 + "\n\n")
        
        print(f"✓ Dados exportados para: {filepath.absolute()}")
        return str(filepath)

class HTMLExporter:
    """Exporta resultados para formato HTML"""
    
    def export(self, data: List[Dict], filename: str = None) -> str:
        """
        Exporta dados para arquivo HTML
        
        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo criado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"scan_export_{timestamp}.html"
        
        # HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Network Scan Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                h1 {{
                    color: #333;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    background-color: white;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .metadata {{
                    background-color: white;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <h1>Network Scan Report</h1>
            
            <div class="metadata">
                <strong>Export Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>Total Devices:</strong> {len(data)}
            </div>
            
            <table>
                <thead>
                    <tr>
        """
        
        # Cabeçalhos da tabela
        if data:
            for key in data[0].keys():
                html += f"<th>{key.upper()}</th>"
            html += "</tr>\n</thead>\n<tbody>\n"
            
            # Dados
            for device in data:
                html += "<tr>\n"
                for value in device.values():
                    html += f"<td>{value}</td>\n"
                html += "</tr>\n"
        
        html += """
            </tbody>
            </table>
            <div class="footer">
                Generated by Network Scanner Tool
            </div>
        </body>
        </html>
        """
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Relatório HTML gerado: {filepath.absolute()}")
        return str(filepath)