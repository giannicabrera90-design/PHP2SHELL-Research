PHP2SHELL Research - Análisis y Detección Responsable

Academic research & exposure assessment for CVE-2026-109618 & CVE-2026-109619 ("PHP2Shell").

⚠️ Este repositorio es solo detección defensiva. No contiene payloads (cargas útiles) de RCE, no hace heap spray, no hace session poisoning ni LFI (Local File Inclusion).
El PoC weaponizado completo (trigger OOM + leak + zval spray) se mantiene en laboratorio privado por responsabilidad ética y legal, dado que CISA lo lista como activamente explotado desde el 26 de octubre de 2026.

¿Qué es PHP2Shell? (sin alucinaciones):

Contrario a muchos writeups generados por IA que hablan de "Session Poisoning + LFI", PHP2Shell en realidad explota vulnerabilidades de corrupción de memoria y desbordamiento por OOM (Out-Of-Memory) a nivel del intérprete de PHP, qué son las siguientes:

CVE-2026-109618: Corrupción de memoria mediante un desbordamiento/agotamiento por OOM (Out-Of-Memory) sin autenticación al mismo tiempo en qué los datos internos de una solicitud se encuentran únicamente parcialmente iniciados, qué permite escalar a una ejecución remota de comandos (RCE).
CVE-2026-109619: Use-after-free - el estado de la solicitud sobrevive a memoria liberada al no limpiarse correctamente luego de un error fatal y se reutiliza en el mismo worker (stale global state).

Ambas son vulnerabilidades de memoria en el núcleo de PHP en C, con CVSS v4.0 9.2 Crítico. Permiten RCE (Remote Code Execution) sin tocar el código de la aplicación.

Vector real: PHP_SESSION_UPLOAD_PROGRESS en multipart → OOM (Out-Of-Memory) con la función longjmp() → dangling pointers post_bytes_processed / current_file_bytes_processed → filtración de chunk base (2MB aligned) y libphp base → fake HashTable → RCE (Remote Code Execution) vía zif_system.

Referencias: GHSA-w8hw-w9fx-j79w, GHSA-6wmf-4rv5-p3rp.

Muchos repositorios mezclan la técnica vieja de 2011 (session poisoning + LFI) con el conjunto de exploits PHP2Shell, no se deben confundir ya qué no son lo mismo y operan en capas distintas.

Este repositorio no hace:

❌ Session poisoning + LFI (Local File Inclusion).
❌ Deserialización con handler mismatch.
❌ Heap spray / zval spray / RCE (Remote Code Execution).

Sí hace:

✅ Detección de versión de PHP.
✅ Veredicto vulnerable, parcheado o desconocido con los builds fijos 8.2.35, 8.3.36, 8.4.27 y 8.5.12.
✅ Correlación con CISA KEV / EPSS (opcional).

Versiones afectadas:

Vulnerables: PHP 5.4.0 - 8.5.11.

Versiones parcheadas: PHP 8.5.12, 8.4.27, 8.3.36, 8.2.35 (21 Oct 2026).

EOL (End of Life) ≤8.1: Vulnerable sin parches oficiales.

Mitigación temporal (por si no se puede migrar rápidamente): session.upload_progress.enabled=0 + reinicio de todos los workers PHP-FPM / Apache.

Uso de la herramienta de detección:

python3 php2shell_check.py https://tu-objetivo.local

python3 php2shell_check.py -i urls.txt --format json

Disclaimer:

Solo para sistemas propios (como máquinas virtuales o laboratorios) o con autorización explícita. No realiza ejecución de código real.

