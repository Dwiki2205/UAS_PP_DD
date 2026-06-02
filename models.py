"""
models.py
=========
Definisi seluruh class/model data menggunakan OOP (Modul 8: Class dan Object).
Setiap class merepresentasikan entitas dalam sistem social media.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


# =============================================================================
# MODUL 2: Variabel dan Tipe Data — setiap field class menggunakan tipe eksplisit
# MODUL 8: Class dan Object — seluruh file ini adalah implementasi OOP
# =============================================================================

@dataclass
class User:
    """
    Representasi pengguna (entitas utama sistem).

    Attributes:
        user_id   : ID unik pengguna
        username  : Nama login unik
        password  : Password ter-hash
        email     : Alamat email
        role      : 'user' | 'moderator' | 'admin'
        bio       : Deskripsi profil
        karma     : Poin reputasi
        badge     : Label berdasarkan karma
        created_at: Waktu registrasi
        is_active : Status akun
    """
    user_id: int = 0
    username: str = ""
    password: str = ""
    email: str = ""
    role: str = "user"
    bio: str = ""
    karma: int = 0
    badge: str = "Beginner"
    created_at: str = ""
    is_active: bool = True

    def to_dict(self) -> dict:
        """Konversi objek User ke dictionary (Modul 7: Dictionary)."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "bio": self.bio,
            "karma": self.karma,
            "badge": self.badge,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }

    def update_badge(self):
        """
        Perbarui badge berdasarkan poin karma.
        Modul 4: Percabangan | Modul 3: Operator perbandingan
        """
        if self.karma >= 500:
            self.badge = "Social Star"
        elif self.karma >= 200:
            self.badge = "Influencer"
        elif self.karma >= 50:
            self.badge = "Active User"
        else:
            self.badge = "Beginner"


@dataclass
class Post:
    """
    Representasi postingan/konten yang dibuat pengguna.

    Attributes:
        post_id    : ID unik postingan
        user_id    : ID pembuat postingan
        username   : Username pembuat (denormalized untuk display)
        content    : Isi teks postingan
        hashtags   : List hashtag yang diekstrak
        likes      : Jumlah like
        comments   : Jumlah komentar
        saves      : Jumlah save
        score      : Feed ranking score
        created_at : Waktu posting
        is_filtered: Apakah konten pernah difilter
    """
    post_id: int = 0
    user_id: int = 0
    username: str = ""
    content: str = ""
    hashtags: List[str] = field(default_factory=list)
    likes: int = 0
    comments: int = 0
    saves: int = 0
    score: float = 0.0
    created_at: str = ""
    is_filtered: bool = False

    def to_dict(self) -> dict:
        """Konversi objek Post ke dictionary."""
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "username": self.username,
            "content": self.content,
            "hashtags": self.hashtags,
            "likes": self.likes,
            "comments": self.comments,
            "saves": self.saves,
            "score": self.score,
            "created_at": self.created_at,
        }


@dataclass
class Comment:
    """
    Representasi komentar pada sebuah postingan.

    Attributes:
        comment_id : ID unik komentar
        post_id    : ID postingan yang dikomentari
        user_id    : ID pemberi komentar
        username   : Username pemberi komentar
        content    : Isi komentar
        created_at : Waktu komentar dibuat
    """
    comment_id: int = 0
    post_id: int = 0
    user_id: int = 0
    username: str = ""
    content: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        """Konversi objek Comment ke dictionary."""
        return {
            "comment_id": self.comment_id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "username": self.username,
            "content": self.content,
            "created_at": self.created_at,
        }


@dataclass
class Community:
    """
    Representasi komunitas/hashtag dalam sistem.

    Attributes:
        community_id : ID unik komunitas
        name         : Nama komunitas (unik)
        description  : Deskripsi komunitas
        creator_id   : ID user pembuat
        member_count : Jumlah anggota
        post_count   : Jumlah postingan terkait
        created_at   : Waktu dibuat
    """
    community_id: int = 0
    name: str = ""
    description: str = ""
    creator_id: int = 0
    member_count: int = 0
    post_count: int = 0
    created_at: str = ""

    def to_dict(self) -> dict:
        """Konversi objek Community ke dictionary."""
        return {
            "community_id": self.community_id,
            "name": self.name,
            "description": self.description,
            "creator_id": self.creator_id,
            "member_count": self.member_count,
            "post_count": self.post_count,
            "created_at": self.created_at,
        }


@dataclass
class Reaction:
    """
    Representasi reaksi (emoji) pada sebuah postingan.

    Attributes:
        reaction_id : ID unik reaksi
        post_id     : ID postingan
        user_id     : ID pemberi reaksi
        emoji       : Jenis reaksi ('❤️','😂','😮','😢','👏')
        created_at  : Waktu reaksi
    """
    reaction_id: int = 0
    post_id: int = 0
    user_id: int = 0
    emoji: str = "❤️"
    created_at: str = ""


@dataclass
class FriendRequest:
    """
    Representasi permintaan pertemanan antar pengguna.

    Attributes:
        request_id  : ID unik permintaan
        sender_id   : ID pengirim
        receiver_id : ID penerima
        status      : 'pending' | 'accepted' | 'rejected'
        created_at  : Waktu permintaan
    """
    request_id: int = 0
    sender_id: int = 0
    receiver_id: int = 0
    status: str = "pending"
    created_at: str = ""


@dataclass
class ViolationLog:
    """
    Log pelanggaran konten yang difilter sistem.

    Attributes:
        log_id      : ID unik log
        user_id     : ID pelanggar
        username    : Username pelanggar
        post_id     : ID postingan pelanggaran
        original    : Teks asli sebelum filter
        filtered    : Teks setelah filter
        created_at  : Waktu pelanggaran
    """
    log_id: int = 0
    user_id: int = 0
    username: str = ""
    post_id: int = 0
    original: str = ""
    filtered: str = ""
    created_at: str = ""


@dataclass
class Session:
    """
    Menyimpan state sesi login aktif.

    Attributes:
        user     : Objek User yang sedang login
        is_logged: Status login
    """
    user: Optional[User] = None
    is_logged: bool = False

    def login(self, user: User):
        """Set sesi login aktif."""
        self.user = user
        self.is_logged = True

    def logout(self):
        """Hapus sesi login."""
        self.user = None
        self.is_logged = False