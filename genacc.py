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
# EMBEDDED WEB ASSETS (STANDALONE ALL-IN-ONE)
# ============================================
import base64
import gzip

EMBEDDED_ASSETS = {'index.html': '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', 'style.css': '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', 'script.js': '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', 'supabase.js': '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'}

def get_embedded_asset(filename):
    if filename in EMBEDDED_ASSETS:
        try:
            raw = base64.b64decode(EMBEDDED_ASSETS[filename])
            return gzip.decompress(raw).decode('utf-8')
        except Exception:
            return ""
    return ""

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
    emb = get_embedded_asset(filename)
    if emb:
        return emb
    return f"Error: File {filename} tidak ditemukan."


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
    Semua aset tertanam langsung di dalam genacc.py dan otomatis diekstrak jika belum ada.
    """
    for fn in ["index.html", "style.css", "script.js", "supabase.js"]:
        local_path = os.path.join(SCRIPT_DIR, fn)
        needs_write = False
        
        if not os.path.exists(local_path):
            needs_write = True
        elif fn == "script.js":
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    c = f.read()
                    if "crackCustomKey" not in c or "ljjzgddqbwpervtablgj" in c:
                        needs_write = True
            except Exception:
                needs_write = True
        elif fn == "index.html":
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    c = f.read()
                    if "create-crack-lic" not in c or "bottom-nav" not in c:
                        needs_write = True
            except Exception:
                needs_write = True
        elif fn == "style.css":
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    c = f.read()
                    if "bottom-nav" not in c:
                        needs_write = True
            except Exception:
                needs_write = True

        if needs_write:
            try:
                content = get_embedded_asset(fn)
                if content:
                    with open(local_path, "w", encoding="utf-8") as f:
                        f.write(content)
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
    if not ok or "create-crack-lic" not in content:
        content = get_embedded_asset("index.html") or fetch_github("index.html")
    return Response(content, mimetype='text/html')

@app.route('/style.css')
def style():
    content, ok = read_local("style.css")
    if not ok or "bottom-nav" not in content:
        content = get_embedded_asset("style.css") or fetch_github("style.css")
    return Response(content, mimetype='text/css')

@app.route('/script.js')
def script():
    content, ok = read_local("script.js")
    if not ok or "crackCustomKey" not in content:
        content = get_embedded_asset("script.js") or fetch_github("script.js")
    return Response(content, mimetype='application/javascript')

@app.route('/supabase.js')
def supabase_js():
    content, ok = read_local("supabase.js")
    if not ok:
        content = get_embedded_asset("supabase.js")
    if content:
        return Response(content, mimetype='application/javascript')
    return Response("/* CDN fallback */", mimetype='application/javascript')


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
