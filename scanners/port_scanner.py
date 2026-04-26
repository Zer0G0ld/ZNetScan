"""
Módulo para escaneamento de portas TCP/UDP
Com suporte a ThreadPoolExecutor, UDP scan e melhorias de performance
"""

import socket
import re
import subprocess
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.service_probes import TCP_PROBES, UDP_PROBES, VERSION_PATTERNS, TTL_OS_MAPPING
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
        
        # Usa os probes do arquivo de configuração
        self.tcp_probes = TCP_PROBES
        self.udp_probes = UDP_PROBES
        self.version_patterns = VERSION_PATTERNS
        
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
            'response_time': None,
            'version': None
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
                banner = self._get_banner_tcp(sock, port)
                # Dentro de scan_port_tcp, depois de obter o banner
                if banner:
                    result['banner'] = banner[:200]
                    # Tenta extrair versão
                    version = self._extract_version(result['service'], banner)
                    if version:
                        result['version'] = version
                        result['service_detailed'] = f"{result['service']} {version}"
                    
                    # NOVO: Análise da resposta HTTP
                    if result['service'] == 'HTTP':
                        http_analysis = self._analyze_http_response(banner, result['service'])
                        result['http_analysis'] = http_analysis
                        if http_analysis.get('message'):
                            result['service_detailed'] = http_analysis['message']
                    
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

    def _analyze_http_response(self, banner: str, service: str) -> Dict:
        """
        Analisa resposta HTTP para detectar redirecionamentos e serviços especiais
        
        Args:
            banner: Banner do serviço
            service: Nome do serviço detectado
            
        Returns:
            Dicionário com análise detalhada
        """
        analysis = {
            'type': service,
            'redirect': None,
            'needs_auth': False,
            'server': None,
            'message': None
        }
        
        if not banner or service != 'HTTP':
            return analysis
        
        # Verifica redirecionamento 301/302/307/308
        redirect_match = re.search(r'(301|302|307|308).*?Location:\s*(https?://[^\s\r\n]+)', banner, re.IGNORECASE)
        if redirect_match:
            analysis['type'] = 'redirect'
            analysis['redirect'] = redirect_match.group(2)
            analysis['message'] = f"🔀 Redireciona para {analysis['redirect']}"
            return analysis
        
        # Verifica necessidade de autenticação
        if re.search(r'401 Unauthorized|403 Forbidden', banner, re.IGNORECASE):
            analysis['type'] = 'auth_required'
            analysis['needs_auth'] = True
            analysis['message'] = '🔒 Requer autenticação'
            return analysis
        
        # Verifica erro do servidor
        if re.search(r'501 Not Implemented|500 Internal Server Error', banner, re.IGNORECASE):
            analysis['type'] = 'special_service'
            analysis['message'] = '⚠️ Serviço não padrão (possível API ou dispositivo embarcado)'
            return analysis
        
        # Extrai servidor
        server_match = re.search(r'Server:\s*([^\r\n]+)', banner, re.IGNORECASE)
        if server_match:
            analysis['server'] = server_match.group(1).strip()
            if 'upnp' in analysis['server'].lower() or 'miniupnp' in analysis['server'].lower():
                analysis['type'] = 'upnp'
                analysis['message'] = '🌐 UPnP - Serviço de descoberta de rede'
            elif 'router' in analysis['server'].lower() or 'gateway' in analysis['server'].lower():
                analysis['type'] = 'router_admin'
                analysis['message'] = '📡 Painel administrativo do roteador'
        
        return analysis
    
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
            
            # Verifica se tem probe específico para UDP
            service_name = self.common_ports.get(port, '').split('-')[0].upper()
            probe = self.udp_probes.get(service_name, [b'\x00\x00'])[0]
            
            start_time = datetime.now()
            sock.sendto(probe, (ip, port))
            
            try:
                data, addr = sock.recvfrom(1024)
                end_time = datetime.now()
                result['status'] = 'open'
                result['response_time'] = round((end_time - start_time).total_seconds() * 1000, 2)
                if data:
                    banner = data[:200].decode('utf-8', errors='ignore')
                    result['banner'] = ''.join(c for c in banner if c.isprintable() or c in '\n\r\t')
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
    
    def _get_banner_tcp(self, sock: socket.socket, port: int) -> Optional[str]:
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
            probes = self.tcp_probes.get(service, [
                b'\r\n',
                b'HEAD / HTTP/1.0\r\n\r\n',
                b'HELP\r\n',
                b'QUIT\r\n',
                b'INFO\r\n',
                b'STATUS\r\n'
            ])
            
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
    
    def _extract_version(self, service: str, banner: str) -> Optional[str]:
        """
        Extrai versão do serviço a partir do banner
        
        Args:
            service: Nome do serviço
            banner: Banner do serviço
            
        Returns:
            Versão detectada ou None
        """
        patterns = self.version_patterns
        
        # Tenta padrões específicos do serviço
        for pattern_name, pattern in patterns.items():
            if pattern_name.upper() in service.upper() or pattern_name.upper() in banner.upper():
                match = re.search(pattern, banner, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        # Padrões genéricos
        generic_patterns = [
            r'(\d+\.\d+\.\d+)',
            r'(\d+\.\d+)',
            r'version[:\s]+(\d+\.\d+)',
            r'v(\d+\.\d+)',
        ]
        
        for pattern in generic_patterns:
            match = re.search(pattern, banner, re.IGNORECASE)
            if match:
                return match.group(1)
        
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
                        version_info = f" [{result.get('version', '')}]" if result.get('version') else ""
                        print(f"  ✓ Porta {result['port']}/TCP aberta - {result['service']}{version_info}")
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
            return self.scan_ports_tcp(ip, ports, max_workers=50)
        else:
            return self.scan_ports_udp(ip, ports, max_workers=20)
    
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
        
        # OS Detection
        os_info = self.detect_os_by_ttl(ip)
        
        return {
            'ip': ip,
            'timestamp': datetime.now().isoformat(),
            'os_detected': os_info,
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
        report.append("=" * 100)
        report.append(f"RELATÓRIO DE SCAN DE PORTAS {protocol}")
        report.append("=" * 100)
        report.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total de portas escaneadas: {len(scan_results)}")
        report.append(f"Portas abertas: {len([p for p in scan_results if p['status'] == 'open'])}")
        report.append("")
        
        report.append("DETALHES:")
        report.append("-" * 100)
        report.append(f"{'PORTA':<8} {'STATUS':<15} {'SERVIÇO':<20} {'VERSÃO':<12} {'TEMPO(ms)':<10} {'BANNER'}")
        report.append("-" * 100)
        
        for port_info in scan_results:
            # CORREÇÃO: trata banner None
            banner = port_info.get('banner', 'N/A')
            if banner is None:
                banner = 'N/A'
            elif len(banner) > 30:
                banner = banner[:27] + "..."
            
            response_time = port_info.get('response_time', 'N/A')
            if response_time and response_time != 'N/A':
                response_time = f"{response_time}ms"
            else:
                response_time = 'N/A'
            
            version = port_info.get('version', '-')
            if version is None:
                version = '-'
            else:
                version = str(version)[:10]
            
            report.append(
                f"{port_info['port']:<8} "
                f"{port_info['status']:<15} "
                f"{port_info['service'][:20]:<20} "
                f"{version:<12} "
                f"{str(response_time):<10} "
                f"{banner}"
            )
        
        report.append("=" * 100)
        
        # Adiciona resumo de serviços
        open_ports = [p for p in scan_results if p['status'] == 'open']
        # Adiciona resumo de serviços (parte modificada)
        if open_ports:
            report.append("\n📊 RESUMO DE SERVIÇOS IDENTIFICADOS:")
            for port_info in open_ports:
                service = port_info['service']
                version = port_info.get('version', '')
                version_str = f" v{version}" if version else ""
                banner = port_info.get('banner', 'Sem banner')
                
                # NOVO: Mostra análise HTTP se disponível
                http_analysis = port_info.get('http_analysis', {})
                if http_analysis.get('message'):
                    service_info = f"{service}{version_str} - {http_analysis['message']}"
                else:
                    service_info = f"{service}{version_str}"
                
                report.append(f"  🔹 Porta {port_info['port']}/{protocol}: {service_info}")
                if banner and banner != 'N/A' and len(str(banner)) > 5:
                    report.append(f"     └─ Banner: {str(banner)[:80]}")
                
                # NOVO: Mostra redirecionamento se houver
                if http_analysis.get('redirect'):
                    report.append(f"     └─ 🔀 Redireciona para: {http_analysis['redirect']}")        
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
    
    def detect_os_by_ttl(self, ip: str) -> Dict:
        """
        Detecta sistema operacional baseado no TTL dos pacotes
        
        Args:
            ip: Endereço IP alvo
            
        Returns:
            Dicionário com SO detectado e confiança
        """
        try:
            # Executa ping para obter TTL
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Extrai TTL da saída
            ttl_match = re.search(r'ttl=(\d+)', result.stdout, re.IGNORECASE)
            
            if ttl_match:
                ttl = int(ttl_match.group(1))
                detected_os = TTL_OS_MAPPING.get(ttl, f'Desconhecido (TTL={ttl})')
                confidence = 'high' if ttl in TTL_OS_MAPPING else 'low'
                
                return {
                    'os': detected_os,
                    'ttl': ttl,
                    'confidence': confidence,
                    'method': 'icmp_ttl'
                }
        except subprocess.TimeoutExpired:
            self.logger.debug(f"Timeout no ping para {ip}")
        except Exception as e:
            self.logger.debug(f"Erro no OS detection: {e}")
        
        return {'os': 'Desconhecido', 'confidence': 'low', 'method': 'none', 'ttl': None}
    
    def scan_advanced(self, ip: str, ports: List[int] = None) -> Dict:
        """
        Scan avançado com detecção de SO e extração de versões
        
        Args:
            ip: Endereço IP alvo
            ports: Lista de portas (opcional, usa top 50 por padrão)
            
        Returns:
            Dicionário com resultados avançados
        """
        if ports is None:
            ports = list(self.common_ports.keys())[:50]  # Top 50 portas
        
        print(f"\n🔬 Scan avançado em {ip}")
        print("-" * 50)
        
        # OS Detection
        os_info = self.detect_os_by_ttl(ip)
        print(f"🖥️  SO Detectado: {os_info['os']} (confiança: {os_info['confidence']})")
        
        # Port Scan
        print(f"\n🔍 Escaneando {len(ports)} portas...")
        results = self.scan_ports_tcp(ip, ports)
        
        # Versões detectadas
        versions = [r for r in results if r.get('version')]
        if versions:
            print(f"\n📌 Versões detectadas:")
            for r in versions:
                print(f"   • {r['service']}: {r['version']}")
        
        return {
            'ip': ip,
            'os': os_info,
            'open_ports': len([r for r in results if r['status'] == 'open']),
            'results': results,
            'versions': versions
        }