"""
Configuração de probes para banner grabbing
"""

# Probes específicos por serviço TCP
TCP_PROBES = {
    'HTTP': [
        b'HEAD / HTTP/1.0\r\n\r\n',
        b'GET / HTTP/1.0\r\n\r\n',
        b'OPTIONS / HTTP/1.0\r\n\r\n'
    ],
    'HTTPS': [
        b'HEAD / HTTP/1.0\r\n\r\n',
        b'GET / HTTP/1.0\r\n\r\n'
    ],
    'SSH': [
        b'SSH-2.0-ZNetScan\r\n',
        b'\n'
    ],
    'SMTP': [
        b'EHLO localhost\r\n',
        b'HELO localhost\r\n',
        b'NOOP\r\n'
    ],
    'FTP': [
        b'USER anonymous\r\n',
        b'HELP\r\n',
        b'FEAT\r\n'
    ],
    'POP3': [
        b'CAPA\r\n',
        b'USER test\r\n',
        b'STAT\r\n'
    ],
    'IMAP': [
        b'CAPABILITY\r\n',
        b'HELP\r\n',
        b'IDLE\r\n'
    ],
    'MySQL': [
        b'\x00\x00\x00\x01\x85\xa2\x1f\x00\x00\x00\x00\x01\x21\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    ],
    'Redis': [
        b'INFO\r\n',
        b'PING\r\n',
        b'COMMAND\r\n'
    ],
    'MongoDB': [
        b'\x39\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xd4\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    ],
    'PostgreSQL': [
        b'\x00\x00\x00\x08\x04\xd2\x16\x2f',
        b'SELECT version();\n'
    ],
    'VNC': [
        b'\x52\x46\x42\x20\x30\x30\x33\x2e\x30\x30\x38',
        b'\x01\x01'
    ],
    'Telnet': [
        b'\xff\xfb\x01\xff\xfb\x03\xff\xfd\x01',
        b'help\r\n'
    ]
}

# Probes específicos por serviço UDP
UDP_PROBES = {
    'DNS': [
        b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01',
    ],
    'SNMP': [
        b'\x30\x2a\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x1d\x02\x02\x00\x00\x02\x01\x00\x02\x01\x00\x30\x0f\x30\x0d\x06\x0a\x2b\x06\x01\x02\x01\x01\x02\x01\x01\x01\x05\x00',
    ],
    'NTP': [
        b'\x1b\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    ],
    'DHCP': [
        b'\x01\x01\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    ],
    'NetBIOS': [
        b'\x81\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    ],
}

# Padrões para extração de versão
VERSION_PATTERNS = {
    'SSH': r'SSH-(\d+\.\d+(?:\.\d+)?)',
    'OpenSSH': r'OpenSSH[_\s](\d+\.\d+(?:\.\d+)?)',
    'Apache': r'Apache/(\d+\.\d+\.\d+)',
    'nginx': r'nginx/(\d+\.\d+\.\d+)',
    'MySQL': r'(\d+\.\d+\.\d+)-',
    'PostgreSQL': r'PostgreSQL (\d+\.\d+)',
    'Redis': r'redis_version:(\d+\.\d+\.\d+)',
    'PHP': r'PHP/(\d+\.\d+\.\d+)',
    'Node.js': r'Node\.js/(\d+\.\d+\.\d+)',
    'Python': r'Python/(\d+\.\d+\.\d+)',
    'IIS': r'Microsoft-IIS/(\d+\.\d+)',
    'Tomcat': r'Apache Tomcat/(\d+\.\d+\.\d+)',
    'Jetty': r'Jetty/(\d+\.\d+\.\d+)',
}

# Mapeamento TTL para SO (valores comuns)
TTL_OS_MAPPING = {
    64: 'Linux/Unix',
    128: 'Windows',
    255: 'Solaris/AIX',
    60: 'FreeBSD',
    64: 'macOS',
    254: 'BSD',
}
