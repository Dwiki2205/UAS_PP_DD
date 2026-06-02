"""
data.py
=======
Database layer menggunakan SQLite.
Menangani seluruh operasi CRUD ke database (Modul 9: File/Database).
Semua query SQL dikelola di sini agar logic dan GUI tetap bersih.
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Tuple
from models import User, Post, Comment, Community, Reaction, FriendRequest, ViolationLog

# =============================================================================
# MODUL 9: File Handling / Database — seluruh file ini adalah implementasi modul 9
# MODUL 7: List/Tuple/Dictionary — hasil query dikembalikan sebagai list/dict
# =============================================================================

DB_PATH = "social_media.db"


def get_connection() -> sqlite3.Connection:
    """
    Buat dan kembalikan koneksi SQLite.
    row_factory diset agar hasil query bisa diakses seperti dictionary.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Akses kolom by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    """
    Hash password menggunakan SHA-256.

    Args:
        password: Password plaintext

    Returns:
        String hex digest dari password
    """
    return hashlib.sha256(password.encode()).hexdigest()


# =============================================================================
# INISIALISASI DATABASE — CREATE TABLE
# =============================================================================

def init_database():
    """
    Buat seluruh tabel database jika belum ada.
    Dipanggil sekali saat aplikasi pertama kali dijalankan.

    Tabel yang dibuat:
        users, posts, comments, communities, community_members,
        post_hashtags, hashtags, likes, reactions, saves,
        follows, friend_requests, violation_logs, karma_history
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Tabel Users ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            role       TEXT DEFAULT 'user' CHECK(role IN ('user','moderator','admin')),
            bio        TEXT DEFAULT '',
            karma      INTEGER DEFAULT 0,
            badge      TEXT DEFAULT 'Beginner',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            is_active  INTEGER DEFAULT 1
        )
    """)

    # --- Tabel Posts ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            post_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            content    TEXT NOT NULL,
            score      REAL DEFAULT 0.0,
            is_filtered INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Comments ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id    INTEGER NOT NULL,
            user_id    INTEGER NOT NULL,
            content    TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Communities ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS communities (
            community_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT UNIQUE NOT NULL,
            description  TEXT DEFAULT '',
            creator_id   INTEGER NOT NULL,
            created_at   TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (creator_id) REFERENCES users(user_id)
        )
    """)

    # --- Tabel Community Members ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_members (
            community_id INTEGER,
            user_id      INTEGER,
            joined_at    TEXT DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (community_id, user_id),
            FOREIGN KEY (community_id) REFERENCES communities(community_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Hashtags ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hashtags (
            hashtag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag        TEXT UNIQUE NOT NULL,
            frequency  INTEGER DEFAULT 0
        )
    """)

    # --- Tabel Post-Hashtag (Many-to-Many) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_hashtags (
            post_id    INTEGER,
            hashtag_id INTEGER,
            PRIMARY KEY (post_id, hashtag_id),
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (hashtag_id) REFERENCES hashtags(hashtag_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Likes ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            like_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id    INTEGER NOT NULL,
            user_id    INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Reactions ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reactions (
            reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            emoji       TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Saves ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saves (
            save_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id    INTEGER NOT NULL,
            user_id    INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Follows ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            follower_id  INTEGER,
            following_id INTEGER,
            created_at   TEXT DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (follower_id, following_id),
            FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (following_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Friend Requests ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friend_requests (
            request_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id   INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status      TEXT DEFAULT 'pending' CHECK(status IN ('pending','accepted','rejected')),
            created_at  TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(sender_id, receiver_id),
            FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Violation Logs ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violation_logs (
            log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            post_id    INTEGER,
            original   TEXT NOT NULL,
            filtered   TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # --- Tabel Karma History ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS karma_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            points     INTEGER NOT NULL,
            reason     TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    _seed_default_users()


def _seed_default_users():
    """
    Isi data awal: akun admin, moderator, dan user demo.
    Hanya dijalankan jika tabel users masih kosong.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        # Data seed: (username, password_plain, email, role)
        seeds = [
            ("admin",     "Admin123",   "admin@social.id",     "admin"),
            ("moderator1","Mod12345",   "mod@social.id",       "moderator"),
            ("alice",     "Alice123",   "alice@social.id",     "user"),
            ("bob",       "Bob12345",   "bob@social.id",       "user"),
            ("charlie",   "Charlie1",   "charlie@social.id",   "user"),
        ]
        for username, pwd, email, role in seeds:
            cursor.execute("""
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, ?)
            """, (username, hash_password(pwd), email, role))

        conn.commit()

        # Buat beberapa post demo
        cursor.execute("SELECT user_id, username FROM users")
        users = cursor.fetchall()
        demo_posts = [
            (users[2]["user_id"], "Halo semua! Ini postingan pertama saya 🎉 #halo #pertama"),
            (users[3]["user_id"], "Python itu menyenangkan! #python #coding #programming"),
            (users[4]["user_id"], "Hari ini belajar CustomTkinter #tkinter #gui #python"),
            (users[2]["user_id"], "Siapa yang suka kopi? ☕ #kopi #pagi #lifestyle"),
            (users[3]["user_id"], "Semangat belajar! 💪 #belajar #motivasi #kampus"),
        ]
        for uid, content in demo_posts:
            cursor.execute("""
                INSERT INTO posts (user_id, content) VALUES (?, ?)
            """, (uid, content))

        conn.commit()
    conn.close()


# =============================================================================
# CRUD: USERS
# =============================================================================

def create_user(username: str, password: str, email: str, role: str = "user") -> Tuple[bool, str]:
    """
    Daftarkan pengguna baru ke database.

    Args:
        username: Nama pengguna (unik)
        password: Password plaintext (akan di-hash)
        email   : Email (unik)
        role    : Role pengguna

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        """, (username, hash_password(password), email, role))
        conn.commit()
        conn.close()
        return True, "Registrasi berhasil!"
    except sqlite3.IntegrityError as e:
        # Tangkap error duplikat username/email
        if "username" in str(e):
            return False, "Username sudah digunakan."
        elif "email" in str(e):
            return False, "Email sudah digunakan."
        return False, f"Error: {e}"
    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"


def get_user_by_login(username: str, password: str) -> Optional[User]:
    """
    Validasi login dan kembalikan objek User jika berhasil.

    Args:
        username: Nama pengguna
        password: Password plaintext

    Returns:
        Objek User atau None jika gagal
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users
            WHERE username = ? AND password = ? AND is_active = 1
        """, (username, hash_password(password)))
        row = cursor.fetchone()
        conn.close()

        if row:
            return _row_to_user(row)
        return None
    except Exception as e:
        print(f"[get_user_by_login] Error: {e}")
        return None


def get_all_users() -> List[User]:
    """Ambil semua pengguna dari database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_user(r) for r in rows]
    except Exception as e:
        print(f"[get_all_users] Error: {e}")
        return []


def get_user_by_id(user_id: int) -> Optional[User]:
    """Ambil pengguna berdasarkan ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return _row_to_user(row) if row else None
    except Exception:
        return None


def update_user(user_id: int, bio: str, email: str) -> Tuple[bool, str]:
    """
    Perbarui profil pengguna (bio dan email).

    Args:
        user_id: ID pengguna
        bio    : Bio baru
        email  : Email baru

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET bio = ?, email = ? WHERE user_id = ?
        """, (bio, email, user_id))
        conn.commit()
        conn.close()
        return True, "Profil berhasil diperbarui."
    except sqlite3.IntegrityError:
        return False, "Email sudah digunakan oleh akun lain."
    except Exception as e:
        return False, f"Error: {e}"


def delete_user(user_id: int) -> Tuple[bool, str]:
    """Hapus (nonaktifkan) pengguna dari sistem."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True, "Pengguna berhasil dinonaktifkan."
    except Exception as e:
        return False, f"Error: {e}"


def search_users(query: str) -> List[User]:
    """
    Cari pengguna dengan partial match, case-insensitive (Bonus: Pencarian Cerdas).

    Args:
        query: Kata kunci pencarian

    Returns:
        List objek User yang cocok
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # LIKE dengan % = partial match; SQLite LIKE sudah case-insensitive untuk ASCII
        cursor.execute("""
            SELECT * FROM users
            WHERE (username LIKE ? OR email LIKE ? OR bio LIKE ?)
            AND is_active = 1
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_user(r) for r in rows]
    except Exception as e:
        print(f"[search_users] Error: {e}")
        return []


def update_karma(user_id: int, points: int, reason: str):
    """
    Tambah/kurang karma pengguna dan catat ke history.

    Args:
        user_id: ID pengguna
        points : Poin yang ditambahkan (bisa negatif)
        reason : Alasan pemberian karma
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET karma = karma + ? WHERE user_id = ?
        """, (points, user_id))
        cursor.execute("""
            INSERT INTO karma_history (user_id, points, reason) VALUES (?, ?, ?)
        """, (user_id, points, reason))

        # Update badge berdasarkan karma terbaru
        cursor.execute("SELECT karma FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            karma = row["karma"]
            # Percabangan untuk menentukan badge (Modul 4)
            if karma >= 500:
                badge = "Social Star"
            elif karma >= 200:
                badge = "Influencer"
            elif karma >= 50:
                badge = "Active User"
            else:
                badge = "Beginner"
            cursor.execute("UPDATE users SET badge = ? WHERE user_id = ?", (badge, user_id))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[update_karma] Error: {e}")


# =============================================================================
# CRUD: POSTS
# =============================================================================

def create_post(user_id: int, content: str, filtered_content: str,
                hashtags: List[str], is_filtered: bool) -> Tuple[bool, str, int]:
    """
    Buat postingan baru dan simpan hashtag terkait.

    Args:
        user_id         : ID pembuat
        content         : Konten asli
        filtered_content: Konten setelah filter kata kasar
        hashtags        : List hashtag yang diekstrak
        is_filtered     : Apakah konten mengandung kata kasar

    Returns:
        Tuple (sukses: bool, pesan: str, post_id: int)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Simpan post dengan konten yang sudah difilter
        cursor.execute("""
            INSERT INTO posts (user_id, content, is_filtered)
            VALUES (?, ?, ?)
        """, (user_id, filtered_content, 1 if is_filtered else 0))
        post_id = cursor.lastrowid

        # Simpan hashtag dan relasi post-hashtag
        for tag in hashtags:
            tag_lower = tag.lower()
            # Insert atau update frekuensi hashtag
            cursor.execute("""
                INSERT INTO hashtags (tag, frequency) VALUES (?, 1)
                ON CONFLICT(tag) DO UPDATE SET frequency = frequency + 1
            """, (tag_lower,))
            cursor.execute("SELECT hashtag_id FROM hashtags WHERE tag = ?", (tag_lower,))
            hashtag_row = cursor.fetchone()
            if hashtag_row:
                cursor.execute("""
                    INSERT OR IGNORE INTO post_hashtags (post_id, hashtag_id)
                    VALUES (?, ?)
                """, (post_id, hashtag_row["hashtag_id"]))

        conn.commit()
        conn.close()

        # Hitung ulang score setelah post dibuat
        update_post_score(post_id)
        return True, "Postingan berhasil dipublikasikan!", post_id
    except Exception as e:
        return False, f"Gagal membuat post: {e}", 0


def get_all_posts(limit: int = 50) -> List[dict]:
    """
    Ambil semua postingan beserta info likes, comments, username.

    Args:
        limit: Jumlah maksimum post yang diambil

    Returns:
        List dictionary postingan
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.post_id, p.user_id, u.username, p.content,
                p.score, p.is_filtered, p.created_at,
                (SELECT COUNT(*) FROM likes   WHERE post_id = p.post_id) AS likes,
                (SELECT COUNT(*) FROM comments WHERE post_id = p.post_id) AS comments,
                (SELECT COUNT(*) FROM saves    WHERE post_id = p.post_id) AS saves
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.score DESC, p.created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_all_posts] Error: {e}")
        return []


def get_posts_by_user(user_id: int) -> List[dict]:
    """Ambil semua postingan milik satu pengguna."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.post_id, p.user_id, u.username, p.content,
                p.score, p.is_filtered, p.created_at,
                (SELECT COUNT(*) FROM likes    WHERE post_id = p.post_id) AS likes,
                (SELECT COUNT(*) FROM comments WHERE post_id = p.post_id) AS comments,
                (SELECT COUNT(*) FROM saves    WHERE post_id = p.post_id) AS saves
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_posts_by_user] Error: {e}")
        return []


def update_post(post_id: int, new_content: str, filtered_content: str,
                hashtags: List[str], is_filtered: bool) -> Tuple[bool, str]:
    """Perbarui isi postingan dan hashtag-nya."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE posts SET content = ?, is_filtered = ? WHERE post_id = ?
        """, (filtered_content, 1 if is_filtered else 0, post_id))

        # Hapus relasi hashtag lama
        cursor.execute("DELETE FROM post_hashtags WHERE post_id = ?", (post_id,))

        # Tambah hashtag baru
        for tag in hashtags:
            tag_lower = tag.lower()
            cursor.execute("""
                INSERT INTO hashtags (tag, frequency) VALUES (?, 1)
                ON CONFLICT(tag) DO UPDATE SET frequency = frequency + 1
            """, (tag_lower,))
            cursor.execute("SELECT hashtag_id FROM hashtags WHERE tag = ?", (tag_lower,))
            hashtag_row = cursor.fetchone()
            if hashtag_row:
                cursor.execute("""
                    INSERT OR IGNORE INTO post_hashtags (post_id, hashtag_id)
                    VALUES (?, ?)
                """, (post_id, hashtag_row["hashtag_id"]))

        conn.commit()
        conn.close()
        update_post_score(post_id)
        return True, "Postingan berhasil diperbarui."
    except Exception as e:
        return False, f"Error: {e}"


def delete_post(post_id: int) -> Tuple[bool, str]:
    """Hapus postingan dari database (cascade ke comments, likes, dll)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        conn.commit()
        conn.close()
        return True, "Postingan berhasil dihapus."
    except Exception as e:
        return False, f"Error: {e}"


def search_posts(query: str) -> List[dict]:
    """Cari postingan dengan partial match (Bonus: Pencarian Cerdas)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.post_id, p.user_id, u.username, p.content,
                p.score, p.is_filtered, p.created_at,
                (SELECT COUNT(*) FROM likes    WHERE post_id = p.post_id) AS likes,
                (SELECT COUNT(*) FROM comments WHERE post_id = p.post_id) AS comments,
                (SELECT COUNT(*) FROM saves    WHERE post_id = p.post_id) AS saves
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.content LIKE ?
            ORDER BY p.score DESC
        """, (f"%{query}%",))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[search_posts] Error: {e}")
        return []


def update_post_score(post_id: int):
    """
    Hitung dan perbarui feed ranking score untuk sebuah postingan.
    Dipanggil setiap kali ada interaksi (like, comment, save).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT created_at FROM posts WHERE post_id = ?", (post_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return

        # Hitung jumlah likes, comments, saves
        cursor.execute("SELECT COUNT(*) FROM likes    WHERE post_id = ?", (post_id,))
        likes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM comments WHERE post_id = ?", (post_id,))
        comments = cursor.fetchone()[0]

        # Hitung recency weight (jam sejak posting)
        try:
            created = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
            hours_old = (datetime.now() - created).total_seconds() / 3600
            recency_weight = max(0, 100 - hours_old * 2)  # Makin tua makin kecil
        except Exception:
            recency_weight = 50

        # Rumus Feed Ranking: skor = (likes × 2) + (comments × 3) + recency_weight
        score = (likes * 2) + (comments * 3) + recency_weight

        cursor.execute("UPDATE posts SET score = ? WHERE post_id = ?", (score, post_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[update_post_score] Error: {e}")


# =============================================================================
# CRUD: COMMENTS
# =============================================================================

def create_comment(post_id: int, user_id: int, content: str) -> Tuple[bool, str]:
    """
    Tambah komentar pada postingan.

    Args:
        post_id : ID postingan
        user_id : ID pemberi komentar
        content : Isi komentar

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)
        """, (post_id, user_id, content))
        conn.commit()
        conn.close()
        update_post_score(post_id)
        return True, "Komentar berhasil ditambahkan."
    except Exception as e:
        return False, f"Error: {e}"


def get_comments_by_post(post_id: int) -> List[dict]:
    """Ambil semua komentar pada sebuah postingan."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.comment_id, c.post_id, c.user_id, u.username,
                   c.content, c.created_at
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.post_id = ?
            ORDER BY c.created_at ASC
        """, (post_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_comments_by_post] Error: {e}")
        return []


def update_comment(comment_id: int, new_content: str) -> Tuple[bool, str]:
    """Perbarui isi komentar."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE comments SET content = ? WHERE comment_id = ?
        """, (new_content, comment_id))
        conn.commit()
        conn.close()
        return True, "Komentar berhasil diperbarui."
    except Exception as e:
        return False, f"Error: {e}"


def delete_comment(comment_id: int, post_id: int) -> Tuple[bool, str]:
    """Hapus komentar dari database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comments WHERE comment_id = ?", (comment_id,))
        conn.commit()
        conn.close()
        update_post_score(post_id)
        return True, "Komentar berhasil dihapus."
    except Exception as e:
        return False, f"Error: {e}"


# =============================================================================
# CRUD: COMMUNITIES / HASHTAGS
# =============================================================================

def create_community(name: str, description: str, creator_id: int) -> Tuple[bool, str]:
    """Buat komunitas baru."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO communities (name, description, creator_id) VALUES (?, ?, ?)
        """, (name, description, creator_id))
        community_id = cursor.lastrowid
        # Kreator otomatis menjadi member pertama
        cursor.execute("""
            INSERT INTO community_members (community_id, user_id) VALUES (?, ?)
        """, (community_id, creator_id))
        conn.commit()
        conn.close()
        return True, f"Komunitas '{name}' berhasil dibuat!"
    except sqlite3.IntegrityError:
        return False, "Nama komunitas sudah ada."
    except Exception as e:
        return False, f"Error: {e}"


def get_all_communities() -> List[dict]:
    """Ambil semua komunitas beserta jumlah anggota dan postingan."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                c.community_id, c.name, c.description, c.creator_id,
                u.username AS creator_name, c.created_at,
                (SELECT COUNT(*) FROM community_members WHERE community_id = c.community_id) AS member_count,
                COALESCE((SELECT frequency FROM hashtags WHERE tag = LOWER(c.name)), 0) AS post_count
            FROM communities c
            JOIN users u ON c.creator_id = u.user_id
            ORDER BY member_count DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_all_communities] Error: {e}")
        return []


def update_community(community_id: int, name: str, description: str) -> Tuple[bool, str]:
    """Perbarui data komunitas."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE communities SET name = ?, description = ? WHERE community_id = ?
        """, (name, description, community_id))
        conn.commit()
        conn.close()
        return True, "Komunitas berhasil diperbarui."
    except sqlite3.IntegrityError:
        return False, "Nama komunitas sudah digunakan."
    except Exception as e:
        return False, f"Error: {e}"


def delete_community(community_id: int) -> Tuple[bool, str]:
    """Hapus komunitas dari database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM communities WHERE community_id = ?", (community_id,))
        conn.commit()
        conn.close()
        return True, "Komunitas berhasil dihapus."
    except Exception as e:
        return False, f"Error: {e}"


def get_trending_hashtags(limit: int = 5) -> List[dict]:
    """
    Ambil hashtag paling trending berdasarkan frekuensi.

    Args:
        limit: Jumlah hashtag yang dikembalikan

    Returns:
        List dictionary {tag, frequency}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tag, frequency FROM hashtags
            ORDER BY frequency DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_trending_hashtags] Error: {e}")
        return []


# =============================================================================
# AKTIVITAS SOSIAL: LIKE, REACTION, SAVE, FOLLOW, FRIEND REQUEST
# =============================================================================

def toggle_like(post_id: int, user_id: int) -> Tuple[bool, str]:
    """
    Toggle like pada postingan (like jika belum, unlike jika sudah).

    Returns:
        Tuple (liked: bool, pesan: str)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Cek apakah sudah like
        cursor.execute("""
            SELECT like_id FROM likes WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))
        existing = cursor.fetchone()

        if existing:
            # Unlike
            cursor.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?",
                           (post_id, user_id))
            conn.commit()
            conn.close()
            update_post_score(post_id)
            return False, "Like dihapus."
        else:
            # Like baru
            cursor.execute("""
                INSERT INTO likes (post_id, user_id) VALUES (?, ?)
            """, (post_id, user_id))
            conn.commit()
            conn.close()
            update_post_score(post_id)
            return True, "Postingan disukai!"
    except Exception as e:
        return False, f"Error: {e}"


def add_reaction(post_id: int, user_id: int, emoji: str) -> Tuple[bool, str]:
    """
    Tambah atau ubah reaksi emoji pada postingan.

    Args:
        post_id : ID postingan
        user_id : ID pemberi reaksi
        emoji   : Emoji reaksi

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reactions (post_id, user_id, emoji) VALUES (?, ?, ?)
            ON CONFLICT(post_id, user_id) DO UPDATE SET emoji = ?
        """, (post_id, user_id, emoji, emoji))
        conn.commit()
        conn.close()
        return True, f"Reaksi {emoji} ditambahkan!"
    except Exception as e:
        return False, f"Error: {e}"


def get_reactions_by_post(post_id: int) -> List[dict]:
    """Ambil semua reaksi pada sebuah postingan."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT emoji, COUNT(*) as count
            FROM reactions WHERE post_id = ?
            GROUP BY emoji ORDER BY count DESC
        """, (post_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return []


def toggle_save(post_id: int, user_id: int) -> Tuple[bool, str]:
    """Toggle simpan postingan."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT save_id FROM saves WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("DELETE FROM saves WHERE post_id = ? AND user_id = ?",
                           (post_id, user_id))
            conn.commit()
            conn.close()
            return False, "Postingan dihapus dari tersimpan."
        else:
            cursor.execute("INSERT INTO saves (post_id, user_id) VALUES (?, ?)",
                           (post_id, user_id))
            conn.commit()
            conn.close()
            return True, "Postingan disimpan!"
    except Exception as e:
        return False, f"Error: {e}"


def get_saved_posts(user_id: int) -> List[dict]:
    """Ambil semua postingan yang disimpan pengguna."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.post_id, p.user_id, u.username, p.content,
                p.score, p.created_at,
                (SELECT COUNT(*) FROM likes    WHERE post_id = p.post_id) AS likes,
                (SELECT COUNT(*) FROM comments WHERE post_id = p.post_id) AS comments,
                (SELECT COUNT(*) FROM saves    WHERE post_id = p.post_id) AS saves
            FROM saves s
            JOIN posts p ON s.post_id = p.post_id
            JOIN users u ON p.user_id = u.user_id
            WHERE s.user_id = ?
            ORDER BY s.created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_saved_posts] Error: {e}")
        return []


def toggle_follow(follower_id: int, following_id: int) -> Tuple[bool, str]:
    """
    Toggle follow pengguna lain.
    Validasi: tidak bisa follow diri sendiri.

    Returns:
        Tuple (followed: bool, pesan: str)
    """
    # Modul 4: Percabangan — validasi follow diri sendiri
    if follower_id == following_id:
        return False, "Tidak bisa follow diri sendiri."
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?
        """, (follower_id, following_id))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                DELETE FROM follows WHERE follower_id = ? AND following_id = ?
            """, (follower_id, following_id))
            conn.commit()
            conn.close()
            return False, "Unfollow berhasil."
        else:
            cursor.execute("""
                INSERT INTO follows (follower_id, following_id) VALUES (?, ?)
            """, (follower_id, following_id))
            conn.commit()
            conn.close()
            return True, "Follow berhasil!"
    except Exception as e:
        return False, f"Error: {e}"


def get_follow_counts(user_id: int) -> dict:
    """Ambil jumlah followers dan following pengguna."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM follows WHERE following_id = ?", (user_id,))
        followers = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM follows WHERE follower_id = ?", (user_id,))
        following = cursor.fetchone()[0]
        conn.close()
        return {"followers": followers, "following": following}
    except Exception as e:
        return {"followers": 0, "following": 0}


def is_following(follower_id: int, following_id: int) -> bool:
    """Cek apakah follower_id sudah follow following_id."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?
        """, (follower_id, following_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


def send_friend_request(sender_id: int, receiver_id: int) -> Tuple[bool, str]:
    """
    Kirim permintaan pertemanan.
    Validasi: tidak ke diri sendiri, tidak duplikat.

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    if sender_id == receiver_id:
        return False, "Tidak bisa mengirim permintaan ke diri sendiri."
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Cek apakah sudah ada request (dalam arah mana pun)
        cursor.execute("""
            SELECT status FROM friend_requests
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
        """, (sender_id, receiver_id, receiver_id, sender_id))
        existing = cursor.fetchone()

        if existing:
            status = existing["status"]
            if status == "pending":
                conn.close()
                return False, "Permintaan sudah dikirim, menunggu konfirmasi."
            elif status == "accepted":
                conn.close()
                return False, "Kalian sudah berteman."
            else:
                # Jika rejected, izinkan kirim ulang
                cursor.execute("""
                    UPDATE friend_requests SET status = 'pending'
                    WHERE sender_id = ? AND receiver_id = ?
                """, (sender_id, receiver_id))
        else:
            cursor.execute("""
                INSERT INTO friend_requests (sender_id, receiver_id) VALUES (?, ?)
            """, (sender_id, receiver_id))

        conn.commit()
        conn.close()
        return True, "Permintaan pertemanan berhasil dikirim!"
    except Exception as e:
        return False, f"Error: {e}"


def respond_friend_request(request_id: int, action: str) -> Tuple[bool, str]:
    """
    Terima atau tolak permintaan pertemanan.

    Args:
        request_id: ID permintaan
        action    : 'accepted' atau 'rejected'

    Returns:
        Tuple (sukses: bool, pesan: str)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE friend_requests SET status = ? WHERE request_id = ?
        """, (action, request_id))
        conn.commit()
        conn.close()
        if action == "accepted":
            return True, "Permintaan pertemanan diterima!"
        return True, "Permintaan pertemanan ditolak."
    except Exception as e:
        return False, f"Error: {e}"


def get_pending_requests(user_id: int) -> List[dict]:
    """Ambil semua permintaan pertemanan yang masuk (pending) untuk user ini."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fr.request_id, fr.sender_id, u.username AS sender_name,
                   fr.status, fr.created_at
            FROM friend_requests fr
            JOIN users u ON fr.sender_id = u.user_id
            WHERE fr.receiver_id = ? AND fr.status = 'pending'
            ORDER BY fr.created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_pending_requests] Error: {e}")
        return []


# =============================================================================
# VIOLATION LOGS
# =============================================================================

def add_violation_log(user_id: int, post_id: int, original: str, filtered: str):
    """Catat pelanggaran konten ke log."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO violation_logs (user_id, post_id, original, filtered)
            VALUES (?, ?, ?, ?)
        """, (user_id, post_id, original, filtered))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[add_violation_log] Error: {e}")


def get_all_violation_logs() -> List[dict]:
    """Ambil semua log pelanggaran (untuk moderator/admin)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT vl.log_id, vl.user_id, u.username, vl.post_id,
                   vl.original, vl.filtered, vl.created_at
            FROM violation_logs vl
            JOIN users u ON vl.user_id = u.user_id
            ORDER BY vl.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_all_violation_logs] Error: {e}")
        return []


def get_violation_logs_by_user(user_id: int) -> List[dict]:
    """Ambil log pelanggaran milik satu pengguna."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM violation_logs WHERE user_id = ? ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return []


# =============================================================================
# ANALYTICS
# =============================================================================

def get_engagement_analytics() -> List[dict]:
    """
    Hitung engagement score per post untuk dashboard analitik.
    Engagement Score = likes + (comments × 2) + saves

    Returns:
        List dict {post_id, username, content, likes, comments, saves, engagement_score}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.post_id,
                u.username,
                SUBSTR(p.content, 1, 60) AS content_preview,
                (SELECT COUNT(*) FROM likes    WHERE post_id = p.post_id) AS likes,
                (SELECT COUNT(*) FROM comments WHERE post_id = p.post_id) AS comments,
                (SELECT COUNT(*) FROM saves    WHERE post_id = p.post_id) AS saves,
                (
                    (SELECT COUNT(*) FROM likes    WHERE post_id = p.post_id) +
                    (SELECT COUNT(*) FROM comments WHERE post_id = p.post_id) * 2 +
                    (SELECT COUNT(*) FROM saves    WHERE post_id = p.post_id)
                ) AS engagement_score
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY engagement_score DESC
            LIMIT 20
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_engagement_analytics] Error: {e}")
        return []


def get_user_activity_summary() -> List[dict]:
    """
    Buat ringkasan aktivitas per pengguna.

    Returns:
        List dict dengan statistik aktivitas setiap user
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                u.user_id, u.username, u.karma, u.badge, u.role,
                (SELECT COUNT(*) FROM posts    WHERE user_id = u.user_id) AS total_posts,
                (SELECT COUNT(*) FROM comments WHERE user_id = u.user_id) AS total_comments,
                (SELECT COUNT(*) FROM likes    WHERE user_id = u.user_id) AS total_likes_given,
                (SELECT COUNT(*) FROM follows  WHERE following_id = u.user_id) AS followers,
                (SELECT COUNT(*) FROM follows  WHERE follower_id = u.user_id) AS following
            FROM users u
            WHERE u.is_active = 1
            ORDER BY u.karma DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[get_user_activity_summary] Error: {e}")
        return []


def get_like_status(post_id: int, user_id: int) -> bool:
    """Cek apakah pengguna sudah like postingan ini."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


def get_save_status(post_id: int, user_id: int) -> bool:
    """Cek apakah pengguna sudah save postingan ini."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM saves WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _row_to_user(row) -> User:
    """Konversi baris SQLite ke objek User."""
    return User(
        user_id=row["user_id"],
        username=row["username"],
        password=row["password"],
        email=row["email"],
        role=row["role"],
        bio=row["bio"] or "",
        karma=row["karma"],
        badge=row["badge"],
        created_at=row["created_at"],
        is_active=bool(row["is_active"]),
    )