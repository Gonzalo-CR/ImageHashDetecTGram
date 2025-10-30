# 🔍 ImageHashDetector

**Versión:** 2.2 - Telegram Edition  
**Autor:** @Gonzalo-CR  
**Licencia:** MIT  
**Estado:** ✅ Funcional y Mejorado con Telegram

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" alt="Python 3.x">
  <img src="https://img.shields.io/badge/Kali_Linux-Avanzado-darkblue?style=for-the-badge&logo=kalilinux" alt="Kali Linux">
  <img src="https://img.shields.io/badge/OSINT-CiberInteligencia-orange?style=for-the-badge" alt="OSINT Tool">
  <img src="https://img.shields.io/badge/Telegram-Integrado-blue?style=for-the-badge&logo=telegram" alt="Telegram Integration">
</p>

## 🌟 ¿Qué es ImageHashDetector?

ImageHashDetector es una herramienta avanzada de ciberinteligencia y OSINT diseñada para detectar imágenes objetivo en sitios web y grupos/canales de Telegram. Utiliza una combinación de hashes perceptuales (pHash, aHash, dHash, wHash) y criptográficos (MD5) para ofrecer resistencia contra técnicas de evasión.

Incluye integración completa con Telegram para monitoreo en tiempo real de grupos y canales, escaneo masivo de historiales, y detección automática de contenido visual sensible.

## 🚀 Características Principales

### 🔐 Detección Multi-Hash Robusta

- 5 tipos de hashes: pHash, aHash, dHash, wHash y MD5
- Resistencia a evasión: Detecta imágenes modificadas, redimensionadas o comprimidas
- Umbral de similitud: Configurable (0-64)
- Verificación cruzada entre múltiples algoritmos

### 📱 Integración Completa con Telegram

- 🔍 **Escaneo de grupos/canales:** Analiza historiales de mensajes en busca de imágenes objetivo
- 👁️ **Monitoreo en tiempo real:** Detecta imágenes nuevas al instante
- 📋 **Escaneo por lotes:** Múltiples grupos simultáneamente
- 🔄 **Exportación automática:** Reportes JSON con timestamp único
- 🔧 **Gestión de sesiones:** Conexión persistente y segura

### 📁 Gestión Completa de Base de Datos

- Agregar imágenes objetivo desde archivo local, URL o Telegram
- Agregar hashes manualmente para casos específicos
- Listar todos los objetivos con sus IDs
- Borrar hash específico por ID
- Limpiar/Resetear base de datos completa

### 📊 Sistema de Reportes Automáticos

- Exportación automática después de cada escaneo
- Formato JSON con timestamp único
- Trazabilidad completa de detecciones
- Nombres únicos: `reporte_scan_YYYYMMDD_HHMMSS.json`, `reporte_telegram_YYYYMMDD_HHMMSS.json`

### 🎯 Modos de Operación Flexibles

- CLI (Línea de Comandos) para automatización
- Menú Interactivo para administración visual
- Escaneo individual de sitios web y grupos Telegram
- Escaneo por lotes desde archivos de texto

## 🛠️ Instalación y Configuración

Asegurate de estar en el directorio de tu proyecto y de tener Python 3.7+ instalado.

### 1. Creación del Entorno Virtual

Es fundamental trabajar dentro de un entorno virtual para aislar las dependencias. Utilizaremos el nombre `cyber_env`.
```bash
# Crear el entorno virtual con python3
python3 -m venv cyber_env

# Activar el entorno
source cyber_env/bin/activate

# El prompt cambia a (cyber_env)...
```

### 2. Instalación de Dependencias

Instalá todas las librerías necesarias con pip:
```bash
(cyber_env) $ pip install pillow imagehash requests beautifulsoup4 telethon
```

📱 **Nota sobre Telethon:** La librería `telethon` es necesaria para las funcionalidades de Telegram.

### 3. Verificación de Instalación

Asegurate de que el script principal se llame `image_hash_detector-TG.py`:
```bash
(cyber_env) $ python image_hash_detector-TG.py --help
```

## 📱 Cómo Usar

### 🎮 Modo Interactivo (Recomendado para Administración)

Inicia el menú interactivo para gestionar la base de datos y realizar escaneos visualmente:
```bash
(cyber_env) $ python image_hash_detector-TG.py --interactive
```

### 📋 Menú Interactivo Completo

| Opción | Descripción | Función |
|--------|-------------|---------|
| [1] | 📷 Agregar imagen objetivo | Añade hashes de una imagen (local o URL) a la DB |
| [2] | #️⃣ Agregar hash manual | Añade un hash específico (ej. phash) manualmente |
| [3] | 🔍 Escanear sitio web | Escanea una URL y exporta automáticamente |
| [4] | 📋 Escanear múltiples sitios | Escanea un archivo de URLs y exporta automáticamente |
| [5] | 🖼️ Verificar imagen específica | Compara una URL de imagen individual con todos los hashes en la DB |
| [6] | 📊 Ver estadísticas | Muestra el recuento de objetivos y el historial de detecciones |
| [7] | 📜 Listar hashes objetivo | Muestra todos los target_ids para gestión |
| [8] | 📱 Funciones de Telegram | Submenú completo para integración con Telegram |
| [9] | 🗑️ Borrar hash por ID | Elimina un hash específico (requiere ID) |
| [10] | 💣 Limpiar/Resetear Base de Datos | Elimina TODOS los hashes (requiere confirmación) |
| [0] | 🚪 Salir | Cierra el programa |

### 📱 Submenú de Telegram

Cuando seleccionas la opción 8 (Funciones de Telegram), accedes a un submenú especializado:

#### 🔌 Estado: No Conectado

- [1] 🔧 Configurar cliente de Telegram
- [0] ↩️ Volver al menú principal

#### ✅ Estado: Conectado

- [1] 🔍 Ver información de conexión
- [2] 📋 Listar grupos/chats disponibles
- [3] 🔍 Escanear grupo específico
- [4] 📋 Escanear múltiples grupos
- [5] 👁️ Monitorear grupo en tiempo real
- [6] 📊 Ver detecciones de Telegram
- [7] 🚪 Desconectar Telegram
- [0] ↩️ Volver al menú principal

### 💻 Modo CLI (Línea de Comandos)

Ideal para scripts y automatización:

| Argumento | Descripción | Ejemplo de Uso |
|-----------|-------------|----------------|
| `--add-image` | Añade una imagen objetivo a la DB | `python image_hash_detector-TG.py --add-image logo.jpg --description "Logo campaña"` |
| `--scan` | URL o archivo con URLs a escanear | `python image_hash_detector-TG.py --scan lista_sitios.txt --threshold 8` |
| `--check-image` | Verifica una única URL de imagen | `python image_hash_detector-TG.py --check-image https://web.com/img.jpg` |
| `--reset-db` | Borra TODA la base de datos | `python image_hash_detector-TG.py --reset-db` |
| `--threshold` | Umbral de similitud (0-64) | `python image_hash_detector-TG.py --scan url.com --threshold 5` |
| `--list` | Lista todos los hashes objetivo | `python image_hash_detector-TG.py --list` |

### 📱 Comandos Específicos de Telegram

| Argumento | Descripción | Ejemplo |
|-----------|-------------|---------|
| `--setup-telegram` | Configurar cliente de Telegram | `python image_hash_detector-TG.py --setup-telegram --api-id 123 --api-hash "abc" --phone "+123456789"` |
| `--telegram-scan` | Escanear grupo/canal | `python image_hash_detector-TG.py --telegram-scan "NombreGrupo" --limit-messages 200` |
| `--telegram-monitor` | Monitoreo en tiempo real | `python image_hash_detector-TG.py --telegram-monitor "CanalImportante"` |
| `--list-groups` | Listar grupos disponibles | `python image_hash_detector-TG.py --list-groups` |
| `--telegram-status` | Ver estado de conexión | `python image_hash_detector-TG.py --telegram-status` |
| `--disconnect-telegram` | Desconectar Telegram | `python image_hash_detector-TG.py --disconnect-telegram` |

## 🚀 Casos de Uso y Automatización

### 📡 Caso 1: Monitoreo Persistente de Sitios Web (Cron/Bucle)

Para establecer un monitoreo continuo que se ejecute cada hora:
```bash
#!/bin/bash

# Activar el entorno virtual
source /ruta/a/tu/proyecto/cyber_env/bin/activate

while true; do
    echo "=== Iniciando escaneo $(date) ==="
    
    # El escaneo genera automáticamente un reporte con timestamp
    python image_hash_detector-TG.py --scan "lista_sitios.txt" --threshold 8
    
    echo "Escaneo completado. Esperando 1 hora..."
    sleep 3600
done
```

Ejecutar en segundo plano:
```bash
(cyber_env) $ chmod +x monitor.sh
(cyber_env) $ nohup ./monitor.sh &
```

### 📱 Caso 2: Monitoreo de Grupos de Telegram en Tiempo Real

Monitorea grupos específicos de Telegram para detectar imágenes objetivo al instante:
```bash
# Configurar Telegram primero (una sola vez)
(cyber_env) $ python image_hash_detector-TG.py --setup-telegram \
  --api-id "TU_API_ID" \
  --api-hash "TU_API_HASH" \
  --phone "+123456789"

# Iniciar monitoreo en tiempo real
(cyber_env) $ python image_hash_detector-TG.py --telegram-monitor "GrupoImportante" --threshold 5
```

Características del monitoreo:

- ✅ Detección en tiempo real de nuevas imágenes
- ✅ Exportación automática al finalizar (Ctrl+C)
- ✅ Umbral de similitud configurable
- ✅ Manejo robusto de errores de conexión

### 🔍 Caso 3: Escaneo Masivo de Historiales de Telegram

Analiza grandes cantidades de mensajes históricos en grupos/canales:
```bash
# Escanear un grupo específico (últimos 500 mensajes)
(cyber_env) $ python image_hash_detector-TG.py --telegram-scan "CanalInvestigacion" --limit-messages 500

# Escanear múltiples grupos desde archivo
(cyber_env) $ echo -e "Grupo1\nGrupo2\nCanal3" > grupos_telegram.txt
(cyber_env) $ while read grupo; do
    python image_hash_detector-TG.py --telegram-scan "$grupo" --limit-messages 100
done < grupos_telegram.txt
```

### 🗄️ Caso 4: Gestión de Base de Datos

Gestión rápida desde la CLI:
```bash
# 1. Añadir nueva imagen objetivo
(cyber_env) $ python image_hash_detector-TG.py --add-image /path/a/imagen_protesta.png \
  --description "Foto de manifestación clave" \
  --tags "protesta, politica"

# 2. Listar para encontrar el ID del objetivo
(cyber_env) $ python image_hash_detector-TG.py --list

# 3. Borrar un hash específico (usar modo interactivo - opción 9)
(cyber_env) $ python image_hash_detector-TG.py --interactive

# 4. Borrado total de la base de datos (requiere confirmación)
(cyber_env) $ python image_hash_detector-TG.py --reset-db
```

### 🤖 Caso 5: Automatización con Crontab

Programa escaneos automáticos usando crontab de Linux:
```bash
# Editar crontab
crontab -e

# Escaneo de sitios web cada 6 horas
0 */6 * * * /ruta/a/tu/proyecto/cyber_env/bin/python \
  /ruta/a/tu/proyecto/image_hash_detector-TG.py \
  --scan /ruta/lista_sitios.txt --threshold 8 >> /var/log/image_scan.log 2>&1

# Escaneo de Telegram cada 12 horas
0 */12 * * * /ruta/a/tu/proyecto/cyber_env/bin/python \
  /ruta/a/tu/proyecto/image_hash_detector-TG.py \
  --telegram-scan "GrupoMonitoreo" --limit-messages 50 >> /var/log/telegram_scan.log 2>&1
```

## 📂 Estructura del Proyecto
```
ImageHashDetector/
├── image_hash_detector-TG.py     # Script principal 
├── cyber_env/                     # Entorno virtual 
├── target_hashes.json             # Base de datos de objetivos
├── lista_sitios.txt               # Lista de URLs web a escanear
├── grupos_telegram.txt            # Lista de grupos Telegram a monitorear
├── reporte_scan_*.json            # Reportes de escaneos web
├── reporte_telegram_*.json        # Reportes de escaneos Telegram
├── reporte_monitoreo_*.json       # Reportes de monitoreo en tiempo real
├── session_+123456789             # Sesión de Telegram (generada automáticamente)
├── monitor.sh                     # Script de monitoreo continuo
└── README.md                      # Documentación
```

## 🏗️ Arquitectura del Sistema

### 🔐 Algoritmo de Detección Multi-Hash
```python
# Ejemplo simplificado del proceso
def compute_hashes(image):
    return {
        'phash': imagehash.phash(image),
        'ahash': imagehash.average_hash(image),
        'dhash': imagehash.dhash(image),
        'whash': imagehash.whash(image),
        'md5': hashlib.md5(image_bytes).hexdigest()
    }
```

### 📱 Integración con Telegram
```python
# Flujo de trabajo para Telegram
1. Configuración de API → Autenticación segura → Conexión persistente
2. Resolución de grupos → Descarga de medios → Procesamiento de imágenes
3. Comparación multi-hash → Detección → Exportación automática
```

### 📊 Flujo de Trabajo Completo

1. Carga de imagen objetivo → Cálculo de 5 hashes → Almacenamiento en DB
2. Escaneo de sitio web → Extracción de imágenes → Comparación multi-hash
3. Escaneo de Telegram → Descarga de medios → Comparación multi-hash
4. Detección positiva → Registro en reporte → Exportación JSON automática

## ✨ Características Técnicas Avanzadas

### 🔬 Ventajas del Multi-Hash

- ✅ **pHash (Perceptual):** Resistente a redimensionamiento
- ✅ **aHash (Average):** Rápido y eficiente
- ✅ **dHash (Difference):** Detecta cambios de gradiente
- ✅ **wHash (Wavelet):** Robusto ante compresión
- ✅ **MD5 (Cryptographic):** Detección exacta

### 🛡️ Resistencia a Evasión

- **Redimensionamiento:** ✓ Detectado
- **Compresión JPEG:** ✓ Detectado
- **Cambios de color:** ✓ Detectado (parcial)
- **Rotación ligera:** ✓ Detectado (con threshold)
- **Recortes menores:** ✓ Detectado (según tipo)

### 📱 Funcionalidades Avanzadas de Telegram

- **Resolución robusta de entidades:** Soporta IDs, nombres y búsqueda aproximada
- **Manejo de errores:** Reconexión automática en caso de desconexión
- **Procesamiento eficiente:** Descarga y análisis en tiempo real
- **Exportación inteligente:** Reportes separados por tipo de escaneo
- **Monitoreo persistente:** Sesiones de larga duración sin interrupciones

### ⚡ Optimizaciones

- Procesamiento paralelo de imágenes
- Caché de resultados recientes
- Validación de URLs antes de descarga
- Manejo robusto de errores HTTP y de Telegram
- Gestión eficiente de memoria para grandes volúmenes

## 🌐 Dependencias y Librerías

| Librería | Versión | Propósito |
|----------|---------|-----------|
| Pillow | 9.0+ | Procesamiento de imágenes |
| imagehash | 4.3+ | Generación de hashes perceptuales |
| requests | 2.28+ | Descarga de imágenes desde URLs |
| beautifulsoup4 | 4.11+ | Extracción de imágenes de HTML |
| telethon | 1.28+ | Integración con Telegram API |

## 🔐 Configuración de Telegram API

Para usar las funciones de Telegram, necesitas obtener credenciales de la API:

1. Visita: https://my.telegram.org/auth
2. Inicia sesión con tu cuenta de Telegram
3. Ve a "API Development Tools"
4. Crea una nueva aplicación y obtén:
   - `api_id`
   - `api_hash`

Ejemplo de configuración:
```bash
# Vía línea de comandos
python image_hash_detector-TG.py --setup-telegram \
  --api-id "1234567" \
  --api-hash "a1b2c3d4e5f6g7h8i9j0" \
  --phone "+1234567890"

# O desde el menú interactivo (Opción 8 → 1)
```

## 🚧 Próximas Mejoras

- Soporte para video frames (análisis por fotogramas)
- Machine Learning para detección avanzada
- Base de datos SQL para grandes volúmenes
- API REST para integración con otros sistemas
- Dashboard web para visualización de resultados
- Notificaciones (email, Telegram, Slack)
- Exportación PDF de reportes
- Modo stealth con rotación de User-Agent
- Soporte para múltiples cuentas de Telegram
- Análisis de metadatos EXIF y otros

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Algunas áreas de mejora:

- Implementar algoritmos de hash adicionales (ColorHash, BlockMeanHash)
- Agregar soporte para imágenes SVG
- Mejorar el rendimiento con multiprocessing
- Crear tests unitarios comprehensivos
- Documentar casos de uso OSINT específicos
- Desarrollar plugins para otras plataformas (Discord, WhatsApp, etc.)

## 📋 Requisitos del Sistema

- **Sistema Operativo:** Linux (Kali recomendado), macOS, Windows
- **Python:** 3.7 o superior
- **RAM:** Mínimo 1GB (más para imágenes grandes y Telegram)
- **Conexión:** Internet estable (para descargar imágenes y conectar con Telegram)
- **Permisos:** Lectura/escritura en directorio del proyecto
- **Telegram:** Cuenta activa de Telegram (para funciones de mensajería)

## ⚠️ Consideraciones Legales y Éticas

**IMPORTANTE:** Esta herramienta está diseñada para:

- Investigación de seguridad autorizada
- Análisis forense digital
- Monitoreo de contenido propio
- Investigaciones OSINT legales
- Cumplimiento normativo y anti-fraude
- Prácticas de laboratorio en entorno seguro

**NO debe ser utilizada para:**

- Violación de privacidad
- Acceso no autorizado a sistemas
- Actividades ilegales de vigilancia
- Violación de términos de servicio de sitios web o Telegram
- Acoso o stalking
- Actividades que violen leyes locales o internacionales

**Responsabilidad del Usuario:** El usuario es responsable del cumplimiento de todas las leyes aplicables en su jurisdicción, incluyendo leyes de protección de datos, privacidad y propiedad intelectual.

**Telegram:** Asegurate de cumplir con los Términos de Servicio de Telegram y obtener los permisos necesarios antes de monitorear grupos o canales.

## 🇦🇷 Hecho con Orgullo

Desarrollado desde Argentina 🇦🇷 por **Gonzalo-CR**, con enfoque en ciberseguridad, inteligencia open-source y herramientas para profesionales de seguridad.

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver LICENSE para más detalles.

---

⭐ **¿Te gusta ImageHashDetector? ¡Dale una estrella al repositorio!**

📱 **¿Problemas con Telegram?** Revisa la documentación de [Telethon](https://docs.telethon.dev/) y asegúrate de tener las credenciales correctas de la API.
