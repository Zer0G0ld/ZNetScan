"""
Consulta de vulnerabilidades (CVE) para serviços identificados
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import setup_logger

class CVELookup:
    """Consulta CVEs conhecidos para serviços e versões"""
    
    def __init__(self, cache_file: str = "cve_cache.json"):
        self.logger = setup_logger()
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Carrega cache de CVEs"""
        try:
            from pathlib import Path
            if Path(self.cache_file).exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_cache(self):
        """Salva cache de CVEs"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass
    
    def query_cve(self, service: str, version: str = None) -> List[Dict]:
        """
        Consulta CVEs para um serviço específico
        
        Args:
            service: Nome do serviço (ex: Apache, nginx, SSH)
            version: Versão do serviço (ex: 2.4.41)
            
        Returns:
            Lista de CVEs encontrados
        """
        cache_key = f"{service}_{version}" if version else service
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        cves = []
        
        try:
            # Usa a API do NVD (National Vulnerability Database)
            base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            
            # Constrói a query
            query = f"{service}"
            if version:
                query += f" {version}"
            
            params = {
                'keywordSearch': query,
                'resultsPerPage': 5
            }
            
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            # Faz a requisição
            req = urllib.request.Request(url, headers={'User-Agent': 'ZNetScan/1.0'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                for vuln in data.get('vulnerabilities', []):
                    cve_data = vuln.get('cve', {})
                    metrics = cve_data.get('metrics', {})
                    
                    # Pega a pontuação CVSS
                    cvss_score = None
                    cvss_severity = None
                    
                    if 'cvssMetricV31' in metrics:
                        cvss = metrics['cvssMetricV31'][0]['cvssData']
                        cvss_score = cvss.get('baseScore')
                        cvss_severity = cvss.get('baseSeverity')
                    
                    cves.append({
                        'id': cve_data.get('id'),
                        'description': cve_data.get('descriptions', [{}])[0].get('value', '')[:200],
                        'cvss_score': cvss_score,
                        'severity': cvss_severity,
                        'published': cve_data.get('published'),
                        'url': f"https://nvd.nist.gov/vuln/detail/{cve_data.get('id')}"
                    })
                    
        except Exception as e:
            self.logger.debug(f"Erro ao consultar CVE para {service}: {e}")
        
        # Cache dos resultados
        self.cache[cache_key] = cves
        self._save_cache()
        
        return cves
    
    def analyze_service(self, service: str, banner: str = None) -> Dict:
        """
        Analisa um serviço e retorna CVEs relevantes
        
        Args:
            service: Nome do serviço
            banner: Banner do serviço para extrair versão
            
        Returns:
            Dicionário com análise de segurança
        """
        # Tenta extrair versão do banner
        version = None
        if banner:
            import re
            # Padrões comuns de versão em banners
            patterns = [
                r'(\d+\.\d+\.\d+)',
                r'(\d+\.\d+)',
                r'version[:\s]+(\d+\.\d+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, banner, re.IGNORECASE)
                if match:
                    version = match.group(1)
                    break
        
        # Consulta CVEs
        cves = self.query_cve(service, version)
        
        # Calcula risco
        risk_level = 'LOW'
        if cves:
            high_cves = [c for c in cves if c.get('severity') == 'HIGH']
            critical_cves = [c for c in cves if c.get('severity') == 'CRITICAL']
            
            if critical_cves:
                risk_level = 'CRITICAL'
            elif high_cves:
                risk_level = 'HIGH'
            else:
                risk_level = 'MEDIUM'
        
        return {
            'service': service,
            'version': version,
            'cves_found': len(cves),
            'risk_level': risk_level,
            'cves': cves[:5],  # Limita a 5 CVEs
            'recommendation': self._get_recommendation(risk_level)
        }
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Retorna recomendação baseada no nível de risco"""
        recommendations = {
            'CRITICAL': '🚨 CRÍTICO! Atualize IMEDIATAMENTE ou isole o serviço!',
            'HIGH': '⚠️ ALTO RISCO! Atualize assim que possível.',
            'MEDIUM': '📌 Risco médio. Considere atualizar na próxima janela.',
            'LOW': '✅ Baixo risco. Mantenha monitorado.'
        }
        return recommendations.get(risk_level, '✅ Sem CVEs conhecidos')
    
    def generate_security_report(self, services: List[Dict]) -> str:
        """
        Gera relatório de segurança baseado nos serviços encontrados
        
        Args:
            services: Lista de serviços com banners
            
        Returns:
            Relatório formatado
        """
        report = []
        report.append("=" * 80)
        report.append("🔒 RELATÓRIO DE SEGURANÇA - ANÁLISE DE VULNERABILIDADES")
        report.append("=" * 80)
        report.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        critical_count = 0
        high_count = 0
        
        for service_info in services:
            service = service_info.get('service', 'unknown')
            banner = service_info.get('banner', '')
            
            analysis = self.analyze_service(service, banner)
            
            if analysis['risk_level'] == 'CRITICAL':
                critical_count += 1
            elif analysis['risk_level'] == 'HIGH':
                high_count += 1
            
            report.append(f"\n📡 SERVIÇO: {service}")
            report.append(f"   Versão detectada: {analysis['version'] or 'Não identificada'}")
            report.append(f"   CVEs conhecidos: {analysis['cves_found']}")
            report.append(f"   Nível de risco: {analysis['risk_level']}")
            report.append(f"   Recomendação: {analysis['recommendation']}")
            
            if analysis['cves']:
                report.append("   Principais CVEs:")
                for cve in analysis['cves'][:3]:
                    report.append(f"     • {cve['id']} - {cve.get('severity', 'N/A')} ({cve.get('cvss_score', 'N/A')})")
                    report.append(f"       {cve['description'][:100]}...")
        
        report.append("")
        report.append("=" * 80)
        report.append("📊 RESUMO:")
        report.append(f"   🔴 Críticos: {critical_count}")
        report.append(f"   🟠 Alto risco: {high_count}")
        report.append("=" * 80)
        
        return "\n".join(report)

if __name__ == "__main__":
    # Teste
    cve = CVELookup()
    
    # Testa consulta
    result = cve.analyze_service("Apache", "Apache/2.4.41")
    print(json.dumps(result, indent=2))
