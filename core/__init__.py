"""
Core engine - Interface com módulo C/ASM
"""

import os
import ctypes
from pathlib import Path

class ZNetCore:
    """Wrapper para o motor C/ASM"""
    
    def __init__(self):
        self.lib = None
        self.load_engine()
    
    def load_engine(self):
        """Carrega a biblioteca compartilhada"""
        lib_path = Path(__file__).parent / "libznet_core.so"
        
        if lib_path.exists():
            try:
                self.lib = ctypes.CDLL(str(lib_path))
                self.lib.quick_syn_scan.argtypes = [
                    ctypes.c_char_p,
                    ctypes.POINTER(ctypes.c_int),
                    ctypes.c_int,
                    ctypes.c_int
                ]
                self.lib.quick_syn_scan.restype = ctypes.POINTER(ScanResult)
                print("✅ Motor C/ASM carregado com sucesso!")
                return True
            except Exception as e:
                print(f"⚠️ Falha ao carregar motor C: {e}")
        
        print("⚠️ Motor C/ASM não disponível, usando fallback Python")
        return False
    
    def syn_scan(self, ip: str, ports: list, timeout_ms: int = 1000):
        """Scan SYN usando motor C"""
        if not self.lib:
            return None
        
        ports_array = (ctypes.c_int * len(ports))(*ports)
        result_ptr = self.lib.quick_syn_scan(
            ip.encode(),
            ports_array,
            len(ports),
            timeout_ms
        )
        
        # Converte resultados
        results = []
        for i, port in enumerate(ports):
            result = result_ptr[i]
            results.append({
                'port': port,
                'status': 'open' if result.status == 1 else 'closed',
                'ttl': result.ttl
            })
        
        return results

class ScanResult(ctypes.Structure):
    _fields_ = [
        ("port", ctypes.c_int),
        ("status", ctypes.c_int),
        ("response_time_us", ctypes.c_long),
        ("ttl", ctypes.c_ubyte)
    ]