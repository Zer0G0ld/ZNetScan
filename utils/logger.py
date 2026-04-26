"""
Sistema de logging para debug e monitoramento
Com suporte a cores, rotação de arquivos e fallback
"""

import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Tenta importar colorama para cores no terminal
try:
    from colorama import init, Fore, Style
    init()  # Inicializa colorama
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Define códigos ANSI manualmente se colorama não estiver disponível
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    
    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        RESET_ALL = '\033[0m'


class ColoredFormatter(logging.Formatter):
    """Formatador personalizado com cores por nível de log"""
    
    # Cores para cada nível
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN + Style.DIM,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        # Salva o nível original
        levelno = record.levelno
        
        # Aplica cor se for console log
        if hasattr(record, 'colored') and record.colored:
            color = self.LEVEL_COLORS.get(levelno, Fore.WHITE)
            record.levelname = f"{color}{record.levelname}{Fore.RESET}"
            
            # Cor para mensagem de erro
            if levelno >= logging.ERROR:
                record.msg = f"{Fore.RED}{record.msg}{Fore.RESET}"
            elif levelno == logging.WARNING:
                record.msg = f"{Fore.YELLOW}{record.msg}{Fore.RESET}"
            elif levelno == logging.INFO:
                record.msg = f"{Fore.GREEN}{record.msg}{Fore.RESET}"
        
        return super().format(record)


def setup_logger(name: str = "NetworkScanner", level=logging.INFO, 
                 log_dir: str = "logs", max_bytes: int = 10485760, 
                 backup_count: int = 5) -> logging.Logger:
    """
    Configura e retorna um logger profissional
    
    Args:
        name: Nome do logger
        level: Nível de logging para console
        log_dir: Diretório para armazenar logs
        max_bytes: Tamanho máximo do arquivo de log (padrão 10MB)
        backup_count: Número de backups mantidos (padrão 5)
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Base level mais baixo
    
    # Evita múltiplos handlers
    if logger.handlers:
        return logger
    
    # Formato base do log
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler para console (com cores)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo com rotação e fallback
    try:
        # Cria diretório de logs se não existir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Nome do arquivo de log (diário)
        log_filename = os.path.join(log_dir, f"scanner_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Handler com rotação (evita arquivos infinitos)
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Log de sucesso na criação do arquivo (apenas debug)
        logger.debug(f"Arquivo de log criado: {log_filename}")
        
    except Exception as e:
        # Fallback: se não conseguir criar arquivo, loga no console
        logger.warning(f"Não foi possível criar arquivo de log: {e}")
        logger.warning("Logs serão salvos apenas no console")
    
    # Handler opcional para erros críticos (arquivo separado)
    try:
        error_log_filename = os.path.join(log_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
        error_handler = RotatingFileHandler(
            error_log_filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
    except Exception:
        pass  # Silencia falha no handler de erro
    
    return logger


def get_logger_with_context(name: str, context: dict = None) -> logging.Logger:
    """
    Retorna logger com contexto adicional (ex: IP, dispositivo)
    
    Args:
        name: Nome do logger
        context: Dicionário com informações de contexto
        
    Returns:
        Logger configurado
    """
    logger = setup_logger(name)
    
    if context:
        # Adiciona adapter para incluir contexto automaticamente
        class ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                context_str = " ".join(f"{k}={v}" for k, v in self.extra.items())
                return f"[{context_str}] {msg}", kwargs
        
        return ContextAdapter(logger, context)
    
    return logger


def log_execution_time(logger):
    """
    Decorator para logar tempo de execução de funções
    
    Uso:
        @log_execution_time(logger)
        def minha_funcao():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = datetime.now()
            result = func(*args, **kwargs)
            end = datetime.now()
            duration = (end - start).total_seconds()
            logger.debug(f"{func.__name__} executado em {duration:.2f} segundos")
            return result
        return wrapper
    return decorator


# Exemplo de uso
if __name__ == "__main__":
    # Teste do logger
    logger = setup_logger("TestLogger", level=logging.DEBUG)
    
    logger.debug("Mensagem de debug (só vai para o arquivo)")
    logger.info("✅ Informação importante")
    logger.warning("⚠️ Aviso: algo pode estar errado")
    logger.error("❌ Erro aconteceu")
    
    # Teste do logger com contexto
    ctx_logger = get_logger_with_context("ScanLogger", {"ip": "192.168.1.1", "device": "router"})
    ctx_logger.info("Iniciando scan")
    
    # Teste do decorator
    @log_execution_time(logger)
    def teste_demorado():
        import time
        time.sleep(1)
    
    teste_demorado()
    
    print("\n✅ Logger testado! Verifique a pasta 'logs/'")