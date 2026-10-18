#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SA SOCIETY - ULTIMATE ADMIN PANEL v3.0
Full Support: Termux + Windows + Linux
Features:
- User & Reseller Management (wleslngeddeshlbgwayn)
- 1-Device HWID Reset for Accounts
- Crack License System (nvsubfeqxfhwrsjuijhy)
- Generate SA-CRACK-[HEX 9 KATA / CUSTOM]
- 1-Device Crack HWID Binding & Reset
- Real-time Stats & Revenue
"""

import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    os.system('chcp 65001 >nul 2>&1')
import json
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# ============================================
# SUPABASE CONFIGURATION
# ============================================
# 1. User & Account Auth DB
AUTH_URL = "https://wleslngeddeshlbgwayn.supabase.co"
AUTH_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsZXNsbmdlZGRlc2hsYmd3YXluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk1NjA4MjIsImV4cCI6MjEwNTEzNjgyMn0.9p_9WY6ZO73yVhMO4JF0FQVgdkDw2U7pZAKW0Ugy5B4"

# 2. Crack & Client License DB
CRACK_URL = "https://nvsubfeqxfhwrsjuijhy.supabase.co"
CRACK_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im52c3ViZmVxeGZod3JzanVpamh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzNjg0NzUsImV4cCI6MjEwNjk0NDQ3NX0.kkNJHhMYk2s5Nfonj3EOMixi7XQ4VU_U0zekhCkHBlk"

# ============================================
# TERMINAL COLORS
# ============================================
class C:
    GREEN  = '\033[92m'
    RED    = '\033[91m'
    YELLOW = '\033[93m'
    CYAN   = '\033[96m'
    WHITE  = '\033[97m'
    GRAY   = '\033[90m'
    ORANGE = '\033[38;5;208m'
    MAGENTA = '\033[95m'
    RESET  = '\033[0m'
    BOLD   = '\033[1m'

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

import ssl
try:
    _ssl_ctx = ssl._create_unverified_context()
    ssl._create_default_https_context = _ssl_ctx
except Exception:
    _ssl_ctx = None

def req_api(base_url, api_key, endpoint, method="GET", body=None, params=None):
    url = f"{base_url}/rest/v1/{endpoint}"
    if params:
        url += "?" + params

    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # 1. Coba pake library requests jika tersedia (Termux/Windows/Linux)
    try:
        import requests
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=12)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=body, timeout=12)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=body, timeout=12)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=12)
        else:
            r = requests.request(method, url, headers=headers, json=body, timeout=12)

        if r.status_code in (200, 201, 204):
            return (r.json() if r.content else {}), None
        return None, f"HTTP {r.status_code}: {r.text}"
    except ImportError:
        pass
    except Exception as e:
        pass

    # 2. Fallback pake urllib standar dengan bypass SSL cert
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx, timeout=12) as resp:
            content = resp.read().decode("utf-8")
            return (json.loads(content) if content else {}), None
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        return None, f"HTTP {e.code}: {err_msg}"
    except Exception as e:
        return None, str(e)

# ============================================
# BANNER
# ============================================
def banner():
    clear()
    print(f"""{C.ORANGE}{C.BOLD}
 +------------------------------------------------------------------+
 |   SA SOCIETY - ADMIN CONTROL CENTER // v3.0 (SA-CRACK)           |
 +------------------------------------------------------------------+{C.RESET}
 {C.GRAY}Auth DB  :{C.RESET} {C.CYAN}{AUTH_URL}{C.RESET}
 {C.GRAY}Crack DB :{C.RESET} {C.CYAN}{CRACK_URL}{C.RESET}
""")

# ============================================
# MENU UTAMA
# ============================================
def menu():
    print(f"{C.ORANGE}+==============================================================+{C.RESET}")
    print(f"|                     {C.BOLD}PILIH MENU MANAJEMEN{C.RESET}                     |")
    print(f"{C.ORANGE}+==============================================================+{C.RESET}")
    print(f"  {C.BOLD}{C.YELLOW}[ ACCOUNT & RESELLER CONTROL (AUTH DB) ]{C.RESET}")
    print(f"  {C.CYAN}[1]{C.RESET} Buat Akun Baru (Admin / Reseller)")
    print(f"  {C.CYAN}[2]{C.RESET} Daftar Semua Akun User & Reseller")
    print(f"  {C.CYAN}[3]{C.RESET} Reset Password Akun")
    print(f"  {C.CYAN}[4]{C.RESET} Reset Device Binding Akun (1-Device Unlock)")
    print(f"  {C.CYAN}[5]{C.RESET} Ubah / Tambah Quota Token Reseller")
    print(f"  {C.CYAN}[6]{C.RESET} Hapus Akun User")
    print()
    print(f"  {C.BOLD}{C.GREEN}[ CRACK LICENSE SYSTEM (NEBULA TOUCH / SA-CRACK) ]{C.RESET}")
    print(f"  {C.CYAN}[7]{C.RESET} Generate Lisensi SA-CRACK (9-Hex / Custom)")
    print(f"  {C.CYAN}[8]{C.RESET} Daftar Semua Lisensi Crack & Status HWID")
    print(f"  {C.CYAN}[9]{C.RESET} Reset HWID Lisensi Crack (1-Device Lock Reset)")
    print(f"  {C.CYAN}[10]{C.RESET} Ban / Unban Lisensi Crack")
    print(f"  {C.CYAN}[11]{C.RESET} Hapus Lisensi Crack")
    print()
    print(f"  {C.RED}[0]{C.RESET} Keluar")
    print(f"{C.ORANGE}+==============================================================+{C.RESET}")

# ============================================
# 1. BUAT AKUN BARU
# ============================================
def create_account():
    print(f"\n{C.YELLOW}{C.BOLD}[+] BUAT AKUN BARU{C.RESET}\n")
    print(f"  {C.CYAN}[1]{C.RESET} Admin (Unlimited Token)")
    print(f"  {C.CYAN}[2]{C.RESET} Reseller (Pakai Quota Token)")
    
    role_choice = input(f"\n{C.CYAN}[?] Pilih Role [1/2]: {C.RESET}").strip()
    if role_choice == "1":
        role = "admin"
    elif role_choice == "2":
        role = "reseller"
    else:
        print(f"{C.RED}[!] Role tidak valid.{C.RESET}")
        return

    username = input(f"{C.CYAN}[?] Username: {C.RESET}").strip()
    password = input(f"{C.CYAN}[?] Password: {C.RESET}").strip()

    if not username or not password:
        print(f"{C.RED}[!] Username dan password wajib diisi.{C.RESET}")
        return

    exp_input = input(f"{C.CYAN}[?] Masa Aktif Akun (hari, default 365, 0 = unlimited): {C.RESET}").strip()
    try:
        exp_days = int(exp_input) if exp_input else 365
    except ValueError:
        exp_days = 365

    expired_at = None
    if exp_days > 0:
        expired_at = (datetime.now() + timedelta(days=exp_days)).isoformat()

    token_quota = 0
    if role == "reseller":
        quota_input = input(f"{C.CYAN}[?] Quota Token Lisensi (default 20): {C.RESET}").strip()
        try:
            token_quota = int(quota_input) if quota_input else 20
        except ValueError:
            token_quota = 20

    data = {
        "username": username,
        "password": password,
        "role": role,
        "token_quota": token_quota,
        "token_used": 0,
        "expired_at": expired_at,
        "device_fingerprint": None,
        "device_model": None,
        "platform": None
    }

    res, err = req_api(AUTH_URL, AUTH_KEY, "users", method="POST", body=data)
    if err:
        print(f"\n{C.RED}[!] Gagal membuat akun: {err}{C.RESET}")
    else:
        print(f"\n{C.GREEN}{C.BOLD}[+] AKUN BERHASIL DIBUAT!{C.RESET}")
        print(f"    Username : {username}")
        print(f"    Password : {password}")
        print(f"    Role     : {role.upper()}")
        print(f"    Quota    : {token_quota if role == 'reseller' else 'Unlimited'}")
        print(f"    Expired  : {expired_at[:19] if expired_at else 'Unlimited'}")

# ============================================
# 2. LIST SEMUA AKUN
# ============================================
def list_accounts():
    print(f"\n{C.YELLOW}{C.BOLD}[*] MEMUAT DAFTAR AKUN DARI SUPABASE...{C.RESET}\n")
    data, err = req_api(AUTH_URL, AUTH_KEY, "users", params="select=*&order=id.asc")
    if err:
        print(f"{C.RED}[!] Gagal memuat data: {err}{C.RESET}")
        return

    if not data:
        print(f"{C.RED}[!] Belum ada akun terdaftar.{C.RESET}")
        return

    print(f"{C.ORANGE}+----+------------------+----------+--------+---------------------+-------------------------+{C.RESET}")
    print(f"| No | Username         | Role     | Quota  | Expired             | Device Terikat          |")
    print(f"{C.ORANGE}+----+------------------+----------+--------+---------------------+-------------------------+{C.RESET}")

    for i, u in enumerate(data, 1):
        uname = (u.get('username') or '')[:16]
        role = (u.get('role') or '')[:8]
        if role == 'reseller':
            quota = f"{u.get('token_used', 0)}/{u.get('token_quota', 0)}"
        else:
            quota = "INF"
        exp = u.get('expired_at') or 'Unlimited'
        if exp != 'Unlimited':
            exp = exp[:19].replace('T', ' ')
        dev = u.get('device_model') or '[ Belum Terikat ]'
        dev = dev[:23]

        print(f"| {i:<2} | {uname:<16} | {role:<8} | {quota:<6} | {exp:<19} | {dev:<23} |")

    print(f"{C.ORANGE}+----+------------------+----------+--------+---------------------+-------------------------+{C.RESET}")

# ============================================
# 3. RESET PASSWORD AKUN
# ============================================
def reset_password():
    data, err = req_api(AUTH_URL, AUTH_KEY, "users", params="select=id,username,role&order=id.asc")
    if err or not data:
        print(f"{C.RED}[!] Gagal memuat data akun.{C.RESET}")
        return

    print(f"\n{C.YELLOW}{C.BOLD}[?] Pilih Akun untuk Reset Password:{C.RESET}\n")
    for i, u in enumerate(data, 1):
        print(f"  {C.CYAN}[{i}]{C.RESET} {u['username']} ({u['role']})")

    pilihan = input(f"\n{C.CYAN}[?] Nomor akun (0 batal): {C.RESET}").strip()
    if pilihan == "0" or not pilihan.isdigit():
        return

    idx = int(pilihan) - 1
    if idx < 0 or idx >= len(data):
        print(f"{C.RED}[!] Pilihan tidak valid.{C.RESET}")
        return

    target = data[idx]
    new_pass = input(f"{C.CYAN}[?] Masukkan Password Baru untuk '{target['username']}': {C.RESET}").strip()
    if not new_pass:
        print(f"{C.RED}[!] Password tidak boleh kosong.{C.RESET}")
        return

    _, err = req_api(AUTH_URL, AUTH_KEY, f"users?id=eq.{target['id']}", method="PATCH", body={"password": new_pass})
    if err:
        print(f"{C.RED}[!] Gagal reset password: {err}{C.RESET}")
    else:
        print(f"{C.GREEN}[+] Password '{target['username']}' berhasil diubah jadi: {new_pass}{C.RESET}")

# ============================================
# 4. RESET DEVICE BINDING AKUN
# ============================================
def reset_device():
    data, err = req_api(AUTH_URL, AUTH_KEY, "users", params="select=id,username,device_model,platform,device_fingerprint&device_fingerprint=not.is.null")
    if err:
        print(f"{C.RED}[!] Gagal memuat: {err}{C.RESET}")
        return

    if not data:
        print(f"\n{C.YELLOW}[i] Tidak ada akun yang sedang terikat hardware device.{C.RESET}")
        return

    print(f"\n{C.YELLOW}{C.BOLD}[?] Akun yang Sedang Terikat Hardware:{C.RESET}\n")
    for i, u in enumerate(data, 1):
        dev = u.get('device_model') or 'Unknown'
        plat = u.get('platform') or 'Unknown'
        print(f"  {C.CYAN}[{i}]{C.RESET} {u['username']} -> {dev} ({plat})")

    pilihan = input(f"\n{C.CYAN}[?] Nomor akun yang mau di-reset HWID (0 batal): {C.RESET}").strip()
    if pilihan == "0" or not pilihan.isdigit():
        return

    idx = int(pilihan) - 1
    if idx < 0 or idx >= len(data):
        print(f"{C.RED}[!] Pilihan tidak valid.{C.RESET}")
        return

    target = data[idx]
    update_data = {
        "device_fingerprint": None,
        "device_model": None,
        "platform": None
    }
    _, err = req_api(AUTH_URL, AUTH_KEY, f"users?id=eq.{target['id']}", method="PATCH", body=update_data)
    if err:
        print(f"{C.RED}[!] Gagal reset device: {err}{C.RESET}")
    else:
        print(f"{C.GREEN}[+] Device lock akun '{target['username']}' berhasil direset! Akun bisa login di device baru.{C.RESET}")

# ============================================
# 5. UBAH QUOTA TOKEN RESELLER
# ============================================
def edit_reseller_quota():
    data, err = req_api(AUTH_URL, AUTH_KEY, "users", params="select=id,username,token_quota,token_used&role=eq.reseller")
    if err or not data:
        print(f"{C.YELLOW}[i] Belum ada akun reseller terdaftar.{C.RESET}")
        return

    print(f"\n{C.YELLOW}{C.BOLD}[?] Pilih Reseller untuk Ubah Token:{C.RESET}\n")
    for i, u in enumerate(data, 1):
        print(f"  {C.CYAN}[{i}]{C.RESET} {u['username']} (Quota: {u.get('token_quota', 0)}, Terpakai: {u.get('token_used', 0)})")

    pilihan = input(f"\n{C.CYAN}[?] Nomor reseller (0 batal): {C.RESET}").strip()
    if pilihan == "0" or not pilihan.isdigit():
        return

    idx = int(pilihan) - 1
    if idx < 0 or idx >= len(data):
        print(f"{C.RED}[!] Pilihan tidak valid.{C.RESET}")
        return

    target = data[idx]
    new_quota = input(f"{C.CYAN}[?] Masukkan Quota Token Baru (sekarang {target.get('token_quota', 0)}): {C.RESET}").strip()
    reset_used = input(f"{C.CYAN}[?] Reset token terpakai jadi 0? (y/n, default n): {C.RESET}").strip().lower()

    patch_data = {"token_quota": int(new_quota)} if new_quota.isdigit() else {}
    if reset_used == 'y':
        patch_data["token_used"] = 0

    if not patch_data:
        print(f"{C.RED}[!] Tidak ada perubahan.{C.RESET}")
        return

    _, err = req_api(AUTH_URL, AUTH_KEY, f"users?id=eq.{target['id']}", method="PATCH", body=patch_data)
    if err:
        print(f"{C.RED}[!] Gagal update quota: {err}{C.RESET}")
    else:
        print(f"{C.GREEN}[+] Token reseller '{target['username']}' berhasil diupdate!{C.RESET}")

# ============================================
# 6. HAPUS AKUN
# ============================================
def delete_account():
    data, err = req_api(AUTH_URL, AUTH_KEY, "users", params="select=id,username,role&order=id.asc")
    if err or not data:
        print(f"{C.RED}[!] Gagal memuat akun.{C.RESET}")
        return

    print(f"\n{C.YELLOW}{C.BOLD}[?] Pilih Akun yang Mau Dihapus:{C.RESET}\n")
    for i, u in enumerate(data, 1):
        print(f"  {C.CYAN}[{i}]{C.RESET} {u['username']} ({u['role']})")

    pilihan = input(f"\n{C.CYAN}[?] Nomor akun (0 batal): {C.RESET}").strip()
    if pilihan == "0" or not pilihan.isdigit():
        return

    idx = int(pilihan) - 1
    if idx < 0 or idx >= len(data):
        print(f"{C.RED}[!] Pilihan tidak valid.{C.RESET}")
        return

    target = data[idx]
    confirm = input(f"{C.RED}[!] Yakin ingin menghapus permanen '{target['username']}'? (y/n): {C.RESET}").strip().lower()
    if confirm != 'y':
        print(f"{C.YELLOW}[i] Dibatalkan.{C.RESET}")
        return

    _, err = req_api(AUTH_URL, AUTH_KEY, f"users?id=eq.{target['id']}", method="DELETE")
    if err:
        print(f"{C.RED}[!] Gagal menghapus: {err}{C.RESET}")
    else:
        print(f"{C.GREEN}[+] Akun '{target['username']}' berhasil dihapus permanen.{C.RESET}")

# ============================================
# 7. GENERATE LISENSI SA-CRACK
# ============================================
def generate_hex_9():
    chars = "0123456789ABCDEF"
    return "".join(random.choice(chars) for _ in range(9))

def generate_crack_license():
    print(f"\n{C.GREEN}{C.BOLD}[+] GENERATE LISENSI SA-CRACK (1-DEVICE LOCK){C.RESET}\n")
    print(f"  {C.CYAN}[1]{C.RESET} 3 Hari (Rp 1.000)")
    print(f"  {C.CYAN}[2]{C.RESET} 7 Hari (Rp 2.000)")
    print(f"  {C.CYAN}[3]{C.RESET} 30 Hari (Rp 5.000)")
    print(f"  {C.CYAN}[4]{C.RESET} Lifetime / Permanen (Rp 20.000)")

    dur_choice = input(f"\n{C.CYAN}[?] Pilih Paket Durasi [1-4, default 3]: {C.RESET}").strip()
    dur_map = {"1": 3, "2": 7, "3": 30, "4": 9999}
    duration_days = dur_map.get(dur_choice, 30)

    price_map = {3: 1000, 7: 2000, 30: 5000, 9999: 20000}
    price = price_map.get(duration_days, 5000)

    nick = input(f"{C.CYAN}[?] Nickname Pengguna / Buyer: {C.RESET}").strip() or "VIP Member"
    custom_key = input(f"{C.CYAN}[?] Custom Key (kosongkan untuk 9-Hex acak): {C.RESET}").strip().upper()

    if custom_key:
        hex_part = custom_key
    else:
        hex_part = generate_hex_9()

    full_key = f"SA-CRACK-{hex_part}"

    owner = input(f"{C.CYAN}[?] Pemilik Storage / Username (default admin): {C.RESET}").strip() or "admin"

    body = {
        "license_key": full_key,
        "duration_days": duration_days,
        "status": "unused",
        "nickname": nick,
        "note": f"by {owner}",
        "price": price,
        "hwid": None
    }

    print(f"\n{C.YELLOW}[*] Menyimpan lisensi ke database Supabase...{C.RESET}")
    res, err = req_api(CRACK_URL, CRACK_KEY, "licenses", method="POST", body=body)

    if err:
        print(f"{C.RED}[!] Gagal generate: {err}{C.RESET}")
    else:
        print(f"\n{C.GREEN}{C.BOLD}================== LISENSI BERHASIL DIBUAT =================={C.RESET}")
        print(f" {C.WHITE}License Key :{C.RESET} {C.ORANGE}{C.BOLD}{full_key}{C.RESET}")
        print(f" {C.WHITE}Storage     :{C.RESET} {C.CYAN}{owner}{C.RESET} (Tersimpan di storage user ini)")
        print(f" {C.WHITE}Nickname    :{C.RESET} {nick}")
        print(f" {C.WHITE}Durasi      :{C.RESET} {'Lifetime / Permanen' if duration_days >= 9999 else f'{duration_days} Hari'}")
        print(f" {C.WHITE}Harga       :{C.RESET} Rp {price:,}")
        print(f" {C.WHITE}Status      :{C.RESET} {C.GREEN}UNUSED (Siap diaktivasi di HP buyer){C.RESET}")
        print(f"{C.GREEN}============================================================={C.RESET}")

# ============================================
# 8. LIST SEMUA LISENSI CRACK (DENGAN STORAGE FILTER)
# ============================================
def list_crack_licenses():
    print(f"\n{C.YELLOW}{C.BOLD}[?] Opsi Tampilan Storage:{C.RESET}")
    filter_user = input(f"{C.CYAN}[?] Filter Storage User / Reseller (kosongkan untuk Semua Storage): {C.RESET}").strip()

    params = "select=*&order=id.desc&limit=50"
    if filter_user:
        params += f"&note=ilike.*{filter_user}*"

    print(f"\n{C.YELLOW}[*] Memuat lisensi dari Supabase...{C.RESET}\n")
    data, err = req_api(CRACK_URL, CRACK_KEY, "licenses", params=params)
    if err:
        print(f"{C.RED}[!] Gagal memuat lisensi: {err}{C.RESET}")
        return

    if not data:
        print(f"{C.YELLOW}[i] Tidak ada lisensi untuk filter storage ini.{C.RESET}")
        return

    print(f"{C.ORANGE}+----+-------------------------+--------------------+----------------+---------+----------+----------------------------------+{C.RESET}")
    print(f"| No | License Key             | Nickname           | Storage Owner  | Durasi  | Status   | HWID Device Terkunci             |")
    print(f"{C.ORANGE}+----+-------------------------+--------------------+----------------+---------+----------+----------------------------------+{C.RESET}")

    for i, lic in enumerate(data, 1):
        key = (lic.get('license_key') or '')[:23]
        nick = (lic.get('nickname') or '')[:18]
        note = lic.get('note') or 'admin'
        owner = note.replace('Generated by ', '').replace('by ', '').replace('via SA Admin CLI', 'admin').strip()[:14]
        dur = 'Life' if lic.get('duration_days', 0) >= 9999 else f"{lic.get('duration_days')}D"
        status = lic.get('status', 'unused')
        hwid = lic.get('hwid') or '[ Unbound ]'
        hwid = hwid[:32]

        status_color = C.GREEN if status == 'active' else (C.YELLOW if status == 'unused' else C.RED)

        print(f"| {i:<2} | {key:<23} | {nick:<18} | {owner:<14} | {dur:<7} | {status_color}{status:<8}{C.RESET} | {hwid:<32} |")

    print(f"{C.ORANGE}+----+-------------------------+--------------------+----------------+---------+----------+----------------------------------+{C.RESET}")

# ============================================
# 9. RESET HWID LISENSI CRACK (1-DEVICE UNLOCK)
# ============================================
def reset_crack_hwid():
    query = input(f"\n{C.CYAN}[?] Masukkan License Key / Nickname untuk Reset HWID: {C.RESET}").strip()
    if not query:
        return

    params = f"select=*&or=(license_key.ilike.*{query}*,nickname.ilike.*{query}*)"
    data, err = req_api(CRACK_URL, CRACK_KEY, "licenses", params=params)

    if err or not data:
        print(f"{C.RED}[!] Lisensi tidak ditemukan.{C.RESET}")
        return

    print(f"\n{C.YELLOW}[*] Lisensi ditemukan:{C.RESET}")
    for i, lic in enumerate(data, 1):
        print(f"  {C.CYAN}[{i}]{C.RESET} {lic['license_key']} | Nick: {lic.get('nickname')} | HWID: {lic.get('hwid') or '[None]'}")

    pilihan = input(f"\n{C.CYAN}[?] Pilih nomor untuk reset HWID (0 batal): {C.RESET}").strip()
    if pilihan == "0" or not pilihan.isdigit():
        return

    idx = int(pilihan) - 1
    if idx < 0 or idx >= len(data):
        return

    target = data[idx]
    update_data = {
        "hwid": None,
        "status": "unused",
        "activated_at": None
    }

    _, err = req_api(CRACK_URL, CRACK_KEY, f"licenses?id=eq.{target['id']}", method="PATCH", body=update_data)
    if err:
        print(f"{C.RED}[!] Gagal reset HWID: {err}{C.RESET}")
    else:
        print(f"\n{C.GREEN}[+] HWID untuk key '{target['license_key']}' BERHASIL DIRESET!{C.RESET}")
        print(f"{C.GREEN}    Status kembali ke UNUSED. Pembeli bisa aktivasi di HP lain.{C.RESET}")

# ============================================
# 10. BAN / UNBAN LISENSI CRACK
# ============================================
def toggle_ban_license():
    query = input(f"\n{C.CYAN}[?] Masukkan License Key untuk Ban/Unban: {C.RESET}").strip()
    if not query:
        return

    data, err = req_api(CRACK_URL, CRACK_KEY, "licenses", params=f"select=*&license_key=ilike.*{query}*")
    if err or not data:
        print(f"{C.RED}[!] Lisensi tidak ditemukan.{C.RESET}")
        return

    target = data[0]
    new_status = "active" if target.get("status") == "banned" else "banned"

    _, err = req_api(CRACK_URL, CRACK_KEY, f"licenses?id=eq.{target['id']}", method="PATCH", body={"status": new_status})
    if err:
        print(f"{C.RED}[!] Gagal update status: {err}{C.RESET}")
    else:
        print(f"{C.GREEN}[+] Status '{target['license_key']}' diubah menjadi: {new_status.upper()}{C.RESET}")

# ============================================
# 11. HAPUS LISENSI CRACK
# ============================================
def delete_crack_license():
    query = input(f"\n{C.CYAN}[?] Masukkan License Key yang Mau Dihapus: {C.RESET}").strip()
    if not query:
        return

    data, err = req_api(CRACK_URL, CRACK_KEY, "licenses", params=f"select=*&license_key=ilike.*{query}*")
    if err or not data:
        print(f"{C.RED}[!] Lisensi tidak ditemukan.{C.RESET}")
        return

    target = data[0]
    confirm = input(f"{C.RED}[!] Hapus permanen key '{target['license_key']}'? (y/n): {C.RESET}").strip().lower()
    if confirm != 'y':
        return

    _, err = req_api(CRACK_URL, CRACK_KEY, f"licenses?id=eq.{target['id']}", method="DELETE")
    if err:
        print(f"{C.RED}[!] Gagal menghapus: {err}{C.RESET}")
    else:
        print(f"{C.GREEN}[+] Key '{target['license_key']}' berhasil dihapus dari database.{C.RESET}")

# ============================================
# MAIN LOOP
# ============================================
def main():
    while True:
        banner()
        menu()
        choice = input(f"\n{C.CYAN}[>] Pilih menu [0-11]: {C.RESET}").strip()

        if choice == "1":
            create_account()
        elif choice == "2":
            list_accounts()
        elif choice == "3":
            reset_password()
        elif choice == "4":
            reset_device()
        elif choice == "5":
            edit_reseller_quota()
        elif choice == "6":
            delete_account()
        elif choice == "7":
            generate_crack_license()
        elif choice == "8":
            list_crack_licenses()
        elif choice == "9":
            reset_crack_hwid()
        elif choice == "10":
            toggle_ban_license()
        elif choice == "11":
            delete_crack_license()
        elif choice == "0":
            print(f"\n{C.GREEN}[+] Keluar. SA SOCIETY PROTECTED.{C.RESET}\n")
            sys.exit(0)
        else:
            print(f"{C.RED}[!] Pilihan tidak valid!{C.RESET}")

        print()
        input(f"{C.YELLOW}[>] Tekan Enter untuk kembali ke menu...{C.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.RED}[!] Program dihentikan oleh user.{C.RESET}")
        sys.exit(0)
