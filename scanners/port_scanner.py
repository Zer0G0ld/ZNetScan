"""
Módulo para escaneamento de portas TCP/UDP
"""

import socket
import threading
from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import setup_logger
from utils.validators import Validators

class PortScanner:
    """Scanner de portas TCP/UDP"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.open_ports = []
        self.common_ports = {
            20: 'FTP-DATA',
            21: 'FTP',
            22: 'SSH',
            23: 'TELNET',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            111: 'RPC',
            135: 'RPC',
            139: 'NetBIOS',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            993: 'IMAPS',
            995: 'POP3S',
            1433: 'MSSQL',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            8080: 'HTTP-ALT',
            8443: 'HTTPS-ALT',
            27017: 'MongoDB',
        }
        
    def scan_port(self, ip: str, port: int, timeout: float = 1.0) -> Dict:
        """
        Escaneia uma porta específica
        
        Args:
            ip: Endereço IP alvo
            port: Número da porta
            timeout: Timeout em segundos
            
        Returns:
            Dicionário com informações da porta
        """
        result = {
            'port': port,
            'service': self.common_ports.get(port, 'unknown'),
            'status': 'closed',
            'banner': None
        }
        
        try:
            # Tentativa de conexão TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = datetime.now()
            connection = sock.connect_ex((ip, port))
            end_time = datetime.now()
            
            if connection == 0:
                result['status'] = 'open'
                result['response_time'] = (end_time - start_time).total_seconds() * 1000  # ms
                
                # Tenta obter banner (para serviços conhecidos)
                banner = self._get_banner(sock)
                if banner:
                    result['banner'] = banner
                    
            sock.close()
            
        except socket.error as e:
            self.logger.debug(f"Erro ao escanear porta {port}: {e}")
            
        except Exception as e:
            self.logger.error(f"Erro inesperado: {e}")
            
        return result
    
    def _get_banner(self, sock: socket.socket) -> Optional[str]:
        """Tenta obter banner do serviço"""
        try:
            sock.settimeout(2)
            
            # Envia comandos comuns para obter banner
            probes = [
                b'\r\n',
                b'HEAD / HTTP/1.0\r\n\r\n',
                b'HELP\r\n',
                b'QUIT\r\n'
            ]
            
            for probe in probes:
                try:
                    sock.send(probe)
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner:
                        return banner[:200]  # Limita tamanho
                except:
                    continue
                    
        except:
            pass
        
        return None
    
    def scan_ports(self, ip: str, ports: List[int], timeout: float = 1.0, 
                   max_threads: int = 50) -> List[Dict]:
        """
        Escaneia múltiplas portas usando threads
        
        Args:
            ip: Endereço IP alvo
            ports: Lista de portas para escanear
            timeout: Timeout por porta
            max_threads: Número máximo de threads simultâneas
            
        Returns:
            Lista de resultados das portas
        """
        if not Validators.validate_ip(ip):
            self.logger.error(f"IP inválido: {ip}")
            return []
        
        self.logger.info(f"Iniciando scan de portas em {ip}")
        self.open_ports = []
        results = []
        threads = []
        
        # Lock para acesso thread-safe
        lock = threading.Lock()
        
        def scan_worker(port):
            result = self.scan_port(ip, port, timeout)
            with lock:
                results.append(result)
                if result['status'] == 'open':
                    self.open_ports.append(port)
                    print(f"  ✓ Porta {port} aberta - {result['service']}")
        
        # Inicia threads
        for port in ports:
            thread = threading.Thread(target=scan_worker, args=(port,))
            thread.start()
            threads.append(thread)
            
            # Limita threads simultâneas
            if len(threads) >= max_threads:
                for t in threads:
                    t.join()
                threads = []
        
        # Aguarda threads restantes
        for t in threads:
            t.join()
        
        # Ordena por número da porta
        results.sort(key=lambda x: x['port'])
        
        self.logger.info(f"Scan de portas concluído. {len(self.open_ports)} portas abertas")
        return results
    
    def scan_common_ports(self, ip: str) -> List[Dict]:
        """
        Escaneia apenas portas comuns
        
        Args:
            ip: Endereço IP alvo
            
        Returns:
            Lista de portas abertas
        """
        ports = list(self.common_ports.keys())
        print(f"Escaneando {len(ports)} portas comuns em {ip}...")
        return self.scan_ports(ip, ports)
    
    def scan_range(self, ip: str, start_port: int = 1, end_port: int = 1024) -> List[Dict]:
        """
        Escaneia um intervalo de portas
        
        Args:
            ip: Endereço IP alvo
            start_port: Porta inicial
            end_port: Porta final
            
        Returns:
            Lista de portas abertas
        """
        ports = list(range(start_port, end_port + 1))
        print(f"Escaneando intervalo {start_port}-{end_port} em {ip}...")
        return self.scan_ports(ip, ports)
    
    def scan_network_ports(self, network: str, ports: List[int]) -> Dict:
        """
        Escaneia portas em toda a rede
        
        Args:
            network: Rede no formato CIDR
            ports: Lista de portas para escanear
            
        Returns:
            Dicionário com IPs e suas portas abertas
        """
        from network.ip_utils import IPUtils
        
        results = {}
        hosts = IPUtils.get_hosts_in_network(network)
        
        print(f"Escaneando {len(hosts)} hosts na rede {network}")
        
        for ip in hosts:
            print(f"\nEscaneando {ip}:")
            open_ports = self.scan_ports(ip, ports)
            if open_ports:
                results[ip] = open_ports
        
        return results
    
    def generate_report(self, scan_results: List[Dict]) -> str:
        """
        Gera relatório formatado do scan
        
        Args:
            scan_results: Resultados do scan
            
        Returns:
            String com relatório formatado
        """
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE SCAN DE PORTAS")
        report.append("=" * 80)
        report.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total de portas escaneadas: {len(scan_results)}")
        report.append(f"Portas abertas: {len([p for p in scan_results if p['status'] == 'open'])}")
        report.append("")
        
        report.append("DETALHES:")
        report.append("-" * 80)
        report.append(f"{'PORTA':<8} {'STATUS':<10} {'SERVIÇO':<15} {'BANNER'}")
        report.append("-" * 80)
        
        for port_info in scan_results:
            banner = port_info.get('banner', 'N/A')
            if len(banner) > 50:
                banner = banner[:47] + "..."
                
            report.append(
                f"{port_info['port']:<8} "
                f"{port_info['status']:<10} "
                f"{port_info['service']:<15} "
                f"{banner}"
            )
        
        report.append("=" * 80)
        
        # Adiciona resumo de serviços
        if self.open_ports:
            report.append("\nSERVIÇOS IDENTIFICADOS:")
            for port in self.open_ports:
                service = self.common_ports.get(port, 'unknown')
                report.append(f"  - Porta {port}: {service}")
        
        return "\n".join(report)
    
    def quick_scan(self, ip: str) -> List[Dict]:
        """
        Scan rápido das portas mais comuns (top 20)
        
        Args:
            ip: Endereço IP alvo
            
        Returns:
            Lista de portas abertas
        """
        top_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 
                     143, 443, 445, 993, 995, 1433, 3306, 3389, 5900, 8080]
        
        print(f"Scan rápido das 20 portas mais comuns em {ip}...")
        return self.scan_ports(ip, top_ports, max_threads=20)