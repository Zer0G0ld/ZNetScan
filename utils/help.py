"""
Sistema de ajuda interativo para o ZNetScan
"""

from typing import Dict, List

class HelpSystem:
    """Sistema de ajuda com categorias e exemplos"""
    
    @staticmethod
    def show_help(command: str = None):
        """Mostra ajuda formatada"""
        if command and command in COMMANDS:
            HelpSystem._show_command_help(command)
        elif command == 'all':
            HelpSystem._show_all_help()
        else:
            HelpSystem._show_main_help()
    
    @staticmethod
    def _show_main_help():
        """Mostra ajuda principal"""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        🚀 ZNetScan - Sistema de Ajuda                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

📋 COMANDOS PRINCIPAIS:

  🔍 SCAN DE REDE:
    znet --method arp              # Scan rápido (requer sudo)
    znet --method ping             # Scan alternativo (sem sudo)
    znet --network 192.168.0.0/24  # Escanear rede específica

  📊 GERENCIAMENTO DE DISPOSITIVOS:
    znet --list-devices            # Listar todos os dispositivos conhecidos
    znet --learn-device <ID> "Nome" # Nomear um dispositivo
    znet --device-history <ID>     # Ver histórico completo
    znet --forget-device <ID>      # Remover dispositivo

  🔌 SCAN DE PORTAS:
    znet --port-scan <IP>          # Escanear portas comuns
    znet --port-scan <IP> --ports 22,80,443  # Portas específicas
    znet --port-scan <IP> --ports range:1-1000  # Intervalo

  ℹ️  INFORMAÇÕES:
    znet --interfaces              # Mostrar interfaces de rede
    znet --mac-info <MAC>          # Analisar um MAC address
    znet help                      # Este menu
    znet help <comando>            # Ajuda específica

  📤 EXPORTAÇÃO:
    znet --method arp --output json -f resultado.json
    znet --method arp --output csv -f resultado.csv
    znet --method arp --output html -f relatorio.html

💡 DICA: Use 'znet help scan' para detalhes sobre scan de rede
       Use 'znet help devices' para gerenciar dispositivos
       Use 'znet help ports' para scan de portas
       Use 'znet help export' para exportação

🔗 Para ajuda completa, visite: https://github.com/Zer0G0ld/ZNetScan
""")
    
    @staticmethod
    def _show_command_help(command: str):
        """Mostra ajuda específica de um comando"""
        if command in COMMANDS:
            print(COMMANDS[command])
        else:
            print(f"\n❌ Comando '{command}' não encontrado")
            print("Use 'znet help' para ver todos os comandos\n")
    
    @staticmethod
    def _show_all_help():
        """Mostra todos os comandos"""
        print("\n" + "=" * 80)
        print("📚 TODOS OS COMANDOS DISPONÍVEIS")
        print("=" * 80)
        
        for cmd_name, cmd_help in COMMANDS.items():
            print(f"\n🔹 {cmd_name.upper()}:")
            print(cmd_help)
            print("-" * 80)


COMMANDS: Dict[str, str] = {
    'scan': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                          🔍 SCAN DE REDE                                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 SINTAXE:
    znet --method <arp|ping> [opções]

📌 PARÂMETROS:
    --method arp      : Scan ARP (rápido, precisa de sudo)
    --method ping     : Scan ICMP (mais lento, não precisa sudo)
    --network CIDR    : Rede a ser escaneada (padrão: 192.168.1.0/24)

📌 EXEMPLOS:
    # Scan rápido com ARP
    sudo znet --method arp

    # Scan ping sem sudo
    znet --method ping

    # Escanear rede específica
    znet --network 192.168.0.0/24 --method arp

📌 SAÍDA:
    O scanner mostra:
    - IP do dispositivo
    - MAC address
    - Fabricante/Identificação
    - Confiabilidade (ALTA/BAIXA para MACs randomizados)
    - Quantas vezes o dispositivo foi visto

📌 DICAS:
    ✅ Use ARP para resultados rápidos e completos
    ✅ O próprio dispositivo não aparece na lista (é a origem)
    ✅ MACs com segundo caractere 2,6,A,E são randomizados (não confiáveis)
""",
    
    'devices': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                      📱 GERENCIAMENTO DE DISPOSITIVOS                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 COMANDOS:

    1. LISTAR DISPOSITIVOS:
       znet --list-devices
       
       Mostra todos os dispositivos já identificados, incluindo:
       - ID único do dispositivo
       - Nome atribuído
       - Quantas vezes foi visto
       - Últimos MAC e IP

    2. NOMEAR DISPOSITIVO:
       znet --learn-device <ID> "Nome do Dispositivo"
       
       Exemplo:
       znet --learn-device dev_20260425_123456 "Celular da Maria"

    3. VER HISTÓRICO:
       znet --device-history <ID>
       
       Mostra:
       - Todos os MACs já usados (útil para randomizados)
       - Todos os IPs já usados
       - Horários mais ativos
       - Contagem total de aparições

    4. REMOVER DISPOSITIVO:
       znet --forget-device <ID>
       
       Remove o dispositivo do banco de dados.

📌 EXEMPLO PRÁTICO:
    # 1. Faça um scan
    znet --method arp
    
    # 2. Veja os IDs
    znet --list-devices
    
    # 3. Nomeie os dispositivos
    znet --learn-device dev_20260425_222407_0 "Roteador"
    znet --learn-device dev_20260425_222407_1 "PC João"
    
    # 4. Veja o histórico de um dispositivo randomizado
    znet --device-history dev_20260425_222407_4

📌 POR QUE USAR?
    Dispositivos modernos (iPhone, Android) mudam de MAC a cada rede.
    O fingerprint identifica que é o mesmo dispositivo mesmo com MAC diferente!
""",
    
    'ports': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                          🔌 SCAN DE PORTAS                                ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 SINTAXE:
    znet --port-scan <IP> [opções]

📌 PARÂMETROS:
    --port-scan <IP>   : Endereço IP alvo
    --ports            : Portas a escanear (comum, lista ou intervalo)

📌 EXEMPLOS:
    # Scan das portas mais comuns (top 20)
    znet --port-scan 192.168.1.1

    # Portas específicas
    znet --port-scan 192.168.1.1 --ports 22,80,443,3306

    # Intervalo de portas
    znet --port-scan 192.168.1.1 --ports range:1-1000

    # Com saída em JSON
    znet --port-scan 192.168.1.1 --output json -f portas.json

📌 PORTAS TOP 20 MAIS COMUNS:
    21(FTP), 22(SSH), 23(Telnet), 25(SMTP), 53(DNS), 80(HTTP),
    110(POP3), 111(RPC), 135(RPC), 139(NetBIOS), 143(IMAP),
    443(HTTPS), 445(SMB), 993(IMAPS), 995(POP3S), 1433(MSSQL),
    3306(MySQL), 3389(RDP), 5900(VNC), 8080(HTTP-ALT)

📌 SAÍDA:
    - Porta: Número da porta
    - Status: open/closed
    - Serviço: Nome do serviço (se conhecido)
    - Banner: Informação do serviço (se obtida)
""",
    
    'export': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                          📤 EXPORTAÇÃO DE RESULTADOS                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 SINTAXE:
    znet --method arp --output <formato> -f <arquivo>

📌 FORMATOS SUPORTADOS:
    json   : Formato JSON estruturado (ideal para APIs)
    csv    : Planilha (abre no Excel, LibreOffice)
    html   : Página web formatada
    txt    : Texto simples legível

📌 EXEMPLOS:

    # JSON (para programação)
    znet --method arp --output json -f scan.json

    # CSV (para planilhas)
    znet --method arp --output csv -f scan.csv

    # HTML (para relatórios visuais)
    znet --method arp --output html -f relatorio.html

    # TXT (log simples)
    znet --method arp --output txt -f scan.txt

📌 ESTRUTURA DO JSON:
    {
      "metadata": {
        "export_date": "2026-04-25T22:33:20",
        "total_devices": 8
      },
      "devices": [
        {
          "ip": "192.168.0.1",
          "mac": "3C:58:5D:78:AD:DE",
          "device_name": "Roteador",
          "reliability": "ALTA",
          "seen_count": 45
        }
      ]
    }

📌 DICAS:
    ✅ Use JSON para integrar com outros sistemas
    ✅ Use CSV para análise em planilhas
    ✅ Use HTML para relatórios bonitos
    ✅ Use o nome do arquivo com data: scan_$(date +%Y%m%d).json
""",
    
    'fingerprint': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                    🆔 SISTEMA DE FINGERPRINT                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 O QUE É?
    O fingerprint identifica dispositivos MESMO quando eles mudam de MAC
    (como iPhones e Androids que randomizam o MAC por privacidade)

📌 COMO FUNCIONA?
    O sistema usa múltiplas características:
    1. Padrão do chip Wi-Fi (mesmo com MAC falso)
    2. Comportamento de horários
    3. Histórico de IPs
    4. Padrões de conexão

📌 NÍVEIS DE CONFIANÇA:
    ✅ ALTA   (70%+)  - Mesmo dispositivo com alta certeza
    ⚠️ MÉDIA  (50-70%) - Provavelmente o mesmo
    ❌ BAIXA  (<50%)   - Dispositivo novo ou inconclusivo

📌 COMANDOS RELACIONADOS:
    --list-devices      : Ver todos os dispositivos conhecidos
    --learn-device     : Nomear um dispositivo manualmente
    --device-history   : Ver histórico completo
    --forget-device    : Remover dispositivo

📌 EXEMPLO PRÁTICO:
    # Um iPhone aparece com MAC diferente a cada scan
    # Scan 1: iPhone com MAC 02:F6:E8:0E:1C:3D
    # Scan 2: iPhone com MAC 9A:B2:C5:2C:39:7F
    
    # O fingerprint detecta que é o MESMO dispositivo!
    # O sistema pergunta: "Você quer nomear este dispositivo?"
    
    znet --learn-device dev_xxx "iPhone do João"

📌 BENEFÍCIOS:
    ✅ Identifica dispositivos mesmo com MAC randomizado
    ✅ Cria histórico de comportamentos
    ✅ Aprende com o tempo
    ✅ Sem falsos positivos (múltiplas características)
""",
    
    'mac': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                          🔢 ANÁLISE DE MAC                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 COMANDO:
    znet --mac-info <MAC_ADDRESS>

📌 EXEMPLOS:
    # Analisar MAC de fábrica
    znet --mac-info 3C:58:5D:78:AD:DE

    # Analisar MAC randomizado
    znet --mac-info 02:F6:E8:0E:1C:3D

📌 O QUE MOSTRA:
    - Se o MAC é de fábrica ou randomizado
    - Fabricante (se identificado)
    - Confiabilidade (ALTA/BAIXA)
    - Recomendação de uso
    - Tipo (unicast/multicast/broadcast)

📌 COMO IDENTIFICAR MAC RANDOMIZADO:
    Segundo caractere do MAC:
    0,4,8,C → MAC de FÁBRICA (confiável)
    2,6,A,E → MAC RANDOMIZADO (não confiável)

    Exemplos:
    3C:58:5D → 'C' → Fábrica ✅
    26:BC:9C → '6' → Randomizado ⚠️
    02:F6:E8 → '2' → Randomizado ⚠️

📌 POR QUE ISSO IMPORTA?
    ❌ Não use MAC randomizado como identificador único
    ✅ Use nosso sistema de fingerprint para identificação persistente
""",
    
    'examples': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                          💡 EXEMPLOS PRÁTICOS                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 CENÁRIO 1: DESCOBRIR TODOS OS DISPOSITIVOS DA REDE
    # Com sudo (recomendado)
    sudo znet --method arp
    
    # Sem sudo (alternativa)
    znet --method ping

📌 CENÁRIO 2: IDENTIFICAR DISPOSITIVOS QUE MUDAM DE MAC
    # Faça scans em dias diferentes
    znet --method arp
    # Depois de alguns dias, execute novamente
    znet --method arp
    
    # O fingerprint vai reconhecer os mesmos dispositivos!
    znet --list-devices

📌 CENÁRIO 3: NOMEAR DISPOSITIVOS
    # Veja os IDs
    znet --list-devices
    
    # Nomeie cada um
    znet --learn-device dev_20260425_222407_0 "Roteador"
    znet --learn-device dev_20260425_222407_1 "PC João"
    znet --learn-device dev_20260425_222407_4 "iPhone Maria"

📌 CENÁRIO 4: AUDITORIA DE SEGURANÇA
    # Escaneie portas do servidor
    znet --port-scan 192.168.1.100 --ports 22,80,443,3306
    
    # Exporte para relatório
    znet --port-scan 192.168.1.100 --output html -f auditoria.html

📌 CENÁRIO 5: MONITORAMENTO CONTÍNUO
    # Script para executar a cada hora
    #!/bin/bash
    while true; do
        znet --method arp --output json -f "scan_$(date +%Y%m%d_%H%M).json"
        sleep 3600
    done

📌 CENÁRIO 6: VER HISTÓRICO DE UM DISPOSITIVO
    # Descubra quantas vezes um celular apareceu
    znet --device-history dev_20260425_222407_4
    
    # Veja todos os MACs que ele já usou
    # Veja horários que costuma aparecer
""",
    
    'troubleshoot': """
╔═══════════════════════════════════════════════════════════════════════════╗
║                          🔧 SOLUÇÃO DE PROBLEMAS                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

📌 ERRO: "arp-scan: command not found"
    # Solução: instalar arp-scan
    sudo apt install arp-scan  # Linux
    brew install arp-scan      # macOS

📌 ERRO: "Permission denied" no scan ARP
    # Solução: executar com sudo
    sudo znet --method arp

📌 ERRO: "znet: command not found"
    # Solução: instalar o pacote
    pip install znetscan

📌 ERRO: Scan muito lento
    # Solução: usar método ARP (mais rápido)
    sudo znet --method arp

📌 ERRO: MACs randomizados não identificados
    # Solução: o sistema já identifica automaticamente
    # Verifique com: znet --mac-info <MAC>

📌 ERRO: Dispositivos duplicados no fingerprint
    # Solução: limpar e re-aprender
    znet --list-devices  # veja os IDs
    znet --forget-device <ID>  # remova duplicados

📌 DICA GERAL:
    Sempre use `--help` para ver opções:
    znet --help
"""
}

# Função para criar um script de help interativo
def create_interactive_help():
    """Cria um script de ajuda interativo"""
    help_script = """#!/usr/bin/env python3
\"\"\"
Ajuda interativa do ZNetScan
\"\"\"

import sys
from utils.help import HelpSystem

def main():
    if len(sys.argv) > 1:
        HelpSystem.show_help(sys.argv[1])
    else:
        HelpSystem.show_help()

if __name__ == "__main__":
    main()
"""
    
    with open("znethelp.py", "w") as f:
        f.write(help_script)
    
    import os
    os.chmod("znethelp.py", 0o755)
    print("✅ Script de ajuda interativo criado: znethelp.py")
    print("   Use: python znethelp.py scan")
    print("   Use: python znethelp.py devices")

if __name__ == "__main__":
    create_interactive_help()