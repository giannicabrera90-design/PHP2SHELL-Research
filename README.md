# PHP2SHELL Research Harness

Framework de investigación académica y análisis de bajo nivel enfocado en vulnerabilidades de corrupción de memoria en el core del motor de PHP (**CVE-2026-109618 / CVE-2026-109619**).

## ⚠️ Aviso Legal y de Seguridad
Este repositorio se publica exclusivamente con **fines educativos y de investigación defensiva** en entornos de laboratorio aislados. Está prohibido ejecutar estas herramientas contra sistemas de producción o servidores sin autorización explícita.

---

## 🏛️ Descripción del Proyecto
A diferencia de las vulnerabilidades tradicionales en frameworks web o aplicaciones de terceros, **PHP2SHELL** explota fallas en la gestión de memoria dinámica (*heap*) del intérprete de PHP en lenguaje C. 

Este harness implementa de manera estricta:
1. **Inducción OOM quirúrgica** mediante el subsistema nativo `session.upload_progress`.
2. **Persistencia de sockets Keep-Alive** para evitar la destrucción limpia del proceso worker de PHP-FPM.
3. **Heap Spraying controlado** para evaluar la persistencia de estados globales obsoletos (*stale global state*) y la divulgación de punteros internos.

---

## 📁 Estructura del Repositorio
```text
PHP2SHELL-Research/
├── README.md
├── harness/
│   ├── trigger_oom.py     # Fase 1: Saturación y generación del dangling pointer
│   └── heap_inspect.py    # Fase 2: Reutilización de socket, heap spray e info leak
└── environment/
    ├── Dockerfile         # Contenedor de laboratorio con versión vulnerable de PHP
    └── php.ini            # Configuración ajustada de memory_limit y upload_progress
