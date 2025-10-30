#!/usr/bin/env python3
"""
ImageHashDetector - Sistema de Detección de Imágenes por Hash Perceptual
En Sitios webs con integración para Telegram (User-Side)
"""

import hashlib
import imagehash
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Set
import argparse
import sys
import os
import asyncio
import logging

# ============================================================================
# CONFIGURACIÓN DE TELEGRAM
# ============================================================================
try:
    from telethon import TelegramClient, events
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
    from telethon.tl.functions.messages import GetHistoryRequest
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    print("⚠️  Telethon no disponible. Instala con: pip install telethon")

# ============================================================================
# COLORES ANSI PARA TERMINAL
# ============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    DARK_GRAY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# ARTE ASCII
# ============================================================================
BANNER = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   ██╗███╗   ███╗ █████╗  ██████╗ ███████╗                             ║
║   ██║████╗ ████║██╔══██╗██╔════╝ ██╔════╝                             ║
║   ██║██╔████╔██║███████║██║  ███╗█████╗                               ║
║   ██║██║╚██╔╝██║██╔══██║██║   ██║██╔══╝                               ║
║   ██║██║ ╚═╝ ██║██║  ██║╚██████╔╝███████╗                             ║
║   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝                             ║
║                                                                       ║
║   ██╗  ██╗ █████╗ ███████╗██╗  ██╗    ██████╗ ███████╗████████╗       ║
║   ██╗  ██║██╔══██╗██╔════╝██║  ██║    ██╔══██╗██╔════╝╚══██╔══╝       ║
║   ███████║███████║███████╗███████║    ██║  ██║█████╗     ██║          ║
║   ██╔══██║██╔══██║╚════██║██╔══██║    ██║  ██║██╔══╝     ██║          ║
║   ██║  ██║██║  ██║███████║██║  ██║    ██████╔╝███████╗   ██║          ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝   ╚═╝          ║
║                                                                       ║
║                   DETECTOR DE IMÁGENES WEB + TELEGRAM                 ║
║              Sistema de Hash Perceptual v2.2 Telegram Edition         ║
║                                                                       ║
║         Laboratorio de Ciberinteligencia y Análisis OSINT             ║
║                                                           by GonzoCR  ║
╚═══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}"""

MENU_SEPARATOR = f"{Colors.CYAN}{'═' * 75}{Colors.ENDC}"
MENU_SEPARATOR_THIN = f"{Colors.CYAN}{'─' * 75}{Colors.ENDC}"

# ============================================================================
# MANEJO GLOBAL DEL EVENT LOOP
# ============================================================================
class TelegramLoopManager:
    _instance = None
    _loop = None
    
    @classmethod
    def get_loop(cls):
        if cls._loop is None:
            try:
                cls._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(cls._loop)
            except RuntimeError:
                cls._loop = asyncio.get_event_loop()
        return cls._loop
    
    @classmethod
    def run_async(cls, coro):
        loop = cls.get_loop()
        if loop.is_running():
            # Si el loop ya está corriendo, usamos un futuro
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()
        else:
            return loop.run_until_complete(coro)

# ============================================================================
# FUNCIONES DE DISPLAY
# ============================================================================
def print_banner():
    """Imprime el banner ASCII"""
    print(BANNER)

def print_section_header(title: str):
    """Imprime un encabezado de sección"""
    print(f"\n{MENU_SEPARATOR}")
    print(f"{Colors.BOLD}{Colors.YELLOW}  📌 {title.upper()}{Colors.ENDC}")
    print(MENU_SEPARATOR)

def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")

def print_detection(message: str):
    """Imprime detección encontrada"""
    print(f"{Colors.RED}{Colors.BOLD}🎯 {message}{Colors.ENDC}")

def print_progress(message: str):
    """Imprime progreso"""
    print(f"{Colors.BLUE}🔍 {message}{Colors.ENDC}")

def print_telegram(message: str):
    """Imprime mensaje relacionado con Telegram"""
    print(f"{Colors.BLUE}📱 {message}{Colors.ENDC}")

# ============================================================================
# CLASE PRINCIPAL 
# ============================================================================
class ImageHashDetector:
    def __init__(self, hash_database_file: str = "target_hashes.json"):
        """
        Inicializa el detector de imágenes
        """
        self.hash_database_file = hash_database_file
        self.target_hashes = self.load_target_hashes()
        self.detected_matches = []
        self.telegram_client = None
        self.telegram_connected = False
        self.telegram_user_info = None
        
    def load_target_hashes(self) -> Dict[str, Dict]:
        """Carga los hashes objetivo desde el archivo JSON"""
        try:
            with open(self.hash_database_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print_warning(f"Archivo {self.hash_database_file} no encontrado. Creando nuevo...")
            return {}
    
    def save_target_hashes(self):
        """Guarda los hashes objetivo en el archivo JSON"""
        with open(self.hash_database_file, 'w') as f:
            json.dump(self.target_hashes, f, indent=2)
    
    def reset_database(self):
        """
        Borra completamente la base de datos de hashes.
        """
        print_section_header("BORRAR BASE DE DATOS")
        confirm = input(f"{Colors.RED}ADVERTENCIA:{Colors.ENDC} ¿Estás seguro de que quieres borrar TODOS los hashes ({len(self.target_hashes)})? (s/N): ").lower()
        if confirm == 's':
            self.target_hashes = {}
            self.save_target_hashes()
            print_success(f"💣 Base de datos {self.hash_database_file} reseteada y vaciada.")
        else:
            print_info("Operación cancelada.")

    def delete_target_hash(self, target_id: str):
        """
        Borra un hash objetivo por su ID.
        """
        print_section_header("BORRAR HASH POR ID")
        if target_id in self.target_hashes:
            target_data = self.target_hashes.pop(target_id)
            self.save_target_hashes()
            print_success(f"Hash {Colors.BOLD}{target_id}{Colors.ENDC} ({target_data['description']}) eliminado de la base de datos.")
        else:
            print_error(f"ID de hash no encontrado: {target_id}")

    def add_target_hash(self, image_path: str, description: str = "", tags: List[str] = None):
        """
        Añade una imagen objetivo calculando sus múltiples hashes
        """
        try:
            print_progress(f"Procesando imagen: {image_path}")
            
            # Cargar imagen
            if image_path.startswith('http'):
                response = requests.get(image_path, timeout=10)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(image_path)
            
            # Calcular múltiples tipos de hash perceptual
            print_info("Calculando hashes perceptuales...")
            ahash = str(imagehash.average_hash(img))
            phash = str(imagehash.phash(img))
            dhash = str(imagehash.dhash(img))
            whash = str(imagehash.whash(img))
            
            # Hash criptográfico MD5 del contenido original
            if not image_path.startswith('http'):
                with open(image_path, 'rb') as f:
                    file_content = f.read()
                md5_hash = hashlib.md5(file_content).hexdigest()
            else:
                img_bytes = BytesIO()
                img.save(img_bytes, format=img.format or 'PNG')
                md5_hash = hashlib.md5(img_bytes.getvalue()).hexdigest()
            
            # Almacenar en la base de datos
            hash_id = f"target_{len(self.target_hashes) + 1}"
            self.target_hashes[hash_id] = {
                "description": description,
                "tags": tags or [],
                "added_date": datetime.now().isoformat(),
                "source": image_path,
                "hashes": {
                    "md5": md5_hash,
                    "ahash": ahash,
                    "phash": phash,
                    "dhash": dhash,
                    "whash": whash
                }
            }
            
            self.save_target_hashes()
            print_success(f"Imagen agregada con ID: {Colors.BOLD}{hash_id}{Colors.ENDC}")
            print(f"   {Colors.CYAN}MD5:{Colors.ENDC}    {md5_hash}")
            print(f"   {Colors.CYAN}pHash:{Colors.ENDC}  {phash}")
            print(f"   {Colors.CYAN}aHash:{Colors.ENDC}  {ahash}")
            print(f"   {Colors.CYAN}dHash:{Colors.ENDC}  {dhash}")
            print(f"   {Colors.CYAN}wHash:{Colors.ENDC}  {whash}")
            return hash_id
            
        except Exception as e:
            print_error(f"Error al procesar imagen: {e}")
            return None
    
    def add_manual_hash(self, hash_value: str, hash_type: str = "phash", 
                       description: str = "", tags: List[str] = None):
        """
        Añade un hash manualmente sin procesar la imagen
        """
        hash_id = f"manual_{len(self.target_hashes) + 1}"
        self.target_hashes[hash_id] = {
            "description": description,
            "tags": tags or [],
            "added_date": datetime.now().isoformat(),
            "source": "manual",
            "hashes": {
                hash_type: hash_value
            }
        }
        self.save_target_hashes()
        print_success(f"Hash manual agregado con ID: {Colors.BOLD}{hash_id}{Colors.ENDC}")
        print(f"   {Colors.CYAN}Tipo:{Colors.ENDC}  {hash_type}")
        print(f"   {Colors.CYAN}Valor:{Colors.ENDC} {hash_value}")
        return hash_id
    
    def compute_image_hashes(self, image_url: str) -> Dict[str, str]:
        """Calcula todos los hashes de una imagen desde URL"""
        try:
            response = requests.get(image_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            
            return {
                "ahash": str(imagehash.average_hash(img)),
                "phash": str(imagehash.phash(img)),
                "dhash": str(imagehash.dhash(img)),
                "whash": str(imagehash.whash(img)),
                "md5": hashlib.md5(response.content).hexdigest()
            }
        except requests.exceptions.RequestException as req_err:
            return {}
        except Exception:
            return {}
    
    def compute_image_hashes_from_bytes(self, image_data: bytes) -> Dict[str, str]:
        """Calcula todos los hashes de una imagen desde bytes"""
        try:
            img = Image.open(BytesIO(image_data))
            
            return {
                "ahash": str(imagehash.average_hash(img)),
                "phash": str(imagehash.phash(img)),
                "dhash": str(imagehash.dhash(img)),
                "whash": str(imagehash.whash(img)),
                "md5": hashlib.md5(image_data).hexdigest()
            }
        except Exception as e:
            return {}
    
    def compare_hashes(self, hash1: str, hash2: str, threshold: int = 5) -> bool:
        """
        Compara dos hashes perceptuales (Hamming distance)
        """
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            return (h1 - h2) <= threshold
        except:
            return hash1 == hash2 
    
    def check_image(self, image_url: str, source: str = "", threshold: int = 5) -> List[Dict]:
        """
        Verifica si una imagen coincide con alguna en la base de datos
        """
        matches = []
        image_hashes = self.compute_image_hashes(image_url)
        
        if not image_hashes:
            return matches
        
        # Comparar con cada hash objetivo
        for target_id, target_data in self.target_hashes.items():
            target_hashes = target_data.get("hashes")
            
            if not target_hashes:
                continue
                
            match_found = False
            match_type = []
            
            # Verificar cada tipo de hash
            for hash_type in ["md5", "phash", "ahash", "dhash", "whash"]:
                if hash_type in target_hashes and hash_type in image_hashes:
                    if hash_type == "md5":
                        if target_hashes[hash_type] == image_hashes[hash_type]:
                            match_found = True
                            match_type.append(f"{hash_type} (exacto)")
                    else:
                        if self.compare_hashes(target_hashes[hash_type], 
                                              image_hashes[hash_type], 
                                              threshold):
                            match_found = True
                            h1 = imagehash.hex_to_hash(target_hashes[hash_type])
                            h2 = imagehash.hex_to_hash(image_hashes[hash_type])
                            distance = h1 - h2
                            match_type.append(f"{hash_type} (distancia: {distance})")
            
            if match_found:
                match = {
                    "target_id": target_id,
                    "description": target_data["description"],
                    "tags": target_data["tags"],
                    "match_types": match_type,
                    "found_url": image_url,
                    "source": source,
                    "timestamp": datetime.now().isoformat()
                }
                matches.append(match)
                self.detected_matches.append(match)
                
                print(f"\n{MENU_SEPARATOR_THIN}")
                print_detection("COINCIDENCIA DETECTADA")
                print(f"   {Colors.BOLD}Target:{Colors.ENDC} {target_id} - {target_data['description']}")
                print(f"   {Colors.BOLD}Match:{Colors.ENDC}  {', '.join(match_type)}")
                print(f"   {Colors.BOLD}URL:{Colors.ENDC}    {image_url}")
                print(f"   {Colors.BOLD}Fuente:{Colors.ENDC} {source}")
                print(MENU_SEPARATOR_THIN)
        
        return matches
    
    def check_image_from_bytes(self, image_data: bytes, source: str = "", message_info: str = "", threshold: int = 5) -> List[Dict]:
        """
        Verifica si una imagen (desde bytes) coincide con alguna en la base de datos
        """
        matches = []
        image_hashes = self.compute_image_hashes_from_bytes(image_data)
        
        if not image_hashes:
            return matches
        
        # Comparar con cada hash objetivo
        for target_id, target_data in self.target_hashes.items():
            target_hashes = target_data.get("hashes")
            
            if not target_hashes:
                continue
                
            match_found = False
            match_type = []
            
            # Verificar cada tipo de hash
            for hash_type in ["md5", "phash", "ahash", "dhash", "whash"]:
                if hash_type in target_hashes and hash_type in image_hashes:
                    if hash_type == "md5":
                        if target_hashes[hash_type] == image_hashes[hash_type]:
                            match_found = True
                            match_type.append(f"{hash_type} (exacto)")
                    else:
                        if self.compare_hashes(target_hashes[hash_type], 
                                              image_hashes[hash_type], 
                                              threshold):
                            match_found = True
                            h1 = imagehash.hex_to_hash(target_hashes[hash_type])
                            h2 = imagehash.hex_to_hash(image_hashes[hash_type])
                            distance = h1 - h2
                            match_type.append(f"{hash_type} (distancia: {distance})")
            
            if match_found:
                match = {
                    "target_id": target_id,
                    "description": target_data["description"],
                    "tags": target_data["tags"],
                    "match_types": match_type,
                    "found_in": message_info,
                    "source": f"Telegram - {source}",
                    "timestamp": datetime.now().isoformat(),
                    "image_hashes": image_hashes
                }
                matches.append(match)
                self.detected_matches.append(match)
                
                print(f"\n{MENU_SEPARATOR_THIN}")
                print_detection("COINCIDENCIA DETECTADA EN TELEGRAM")
                print(f"   {Colors.BOLD}Target:{Colors.ENDC} {target_id} - {target_data['description']}")
                print(f"   {Colors.BOLD}Match:{Colors.ENDC}  {', '.join(match_type)}")
                print(f"   {Colors.BOLD}Fuente:{Colors.ENDC} {source}")
                print(f"   {Colors.BOLD}Info:{Colors.ENDC}   {message_info}")
                print(MENU_SEPARATOR_THIN)
        
        return matches
    
    def scan_webpage(self, url: str, threshold: int = 5) -> List[Dict]:
        """
        Escanea todas las imágenes de una página web
        """
        print_section_header(f"Escaneando: {url}")
        all_matches = []
        
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status() 
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar todas las imágenes
            images = soup.find_all('img')
            print_info(f"Encontradas {Colors.BOLD}{len(images)}{Colors.ENDC} imágenes")
            print()
            
            # Formatos a ignorar que saturan el output o son incompatibles
            IGNORED_EXTENSIONS = ('.svg', '.gif', '.ico', '.pdf', '.js', '.css') 

            for idx, img in enumerate(images, 1):
                img_url = img.get('src') or img.get('data-src')
                if not img_url:
                    continue
                
                # Convertir URL relativa a absoluta
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    from urllib.parse import urljoin
                    img_url = urljoin(url, img_url)
                elif not img_url.startswith('http'):
                    continue
                
                # Saltar formatos no soportados/irrelevantes
                if img_url.lower().endswith(IGNORED_EXTENSIONS):
                     print(f"   [{idx}/{len(images)}] {Colors.YELLOW}⏭️  Saltando {img_url.split('/')[-1]} (Formato ignorado){Colors.ENDC}")
                     continue
                
                print(f"   [{idx}/{len(images)}] {Colors.BLUE}🔍 Verificando imagen...{Colors.ENDC}", end='\r')
                matches = self.check_image(img_url, source=url, threshold=threshold)
                all_matches.extend(matches)
                
                if not matches:
                    # Limpiar la línea de "Verificando" si no hubo coincidencia
                    sys.stdout.write(f"   [{idx}/{len(images)}] {Colors.GREEN}✓{Colors.ENDC} Verificada{' ' * 50}\r")
                    sys.stdout.flush()
                
                time.sleep(0.1) # Pausa mínima
            
            print()
            print_success(f"Escaneo de {url} completado.")
            
        except requests.exceptions.RequestException as e:
            print_error(f"Error de red/HTTP al escanear {url}: {e}")
        except Exception as e:
            print_error(f"Error general al escanear {url}: {e}")
        
        return all_matches
    
    # ============================================================================
    # FUNCIONALIDADES DE TELEGRAM 
    # ============================================================================
    
    async def _setup_telegram_client_async(self, api_id: str, api_hash: str, phone: str):
        """Configura el cliente de Telegram (versión asíncrona interna)"""
        if not TELETHON_AVAILABLE:
            return False
            
        try:
            # Cerrar cliente existente si hay uno
            if self.telegram_client and self.telegram_client.is_connected():
                await self.telegram_client.disconnect()
            
            self.telegram_client = TelegramClient(f"session_{phone}", api_id, api_hash)
            await self.telegram_client.start(phone=phone)
            
            # Obtener información del usuario
            me = await self.telegram_client.get_me()
            self.telegram_user_info = {
                'id': me.id,
                'username': me.username or "Sin username",
                'first_name': me.first_name or "",
                'last_name': me.last_name or "",
                'phone': phone
            }
            
            self.telegram_connected = True
            return True
            
        except Exception as e:
            print_error(f"Error al configurar Telegram: {e}")
            self.telegram_connected = False
            self.telegram_user_info = None
            return False

    def setup_telegram_client(self, api_id: str, api_hash: str, phone: str):
        """Configura el cliente de Telegram (versión síncrona para el menú)"""
        print_progress("Configurando cliente de Telegram...")
        success = TelegramLoopManager.run_async(self._setup_telegram_client_async(api_id, api_hash, phone))
        
        if success:
            print_success("Cliente de Telegram configurado correctamente")
            user = self.telegram_user_info
            username_display = f"@{user['username']}" if user['username'] != "Sin username" else "(sin username)"
            print_info(f"Conectado como: {user['first_name']} {user['last_name']} {username_display}")
        else:
            print_error("Error en la configuración de Telegram")
        
        return success

    async def _disconnect_telegram_async(self):
        """Desconecta el cliente de Telegram (versión asíncrona interna)"""
        if self.telegram_client and self.telegram_client.is_connected():
            await self.telegram_client.disconnect()
            self.telegram_connected = False
            self.telegram_user_info = None
            return True
        return False

    def disconnect_telegram(self):
        """Desconecta el cliente de Telegram (versión síncrona)"""
        success = TelegramLoopManager.run_async(self._disconnect_telegram_async())
        if success:
            print_success("Desconectado de Telegram")
        else:
            print_warning("No hay conexión activa de Telegram")
        return success

    def get_telegram_status(self):
        """Obtiene el estado de conexión de Telegram"""
        if self.telegram_connected and self.telegram_user_info:
            return {
                'connected': True,
                'user': self.telegram_user_info
            }
        return {'connected': False, 'user': None}

    async def _resolve_group_entity(self, group_identifier: str):
        """Resuelve una entidad de grupo de manera robusta"""
        entity = None
        
        # Intentar como ID numérico (incluyendo negativos)
        if group_identifier.lstrip('-').isdigit():
            try:
                entity = await self.telegram_client.get_entity(int(group_identifier))
                return entity
            except Exception:
                pass
        
        # Buscar en diálogos por nombre (case insensitive)
        async for dialog in self.telegram_client.iter_dialogs():
            if dialog.name and group_identifier.lower() in dialog.name.lower():
                print_success(f"Grupo encontrado: {dialog.name}")
                return dialog.entity
                
        try:
            entity = await self.telegram_client.get_entity(group_identifier)
            return entity
        except Exception as e:
            raise Exception(f"No se pudo encontrar el grupo: {group_identifier}. Error: {e}")

    async def _scan_telegram_group_async(self, group_identifier: str, limit_messages: int = 100, threshold: int = 5):
        """
        Escanea un grupo/canal de Telegram en busca de imágenes que coincidan (versión asíncrona MEJORADA)
        """
        if not self.telegram_client or not self.telegram_connected:
            return []
        
        matches_found = []
        
        try:
            # Resolución robusta de entidades
            entity = await self._resolve_group_entity(group_identifier)
            group_name = getattr(entity, 'title', getattr(entity, 'name', group_identifier))
            
            print_info(f"Escaneando grupo: {group_name}")
            
            # Obtener mensajes
            messages = await self.telegram_client.get_messages(entity, limit=limit_messages)
            
            print_info(f"Analizando {len(messages)} mensajes...")
            
            for i, message in enumerate(messages, 1):
                if message.media:
                    # Verificar si es una imagen
                    if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
                        try:
                            print(f"   [{i}/{len(messages)}] Procesando imagen...", end='\r')
                            
                            # Descargar la imagen
                            image_data = await self.telegram_client.download_media(message.media, file=BytesIO())
                            
                            if image_data:
                                # Verificar si es realmente una imagen descargable
                                if hasattr(image_data, 'getvalue'):
                                    image_bytes = image_data.getvalue()
                                else:
                                    image_bytes = image_data
                                
                                # Crear información del mensaje
                                sender = await message.get_sender()
                                sender_name = getattr(sender, 'username', getattr(sender, 'first_name', 'Unknown'))
                                message_info = f"MsgID: {message.id} | From: {sender_name} | Date: {message.date}"
                                
                                # Verificar la imagen
                                matches = self.check_image_from_bytes(
                                    image_bytes, 
                                    source=group_name,
                                    message_info=message_info,
                                    threshold=threshold
                                )
                                matches_found.extend(matches)
                                
                        except Exception as e:
                            continue  # Saltar si no se puede procesar la imagen
            
            print_success(f"Escaneo de {group_name} completado. Encontradas: {len(matches_found)} coincidencias")
            
        except Exception as e:
            print_error(f"Error al escanear grupo {group_identifier}: {e}")
        
        return matches_found

    def scan_telegram_group(self, group_identifier: str, limit_messages: int = 100, threshold: int = 5):
        """
        Escanea un grupo/canal de Telegram en busca de imágenes que coincidan
        """
        print_telegram(f"Iniciando escaneo de grupo: {group_identifier}")
        matches = TelegramLoopManager.run_async(self._scan_telegram_group_async(group_identifier, limit_messages, threshold))
        
        # EXPORTACIÓN AUTOMÁTICA DE RESULTADOS
        if matches:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_telegram_{timestamp}.json"
            print_section_header("EXPORTANDO RESULTADOS AUTOMÁTICAMENTE")
            self.export_matches(filename)
        else:
            print_warning("No se encontraron coincidencias en el grupo")
        
        return matches
    
    async def _monitor_telegram_group_async(self, group_identifier: str, threshold: int = 5):
        """
        Monitorea en tiempo real un grupo/canal de Telegram
        """
        if not self.telegram_client or not self.telegram_connected:
            return
        
        # MEJORA: Resolver la entidad de manera robusta
        entity = await self._resolve_group_entity(group_identifier)
        group_name = getattr(entity, 'title', getattr(entity, 'name', group_identifier))
        
        print_telegram(f"Iniciando monitorización en tiempo real de: {group_name}")
        
        # Contador para exportación automática
        detection_count = 0
        start_time = datetime.now()
        session_matches = []
        
        @self.telegram_client.on(events.NewMessage(chats=entity))
        async def handler(event):
            nonlocal detection_count, session_matches
            if event.message.media:
                if isinstance(event.message.media, (MessageMediaPhoto, MessageMediaDocument)):
                    try:
                        # Descargar la imagen
                        image_data = await self.telegram_client.download_media(event.message.media, file=BytesIO())
                        
                        if image_data and hasattr(image_data, 'getvalue'):
                            image_bytes = image_data.getvalue()
                            
                            # Crear información del mensaje
                            sender = await event.message.get_sender()
                            sender_name = getattr(sender, 'username', getattr(sender, 'first_name', 'Unknown'))
                            message_info = f"MsgID: {event.message.id} | From: {sender_name} | Real-time"
                            
                            # Verificar la imagen
                            matches = self.check_image_from_bytes(
                                image_bytes,
                                source=group_name,
                                message_info=message_info,
                                threshold=threshold
                            )
                            
                            if matches:
                                detection_count += len(matches)
                                session_matches.extend(matches)
                            
                    except Exception as e:
                        pass  # Saltar errores en tiempo real
    
        print_success(f"Monitorizando {group_name}. Presiona Ctrl+C para detener y exportar.")
        
        try:
            await self.telegram_client.run_until_disconnected()
        except KeyboardInterrupt:
            print_info("Monitorización detenida por el usuario")
            
            # Exportación automática al finalizar monitoreo
            if detection_count > 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reporte_monitoreo_{group_name}_{timestamp}.json"
                print_section_header("EXPORTANDO RESULTADOS DEL MONITOREO")
                try:
                    # Exportar solo las detecciones de esta sesión de monitoreo
                    with open(filename, 'w') as f:
                        json.dump(session_matches, f, indent=2)
                    print_success(f"Reporte de monitoreo exportado: {Colors.BOLD}{filename}{Colors.ENDC}")
                    print_info(f"Total de detecciones en esta sesión: {detection_count}")
                    print_info(f"Duración del monitoreo: {(datetime.now() - start_time).total_seconds():.0f} segundos")
                except Exception as e:
                    print_error(f"Error al exportar el reporte: {e}")
            else:
                print_warning("No se encontraron coincidencias durante el monitoreo")

    def monitor_telegram_group(self, group_identifier: str, threshold: int = 5):
        """
        Monitorea en tiempo real un grupo/canal de Telegram
        """
        try:
            TelegramLoopManager.run_async(self._monitor_telegram_group_async(group_identifier, threshold))
        except KeyboardInterrupt:
            print_info("Monitorización detenida por el usuario")
        except Exception as e:
            print_error(f"Error en monitorización: {e}")
    
    async def _get_user_groups_async(self):
        """Obtiene la lista de grupos/chats del usuario (versión asíncrona)"""
        if not self.telegram_client or not self.telegram_connected:
            return []
        
        groups = []
        async for dialog in self.telegram_client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                groups.append({
                    'name': dialog.name,
                    'id': dialog.id,
                    'entity': dialog.entity
                })
        
        return groups

    def get_user_groups(self):
        """Obtiene la lista de grupos/chats del usuario (versión síncrona)"""
        return TelegramLoopManager.run_async(self._get_user_groups_async())
    
    def export_matches(self, filename: str = "matches_report.json"):
        """Exporta las coincidencias detectadas a un archivo JSON"""
        if not self.detected_matches:
             print_warning("No hay coincidencias detectadas para exportar.")
             return
             
        try:
            with open(filename, 'w') as f:
                json.dump(self.detected_matches, f, indent=2)
            print_success(f"Reporte exportado: {Colors.BOLD}{filename}{Colors.ENDC}")
        except Exception as e:
            print_error(f"Error al exportar el reporte a {filename}: {e}")

    
    def list_targets(self):
        """Muestra todos los hashes objetivo cargados"""
        print_section_header("HASHES OBJETIVO REGISTRADOS")
        
        if not self.target_hashes:
            print_warning("No hay hashes objetivo registrados")
            print_info("Usa la opción 1 o 2 para agregar hashes")
            return
        
        for target_id, data in self.target_hashes.items():
            print(f"\n{Colors.BOLD}{Colors.CYAN}╔═══ {target_id} ═══╗{Colors.ENDC}")
            print(f"{Colors.BOLD}Descripción:{Colors.ENDC} {data['description']}")
            print(f"{Colors.BOLD}Tags:{Colors.ENDC}        {', '.join(data['tags']) if data['tags'] else 'Sin tags'}")
            print(f"{Colors.BOLD}Fecha:{Colors.ENDC}       {data['added_date']}")
            print(f"{Colors.BOLD}Origen:{Colors.ENDC}      {data['source']}")
            print(f"\n{Colors.YELLOW}Hashes:{Colors.ENDC}")
            for hash_type, hash_value in data['hashes'].items():
                print(f"  • {hash_type.upper():6} → {hash_value}")
        
        print(f"\n{MENU_SEPARATOR}")
        print_info(f"Total de hashes objetivo: {Colors.BOLD}{len(self.target_hashes)}{Colors.ENDC}")

    def show_stats(self):
        """Muestra estadísticas del sistema"""
        print_section_header("ESTADÍSTICAS DEL SISTEMA")
        
        print(f"{Colors.BOLD}📊 Base de Datos:{Colors.ENDC}")
        print(f"   • Imágenes objetivo: {Colors.GREEN}{len(self.target_hashes)}{Colors.ENDC}")
        print(f"   • Detecciones totales: {Colors.GREEN}{len(self.detected_matches)}{Colors.ENDC}")
        
        # Mostrar estado de Telegram
        tg_status = self.get_telegram_status()
        if tg_status['connected']:
            user = tg_status['user']
            print(f"\n{Colors.BOLD}📱 Estado Telegram:{Colors.ENDC}")
            print(f"   • Conectado como: {user['first_name']} {user['last_name'] or ''}")
            print(f"   • Username: @{user['username']}")
            print(f"   • Teléfono: {user['phone']}")
        else:
            print(f"\n{Colors.BOLD}📱 Estado Telegram:{Colors.ENDC} {Colors.RED}❌ No conectado{Colors.ENDC}")
        
        # Estadísticas por fuente
        sources = {}
        for match in self.detected_matches:
            source = match.get('source', 'Desconocido')
            sources[source] = sources.get(source, 0) + 1
        
        if sources:
            print(f"\n{Colors.BOLD}🌐 Detecciones por fuente:{Colors.ENDC}")
            for source, count in sources.items():
                print(f"   • {source}: {count}")
        
        if self.detected_matches:
            print(f"\n{Colors.BOLD}🎯 Última Detección:{Colors.ENDC}")
            last = self.detected_matches[-1]
            print(f"   • Target: {last['target_id']}")
            print(f"   • Descripción: {last['description']}")
            print(f"   • Fuente: {last.get('source', 'N/A')}")
            print(f"   • Timestamp: {last['timestamp']}")
        
        print(f"\n{Colors.BOLD}📁 Archivos:{Colors.ENDC}")
        print(f"   • Base de datos: {self.hash_database_file}")
        print(f"   • Estado: {Colors.GREEN}✓ Activa{Colors.ENDC}" if self.target_hashes else f"{Colors.YELLOW}⚠ Vacía{Colors.ENDC}")

# ============================================================================
# MENÚ INTERACTIVO 
# ============================================================================
def interactive_menu():
    """Menú interactivo principal"""
    detector = ImageHashDetector()
    
    while True:
        os.system('clear')
        print_banner()
        
        # Mostrar estado de Telegram en el banner del menú
        tg_status = detector.get_telegram_status()
        if tg_status['connected']:
            user = tg_status['user']
            username_display = f"@{user['username']}" if user['username'] != "Sin username" else "(sin username)"
            telegram_status_display = f"{Colors.GREEN}✅ Conectado como: {user['first_name']} {username_display}{Colors.ENDC}"
        else:
            telegram_status_display = f"{Colors.RED}❌ No conectado{Colors.ENDC}"
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}MENÚ PRINCIPAL{Colors.ENDC} {Colors.GRAY}| Telegram: {telegram_status_display}{Colors.ENDC}")
        print(MENU_SEPARATOR_THIN)
        print(f"{Colors.GREEN}[1]{Colors.ENDC} 📷 Agregar imagen objetivo")
        print(f"{Colors.GREEN}[2]{Colors.ENDC} #️⃣  Agregar hash manual")
        print(f"{Colors.GREEN}[3]{Colors.ENDC} 🔍 Escanear sitio web (y Exportar)")
        print(f"{Colors.GREEN}[4]{Colors.ENDC} 📋 Escanear múltiples sitios (y Exportar)")
        print(f"{Colors.GREEN}[5]{Colors.ENDC} 🖼️  Verificar imagen específica")
        print(f"{Colors.GREEN}[6]{Colors.ENDC} 📊 Ver estadísticas")
        print(f"{Colors.GREEN}[7]{Colors.ENDC} 📜 Listar hashes objetivo")
        print(f"{Colors.GREEN}[8]{Colors.ENDC} 📱 Funciones de Telegram")
        print(f"{Colors.YELLOW}[9]{Colors.ENDC} 🗑️  Borrar hash por ID")
        print(f"{Colors.YELLOW}[10]{Colors.ENDC} 💣 Limpiar/Resetear Base de Datos")
        print(f"{Colors.RED}[0]{Colors.ENDC} 🚪 Salir")
        print(MENU_SEPARATOR_THIN)
        
        try:
            choice = input(f"{Colors.BOLD}Seleccione una opción: {Colors.ENDC}").strip()
            
            if choice == '1':
                print_section_header("AGREGAR IMAGEN OBJETIVO")
                path = input("Ruta o URL de la imagen: ").strip()
                desc = input("Descripción: ").strip()
                tags_input = input("Tags (separados por comas): ").strip()
                tags = [t.strip() for t in tags_input.split(',')] if tags_input else []
                detector.add_target_hash(path, desc, tags)
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
            
            elif choice == '2':
                print_section_header("AGREGAR HASH MANUAL")
                hash_val = input("Valor del hash: ").strip()
                hash_type = input("Tipo (md5/phash/ahash/dhash/whash) [phash]: ").strip() or "phash"
                desc = input("Descripción: ").strip()
                tags_input = input("Tags (separados por comas): ").strip()
                tags = [t.strip() for t in tags_input.split(',')] if tags_input else []
                detector.add_manual_hash(hash_val, hash_type, desc, tags)
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
            
            elif choice == '3':
                print_section_header("ESCANEAR SITIO WEB")
                url = input("URL del sitio: ").strip()
                threshold = input("Umbral de similitud (0-64) [5]: ").strip()
                threshold = int(threshold) if threshold else 5
                detector.scan_webpage(url, threshold)
                
                if detector.detected_matches:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"reporte_scan_{timestamp}.json"
                    print_section_header("EXPORTANDO RESULTADOS AUTOMÁTICAMENTE")
                    detector.export_matches(filename)
                else:
                    print_warning("Escaneo completado. No se encontraron coincidencias para exportar.")
                
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
            
            elif choice == '4':
                print_section_header("ESCANEAR MÚLTIPLES SITIOS")
                file_path = input("Ruta del archivo con URLs: ").strip()
                threshold = input("Umbral de similitud (0-64) [5]: ").strip()
                threshold = int(threshold) if threshold else 5
                
                try:
                    with open(file_path, 'r') as f:
                        urls = [line.strip() for line in f if line.strip().startswith(('http://', 'https://'))]
                    print_info(f"Leyendo {len(urls)} URLs desde el archivo")
                    
                    for url in urls:
                        detector.scan_webpage(url, threshold)
                        print()
                        
                    if detector.detected_matches:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"reporte_scan_lote_{timestamp}.json"
                        print_section_header("EXPORTANDO RESULTADOS AUTOMÁTICAMENTE")
                        detector.export_matches(filename)
                    else:
                        print_warning("Escaneo de lote completado. No se encontraron coincidencias para exportar.")
                        
                except FileNotFoundError:
                    print_error(f"Archivo no encontrado: {file_path}")
                
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
            
            elif choice == '5':
                print_section_header("VERIFICAR IMAGEN ESPECÍFICA")
                url = input("URL de la imagen: ").strip()
                threshold = input("Umbral de similitud (0-64) [5]: ").strip()
                threshold = int(threshold) if threshold else 5
                detector.check_image(url, threshold=threshold)
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
            
            elif choice == '6':
                detector.show_stats()
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
            
            elif choice == '7':
                detector.list_targets()
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")

            elif choice == '8':
                telegram_menu(detector)
            
            elif choice == '9':
                detector.list_targets()
                target_id = input(f"\n{Colors.BOLD}Ingrese el ID del hash a borrar (ej. target_1):{Colors.ENDC} ").strip()
                if target_id:
                    detector.delete_target_hash(target_id)
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")

            elif choice == '10':
                detector.reset_database()
                input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
            
            elif choice == '0':
                # Desconectar Telegram antes de salir
                if detector.telegram_connected:
                    print_info("Desconectando Telegram...")
                    detector.disconnect_telegram()
                print_section_header("SALIENDO DEL SISTEMA")
                print_info("¡Hasta pronto!")
                sys.exit(0)
            
            else:
                print_error("Opción no válida")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Operación cancelada{Colors.ENDC}")
            input(f"{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
        except Exception as e:
            print_error(f"Error: {e}")
            input(f"{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")

def telegram_menu(detector):
    """Submenú para funciones de Telegram"""
    while True:
        os.system('clear')
        print_banner()
        
        # Mostrar estado actual de Telegram
        tg_status = detector.get_telegram_status()
        if tg_status['connected']:
            user = tg_status['user']
            username_display = f"@{user['username']}" if user['username'] != "Sin username" else "(sin username)"
            status_display = f"{Colors.GREEN}✅ Conectado como: {user['first_name']} {username_display}{Colors.ENDC}"
            menu_options = [
                f"{Colors.GREEN}[1]{Colors.ENDC} 🔍 Ver información de conexión",
                f"{Colors.GREEN}[2]{Colors.ENDC} 📋 Listar grupos/chats disponibles", 
                f"{Colors.GREEN}[3]{Colors.ENDC} 🔍 Escanear grupo específico",
                f"{Colors.GREEN}[4]{Colors.ENDC} 📋 Escanear múltiples grupos",
                f"{Colors.GREEN}[5]{Colors.ENDC} 👁️  Monitorear grupo en tiempo real",
                f"{Colors.GREEN}[6]{Colors.ENDC} 📊 Ver detecciones de Telegram",
                f"{Colors.YELLOW}[7]{Colors.ENDC} 🚪 Desconectar Telegram",
                f"{Colors.YELLOW}[0]{Colors.ENDC} ↩️  Volver al menú principal"
            ]
        else:
            status_display = f"{Colors.RED}❌ No conectado{Colors.ENDC}"
            menu_options = [
                f"{Colors.GREEN}[1]{Colors.ENDC} 🔧 Configurar cliente de Telegram",
                f"{Colors.YELLOW}[0]{Colors.ENDC} ↩️  Volver al menú principal"
            ]
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}MENÚ TELEGRAM{Colors.ENDC} {Colors.GRAY}| Estado: {status_display}{Colors.ENDC}")
        print(MENU_SEPARATOR_THIN)
        
        for option in menu_options:
            print(option)
        print(MENU_SEPARATOR_THIN)
        
        try:
            choice = input(f"{Colors.BOLD}Seleccione una opción: {Colors.ENDC}").strip()
            
            if tg_status['connected']:
                # MENÚ CUANDO ESTÁ CONECTADO
                if choice == '1':
                    print_section_header("INFORMACIÓN DE CONEXIÓN TELEGRAM")
                    user = tg_status['user']
                    print(f"{Colors.BOLD}👤 Usuario:{Colors.ENDC}")
                    print(f"   • Nombre: {user['first_name']} {user['last_name'] or ''}")
                    print(f"   • Username: @{user['username']}")
                    print(f"   • ID: {user['id']}")
                    print(f"   • Teléfono: {user['phone']}")
                    print(f"\n{Colors.BOLD}📊 Estado:{Colors.ENDC} {Colors.GREEN}✅ Conectado{Colors.ENDC}")
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '2':
                    print_section_header("GRUPOS DISPONIBLES")
                    try:
                        groups = detector.get_user_groups()
                        if groups:
                            print_info("Grupos y canales disponibles:")
                            for i, group in enumerate(groups, 1):
                                print(f"  {i}. {group['name']} (ID: {group['id']})")
                        else:
                            print_warning("No se encontraron grupos o canales")
                    except Exception as e:
                        print_error(f"Error al obtener grupos: {e}")
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '3':
                    print_section_header("ESCANEAR GRUPO DE TELEGRAM")
                    group_id = input("ID o nombre del grupo: ").strip()
                    limit = input("Límite de mensajes [100]: ").strip()
                    limit = int(limit) if limit.isdigit() else 100
                    threshold = input("Umbral de similitud (0-64) [5]: ").strip()
                    threshold = int(threshold) if threshold else 5
                    
                    try:
                        detector.scan_telegram_group(group_id, limit, threshold)
                    except Exception as e:
                        print_error(f"Error al escanear grupo: {e}")
                    
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '4':
                    print_section_header("ESCANEAR MÚLTIPLES GRUPOS")
                    groups_input = input("IDs o nombres de grupos (separados por comas): ").strip()
                    groups = [g.strip() for g in groups_input.split(',')]
                    limit = input("Límite de mensajes por grupo [100]: ").strip()
                    limit = int(limit) if limit.isdigit() else 100
                    threshold = input("Umbral de similitud (0-64) [5]: ").strip()
                    threshold = int(threshold) if threshold else 5
                    
                    total_matches = []
                    for group in groups:
                        try:
                            matches = detector.scan_telegram_group(group, limit, threshold)
                            total_matches.extend(matches)
                            print()
                        except Exception as e:
                            print_error(f"Error al escanear grupo {group}: {e}")
                    
                    if total_matches:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"reporte_telegram_lote_{timestamp}.json"
                        print_section_header("EXPORTANDO RESULTADOS")
                        detector.export_matches(filename)
                    else:
                        print_warning("No se encontraron coincidencias en los grupos")
                    
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '5':
                    print_section_header("MONITOREAR GRUPO EN TIEMPO REAL")
                    group_id = input("ID o nombre del grupo: ").strip()
                    threshold = input("Umbral de similitud (0-64) [5]: ").strip()
                    threshold = int(threshold) if threshold else 5
                    
                    print_warning("Esta operación se ejecutará hasta que pulses Ctrl+C")
                    print_info("Al detener (Ctrl+C) se exportará automáticamente un reporte")
                    confirm = input("¿Continuar? (s/N): ").lower()
                    
                    if confirm == 's':
                        try:
                            detector.monitor_telegram_group(group_id, threshold)
                        except KeyboardInterrupt:
                            print_info("Monitorización detenida por el usuario")
                        except Exception as e:
                            print_error(f"Error en monitorización: {e}")
                    else:
                        print_info("Operación cancelada")
                    
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '6':
                    print_section_header("DETECCIONES DE TELEGRAM")
                    telegram_matches = [m for m in detector.detected_matches if 'Telegram' in m.get('source', '')]
                    
                    if telegram_matches:
                        print_info(f"Se encontraron {len(telegram_matches)} detecciones en Telegram:")
                        for match in telegram_matches:
                            print(f"\n  {Colors.BOLD}Target:{Colors.ENDC} {match['target_id']}")
                            print(f"  {Colors.BOLD}Descripción:{Colors.ENDC} {match['description']}")
                            print(f"  {Colors.BOLD}Fuente:{Colors.ENDC} {match['source']}")
                            print(f"  {Colors.BOLD}Fecha:{Colors.ENDC} {match['timestamp']}")
                    else:
                        print_warning("No hay detecciones de Telegram")
                    
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '7':
                    print_section_header("DESCONECTAR TELEGRAM")
                    confirm = input("¿Estás seguro de que quieres desconectar Telegram? (s/N): ").lower()
                    if confirm == 's':
                        detector.disconnect_telegram()
                    else:
                        print_info("Operación cancelada")
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '0':
                    break
                
                else:
                    print_error("Opción no válida")
                    time.sleep(1)
            
            else:
                # MENÚ CUANDO NO ESTÁ CONECTADO
                if choice == '1':
                    print_section_header("CONFIGURAR TELEGRAM")
                    if not TELETHON_AVAILABLE:
                        print_error("Telethon no está instalado.")
                        print_info("Instala con: pip install telethon")
                        input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                        continue
                    
                    api_id = input("API ID: ").strip()
                    api_hash = input("API Hash: ").strip()
                    phone = input("Número de teléfono: ").strip()
                    
                    if api_id and api_hash and phone:
                        detector.setup_telegram_client(api_id, api_hash, phone)
                    else:
                        print_error("Faltan datos de configuración")
                    
                    input(f"\n{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")
                
                elif choice == '0':
                    break
                
                else:
                    print_error("Opción no válida")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Volviendo al menú principal...{Colors.ENDC}")
            break
        except Exception as e:
            print_error(f"Error: {e}")
            input(f"{Colors.CYAN}Presiona ENTER para continuar...{Colors.ENDC}")

# ============================================================================
# FUNCIÓN PRINCIPAL (CLI)
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Sistema de Detección de Imágenes por Hash Perceptual con Telegram",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Iniciar en modo interactivo (menú visual)')
    parser.add_argument('--add-image', help='Agregar imagen objetivo (ruta o URL)')
    parser.add_argument('--add-hash', help='Agregar hash manualmente')
    parser.add_argument('--hash-type', default='phash', 
                       choices=['md5', 'phash', 'ahash', 'dhash', 'whash'],
                       help='Tipo de hash (para --add-hash)')
    parser.add_argument('--description', default='', help='Descripción de la imagen')
    parser.add_argument('--tags', help='Tags separados por comas')
    parser.add_argument('--scan', help='URL de página web a escanear (o archivo con URLs)')
    parser.add_argument('--check-image', help='Verificar una imagen específica (URL)')
    parser.add_argument('--threshold', type=int, default=5, 
                       help='Umbral de similitud (0-64, menor = más estricto)')
    parser.add_argument('--list', action='store_true', help='Listar hashes objetivo')
    parser.add_argument('--stats', action='store_true', help='Mostrar estadísticas')
    parser.add_argument('--reset-db', action='store_true', help='Borrar TODA la base de datos de hashes')
    
    # Opciones de Telegram
    parser.add_argument('--setup-telegram', action='store_true', help='Configurar cliente de Telegram')
    parser.add_argument('--api-id', help='API ID de Telegram')
    parser.add_argument('--api-hash', help='API Hash de Telegram')
    parser.add_argument('--phone', help='Número de teléfono para Telegram')
    parser.add_argument('--telegram-scan', help='Escanear grupo/canal de Telegram')
    parser.add_argument('--telegram-monitor', help='Monitorear grupo/canal de Telegram en tiempo real')
    parser.add_argument('--limit-messages', type=int, default=100, help='Límite de mensajes a escanear en Telegram')
    parser.add_argument('--list-groups', action='store_true', help='Listar grupos disponibles en Telegram')
    parser.add_argument('--telegram-status', action='store_true', help='Ver estado de conexión de Telegram')
    parser.add_argument('--disconnect-telegram', action='store_true', help='Desconectar Telegram')
    
    parser.add_argument('--no-banner', action='store_true', help='No mostrar banner ASCII')
    
    args = parser.parse_args()
    
    # Si no hay argumentos, mostrar banner y ayuda
    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        print(f"\n{Colors.YELLOW}💡 Tip:{Colors.ENDC} Usa {Colors.GREEN}--interactive{Colors.ENDC} para el menú visual")
        sys.exit(0)
    
    # Modo interactivo
    if args.interactive:
        interactive_menu()
        return
    
    # Mostrar banner (si no está deshabilitado)
    if not args.no_banner:
        print_banner()
    
    detector = ImageHashDetector()

    if args.reset_db:
        detector.reset_database()
        return
    
    if args.list:
        detector.list_targets()
    
    if args.stats:
        detector.show_stats()
    
    if args.add_image:
        print_section_header("AGREGANDO IMAGEN OBJETIVO")
        tags = args.tags.split(',') if args.tags else []
        detector.add_target_hash(args.add_image, args.description, tags)
    
    if args.add_hash:
        print_section_header("AGREGANDO HASH MANUAL")
        tags = args.tags.split(',') if args.tags else []
        detector.add_manual_hash(args.add_hash, args.hash_type, args.description, tags)
    
    if args.check_image:
        print_section_header("VERIFICANDO IMAGEN")
        detector.check_image(args.check_image, threshold=args.threshold)
    
    if args.scan:
        scan_target = args.scan
        urls_to_scan = []
        is_batch = False

        try:
            with open(scan_target, 'r') as f:
                urls_to_scan = [line.strip() for line in f if line.strip().startswith(('http://', 'https://'))]
            print_info(f"Leyendo {Colors.BOLD}{len(urls_to_scan)}{Colors.ENDC} URLs desde el archivo: {scan_target}")
            is_batch = True
        
        except FileNotFoundError:
            urls_to_scan.append(scan_target)

        for url in urls_to_scan:
            detector.scan_webpage(url, threshold=args.threshold)
            print()
            
        if detector.detected_matches:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_prefix = "reporte_scan_lote_" if is_batch else "reporte_scan_"
            filename = f"{filename_prefix}{timestamp}.json"
            print_section_header("EXPORTANDO RESULTADOS AUTOMÁTICAMENTE")
            detector.export_matches(filename)
        else:
            print_warning("Escaneo completado. No se encontraron coincidencias para exportar.")

    # Funcionalidades de Telegram
    if args.setup_telegram:
        if not TELETHON_AVAILABLE:
            print_error("Telethon no está disponible. Instala con: pip install telethon")
            return
            
        if args.api_id and args.api_hash and args.phone:
            detector.setup_telegram_client(args.api_id, args.api_hash, args.phone)
        else:
            print_error("Se necesitan --api-id, --api-hash y --phone para configurar Telegram")
    
    if args.telegram_status:
        status = detector.get_telegram_status()
        if status['connected']:
            user = status['user']
            print_section_header("ESTADO TELEGRAM")
            print(f"{Colors.GREEN}✅ Conectado{Colors.ENDC}")
            print(f"Usuario: {user['first_name']} {user['last_name'] or ''}")
            print(f"Username: @{user['username']}")
            print(f"Teléfono: {user['phone']}")
        else:
            print_section_header("ESTADO TELEGRAM")
            print(f"{Colors.RED}❌ No conectado{Colors.ENDC}")
    
    if args.disconnect_telegram:
        detector.disconnect_telegram()
    
    if args.list_groups:
        status = detector.get_telegram_status()
        if not status['connected']:
            print_error("Telegram no está configurado")
        else:
            groups = detector.get_user_groups()
            if groups:
                print_section_header("GRUPOS DE TELEGRAM")
                for group in groups:
                    print(f"  • {group['name']} (ID: {group['id']})")
            else:
                print_warning("No se encontraron grupos")
    
    if args.telegram_scan:
        status = detector.get_telegram_status()
        if not status['connected']:
            print_error("Telegram no está configurado")
        else:
            detector.scan_telegram_group(args.telegram_scan, args.limit_messages, args.threshold)
    
    if args.telegram_monitor:
        status = detector.get_telegram_status()
        if not status['connected']:
            print_error("Telegram no está configurado")
        else:
            print_warning("Iniciando monitorización en tiempo real. Presiona Ctrl+C para detener.")
            try:
                detector.monitor_telegram_group(args.telegram_monitor, args.threshold)
            except KeyboardInterrupt:
                print_info("Monitorización detenida")

if __name__ == "__main__":
    main()
