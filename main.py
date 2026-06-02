"""
main.py
=======
Entry point aplikasi Simple Social Media Platform.
Menginisialisasi database, menginstal dependensi jika perlu,
dan menjalankan aplikasi GUI.

Jalankan dengan: python main.py

Dependensi:
    - customtkinter  (pip install customtkinter)
    - Pillow         (pip install Pillow)  — opsional, untuk gambar
    - Python 3.9+
    - sqlite3        — sudah built-in

Arsitektur MVC ringan:
    main.py  → Entry point + inisialisasi
    gui.py   → View (semua tampilan)
    logic.py → Controller (business logic)
    data.py  → Model (database layer)
    models.py → Data classes (entitas)
"""

# =============================================================================
# MODUL 1: Input Output — print pesan status ke console
# MODUL 2: Variabel dan Tipe Data — konstanta dan tipe
# MODUL 4: Percabangan — validasi startup
# MODUL 6: Fungsi — fungsi main()
# MODUL 8: Class dan Object — semua digunakan melalui import
# MODUL 9: File/Database — inisialisasi SQLite di sini
# =============================================================================

import sys
import os


def check_dependencies() -> bool:
    """
    Periksa apakah dependensi yang dibutuhkan sudah tersedia.
    Jika belum, tampilkan instruksi instalasi.

    Returns:
        True jika semua dependensi tersedia, False jika ada yang kurang.
    """
    missing = []

    # Cek customtkinter
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    # Cek sqlite3 (seharusnya sudah built-in)
    try:
        import sqlite3
    except ImportError:
        missing.append("sqlite3")

    # Modul 4: Percabangan — jika ada yang missing
    if missing:
        print("=" * 55)
        print("❌ Dependensi berikut belum terinstal:")
        # Modul 5: Perulangan — tampilkan tiap missing package
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstal dengan perintah:")
        print("   pip install customtkinter")
        print("=" * 55)
        return False

    return True


def init_app():
    """
    Inisialisasi awal aplikasi:
        1. Buat folder data jika belum ada
        2. Inisialisasi database SQLite
        3. Pastikan file log ada
    """
    # Modul 9: File Handling — pastikan file/folder ada
    print("🚀 Menginisialisasi Social Media Platform...")

    # Buat database jika belum ada
    import data as db
    db.init_database()
    print("✅ Database SQLite siap.")

    # Buat file log jika belum ada (Modul 9: File I/O)
    if not os.path.exists("violation_log.txt"):
        with open("violation_log.txt", "w", encoding="utf-8") as f:
            f.write("=== VIOLATION LOG — SOCIAL MEDIA PLATFORM ===\n\n")
        print("✅ File log pelanggaran dibuat.")

    print("✅ Inisialisasi selesai. Memulai GUI...\n")


def main():
    """
    Fungsi utama: entry point aplikasi.
    Menjalankan seluruh flow startup dan menampilkan GUI.
    """
    print("=" * 55)
    print("  🌐  SIMPLE SOCIAL MEDIA PLATFORM")
    print("       UAS Prinsip Pemrograman 2025/2026")
    print("=" * 55)

    # Cek dependensi sebelum melanjutkan
    if not check_dependencies():
        sys.exit(1)

    # Inisialisasi database dan file pendukung
    init_app()

    # Import dan jalankan GUI
    # (import dilakukan di sini setelah check dependencies berhasil)
    from gui import SocialMediaApp

    # Modul 8: Class dan Object — instansiasi kelas utama
    app = SocialMediaApp()

    # Modul 1: Input Output — print konfirmasi ke console
    print("✅ Aplikasi berjalan. Tutup window untuk keluar.\n")

    # Mulai event loop Tkinter
    app.mainloop()

    print("\n👋 Aplikasi ditutup. Sampai jumpa!")


# Entry point Python standar
if __name__ == "__main__":
    main()