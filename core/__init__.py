"""
Core engine - Interface com módulo C/ASM
Suporte multi-arquitetura: x86_64 e ARM64 (aarch64/arm64)
"""

import os
import sys
import ctypes
import platform
from pathlib import Path

class ScanResult(ctypes.Structure):
    _fields_ = [
        ("port", ctypes.c_int),
        ("status", ctypes.c_int),
        ("response_time_us", ctypes.c_long),
        ("ttl", ctypes.c_ubyte)
    ]

class ZNetCore:
    """Wrapper para o motor C/ASM multi-arquitetura"""

    def __init__(self):
        self.lib = None
        self.arch = platform.machine()
        self.load_engine()

    def load_engine(self):
        """Carrega a biblioteca compartilhada apropriada para a arquitetura"""
        
        # Caminho da biblioteca
        lib_path = Path(__file__).parent / "libznet_core.so"
        
        # Verifica se existe
        if not lib_path.exists():
            print(f"⚠️ Biblioteca não encontrada: {lib_path}")
            print(f"   Execute 'make' na pasta core/")
            print(f"   Arquitetura atual: {self.arch}")
            return False
        
        # Verifica compatibilidade da arquitetura
        try:
            # Tenta carregar
            self.lib = ctypes.CDLL(str(lib_path))
            
            # Configura a função exportada
            self.lib.quick_syn_scan.argtypes = [
                ctypes.c_char_p,
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_int,
                ctypes.c_int
            ]
            self.lib.quick_syn_scan.restype = ctypes.POINTER(ScanResult)
            
            print(f"✅ Motor C/ASM carregado com sucesso!")
            print(f"   Arquitetura: {self.arch}")
            return True
            
        except Exception as e:
            print(f"❌ Falha ao carregar motor C: {e}")
            print(f"   Possível incompatibilidade de arquitetura")
            print(f"   Esperado: {self.arch}")
            return False

    def syn_scan(self, ip: str, ports: list, timeout_ms: int = 1000):
        """Scan SYN usando motor C (requer root/permissões)"""
        if not self.lib:
            print("⚠️ Motor C não disponível, use fallback Python")
            return None

        # Converte lista de ports para array C
        ports_array = (ctypes.c_int * len(ports))(*ports)
        
        # Chama a função C
        result_ptr = self.lib.quick_syn_scan(
            ip.encode('utf-8'),
            ports_array,
            len(ports),
            timeout_ms
        )

        if not result_ptr:
            return None

        # Converte resultados para Python
        results = []
        for i in range(len(ports)):
            result = result_ptr[i]
            results.append({
                'port': result.port,
                'status': 'open' if result.status == 1 else 'closed',
                'response_time_us': result.response_time_us,
                'ttl': result.ttl
            })

        return results

    def is_available(self):
        """Verifica se o motor C está disponível"""
        return self.lib is not None

# Teste rápido se executado diretamente
if __name__ == "__main__":
    print("Testando ZNetCore...")
    core = ZNetCore()
    if core.is_available():
        print("✅ Core disponível")
    else:
        print("❌ Core não disponível")