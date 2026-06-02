"""
logic.py
========
Business logic layer — semua komputasi, algoritma, dan aturan bisnis.
Tidak ada akses langsung ke GUI atau database (melalui data.py saja).

Modul yang diimplementasikan:
    - Modul 3: Operator (feed ranking formula)
    - Modul 4: Percabangan (validasi, filter)
    - Modul 5: Perulangan (parsing hashtag, filter loop)
    - Modul 6: Fungsi (semua fungsi di file ini)
    - Modul 7: List/Dictionary (struktur data)
"""

import re
import csv
import os
from datetime import datetime
from typing import List, Tuple, Dict

import data as db

# =============================================================================
# MODUL 2: Variabel dan Tipe Data — konstanta konfigurasi sistem
# =============================================================================

# Daftar kata kasar yang akan difilter (dapat diperluas)
BANNED_WORDS: List[str] = [
    "bajingan", "bangsat", "brengsek", "sialan", "keparat",
    "babi", "anjing", "goblok", "idiot", "tolol",
    "stupid", "idiot", "damn", "hell", "crap",
]

# Konfigurasi karma per aktivitas
KARMA_RULES: Dict[str, int] = {
    "post_created": 5,
    "post_liked":   1,   # karma untuk pemilik post yang di-like
    "commented":    2,   # karma untuk komentator
    "post_saved":   1,
    "followed":     1,   # karma untuk yang di-follow
}

# Batasan validasi
MIN_PASSWORD_LENGTH: int = 8
MAX_POST_LENGTH: int = 500
MAX_COMMENT_LENGTH: int = 300


# =============================================================================
# VALIDASI INPUT (Modul 4: Percabangan | Modul 1: Input Output)
# =============================================================================

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validasi kekuatan password.
    Aturan: minimal 8 karakter, harus ada huruf dan angka.

    Args:
        password: Password yang akan divalidasi

    Returns:
        Tuple (valid: bool, pesan: str)
    """
    # Percabangan bertingkat untuk setiap aturan
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password minimal {MIN_PASSWORD_LENGTH} karakter."

    has_letter = False
    has_digit  = False

    # Modul 5: Perulangan — iterasi setiap karakter
    for char in password:
        if char.isalpha():
            has_letter = True
        if char.isdigit():
            has_digit = True

    if not has_letter:
        return False, "Password harus mengandung huruf."
    if not has_digit:
        return False, "Password harus mengandung angka."

    return True, "Password valid."


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validasi format username.
    Aturan: 3-20 karakter, hanya huruf, angka, dan underscore.

    Args:
        username: Username yang akan divalidasi

    Returns:
        Tuple (valid: bool, pesan: str)
    """
    if not username or len(username.strip()) == 0:
        return False, "Username tidak boleh kosong."
    if len(username) < 3:
        return False, "Username minimal 3 karakter."
    if len(username) > 20:
        return False, "Username maksimal 20 karakter."
    # Regex: hanya huruf, angka, underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username hanya boleh huruf, angka, dan underscore."
    return True, "Username valid."


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validasi format email.

    Args:
        email: Email yang akan divalidasi

    Returns:
        Tuple (valid: bool, pesan: str)
    """
    if not email or len(email.strip()) == 0:
        return False, "Email tidak boleh kosong."
    # Regex sederhana untuk format email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Format email tidak valid."
    return True, "Email valid."


def validate_post_content(content: str) -> Tuple[bool, str]:
    """
    Validasi isi postingan.

    Args:
        content: Isi postingan

    Returns:
        Tuple (valid: bool, pesan: str)
    """
    if not content or len(content.strip()) == 0:
        return False, "Konten postingan tidak boleh kosong."
    if len(content) > MAX_POST_LENGTH:
        return False, f"Postingan maksimal {MAX_POST_LENGTH} karakter."
    return True, "Konten valid."


# =============================================================================
# CONTENT FILTER SIMULATION (Fitur Opsional d)
# Modul 2: String | Modul 4: Conditional | Modul 9: File I/O
# =============================================================================

def filter_content(text: str) -> Tuple[str, bool]:
    """
    Filter kata kasar dalam teks dan ganti dengan ***.
    Tidak case-sensitive.

    Args:
        text: Teks yang akan difilter

    Returns:
        Tuple (filtered_text: str, has_violation: bool)
    """
    filtered_text = text
    has_violation = False

    # Modul 5: Perulangan — iterasi setiap kata kasar
    for word in BANNED_WORDS:
        # re.IGNORECASE = case-insensitive matching
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(filtered_text):
            # Ganti dengan *** sepanjang kata
            replacement = "*" * len(word)
            filtered_text = pattern.sub(replacement, filtered_text)
            has_violation = True

    return filtered_text, has_violation


def save_violation_to_file(username: str, original: str, filtered: str):
    """
    Simpan log pelanggaran ke file teks (Modul 9: File I/O).

    Args:
        username: Username pelanggar
        original: Teks asli
        filtered: Teks setelah difilter
    """
    try:
        # Modul 9: File Handling — tulis ke file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"[{timestamp}] USER: {username}\n"
            f"  ORIGINAL : {original}\n"
            f"  FILTERED : {filtered}\n"
            f"  {'─' * 50}\n"
        )
        with open("violation_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[save_violation_to_file] Error: {e}")


# =============================================================================
# HASHTAG PARSER & TREND TRACKER (Fitur Opsional b)
# Modul 2: String | Modul 5: Perulangan | Modul 7: Dict
# =============================================================================

def parse_hashtags(text: str) -> List[str]:
    """
    Ekstrak semua #hashtag dari teks postingan.
    Menggunakan regex untuk mendeteksi kata setelah #.

    Args:
        text: Teks postingan

    Returns:
        List hashtag unik (tanpa #, lowercase)

    Example:
        >>> parse_hashtags("Belajar #Python dan #coding hari ini #python")
        ['python', 'coding']
    """
    # Regex: temukan semua kata yang diawali #
    raw_tags = re.findall(r'#(\w+)', text)

    # Hilangkan duplikat sambil pertahankan urutan (dict trick)
    seen = {}
    unique_tags = []
    # Modul 5: Perulangan — iterasi hasil regex
    for tag in raw_tags:
        tag_lower = tag.lower()
        if tag_lower not in seen:
            seen[tag_lower] = True
            unique_tags.append(tag_lower)

    return unique_tags


def get_top_trending(limit: int = 5) -> List[dict]:
    """
    Ambil Top N hashtag trending dari database.

    Args:
        limit: Jumlah hashtag yang dikembalikan

    Returns:
        List dict {tag, frequency}
    """
    return db.get_trending_hashtags(limit)


# =============================================================================
# FEED RANKING ALGORITHM (Fitur Opsional a)
# Modul 3: Operator | Modul 5: Perulangan | Modul 7: List/Dict
# =============================================================================

def calculate_feed_score(likes: int, comments: int, created_at_str: str) -> float:
    """
    Hitung feed ranking score sesuai formula UAS:
        skor = (likes × 2) + (comments × 3) + recency_weight

    Args:
        likes      : Jumlah like pada post
        comments   : Jumlah komentar pada post
        created_at_str: Waktu posting (string)

    Returns:
        Score sebagai float

    Penjelasan formula:
        - likes × 2    : Like bernilai 2 poin
        - comments × 3 : Komentar lebih berharga (mendorong diskusi)
        - recency_weight: Poin tambahan untuk post yang baru
    """
    try:
        created = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
        hours_old = (datetime.now() - created).total_seconds() / 3600
        # Recency weight: mulai dari 100, berkurang 2 poin per jam
        recency_weight = max(0.0, 100.0 - (hours_old * 2))
    except Exception:
        recency_weight = 50.0

    # Modul 3: Operator aritmatika
    score = (likes * 2) + (comments * 3) + recency_weight
    return round(score, 2)


def sort_feed_by_score(posts: List[dict]) -> List[dict]:
    """
    Urutkan daftar post berdasarkan score (descending).

    Args:
        posts: List dictionary postingan

    Returns:
        List postingan terurut
    """
    # Modul 5: Perulangan (implisit dalam sorted)
    # Modul 3: Operator — akses key score
    return sorted(posts, key=lambda p: p.get("score", 0), reverse=True)


# =============================================================================
# REPUTATION / KARMA SYSTEM (Fitur Opsional c)
# Modul 8: Class | Modul 4: Percabangan | Modul 3: Operator
# =============================================================================

def award_karma(user_id: int, action: str):
    """
    Berikan poin karma kepada pengguna berdasarkan aksi yang dilakukan.

    Args:
        user_id: ID pengguna yang mendapat karma
        action : Jenis aksi (key dari KARMA_RULES)
    """
    # Modul 4: Percabangan — cek apakah action ada di aturan
    if action in KARMA_RULES:
        points = KARMA_RULES[action]
        db.update_karma(user_id, points, action)


def get_badge_for_karma(karma: int) -> str:
    """
    Tentukan badge berdasarkan poin karma.

    Args:
        karma: Poin karma pengguna

    Returns:
        Nama badge sebagai string

    Badge System:
        - Beginner   : 0 - 49 karma
        - Active User: 50 - 199 karma
        - Influencer : 200 - 499 karma
        - Social Star: 500+ karma
    """
    # Modul 4: Percabangan bertingkat
    if karma >= 500:
        return "⭐ Social Star"
    elif karma >= 200:
        return "🔥 Influencer"
    elif karma >= 50:
        return "✅ Active User"
    else:
        return "🌱 Beginner"


def get_karma_progress(karma: int) -> Tuple[int, int, str]:
    """
    Hitung progress karma menuju badge berikutnya.

    Args:
        karma: Karma saat ini

    Returns:
        Tuple (karma_saat_ini, target_berikutnya, nama_badge_berikutnya)
    """
    # Modul 7: Tuple — kembalikan multiple nilai
    thresholds = [(50, "Active User"), (200, "Influencer"), (500, "Social Star")]
    for threshold, badge_name in thresholds:
        if karma < threshold:
            return karma, threshold, badge_name
    return karma, karma, "Social Star (Max)"


# =============================================================================
# EXPORT & REPORTING (Dashboard Analitik)
# Modul 9: File Handling | Modul 5: Perulangan | Modul 7: Dict
# =============================================================================

def export_analytics_txt(filename: str = "analytics_report.txt") -> Tuple[bool, str]:
    """
    Export laporan analitik lengkap ke file TXT.

    Args:
        filename: Nama file output

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    try:
        engagement = db.get_engagement_analytics()
        trending   = db.get_trending_hashtags(10)
        users      = db.get_user_activity_summary()
        timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Modul 9: File Handling — tulis ke file
        with open(filename, "w", encoding="utf-8") as f:
            # Header laporan
            f.write("=" * 60 + "\n")
            f.write("    LAPORAN ANALITIK SOCIAL MEDIA PLATFORM\n")
            f.write(f"    Digenerate: {timestamp}\n")
            f.write("=" * 60 + "\n\n")

            # Seksi 1: Engagement Score per Post
            f.write("[ ENGAGEMENT SCORE PER POST ]\n")
            f.write("-" * 60 + "\n")
            # Modul 5: Perulangan — iterasi data engagement
            for i, item in enumerate(engagement, 1):
                f.write(f"{i:2}. @{item['username']}: {item['content_preview'][:40]}...\n")
                f.write(f"    Likes: {item['likes']} | Comments: {item['comments']} "
                        f"| Saves: {item['saves']} | Score: {item['engagement_score']}\n")
            f.write("\n")

            # Seksi 2: Trending Hashtags
            f.write("[ TOP TRENDING HASHTAGS ]\n")
            f.write("-" * 60 + "\n")
            for i, tag in enumerate(trending, 1):
                f.write(f"{i:2}. #{tag['tag']} — {tag['frequency']} kali digunakan\n")
            f.write("\n")

            # Seksi 3: User Activity Summary
            f.write("[ USER ACTIVITY SUMMARY ]\n")
            f.write("-" * 60 + "\n")
            for i, user in enumerate(users, 1):
                f.write(
                    f"{i:2}. @{user['username']} [{user['badge']}] "
                    f"Karma: {user['karma']} | Posts: {user['total_posts']} "
                    f"| Comments: {user['total_comments']} "
                    f"| Followers: {user['followers']}\n"
                )

            f.write("\n" + "=" * 60 + "\n")
            f.write("    Akhir Laporan\n")
            f.write("=" * 60 + "\n")

        return True, f"Laporan berhasil disimpan ke '{filename}'."
    except Exception as e:
        return False, f"Gagal export TXT: {e}"


def export_analytics_csv(filename: str = "analytics_report.csv") -> Tuple[bool, str]:
    """
    Export laporan analitik ke file CSV.

    Args:
        filename: Nama file output CSV

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    try:
        engagement = db.get_engagement_analytics()
        users      = db.get_user_activity_summary()

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Sheet 1: Engagement
            writer.writerow(["POST ENGAGEMENT REPORT"])
            writer.writerow(["Post ID", "Username", "Content Preview",
                             "Likes", "Comments", "Saves", "Engagement Score"])
            # Modul 5: Perulangan — tulis setiap baris
            for item in engagement:
                writer.writerow([
                    item["post_id"],
                    item["username"],
                    item["content_preview"],
                    item["likes"],
                    item["comments"],
                    item["saves"],
                    item["engagement_score"],
                ])

            writer.writerow([])  # Baris kosong pemisah

            # Sheet 2: User Activity
            writer.writerow(["USER ACTIVITY SUMMARY"])
            writer.writerow(["User ID", "Username", "Role", "Karma", "Badge",
                             "Total Posts", "Total Comments",
                             "Likes Given", "Followers", "Following"])
            for user in users:
                writer.writerow([
                    user["user_id"],
                    user["username"],
                    user["role"],
                    user["karma"],
                    user["badge"],
                    user["total_posts"],
                    user["total_comments"],
                    user["total_likes_given"],
                    user["followers"],
                    user["following"],
                ])

        return True, f"Data berhasil disimpan ke '{filename}'."
    except Exception as e:
        return False, f"Gagal export CSV: {e}"


# =============================================================================
# SMART SEARCH (Bonus)
# Modul 2: String | Modul 4: Conditional | Modul 7: List
# =============================================================================

def smart_search(query: str, search_type: str = "all") -> dict:
    """
    Pencarian cerdas: partial match, case-insensitive di semua entitas.

    Args:
        query      : Kata kunci pencarian
        search_type: 'all' | 'users' | 'posts' | 'hashtags'

    Returns:
        Dictionary {users: [...], posts: [...], hashtags: [...]}
    """
    results = {"users": [], "posts": [], "hashtags": []}

    if not query or len(query.strip()) == 0:
        return results

    query = query.strip().lower()  # Case-insensitive: lowercase semua

    # Modul 4: Percabangan — cari berdasarkan tipe
    if search_type in ("all", "users"):
        results["users"] = db.search_users(query)

    if search_type in ("all", "posts"):
        results["posts"] = db.search_posts(query)

    if search_type in ("all", "hashtags"):
        try:
            import sqlite3
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tag, frequency FROM hashtags
                WHERE tag LIKE ? ORDER BY frequency DESC LIMIT 10
            """, (f"%{query}%",))
            rows = cursor.fetchall()
            conn.close()
            results["hashtags"] = [dict(r) for r in rows]
        except Exception:
            results["hashtags"] = []

    return results


def process_new_post(user_id: int, content: str) -> Tuple[bool, str, int]:
    """
    Proses pembuatan post baru: filter konten, parse hashtag, simpan ke DB,
    beri karma, catat log jika ada pelanggaran.

    Args:
        user_id: ID pembuat post
        content: Isi postingan asli

    Returns:
        Tuple (sukses: bool, pesan: str, post_id: int)
    """
    # Validasi konten
    valid, msg = validate_post_content(content)
    if not valid:
        return False, msg, 0

    # Filter konten kasar
    filtered_content, has_violation = filter_content(content)

    # Parse hashtag dari konten asli
    hashtags = parse_hashtags(content)

    # Simpan ke database
    success, message, post_id = db.create_post(
        user_id, content, filtered_content, hashtags, has_violation
    )

    if success:
        # Beri karma untuk membuat post
        award_karma(user_id, "post_created")

        # Jika ada pelanggaran, catat log
        if has_violation:
            user = db.get_user_by_id(user_id)
            username = user.username if user else "unknown"
            db.add_violation_log(user_id, post_id, content, filtered_content)
            save_violation_to_file(username, content, filtered_content)
            message += " (Konten mengandung kata tidak pantas dan telah difilter.)"

    return success, message, post_id