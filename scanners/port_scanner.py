"""
Módulo para escaneamento de portas TCP/UDP
Com suporte a ThreadPoolExecutor, UDP scan e melhorias de performance
"""

import socket
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import setup_logger
from utils.validators import Validators

class PortScanner:
    """Scanner de portas TCP/UDP com alta performance"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.open_ports = []
        self.scan_results = []
        
        # Banco de dados de portas conhecidas
        self.common_ports = {
            20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'TELNET', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 111: 'RPC', 135: 'RPC',
            139: 'NetBIOS', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
            993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL', 3306: 'MySQL',
            3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
            8080: 'HTTP-ALT', 8443: 'HTTPS-ALT', 27017: 'MongoDB',
        }
        
        # Probes específicos por serviço (banner grabbing avançado)
        self.service_probes = {
            'HTTP': [b'HEAD / HTTP/1.0\r\n\r\n', b'GET / HTTP/1.0\r\n\r\n'],
            'SSH': [b'SSH-2.0-ZNetScan\r\n'],
            'SMTP': [b'EHLO localhost\r\n', b'HELO localhost\r\n'],
            'FTP': [b'USER anonymous\r\n', b'HELP\r\n'],
            'POP3': [b'CAPA\r\n', b'USER test\r\n'],
            'IMAP': [b'CAPABILITY\r\n', b'HELP\r\n'],
            'MySQL': [b'\x00\x00\x00\x01\x85\xa2\x1f\x00\x00\x00\x00\x01\x21\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'],
            'Redis': [b'INFO\r\n', b'PING\r\n'],
            'MongoDB': [b'\x39\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xd4\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'],
        }
        
    def scan_port_tcp(self, ip: str, port: int, timeout: float = 1.0) -> Dict:
        """
        Escaneia uma porta TCP específica
        
        Args:
            ip: Endereço IP alvo
            port: Número da porta
            timeout: Timeout em segundos
            
        Returns:
            Dicionário com informações da porta
        """
        result = {
            'port': port,
            'protocol': 'TCP',
            'service': self.common_ports.get(port, 'unknown'),
            'status': 'closed',
            'banner': None,
            'response_time': None
        }
        
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = datetime.now()
            connection = sock.connect_ex((ip, port))
            end_time = datetime.now()
            
            if connection == 0:
                result['status'] = 'open'
                result['response_time'] = round((end_time - start_time).total_seconds() * 1000, 2)
                
                # Tenta obter banner com probes específicos
                banner = self._get_banner_advanced(sock, port)
                if banner:
                    result['banner'] = banner[:200]  # Limita tamanho
                    
        except socket.timeout:
            self.logger.debug(f"Timeout na porta {port}")
        except socket.error as e:
            self.logger.debug(f"Erro na porta {port}: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado na porta {port}: {e}")
        finally:
            if sock:
                sock.close()
            
        return result
    
    def scan_port_udp(self, ip: str, port: int, timeout: float = 2.0) -> Dict:
        """
        Escaneia uma porta UDP específica
        
        Atenção: Scan UDP é menos confiável pois não há confirmação de conexão.
        Portas abertas podem não responder, e portas fechadas retornam ICMP.
        
        Args:
            ip: Endereço IP alvo
            port: Número da porta
            timeout: Timeout em segundos
            
        Returns:
            Dicionário com informações da porta
        """
        result = {
            'port': port,
            'protocol': 'UDP',
            'service': self.common_ports.get(port, 'unknown'),
            'status': 'unknown',
            'banner': None,
            'response_time': None
        }
        
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            
            # Envia probe vazio (alguns serviços respondem)
            start_time = datetime.now()
            sock.sendto(b'\x00\x00', (ip, port))
            
            try:
                data, addr = sock.recvfrom(1024)
                end_time = datetime.now()
                result['status'] = 'open'
                result['response_time'] = round((end_time - start_time).total_seconds() * 1000, 2)
                if data:
                    result['banner'] = data[:200].decode('utf-8', errors='ignore')
            except socket.timeout:
                # UDP é tricky: timeout pode significar aberto (filtrado) ou fechado
                result['status'] = 'open|filtered'
            except socket.error:
                result['status'] = 'closed'
                
        except Exception as e:
            self.logger.debug(f"Erro UDP na porta {port}: {e}")
        finally:
            if sock:
                sock.close()
            
        return result
    
    def _get_banner_advanced(self, sock: socket.socket, port: int) -> Optional[str]:
        """
        Tenta obter banner usando probes específicos por serviço
        
        Args:
            sock: Socket conectado
            port: Número da porta (para identificar serviço)
            
        Returns:
            Banner do serviço ou None
        """
        try:
            sock.settimeout(3)
            
            # Detecta serviço baseado na porta
            service = self.common_ports.get(port, '').split('-')[0].upper()
            
            # Probes específicos para o serviço
            probes = []
            
            if service in self.service_probes:
                probes = self.service_probes[service]
            else:
                # Probes genéricos
                probes = [
                    b'\r\n',
                    b'HEAD / HTTP/1.0\r\n\r\n',
                    b'HELP\r\n',
                    b'QUIT\r\n',
                    b'INFO\r\n',
                    b'STATUS\r\n'
                ]
            
            # Tenta cada probe
            for probe in probes:
                try:
                    sock.send(probe)
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner and len(banner) > 5:
                        # Limpa caracteres não imprimíveis
                        banner = ''.join(char for char in banner if char.isprintable() or char in '\n\r\t')
                        return banner[:200]
                except (socket.timeout, socket.error, UnicodeDecodeError):
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Erro no banner grabbing: {e}")
            
        return None
    
    def scan_ports_tcp(self, ip: str, ports: List[int], timeout: float = 1.0, 
                       max_workers: int = 100) -> List[Dict]:
        """
        Escaneia múltiplas portas TCP usando ThreadPoolExecutor (mais eficiente)
        
        Args:
            ip: Endereço IP alvo
            ports: Lista de portas para escanear
            timeout: Timeout por porta
            max_workers: Número máximo de threads simultâneas
            
        Returns:
            Lista de resultados das portas
        """
        if not Validators.validate_ip(ip):
            self.logger.error(f"IP inválido: {ip}")
            return []
        
        self.logger.info(f"Iniciando scan TCP em {ip} com {len(ports)} portas")
        self.open_ports = []
        results = []
        
        def scan_worker(port):
            result = self.scan_port_tcp(ip, port, timeout)
            if result['status'] == 'open':
                self.open_ports.append(port)
            return result
        
        # Usa ThreadPoolExecutor para gerenciar as threads automaticamente
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scan_worker, port): port for port in ports}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    if result['status'] == 'open':
                        print(f"  ✓ Porta {result['port']}/TCP aberta - {result['service']}")
                except Exception as e:
                    port = futures[future]
                    self.logger.debug(f"Erro na porta {port}: {e}")
        
        # Ordena por número da porta
        results.sort(key=lambda x: x['port'])
        
        self.logger.info(f"Scan TCP concluído. {len(self.open_ports)} portas abertas")
        return results
    
    def scan_ports_udp(self, ip: str, ports: List[int], timeout: float = 2.0,
                       max_workers: int = 50) -> List[Dict]:
        """
        Escaneia múltiplas portas UDP
        
        Args:
            ip: Endereço IP alvo
            ports: Lista de portas para escanear
            timeout: Timeout por porta
            max_workers: Número máximo de threads simultâneas
            
        Returns:
            Lista de resultados das portas
        """
        if not Validators.validate_ip(ip):
            self.logger.error(f"IP inválido: {ip}")
            return []
        
        self.logger.info(f"Iniciando scan UDP em {ip} com {len(ports)} portas")
        results = []
        udp_open = []
        
        def scan_worker(port):
            return self.scan_port_udp(ip, port, timeout)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scan_worker, port): port for port in ports}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    if result['status'] in ['open', 'open|filtered']:
                        udp_open.append(result['port'])
                        print(f"  ✓ Porta {result['port']}/UDP - {result['status']} - {result['service']}")
                except Exception as e:
                    port = futures[future]
                    self.logger.debug(f"Erro UDP na porta {port}: {e}")
        
        results.sort(key=lambda x: x['port'])
        self.logger.info(f"Scan UDP concluído. {len(udp_open)} portas abertas/filtradas")
        return results
    
    def scan_common_ports(self, ip: str, protocol: str = 'tcp') -> List[Dict]:
        """
        Escaneia apenas portas comuns
        
        Args:
            ip: Endereço IP alvo
            protocol: 'tcp' ou 'udp'
            
        Returns:
            Lista de portas abertas
        """
        ports = list(self.common_ports.keys())
        print(f"Escaneando {len(ports)} portas comuns ({protocol.upper()}) em {ip}...")
        
        if protocol.lower() == 'tcp':
            return self.scan_ports_tcp(ip, ports)
        else:
            return self.scan_ports_udp(ip, ports)
    
    def scan_range(self, ip: str, start_port: int = 1, end_port: int = 1024,
                   protocol: str = 'tcp') -> List[Dict]:
        """
        Escaneia um intervalo de portas
        
        Args:
            ip: Endereço IP alvo
            start_port: Porta inicial
            end_port: Porta final
            protocol: 'tcp' ou 'udp'
            
        Returns:
            Lista de portas abertas
        """
        ports = list(range(start_port, end_port + 1))
        print(f"Escaneando intervalo {start_port}-{end_port} ({protocol.upper()}) em {ip}...")
        
        if protocol.lower() == 'tcp':
            return self.scan_ports_tcp(ip, ports)
        else:
            return self.scan_ports_udp(ip, ports)
    
    def scan_full(self, ip: str, max_workers: int = 100) -> Dict:
        """
        Scan completo: TCP + UDP nas portas comuns
        
        Args:
            ip: Endereço IP alvo
            max_workers: Número máximo de threads
            
        Returns:
            Dicionário com resultados TCP e UDP
        """
        print(f"\n🔍 Iniciando scan completo em {ip}")
        print("=" * 50)
        
        # Scan TCP
        print("\n📡 Scan TCP:")
        tcp_results = self.scan_common_ports(ip, 'tcp')
        
        # Scan UDP
        print("\n📡 Scan UDP:")
        udp_results = self.scan_common_ports(ip, 'udp')
        
        return {
            'ip': ip,
            'timestamp': datetime.now().isoformat(),
            'tcp': tcp_results,
            'udp': udp_results,
            'total_open_tcp': len([r for r in tcp_results if r['status'] == 'open']),
            'total_open_udp': len([r for r in udp_results if r['status'] in ['open', 'open|filtered']])
        }
    
    def generate_report(self, scan_results: List[Dict], protocol: str = 'TCP') -> str:
        """
        Gera relatório formatado do scan
        
        Args:
            scan_results: Resultados do scan
            protocol: Protocolo (TCP/UDP)
            
        Returns:
            String com relatório formatado
        """
        report = []
        report.append("=" * 90)
        report.append(f"RELATÓRIO DE SCAN DE PORTAS {protocol}")
        report.append("=" * 90)
        report.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total de portas escaneadas: {len(scan_results)}")
        report.append(f"Portas abertas: {len([p for p in scan_results if p['status'] == 'open'])}")
        report.append("")
        
        report.append("DETALHES:")
        report.append("-" * 90)
        report.append(f"{'PORTA':<8} {'STATUS':<15} {'SERVIÇO':<15} {'TEMPO(ms)':<10} {'BANNER'}")
        report.append("-" * 90)
        
        for port_info in scan_results:
            banner = port_info.get('banner', 'N/A')
            if len(banner) > 40:
                banner = banner[:37] + "..."
            
            response_time = port_info.get('response_time', 'N/A')
            if response_time:
                response_time = f"{response_time}ms"
            
            report.append(
                f"{port_info['port']:<8} "
                f"{port_info['status']:<15} "
                f"{port_info['service']:<15} "
                f"{str(response_time):<10} "
                f"{banner}"
            )
        
        report.append("=" * 90)
        
        # Adiciona resumo de serviços
        open_ports = [p for p in scan_results if p['status'] == 'open']
        if open_ports:
            report.append("\n📊 RESUMO DE SERVIÇOS IDENTIFICADOS:")
            for port_info in open_ports:
                service = port_info['service']
                banner = port_info.get('banner', 'Sem banner')
                report.append(f"  🔹 Porta {port_info['port']}/{protocol}: {service}")
                if banner and banner != 'N/A':
                    report.append(f"     └─ Banner: {banner[:80]}")
        
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
        
        print(f"⚡ Scan rápido das 20 portas mais comuns em {ip}...")
        return self.scan_ports_tcp(ip, top_ports, max_workers=20)
    
    def scan_port_with_detection(self, ip: str, port: int, timeout: float = 2.0) -> Dict:
        """
        Scan detalhado de uma porta específica com detecção de serviço
        """
        result = self.scan_port_tcp(ip, port, timeout)
        
        if result['status'] == 'open':
            # Tenta identificar versão do serviço
            if result['banner']:
                import re
                # Extrai versão de banners comuns
                version_patterns = {
                    'SSH': r'SSH-(\d+\.\d+)',
                    'Apache': r'Apache/(\d+\.\d+\.\d+)',
                    'nginx': r'nginx/(\d+\.\d+\.\d+)',
                    'OpenSSH': r'OpenSSH[_\s](\d+\.\d+)',
                }
                
                for service, pattern in version_patterns.items():
                    match = re.search(pattern, result['banner'], re.IGNORECASE)
                    if match:
                        result['version'] = match.group(1)
                        result['service_detailed'] = f"{service} {result['version']}"
                        break
        
        return result