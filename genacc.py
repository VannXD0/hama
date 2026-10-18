#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SA SOCIETY - MEMBER PANEL & LICENSE MANAGER (CLI + WEB)
Support: Termux (Android) + Windows + Linux + Mac
Theme: Fiery Orange & Warm Amber
"""

import os
import sys
import time
import json
import uuid
import hashlib
import platform
import getpass
import threading
import webbrowser
import random
from datetime import datetime, timedelta
import ssl

try:
    _ssl_ctx = ssl._create_unverified_context()
    ssl._create_default_https_context = _ssl_ctx
except Exception:
    pass

try:
    import requests
    from flask import Flask, Response, jsonify, request
except ImportError as e:
    import subprocess
    print(f"\n[*] Dependensi belum lengkap di Termux ({e}). Menginstall otomatis...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "flask", "flask-cors"])
        import requests
        from flask import Flask, Response, jsonify, request
        print("[+] Sukses install dependensi!\n")
    except Exception:
        print("\n[!] Silakan jalankan perintah ini di Termux:")
        print("    pkg update && pkg install python -y && pip install requests flask flask-cors\n")
        sys.exit(1)

# Graceful CORS for Termux/environments where flask-cors isn't installed
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

# ============================================
# CONFIGURATION
# ============================================
SUPABASE_URL = "https://wleslngeddeshlbgwayn.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsZXNsbmdlZGRlc2hsYmd3YXluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk1NjA4MjIsImV4cCI6MjEwNTEzNjgyMn0."
    "9p_9WY6ZO73yVhMO4JF0FQVgdkDw2U7pZAKW0Ugy5B4"
)

# Crack License DB (nvsubfeqxfhwrsjuijhy)
CRACK_URL = "https://nvsubfeqxfhwrsjuijhy.supabase.co"
CRACK_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im52c3ViZmVxeGZod3JzanVpamh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNjg0NzUsImV4cCI6MjEwNjk0NDQ3NX0."
    "kkNJHhMYk2s5Nfonj3EOMixi7XQ4VU_U0zekhCkHBlk"
)

GITHUB_RAW = "https://raw.githubusercontent.com/VannXD0/hama/main"
PORT = 5000

CACHE = {}
CACHE_DURATION = 60

app = Flask(__name__)
if HAS_CORS:
    CORS(app)
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        return response

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

CURRENT_USER = {}   # stores active CLI session; shared with web via /api/session
FLASK_RUNNING = False

# ============================================
# COLORS & THEME (VIBRANT ORANGE & AMBER)
# ============================================
O_PRIMARY = "\033[38;5;208m"   # Vivid Orange
O_AMBER   = "\033[38;5;214m"   # Bright Glowing Amber
O_DEEP    = "\033[38;5;202m"   # Fiery Deep Orange
O_PEACH   = "\033[38;5;216m"   # Soft Warm Peach
C_WHITE   = "\033[97m"         # Crisp White
C_GRAY    = "\033[90m"         # Muted Gray
C_GREEN   = "\033[92m"         # Success Green
C_RED     = "\033[91m"         # Alert Red
C_BOLD    = "\033[1m"          # Bold text
C_RESET   = "\033[0m"          # Reset ANSI

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def secure_password_input(prompt="Password: "):
    """
    Cross-platform password input with * masking.
    - Windows: uses msvcrt char-by-char with * echo
    - Termux / Linux / macOS: uses termios + tty char-by-char with * echo
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()

    # Windows path — msvcrt available
    if os.name == 'nt':
        try:
            import msvcrt
            chars = []
            while True:
                ch = msvcrt.getwch()
                if ch in ('\r', '\n'):       # Enter
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    break
                elif ch == '\x03':           # Ctrl+C
                    sys.stdout.write('\n')
                    raise KeyboardInterrupt
                elif ch in ('\x08', '\x7f'): # Backspace
                    if chars:
                        chars.pop()
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                else:
                    chars.append(ch)
                    sys.stdout.write('*')
                    sys.stdout.flush()
            return ''.join(chars)
        except Exception:
            return input()
    else:
        # Termux / Linux / macOS: termios + tty with * echo
        try:
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            chars = []
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ('\r', '\n'):       # Enter
                        sys.stdout.write('\r\n')
                        sys.stdout.flush()
                        break
                    elif ch == '\x03':           # Ctrl+C
                        sys.stdout.write('\r\n')
                        sys.stdout.flush()
                        raise KeyboardInterrupt
                    elif ch in ('\x08', '\x7f'): # Backspace
                        if chars:
                            chars.pop()
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                    elif ch == '\x04':           # Ctrl+D (EOF)
                        break
                    else:
                        chars.append(ch)
                        sys.stdout.write('*')
                        sys.stdout.flush()
                return ''.join(chars)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            try:
                p = getpass.getpass('')
                return p if p else input()
            except Exception:
                return input()

def banner():
    clear_screen()
    try:
        cols = os.get_terminal_size().columns
    except Exception:
        cols = 60

    if cols < 64:
        # Compact mobile banner designed specifically for Termux portrait mode
        print(f"""{O_DEEP}
+======================================================+
|  {C_BOLD}{O_PRIMARY}[SA SOCIETY]{C_RESET}{O_DEEP} - MEMBER PANEL & LICENSE              |
|  {O_AMBER}Platform: Termux Android | Windows | Linux | Mac{O_DEEP}  |
+======================================================+{C_RESET}""")
    else:
        # Full desktop banner for wide terminals
        print(f"""{O_DEEP}
+==============================================================+
|                                                              |
|   {O_PRIMARY}███████╗ █████╗     ███████╗ ██████╗  ██████╗██╗███████╗{O_DEEP}   |
|   {O_PRIMARY}██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔════╝██║██╔════╝{O_DEEP}   |
|   {O_AMBER}███████╗███████║    ███████╗██║   ██║██║     ██║█████╗{O_DEEP}     |
|   {O_AMBER}╚════██║██╔══██║    ╚════██║██║   ██║██║     ██║██╔══╝{O_DEEP}     |
|   {O_PRIMARY}███████║██║  ██║    ███████║╚██████╔╝╚██████╗██║███████╗{O_DEEP}   |
|   {O_PRIMARY}╚══════╝╚═╝  ╚═╝    ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝{O_DEEP}   |
|                                                              |
|            {C_BOLD}{O_AMBER}SA SOCIETY - MEMBER PANEL & LICENSE{C_RESET}{O_DEEP}               |
+==============================================================+{C_RESET}
""")

# ============================================
# ACCURATE DEVICE DETECTION & FINGERPRINT
# ============================================
def get_device_info():
    """
    Sistem HWID Permanen & Akurat (Bener-bener Nempel ke Hardware Asli).
    - Windows: MachineGuid (Registry Cryptography) + BIOS Model + CPU Processor + C: Drive Volume Serial.
               Tidak akan berubah meski ganti Wi-Fi, Hotspot, VPN, atau update Windows.
    - Android/Termux: Hardware Serial + Chipset Board + Brand/Model + Persistent Device Seed.
    - Linux: Machine-ID + Product UUID.
    - macOS: IOPlatformUUID.
    Device model mencerminkan identitas perangkat fisik & user pemiliknya.
    """
    is_termux = bool(os.environ.get('PREFIX') and 'com.termux' in os.environ.get('PREFIX', '')) or os.path.exists('/data/data/com.termux')
    
    platform_name = "Unknown OS"
    device_model = "Unknown Device"
    raw_hwid_components = []

    # 1. WINDOWS
    if platform.system() == "Windows" and not is_termux:
        try:
            win_ver = sys.getwindowsversion()
            is_win11 = (win_ver.major == 10 and win_ver.build >= 22000) or win_ver.major > 10
            is_64bit = platform.machine().endswith('64') or '64' in platform.architecture()[0]
            arch_str = "64-bit" if is_64bit else "32-bit"
            platform_name = f"Windows 11 ({arch_str})" if is_win11 else f"Windows 10 ({arch_str})"
        except Exception:
            platform_name = f"Windows ({platform.release()})"

        # A. MachineGuid (Kunci registri instalasi unik Windows - 100% permanen)
        machine_guid = ""
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography')
            machine_guid, _ = winreg.QueryValueEx(k, 'MachineGuid')
        except Exception:
            pass

        # B. BIOS & Hardware Product Model
        vendor = ""
        model = ""
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\BIOS')
            vals = {winreg.EnumValue(k, i)[0]: winreg.EnumValue(k, i)[1] for i in range(winreg.QueryInfoKey(k)[1])}
            mfg = vals.get('SystemManufacturer', '').strip()
            family = vals.get('SystemFamily', '').strip()
            prod = vals.get('SystemProductName', '').strip()
            ver = vals.get('SystemVersion', '').strip()

            ignored = {'none', 'default string', 'system product name', 'to be filled by o.e.m.', ''}
            candidates = [x for x in [family, ver, prod] if x and x.lower() not in ignored]
            mname = candidates[0] if candidates else ''

            if mfg and mname:
                model = f"{mfg} {mname}".strip() if mfg.lower() not in mname.lower() else mname
            elif mfg:
                model = mfg
            elif mname:
                model = mname
            else:
                model = "PC / Laptop"
        except Exception:
            model = "PC / Laptop"

        # C. CPU Processor String
        cpu_name = ""
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0')
            cpu_name, _ = winreg.QueryValueEx(k, 'ProcessorNameString')
            cpu_name = cpu_name.strip()
        except Exception:
            pass

        # D. Volume Serial of System Drive (C:)
        vol_serial_str = ""
        try:
            import ctypes
            vol_serial = ctypes.c_ulong()
            ctypes.windll.kernel32.GetVolumeInformationW('C:\\', None, 0, ctypes.byref(vol_serial), None, None, None, 0)
            vol_serial_str = hex(vol_serial.value)
        except Exception:
            pass

        # E. Owner Tag (Mencerminkan device punya si admin/reseller)
        username = os.environ.get('USERNAME') or os.environ.get('USER') or ''
        comp_name = os.environ.get('COMPUTERNAME') or platform.node()
        owner_tag = f"[{username}]" if username else f"[{comp_name}]"
        device_model = f"{model} {owner_tag}".strip()

        raw_hwid_components = [
            "WIN-HWID",
            machine_guid or comp_name,
            model,
            cpu_name,
            vol_serial_str
        ]

    # 2. ANDROID (TERMUX)
    elif is_termux:
        try:
            rel = os.popen('getprop ro.build.version.release').read().strip()
            sdk = os.popen('getprop ro.build.version.sdk').read().strip()
            platform_name = f"Android {rel} [Termux]" if rel else "Android [Termux]"
        except Exception:
            platform_name = "Android [Termux]"

        brand = os.popen('getprop ro.product.brand').read().strip() or os.popen('getprop ro.product.manufacturer').read().strip()
        market = os.popen('getprop ro.product.marketname').read().strip()
        model_name = os.popen('getprop ro.product.model').read().strip()
        serial = os.popen('getprop ro.serialno').read().strip() or os.popen('getprop ro.boot.serialno').read().strip()
        board = os.popen('getprop ro.board.platform').read().strip() or os.popen('getprop ro.product.board').read().strip()

        if market:
            dev_name = f"{brand} {market}".strip() if brand and brand.lower() not in market.lower() else market
        elif brand and model_name:
            dev_name = f"{brand} {model_name}".strip() if brand.lower() not in model_name.lower() else model_name
        elif model_name:
            dev_name = model_name
        else:
            dev_name = "Android Device"

        device_model = f"{dev_name} [Termux]".strip()

        # Persistent Seed di storage privat Termux
        config_dir = os.path.expanduser("~/.sa_society")
        token_file = os.path.join(config_dir, "hardware.hwid")
        termux_seed = ""
        try:
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            if os.path.exists(token_file):
                with open(token_file, "r", encoding="utf-8") as f:
                    termux_seed = f.read().strip()
            if not termux_seed:
                termux_seed = str(uuid.uuid4())
                with open(token_file, "w", encoding="utf-8") as f:
                    f.write(termux_seed)
        except Exception:
            termux_seed = "termux_hwid_seed"

        raw_hwid_components = [
            "ANDROID-HWID",
            serial or "NO_SERIAL",
            board or "NO_BOARD",
            brand,
            model_name,
            termux_seed
        ]

    # 3. MACOS (DARWIN)
    elif platform.system() == "Darwin":
        try:
            mac_ver = os.popen('sw_vers -productVersion').read().strip()
            platform_name = f"macOS {mac_ver}" if mac_ver else "macOS"
        except Exception:
            platform_name = f"macOS ({platform.mac_ver()[0]})"

        try:
            hw_model = os.popen('sysctl -n hw.model').read().strip()
            device_model = f"{hw_model or platform.node()} [{os.environ.get('USER', 'Mac')}]"
        except Exception:
            device_model = f"{platform.node()} [{os.environ.get('USER', 'Mac')}]"

        mac_uuid = os.popen("ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/ { print $3; }'").read().strip().replace('"', '')
        raw_hwid_components = ["DARWIN-HWID", mac_uuid or platform.node(), platform.machine()]

    # 4. LINUX
    else:
        try:
            distro = "Linux"
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            distro = line.split('=', 1)[1].strip().strip('"')
                            break
            platform_name = distro
        except Exception:
            platform_name = f"Linux ({platform.release()})"

        vendor = ""
        product = ""
        try:
            if os.path.exists('/sys/devices/virtual/dmi/id/sys_vendor'):
                with open('/sys/devices/virtual/dmi/id/sys_vendor') as f:
                    vendor = f.read().strip()
            if os.path.exists('/sys/devices/virtual/dmi/id/product_name'):
                with open('/sys/devices/virtual/dmi/id/product_name') as f:
                    product = f.read().strip()
            base_model = f"{vendor} {product}".strip() if (vendor and product) else platform.node()
        except Exception:
            base_model = platform.node()

        device_model = f"{base_model} [{os.environ.get('USER', 'Linux')}]"

        machine_id = ""
        for mid_path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
            if os.path.exists(mid_path):
                try:
                    with open(mid_path, 'r') as f:
                        machine_id = f.read().strip()
                        if machine_id:
                            break
                except Exception:
                    pass

        raw_hwid_components = ["LINUX-HWID", machine_id or platform.node(), platform.machine()]

    # 5. HASIL AKHIR: SHA-256 FINGERPRINT
    raw_str = ":".join(str(c) for c in raw_hwid_components)
    fingerprint = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:32]

    # Simpan cache di file lokal agar konsisten
    try:
        config_dir = os.path.expanduser("~/.sa_society")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        hw_cache_file = os.path.join(config_dir, "device_id.json")
        with open(hw_cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "device_fingerprint": fingerprint,
                "device_model": device_model,
                "platform": platform_name,
                "raw_hwid": raw_str,
                "updated_at": str(datetime.now())
            }, f, indent=2)
    except Exception:
        pass

    return {
        "device_fingerprint": fingerprint,
        "device_model": device_model or "Unknown Device",
        "platform": platform_name
    }

# ============================================
# SUPABASE REST CLIENT
# ============================================
def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def authenticate_user(username, password):
    url = f"{SUPABASE_URL}/rest/v1/users"
    params = {
        "username": f"eq.{username}",
        "password": f"eq.{password}",
        "select": "id,username,role,token_quota,token_used,expired_at,device_fingerprint,device_model,platform"
    }
    try:
        res = requests.get(url, headers=get_supabase_headers(), params=params, timeout=10)
        if res.status_code == 200:
            users = res.json()
            if users and len(users) > 0:
                return users[0], None
            return None, "Username atau password salah!"
        else:
            return None, f"Database error ({res.status_code}): {res.text}"
    except Exception as e:
        return None, f"Gagal terhubung ke database: {str(e)}"

def update_user_device(user_id, update_data):
    url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
    try:
        res = requests.patch(url, headers=get_supabase_headers(), json=update_data, timeout=10)
        return res.status_code in [200, 204]
    except Exception:
        return False

# ============================================
# WEB SERVER & ASSET FETCHING (GITHUB RAW)
# ============================================
def fetch_github(filename):
    if filename in CACHE:
        cached_time, cached_content = CACHE[filename]
        if time.time() - cached_time < CACHE_DURATION:
            return cached_content
    
    # Try primary repository (VannXD0/hama) then fallback
    for repo_base in [GITHUB_RAW, "https://raw.githubusercontent.com/Xyr0Dev/hama/main"]:
        try:
            r = requests.get(f"{repo_base}/{filename}", timeout=10)
            if r.status_code == 200:
                CACHE[filename] = (time.time(), r.text)
                return r.text
        except Exception:
            continue
    return f"Error: File {filename} tidak ditemukan di repository GitHub."


# ── Local asset path (same folder as genacc.py) ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def read_local(filename):
    """Read a local asset file next to genacc.py."""
    path = os.path.join(SCRIPT_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read(), True
    except Exception:
        return None, False

def ensure_web_assets():
    """
    Pastikan semua file web (index.html, script.js, style.css, supabase.js)
    tersedia secara lokal di folder genacc.py agar tidak tergantung koneksi GitHub & anti-404.
    """
    files_to_check = {
        "script.js": "https://raw.githubusercontent.com/VannXD0/hama/main/script.js",
        "index.html": "https://raw.githubusercontent.com/VannXD0/hama/main/index.html",
        "style.css": "https://raw.githubusercontent.com/VannXD0/hama/main/style.css",
        "supabase.js": "https://raw.githubusercontent.com/VannXD0/hama/main/supabase.js"
    }

    for fn, url in files_to_check.items():
        local_path = os.path.join(SCRIPT_DIR, fn)
        needs_download = False
        
        if not os.path.exists(local_path):
            needs_download = True
        elif fn == "script.js":
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "ljjzgddqbwpervtablgj" in content or "crackCustomKey" not in content:
                        needs_download = True
            except Exception:
                needs_download = True
        elif fn == "index.html":
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "create-crack-lic" not in content or "bottom-nav" not in content:
                        needs_download = True
            except Exception:
                needs_download = True
        elif fn == "style.css":
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "bottom-nav" not in content:
                        needs_download = True
            except Exception:
                needs_download = True

        if needs_download:
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    text = r.text
                    if fn == "script.js":
                        text = text.replace("https://ljjzgddqbwpervtablgj.supabase.co", "https://wleslngeddeshlbgwayn.supabase.co")
                        text = text.replace("ljjzgddqbwpervtablgj", "wleslngeddeshlbgwayn")
                        text = text.replace("4FDByk8iEv3RWpx6t2dj7sgLn3DUqL3HQh-tvX0LPss", "9p_9WY6ZO73yVhMO4JF0FQVgdkDw2U7pZAKW0Ugy5B4")
                    with open(local_path, "w", encoding="utf-8") as f:
                        f.write(text)
            except Exception:
                pass

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def index():
    content, ok = read_local("index.html")
    if not ok:
        content = fetch_github("index.html")
        if "supabase.js" not in content:
            content = content.replace("</body>", '<script src="supabase.js"></script>\n<script src="script.js?v=termux_auto"></script>\n</body>')
        else:
            content = content.replace('src="script.js"', 'src="script.js?v=termux_auto"')
    return Response(content, mimetype='text/html')

@app.route('/style.css')
def style():
    content, ok = read_local("style.css")
    if not ok:
        content = fetch_github("style.css")
    return Response(content, mimetype='text/css')

@app.route('/script.js')
def script():
    content, ok = read_local("script.js")
    if not ok:
        content = fetch_github("script.js")
    
    # Auto-repair dead Supabase URL & Key dari GitHub
    content = content.replace("https://ljjzgddqbwpervtablgj.supabase.co", "https://wleslngeddeshlbgwayn.supabase.co")
    content = content.replace("ljjzgddqbwpervtablgj", "wleslngeddeshlbgwayn")
    content = content.replace("4FDByk8iEv3RWpx6t2dj7sgLn3DUqL3HQh-tvX0LPss", "9p_9WY6ZO73yVhMO4JF0FQVgdkDw2U7pZAKW0Ugy5B4")
    
    # Auto-login jika sudah authenticated via CLI
    if "applySession(cli);" not in content:
        content = content.replace("if (passInp) passInp.focus();", "applySession(cli);")

    # Auto-repair JWT missing dot jika ada
    if "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJpc3Mi" in content:
        content = content.replace(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJpc3Mi",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3Mi"
        )
    return Response(content, mimetype='application/javascript')

@app.route('/supabase.js')
def supabase_js():
    content, ok = read_local("supabase.js")
    if ok:
        return Response(content, mimetype='application/javascript')
    
    # Fallback ke CDN resmi agar tidak pernah 404 di Termux
    try:
        cdn_url = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.39.8/dist/umd/supabase.min.js"
        r = requests.get(cdn_url, timeout=10)
        if r.status_code == 200:
            try:
                with open(os.path.join(SCRIPT_DIR, "supabase.js"), "w", encoding="utf-8") as f:
                    f.write(r.text)
            except Exception:
                pass
            return Response(r.text, mimetype='application/javascript')
    except Exception:
        pass

    return Response(fetch_github("supabase.js"), mimetype='application/javascript')

@app.route('/<path:path>')
def static_files(path):
    content, ok = read_local(path)
    if not ok:
        content = fetch_github(path)
    mime = 'text/plain'
    if path.endswith('.html'):
        mime = 'text/html'
    elif path.endswith('.css'):
        mime = 'text/css'
    elif path.endswith('.js'):
        mime = 'application/javascript'
    elif path.endswith('.json'):
        mime = 'application/json'
    return Response(content, mimetype=mime)

@app.route('/api/session')
def api_session():
    """
    Return the active CLI session so the web panel can auto-login.
    If no user is logged in via CLI, returns {}.
    """
    if CURRENT_USER:
        return jsonify({
            "id":                 CURRENT_USER.get("id"),
            "username":           CURRENT_USER.get("username"),
            "role":               CURRENT_USER.get("role"),
            "token_quota":        CURRENT_USER.get("token_quota", 0),
            "token_used":         CURRENT_USER.get("token_used", 0),
            "device_fingerprint": CURRENT_USER.get("device_fingerprint"),
        })
    return jsonify({})

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    Direct web login endpoint executed locally on Flask server.
    Bypasses browser CORS, DNS issues, and ensures instant device binding.
    """
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username dan password tidak boleh kosong!"}), 400

    user, err = authenticate_user(username, password)
    if err or not user:
        return jsonify({"success": False, "error": err or "Username atau password salah!"}), 401

    if user.get('expired_at'):
        try:
            exp_str = user['expired_at'].replace('Z', '')
            exp_dt = datetime.fromisoformat(exp_str)
            if datetime.now() > exp_dt:
                return jsonify({"success": False, "error": f"Akun sudah kedaluwarsa sejak {exp_dt.strftime('%Y-%m-%d %H:%M')}. Hubungi admin."}), 403
        except Exception:
            pass

    dev_info = get_device_info()
    current_fp = dev_info['device_fingerprint']
    stored_fp = user.get('device_fingerprint')

    if not stored_fp:
        update_data = {
            "device_fingerprint": current_fp,
            "device_model": dev_info['device_model'],
            "platform": dev_info['platform']
        }
        update_user_device(user['id'], update_data)
        user.update(update_data)
    elif stored_fp != current_fp:
        return jsonify({
            "success": False,
            "error": f"Akses Ditolak: Akun ini terikat pada device lain ({user.get('device_model', 'Unknown')}). Hubungi Admin untuk reset."
        }), 403
    else:
        update_data = {
            "device_model": dev_info['device_model'],
            "platform": dev_info['platform']
        }
        update_user_device(user['id'], update_data)
        user.update(update_data)

    CURRENT_USER.clear()
    CURRENT_USER.update(user)

    return jsonify({
        "success": True,
        "user": {
            "id":                 user.get("id"),
            "username":           user.get("username"),
            "role":               user.get("role"),
            "token_quota":        user.get("token_quota", 0),
            "token_used":         user.get("token_used", 0),
            "device_fingerprint": user.get("device_fingerprint")
        }
    })

@app.route('/api/device')
def api_device():
    """
    Return current hardware device fingerprint and metadata
    so the web panel can enforce 1 account = 1 device binding.
    """
    return jsonify(get_device_info())

def open_browser():
    time.sleep(1.2)
    # Gunakan 127.0.0.1 agar resolusi IP loopback di Chrome Android selalu instan & tidak terhalang Private DNS
    url = f"http://127.0.0.1:{PORT}"
    is_termux = bool(os.environ.get('PREFIX') and 'com.termux' in os.environ.get('PREFIX', '')) or os.path.exists('/data/data/com.termux')
    if is_termux:
        ret = os.system(f"termux-open-url {url} 2>/dev/null")
        if ret != 0:
            os.system(f"am start -a android.intent.action.VIEW -d {url} >/dev/null 2>&1")
    else:
        try:
            webbrowser.open(url)
        except Exception:
            pass

def start_web_server():
    global FLASK_RUNNING, PORT
    if not FLASK_RUNNING:
        FLASK_RUNNING = True
        try:
            ensure_web_assets()
        except Exception:
            pass
        def _run_server():
            global PORT
            for p in range(5000, 5010):
                try:
                    PORT = p
                    app.run(host='0.0.0.0', port=p, debug=False, use_reloader=False)
                    break
                except Exception:
                    continue
        server_thread = threading.Thread(target=_run_server, daemon=True)
        server_thread.start()

# ============================================
# CLI INTERACTION & MENUS (ORANGE THEME)
# ============================================
def login_flow():
    banner()
    dev_info = get_device_info()
    print(f" {C_GRAY}[*] Platform :{C_RESET} {O_PEACH}{dev_info['platform']}{C_RESET}")
    print(f" {C_GRAY}[*] Device   :{C_RESET} {O_PEACH}{dev_info['device_model']}{C_RESET}")
    print(f" {C_GRAY}[*] HW-Hash  :{C_RESET} {C_GRAY}{dev_info['device_fingerprint'][:16]}...{C_RESET}\n")
    print(f"{C_BOLD}{O_AMBER}--- SILAHKAN LOGIN ---{C_RESET}\n")

    username = input(f"{O_PRIMARY}[?] Username: {C_RESET}").strip()
    if not username:
        print(f"{C_RED}[!] Username tidak boleh kosong.{C_RESET}")
        time.sleep(1.5)
        return None

    password = secure_password_input(f"{O_PRIMARY}[?] Password: {C_RESET}").strip()
    if not password:
        print(f"{C_RED}[!] Password tidak boleh kosong.{C_RESET}")
        time.sleep(1.5)
        return None

    print(f"\n{O_AMBER}[*] Menghubungkan ke Supabase...{C_RESET}")
    user, err = authenticate_user(username, password)

    if err or not user:
        print(f"{C_RED}[!] Login Gagal: {err or 'User tidak ditemukan'}{C_RESET}")
        input(f"\n{C_GRAY}Tekan Enter untuk mencoba lagi...{C_RESET}")
        return None

    # 1. Cek masa aktif akun (expired_at)
    if user.get('expired_at'):
        try:
            exp_str = user['expired_at'].replace('Z', '')
            exp_dt = datetime.fromisoformat(exp_str)
            if datetime.now() > exp_dt:
                print(f"{C_RED}[!] Akun sudah kedaluwarsa sejak {exp_dt.strftime('%Y-%m-%d %H:%M')}. Hubungi admin.{C_RESET}")
                input(f"\n{C_GRAY}Tekan Enter untuk kembali...{C_RESET}")
                return None
        except Exception:
            pass

    # 2. Device Binding Check (1 Akun = 1 Device)
    current_fp = dev_info['device_fingerprint']
    stored_fp = user.get('device_fingerprint')
    now_iso = datetime.utcnow().isoformat() + "Z"

    if not stored_fp:
        # First login -> Binding device sekarang
        print(f"{C_GREEN}[*] Mengikat akun ke device ini (First Login)...{C_RESET}")
        update_data = {
            "device_fingerprint": current_fp,
            "device_model": dev_info['device_model'],
            "platform": dev_info['platform']
        }
        update_user_device(user['id'], update_data)
        user.update(update_data)
    elif stored_fp != current_fp:
        # Device tidak cocok!
        if user.get('role') == 'admin':
            print(f"\n{O_AMBER}[!] PERINGATAN: Perbedaan Device terdeteksi pada Akun ADMIN.{C_RESET}")
            print(f"{C_GRAY}Terdaftar di : {user.get('device_model', 'Unknown')} ({user.get('platform', 'Unknown')}){C_RESET}")
            print(f"{C_GRAY}Device Baru  : {dev_info['device_model']} ({dev_info['platform']}){C_RESET}")
            confirm = input(f"\n{O_PRIMARY}[?] Reset & ikat akun Admin ke device ini sekarang? (y/n): {C_RESET}").strip().lower()
            if confirm == 'y':
                update_data = {
                    "device_fingerprint": current_fp,
                    "device_model": dev_info['device_model'],
                    "platform": dev_info['platform']
                }
                update_user_device(user['id'], update_data)
                user.update(update_data)
                print(f"{C_GREEN}[✓] Device binding Admin berhasil di-reset & diikat ke device ini!{C_RESET}")
            else:
                return None
        else:
            print(f"\n{C_RED}[!] AKSES DITOLAK: DEVICE BINDING MISMATCH{C_RESET}")
            print(f"{C_RED}Akun ini sudah terikat ke device lain!{C_RESET}")
            print(f"{C_GRAY}Terdaftar di : {user.get('device_model', 'Unknown')} ({user.get('platform', 'Unknown')}){C_RESET}")
            print(f"{C_GRAY}Device Anda  : {dev_info['device_model']} ({dev_info['platform']}){C_RESET}")
            print(f"{O_AMBER}[!] Hubungi Admin untuk reset device binding.{C_RESET}")
            input(f"\n{C_GRAY}Tekan Enter untuk kembali...{C_RESET}")
            return None
    else:
        # Device valid, update device info
        update_data = {
            "device_model": dev_info['device_model'],
            "platform": dev_info['platform']
        }
        update_user_device(user['id'], update_data)
        user.update(update_data)

    print(f"{C_GREEN}[✓] Login Berhasil! Selamat datang, {user['username']}.{C_RESET}")
    # Publish session to web panel via /api/session
    CURRENT_USER.clear()
    CURRENT_USER.update(user)
    time.sleep(1)
    return user

def show_account_info(user):
    banner()
    quota = user.get('token_quota', 0) or 0
    used = user.get('token_used', 0) or 0
    sisa = max(0, quota - used)
    role = (user.get('role') or 'member').upper()
    expired = user.get('expired_at') or 'Unlimited / Permanen'

    print(f"{C_BOLD}{O_AMBER}================ INFORMASI AKUN ================{C_RESET}\n")
    print(f" {O_PRIMARY}Username          :{C_RESET} {C_WHITE}{user.get('username')}{C_RESET}")
    print(f" {O_PRIMARY}Role              :{C_RESET} {C_GREEN if role == 'ADMIN' else O_AMBER}{role}{C_RESET}")
    
    if role == 'RESELLER':
        print(f" {O_PRIMARY}Token Quota       :{C_RESET} {quota}")
        print(f" {O_PRIMARY}Token Terpakai    :{C_RESET} {used}")
        print(f" {O_PRIMARY}Sisa Token        :{C_RESET} {C_GREEN if sisa > 0 else C_RED}{sisa}{C_RESET}")
    else:
        print(f" {O_PRIMARY}Token Quota       :{C_RESET} {C_GREEN}Unlimited (Admin){C_RESET}")

    print(f" {O_PRIMARY}Masa Aktif Akun   :{C_RESET} {expired}")
    print(f" {O_PRIMARY}Device Terdaftar  :{C_RESET} {O_PEACH}{user.get('device_model', 'N/A')}{C_RESET}")
    print(f" {O_PRIMARY}Platform          :{C_RESET} {O_PEACH}{user.get('platform', 'N/A')}{C_RESET}")
    print(f" {O_PRIMARY}Device Fingerprint:{C_RESET} {C_GRAY}{user.get('device_fingerprint', 'N/A')}{C_RESET}")
    print(f" {O_PRIMARY}Login Pertama     :{C_RESET} {user.get('first_login_at', 'N/A')}")
    print(f" {O_PRIMARY}Login Terakhir    :{C_RESET} {user.get('last_login_at', 'N/A')}")
    print(f"\n{C_BOLD}{O_AMBER}================================================{C_RESET}")
    input(f"\n{C_GRAY}Tekan Enter untuk kembali ke menu...{C_RESET}")

def web_panel_menu():
    banner()
    print(f"{C_BOLD}{O_AMBER}--- WEB PANEL & KEY GENERATOR ---{C_RESET}\n")
    start_web_server()
    print(f"{C_GREEN}[✓] Web Server aktif di background!{C_RESET}")
    print(f"{O_PRIMARY}[*] URL Local  :{C_RESET} {O_AMBER}http://localhost:{PORT}{C_RESET}")
    print(f"{O_PRIMARY}[*] URL IP     :{C_RESET} {O_AMBER}http://127.0.0.1:{PORT}{C_RESET}")

    is_termux = bool((os.environ.get('PREFIX') and 'com.termux' in os.environ.get('PREFIX', '')) or os.path.exists('/data/data/com.termux'))
    if is_termux:
        print(f"\n{O_PRIMARY}[*] Membuka browser Android...{C_RESET}")
        print(f"{C_GRAY}[i] Jika browser tidak otomatis terbuka, tap link:{C_RESET} {O_AMBER}http://127.0.0.1:{PORT}{C_RESET}")
    else:
        print(f"\n{O_PRIMARY}[*] Membuka browser otomatis...{C_RESET}")

    open_browser()
    print(f"\n{C_GRAY}Gunakan web panel untuk generate key dan kelola lisensi.{C_RESET}")
    print(f"{C_GRAY}(Server web tetap menyala selama aplikasi CLI berjalan){C_RESET}\n")
    input(f"{C_BOLD}{O_AMBER}Tekan Enter untuk kembali ke menu utama...{C_RESET}")

def quick_generate_crack_cli(user):
    import random
    banner()
    print(f"{C_BOLD}{O_AMBER}--- GENERATE LISENSI SA-CRACK (1-DEVICE LOCK) ---{C_RESET}\n")

    # Cek kuota token jika reseller
    role = user.get('role', 'member')
    quota = user.get('token_quota', 0)
    used = user.get('token_used', 0)
    if role == 'reseller':
        if used >= quota:
            print(f"{C_RED}[!] Kuota token Anda sudah habis ({used}/{quota})! Hubungi Admin.{C_RESET}")
            input(f"\n{C_GRAY}Tekan Enter untuk kembali...{C_RESET}")
            return
        print(f" {C_GRAY}[*] Sisa Token Anda:{C_RESET} {C_GREEN}{quota - used}{C_RESET} token\n")

    print(f" {O_PRIMARY}[1]{C_RESET} 3 Hari (Rp 1.000)")
    print(f" {O_PRIMARY}[2]{C_RESET} 7 Hari (Rp 2.000)")
    print(f" {O_PRIMARY}[3]{C_RESET} 30 Hari (Rp 5.000)")
    print(f" {O_PRIMARY}[4]{C_RESET} Lifetime / Permanen (Rp 20.000)")

    dur_choice = input(f"\n{O_PRIMARY}[?] Pilih durasi paket [1-4, default 3]: {C_RESET}").strip()
    dur_map = {"1": 3, "2": 7, "3": 30, "4": 9999}
    duration_days = dur_map.get(dur_choice, 30)
    price_map = {3: 1000, 7: 2000, 30: 5000, 9999: 20000}
    price = price_map.get(duration_days, 5000)

    nick = input(f"{O_PRIMARY}[?] Nickname Pengguna / Buyer: {C_RESET}").strip() or "VIP Member"

    count_str = input(f"{O_PRIMARY}[?] Jumlah Key yang ingin digenerate [default 1]: {C_RESET}").strip()
    if count_str.isdigit() and int(count_str) > 0:
        count = int(count_str)
    else:
        count = 1

    if role == 'reseller' and (used + count) > quota:
        print(f"\n{C_RED}[!] Kuota token tidak mencukupi! Butuh {count} token, sisa: {quota - used} token.{C_RESET}")
        input(f"\n{C_GRAY}Tekan Enter untuk kembali...{C_RESET}")
        return

    custom_key = input(f"{O_PRIMARY}[?] Custom Key (kosongkan untuk random 9-hex): {C_RESET}").strip().upper()

    chars = "0123456789ABCDEF"
    records = []
    generated_keys = []

    for i in range(count):
        if custom_key and count == 1:
            hex_part = custom_key
        elif custom_key:
            sub = "".join(random.choice(chars) for _ in range(4))
            hex_part = f"{custom_key}-{sub}"
        else:
            hex_part = "".join(random.choice(chars) for _ in range(9))

        full_key = f"SA-CRACK-{hex_part}"
        generated_keys.append(full_key)
        records.append({
            "license_key": full_key,
            "duration_days": duration_days,
            "status": "unused",
            "nickname": f"{nick} #{i+1}" if count > 1 else nick,
            "note": f"Generated via genacc.py CLI by {user.get('username')}",
            "price": price,
            "hwid": None
        })

    print(f"\n{O_AMBER}[*] Menyimpan {count} lisensi ke Supabase...{C_RESET}")
    url = f"{CRACK_URL}/rest/v1/licenses"
    headers = {
        "apikey": CRACK_KEY,
        "Authorization": f"Bearer {CRACK_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        resp = requests.post(url, json=records, headers=headers, timeout=15)
        if resp.status_code in (200, 201):
            # Potong kuota token reseller jika bukan admin
            if role == 'reseller':
                new_used = used + count
                patch_url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user['id']}"
                patch_hdr = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                }
                requests.patch(patch_url, json={"token_used": new_used}, headers=patch_hdr, timeout=5)
                user['token_used'] = new_used

            dur_label = 'Lifetime / Permanen' if duration_days >= 9999 else f'{duration_days} Hari'
            print(f"\n{C_GREEN}{C_BOLD}══════════════════ {count} LISENSI BERHASIL DIBUAT ══════════════════{C_RESET}")
            print(f" {C_WHITE}Durasi      :{C_RESET} {dur_label}")
            print(f" {C_WHITE}Harga/key   :{C_RESET} Rp {price:,}")
            print(f" {C_WHITE}Status      :{C_RESET} {C_GREEN}UNUSED (Siap dipakai di HP buyer){C_RESET}")
            print(f"{C_GRAY}─────────────────────────────────────────────────────────────{C_RESET}")
            for idx, k in enumerate(generated_keys, 1):
                print(f" {O_AMBER}[{idx:02d}]{C_RESET} {C_BOLD}{k}{C_RESET}")
            print(f"{C_GREEN}═════════════════════════════════════════════════════════════{C_RESET}")

            if count > 1:
                out_fn = f"crack_keys_{int(time.time())}.txt"
                try:
                    with open(out_fn, "w", encoding="utf-8") as fp:
                        fp.write("\n".join(generated_keys))
                    print(f"\n{C_GREEN}[✓] Semua key telah diexport ke: {out_fn}{C_RESET}")
                except Exception:
                    pass
        else:
            print(f"{C_RED}[!] Gagal membuat lisensi: {resp.text}{C_RESET}")
    except Exception as e:
        print(f"{C_RED}[!] Error koneksi ke server lisensi: {e}{C_RESET}")

    input(f"\n{C_GRAY}Tekan Enter untuk kembali ke menu...{C_RESET}")

def reset_device_binding_admin_cli(user):
    banner()
    print(f"{C_BOLD}{O_AMBER}--- RESET DEVICE BINDING MEMBER / RESELLER ---{C_RESET}\n")
    print(f"{O_AMBER}[*] Mengambil daftar akun dari database Supabase...{C_RESET}")
    url = f"{SUPABASE_URL}/rest/v1/users"
    params = {"select": "id,username,role,device_model,platform,device_fingerprint"}
    try:
        res = requests.get(url, headers=get_supabase_headers(), params=params, timeout=10)
        if res.status_code != 200:
            print(f"{C_RED}[!] Gagal mengambil data: {res.text}{C_RESET}")
            input(f"\n{C_GRAY}Tekan Enter untuk kembali...{C_RESET}")
            return
        users = res.json()
        if not users:
            print(f"{C_RED}[!] Tidak ada user terdaftar.{C_RESET}")
            input(f"\n{C_GRAY}Tekan Enter untuk kembali...{C_RESET}")
            return

        print(f"\n{C_GRAY}{'No':<4} {'Username':<15} {'Role':<10} {'Device Terikat':<32} {'Status Binding'}{C_RESET}")
        print(f"{C_GRAY}{'─'*78}{C_RESET}")
        for idx, u in enumerate(users, 1):
            fp = u.get('device_fingerprint')
            st = f"{C_GREEN}TERIKAT{C_RESET}" if fp else f"{C_GRAY}BEBAS (UNBOUND){C_RESET}"
            dev = u.get('device_model') or '—'
            print(f"[{idx:<2}] {u['username']:<15} {u.get('role','').upper():<10} {dev[:30]:<32} {st}")

        print(f"\n{C_GRAY}[0] Batal / Kembali ke Menu Utama{C_RESET}\n")
        pilih = input(f"{O_PRIMARY}[?] Pilih nomor akun yang ingin di-reset [0-{len(users)}]: {C_RESET}").strip()
        if not pilih or pilih == "0":
            return
        
        try:
            sel_idx = int(pilih) - 1
            if sel_idx < 0 or sel_idx >= len(users):
                print(f"{C_RED}[!] Nomor tidak valid.{C_RESET}")
                time.sleep(1)
                return
        except ValueError:
            print(f"{C_RED}[!] Masukkan angka yang valid.{C_RESET}")
            time.sleep(1)
            return

        target_user = users[sel_idx]
        confirm = input(f"\n{C_RED}[?] Yakin ingin reset binding device untuk akun '{target_user['username']}'? (y/n): {C_RESET}").strip().lower()
        if confirm == 'y':
            update_data = {
                "device_fingerprint": None,
                "device_model": None,
                "platform": None
            }
            ok = update_user_device(target_user['id'], update_data)
            if ok:
                print(f"\n{C_GREEN}[✓] Sukses! Device binding untuk '{target_user['username']}' telah di-reset.{C_RESET}")
                print(f"{C_GREEN}Akun tersebut sekarang bisa login dan mengikat device baru.{C_RESET}")
            else:
                print(f"{C_RED}[!] Gagal update database Supabase.{C_RESET}")
        else:
            print(f"{O_AMBER}[*] Reset dibatalkan.{C_RESET}")
    except Exception as e:
        print(f"{C_RED}[!] Error: {e}{C_RESET}")
    
    input(f"\n{C_GRAY}Tekan Enter untuk kembali ke menu...{C_RESET}")

def main_menu(user):
    is_admin = (user.get('role', '').lower() == 'admin')
    while True:
        banner()
        print(f"Halo, {C_WHITE}{user.get('username')}{C_RESET} | Role: {O_AMBER}{user.get('role', '').upper()}{C_RESET}\n")
        print(f"{C_BOLD}{O_DEEP}[ MENU UTAMA ]{C_RESET}")
        print(f"  {O_AMBER}[1]{C_RESET} Info Account")
        print(f"  {O_AMBER}[2]{C_RESET} Open Web Panel (Generate Key via Browser)")
        print(f"  {O_AMBER}[3]{C_RESET} Quick Generate SA-CRACK License (CLI)")
        print(f"  {O_AMBER}[4]{C_RESET} Switch / Relogin Akun")
        if is_admin:
            print(f"  {O_AMBER}[5]{C_RESET} Reset Device Binding Akun (Admin Tool)")
        print(f"  {O_AMBER}[0]{C_RESET} Keluar\n")

        valid_max = 5 if is_admin else 4
        pilihan = input(f"{O_PRIMARY}[?] Masukkan pilihan [0-{valid_max}]: {C_RESET}").strip()
        if pilihan == "1":
            show_account_info(user)
        elif pilihan == "2":
            web_panel_menu()
        elif pilihan == "3":
            quick_generate_crack_cli(user)
        elif pilihan == "4":
            CURRENT_USER.clear()   # invalidate web session before relogin
            return True
        elif is_admin and pilihan == "5":
            reset_device_binding_admin_cli(user)
        elif pilihan == "0":
            CURRENT_USER.clear()
            banner()
            print(f"{O_AMBER}[*] Keluar dari program. Terima kasih!{C_RESET}\n")
            sys.exit(0)
        else:
            print(f"{C_RED}[!] Pilihan tidak valid.{C_RESET}")
            time.sleep(1)

def main():
    while True:
        user = login_flow()
        if user:
            relogin = main_menu(user)
            if not relogin:
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C_RED}[!] Program dihentikan oleh user.{C_RESET}")
        sys.exit(0)
