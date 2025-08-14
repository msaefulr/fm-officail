import sqlite3
from pathlib import Path
import hashlib, os
from datetime import datetime
from urllib.parse import quote_plus

# Direktori aplikasi dan database
APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "data" / "hadroh.db"
UPLOAD_DIR = APP_DIR / "uploads"

# Nomor WhatsApp admin (default)
ADMIN_WA = os.environ.get("HADROH_ADMIN_WA", "6281234567890")

# --------------------------
# Fungsi koneksi database
# --------------------------
def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------
# Inisialisasi database
# --------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Tabel fasilitas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fasilitas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        kategori TEXT,
        kondisi TEXT,
        lokasi TEXT,
        foto TEXT
    );
    """)

    # Tabel keuangan
    cur.execute("""
    CREATE TABLE IF NOT EXISTS keuangan(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipe TEXT CHECK(tipe IN ('pemasukan','pengeluaran')) NOT NULL,
        kategori TEXT,
        jumlah REAL NOT NULL,
        tanggal TEXT NOT NULL,
        keterangan TEXT,
        bukti TEXT
    );
    """)

    # Tabel jadwal
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jadwal(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT NOT NULL,
        acara TEXT,
        lokasi TEXT,
        status TEXT CHECK(status IN ('kosong','terisi')) NOT NULL DEFAULT 'kosong'
    );
    """)

    # Tabel booking
    cur.execute("""
    CREATE TABLE IF NOT EXISTS booking(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pengundang TEXT NOT NULL,
        tanggal TEXT NOT NULL,
        lokasi TEXT,
        keterangan TEXT,
        status TEXT DEFAULT 'pending'
    );
    """)

    # Tabel user (tanpa seed default)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin','bendahara','anggota')) NOT NULL DEFAULT 'anggota'
    );
    """)

    conn.commit()
    conn.close()

# --------------------------
# Fungsi hash password
# --------------------------
def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def verify_password(plain, hashed):
    return sha256(plain) == hashed

# --------------------------
# Fungsi simpan upload file
# --------------------------
def save_upload(file, subdir: str):
    if file is None:
        return None
    folder = UPLOAD_DIR / subdir
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
    path = folder / name
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    return str(path.relative_to(APP_DIR))

# --------------------------
# Fungsi WA link
# --------------------------
def wa_link(phone: str, text: str) -> str:
    return f"https://wa.me/{phone}?text={quote_plus(text)}"

# --------------------------
# Format mata uang Rupiah
# --------------------------
def format_rp(n: float) -> str:
    try:
        return f"Rp {n:,.0f}".replace(",", ".")
    except:
        return "Rp 0"
