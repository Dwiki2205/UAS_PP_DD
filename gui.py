"""
gui.py
======
Seluruh komponen GUI menggunakan CustomTkinter.
Mengelola semua halaman, navigasi, dan interaksi pengguna.

Modul yang diimplementasikan:
    - Modul 1: Input Output (form input, tampilan output)
    - Modul 4: Percabangan (role-based navigation)
    - Modul 5: Perulangan (render post cards)
    - Modul 8: Class dan Object (setiap frame adalah class)
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter as ctk
from typing import Optional, Callable
from datetime import datetime

import data as db
import logic
from models import Session, User

# =============================================================================
# KONFIGURASI TEMA GLOBAL - WARNA YANG LEBIH USER-FRIENDLY
# =============================================================================

# Palet warna untuk dark mode (lebih soft, ramah mata)
DARK_COLORS = {
    "bg_primary":   "#0F172A",      # Slate 900 - lebih gelap tapi soft
    "bg_secondary": "#1E293B",      # Slate 800
    "bg_card":      "#334155",       # Slate 700
    "accent":       "#3B82F6",       # Biru terang (primary)
    "accent2":      "#8B5CF6",       # Ungu (secondary)
    "accent_hover": "#2563EB",       # Biru lebih gelap untuk hover
    "text_primary": "#F1F5F9",       # Slate 100
    "text_secondary":"#94A3B8",      # Slate 400
    "success":      "#10B981",       # Emerald 500
    "warning":      "#F59E0B",       # Amber 500
    "danger":       "#EF4444",       # Red 500
    "info":         "#06B6D4",       # Cyan 500
    "border":       "#475569",       # Slate 600
}

# Palet warna untuk light mode (lebih soft, tidak menyilaukan)
LIGHT_COLORS = {
    "bg_primary":   "#F8FAFC",       # Slate 50
    "bg_secondary": "#FFFFFF",       # Putih murni
    "bg_card":      "#F1F5F9",       # Slate 100
    "accent":       "#3B82F6",       # Biru (primary)
    "accent2":      "#8B5CF6",       # Ungu (secondary)
    "accent_hover": "#2563EB",       # Biru lebih gelap
    "text_primary": "#0F172A",       # Slate 900
    "text_secondary":"#475569",      # Slate 600
    "success":      "#10B981",       # Emerald 500
    "warning":      "#F59E0B",       # Amber 500
    "danger":       "#EF4444",       # Red 500
    "info":         "#06B6D4",       # Cyan 500
    "border":       "#E2E8F0",       # Slate 200
}


class SocialMediaApp(ctk.CTk):
    """
    Window utama aplikasi Social Media Platform.
    Mengatur navigasi antar frame dan state session.

    Attributes:
        session    : Objek Session yang menyimpan user login
        current_frame: Frame yang sedang ditampilkan
        colors     : Dictionary warna tema aktif
        is_dark    : Boolean mode gelap/terang
    """

    def __init__(self):
        """Inisialisasi window utama dan tampilkan halaman login."""
        super().__init__()
        self.title("SocialHub — Simple Social Media Platform")
        
        # Ukuran window yang lebih responsif
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(1200, screen_width - 100)
        window_height = min(750, screen_height - 100)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(800, 600)

        # State aplikasi
        self.session    = Session()        # Sesi login aktif
        self.is_dark    = True             # Default: dark mode
        self.colors     = DARK_COLORS.copy()
        self.current_frame: Optional[ctk.CTkFrame] = None

        # Setup tema CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Konfigurasi grid window utama
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tampilkan halaman login pertama kali
        self.show_login()

    def toggle_theme(self):
        """
        Toggle antara dark mode dan light mode (Bonus: GUI Dinamis).
        Memperbarui seluruh warna aplikasi.
        """
        self.is_dark = not self.is_dark
        if self.is_dark:
            self.colors = DARK_COLORS.copy()
            ctk.set_appearance_mode("dark")
        else:
            self.colors = LIGHT_COLORS.copy()
            ctk.set_appearance_mode("light")

        # Refresh halaman yang sedang ditampilkan
        if self.session.is_logged:
            self.show_main()

    def show_frame(self, frame_class, **kwargs):
        """
        Ganti frame yang ditampilkan (navigasi tanpa restart).

        Args:
            frame_class: Class frame yang akan ditampilkan
            **kwargs   : Argumen tambahan untuk frame
        """
        # Hapus frame lama jika ada
        if self.current_frame:
            self.current_frame.destroy()

        # Buat dan tampilkan frame baru
        self.current_frame = frame_class(self, self.session, self.colors, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_login(self):
        """Tampilkan halaman login."""
        self.show_frame(LoginFrame)

    def show_main(self, page: str = "feed"):
        """Tampilkan halaman utama (setelah login)."""
        self.show_frame(MainFrame, initial_page=page)

    def do_logout(self):
        """Logout dan kembali ke halaman login."""
        self.session.logout()
        self.show_login()


# =============================================================================
# FRAME: LOGIN & REGISTER
# =============================================================================

class LoginFrame(ctk.CTkFrame):
    """
    Halaman login dan registrasi.

    Menangani:
        - Form login dengan validasi
        - Form registrasi pengguna baru
        - Toggle password visibility
    """

    def __init__(self, master: SocialMediaApp, session: Session, colors: dict):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.master_app = master
        self.session    = session
        self.colors     = colors
        self._build_ui()

    def _build_ui(self):
        """Bangun seluruh komponen UI halaman login."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Panel kiri: Branding / Ilustrasi
        left_panel = ctk.CTkFrame(self, fg_color=self.colors["bg_secondary"], corner_radius=0)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        brand_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        brand_frame.grid(row=0, column=0)

        # Gradient effect untuk logo
        logo_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        logo_frame.pack(pady=(0, 10))
        
        ctk.CTkLabel(logo_frame, text="🌐", font=ctk.CTkFont(size=80)).pack()
        
        ctk.CTkLabel(
            brand_frame, text="SocialHub",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=self.colors["accent"]
        ).pack()
        
        ctk.CTkLabel(
            brand_frame, text="Connect · Share · Discover",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        ).pack(pady=5)

        # Fitur highlights dengan icon
        features = [
            ("✨", "Feed Ranking Algorithm"),
            ("🔥", "Trending Hashtags"),
            ("⭐", "Karma & Badge System"),
            ("🛡️", "Content Filter")
        ]
        for icon, feat in features:
            frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
            frame.pack(pady=2)
            ctk.CTkLabel(frame, text=icon, font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkLabel(
                frame, text=feat,
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_secondary"]
            ).pack(side="left", padx=5)

        # Panel kanan: Form login
        right_panel = ctk.CTkFrame(self, fg_color=self.colors["bg_primary"], corner_radius=0)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        form_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_frame.grid(row=0, column=0, padx=40)

        # Tab: Login / Register
        self.tab_view = ctk.CTkTabview(
            form_frame, width=400, height=450,
            fg_color=self.colors["bg_secondary"],
            segmented_button_fg_color=self.colors["bg_card"],
            segmented_button_selected_color=self.colors["accent"],
            segmented_button_selected_hover_color=self.colors["accent_hover"],
        )
        self.tab_view.pack()
        self.tab_view.add("Login")
        self.tab_view.add("Register")

        self._build_login_tab()
        self._build_register_tab()

    def _build_login_tab(self):
        """Bangun form login di dalam tab 'Login'."""
        tab = self.tab_view.tab("Login")

        ctk.CTkLabel(tab, text="Selamat Datang Kembali!",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(pady=(30, 10))

        ctk.CTkLabel(tab, text="Username",
                     text_color=self.colors["text_secondary"]).pack(anchor="w", padx=25)
        self.login_username = ctk.CTkEntry(
            tab, placeholder_text="Masukkan username",
            fg_color=self.colors["bg_card"], width=350, height=42
        )
        self.login_username.pack(padx=25, pady=(2, 15))

        ctk.CTkLabel(tab, text="Password",
                     text_color=self.colors["text_secondary"]).pack(anchor="w", padx=25)
        
        # Password frame dengan show/hide button
        pwd_frame = ctk.CTkFrame(tab, fg_color="transparent")
        pwd_frame.pack(padx=25, pady=(2, 5))
        
        self.login_password = ctk.CTkEntry(
            pwd_frame, placeholder_text="Masukkan password",
            show="•", fg_color=self.colors["bg_card"], width=310, height=42
        )
        self.login_password.pack(side="left")
        
        self.show_pwd_var = tk.BooleanVar(value=False)
        ctk.CTkButton(
            pwd_frame, text="👁️", width=35, height=42,
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["accent2"],
            command=self._toggle_password_visibility
        ).pack(side="left", padx=(5, 0))

        # Bind Enter key untuk login cepat
        self.login_password.bind("<Return>", lambda e: self._do_login())

        # Label pesan error/sukses
        self.login_msg = ctk.CTkLabel(tab, text="", text_color=self.colors["danger"])
        self.login_msg.pack(pady=5)

        ctk.CTkButton(
            tab, text="Login", width=350, height=42,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._do_login
        ).pack(padx=25, pady=15)

        # Info akun demo
        demo_frame = ctk.CTkFrame(tab, fg_color=self.colors["bg_card"], corner_radius=8)
        demo_frame.pack(pady=10, padx=25, fill="x")
        
        ctk.CTkLabel(
            demo_frame,
            text="🔐 Akun Demo",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(anchor="w", padx=10, pady=(5, 0))
        
        ctk.CTkLabel(
            demo_frame,
            text="admin / Admin123  |  mod / Mod12345  |  alice / Alice123",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"]
        ).pack(pady=5, padx=10)

    def _build_register_tab(self):
        """Bangun form registrasi di dalam tab 'Register'."""
        tab = self.tab_view.tab("Register")

        ctk.CTkLabel(tab, text="Buat Akun Baru",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(pady=(20, 10))

        fields = [
            ("Username", "reg_username", "Minimal 3 karakter"),
            ("Email",    "reg_email",    "user@example.com"),
            ("Password", "reg_password", "Min 8 karakter, huruf+angka"),
        ]

        for label, attr, placeholder in fields:
            ctk.CTkLabel(tab, text=label,
                         text_color=self.colors["text_secondary"]).pack(anchor="w", padx=25)
            show_char = "•" if "password" in attr.lower() else ""
            entry = ctk.CTkEntry(
                tab, placeholder_text=placeholder,
                show=show_char, fg_color=self.colors["bg_card"], width=350, height=42
            )
            entry.pack(padx=25, pady=(2, 12))
            setattr(self, attr, entry)

        self.reg_msg = ctk.CTkLabel(tab, text="", text_color=self.colors["danger"])
        self.reg_msg.pack()

        ctk.CTkButton(
            tab, text="Daftar Sekarang", width=350, height=42,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._do_register
        ).pack(padx=25, pady=15)

        ctk.CTkLabel(
            tab,
            text="Dengan mendaftar, Anda menyetujui Syarat & Ketentuan",
            font=ctk.CTkFont(size=9),
            text_color=self.colors["text_secondary"]
        ).pack(pady=5)

    def _toggle_password_visibility(self):
        """Toggle visibility password field."""
        if self.show_pwd_var.get():
            self.login_password.configure(show="")
            self.show_pwd_var.set(False)
        else:
            self.login_password.configure(show="•")
            self.show_pwd_var.set(True)

    def _do_login(self):
        """
        Proses login: validasi input dan autentikasi.
        Modul 1: Input | Modul 4: Percabangan | Modul 6: Fungsi
        """
        username = self.login_username.get().strip()
        password = self.login_password.get()

        # Validasi input kosong (Modul 4: Percabangan)
        if not username or not password:
            self.login_msg.configure(text="⚠ Username dan password wajib diisi.")
            return

        # Autentikasi via data layer
        user = db.get_user_by_login(username, password)

        if user:
            self.session.login(user)
            # Reset message
            self.login_msg.configure(text="")
            self.master_app.show_main()
        else:
            self.login_msg.configure(text="❌ Username atau password salah.")

    def _do_register(self):
        """
        Proses registrasi pengguna baru dengan validasi lengkap.
        """
        username = self.reg_username.get().strip()
        email    = self.reg_email.get().strip()
        password = self.reg_password.get()

        # Reset message
        self.reg_msg.configure(text="")

        # Validasi username
        valid, msg = logic.validate_username(username)
        if not valid:
            self.reg_msg.configure(text=f"⚠ {msg}")
            return

        # Validasi email
        valid, msg = logic.validate_email(email)
        if not valid:
            self.reg_msg.configure(text=f"⚠ {msg}")
            return

        # Validasi password
        valid, msg = logic.validate_password(password)
        if not valid:
            self.reg_msg.configure(text=f"⚠ {msg}")
            return

        # Simpan ke database
        success, message = db.create_user(username, password, email)
        if success:
            self.reg_msg.configure(text=f"✅ {message}", text_color=self.colors["success"])
            # Reset form
            self.reg_username.delete(0, "end")
            self.reg_email.delete(0, "end")
            self.reg_password.delete(0, "end")
            # Switch ke tab login
            self.tab_view.set("Login")
        else:
            self.reg_msg.configure(text=f"❌ {message}")


# =============================================================================
# FRAME: MAIN (Container dengan Sidebar + Content)
# =============================================================================

class MainFrame(ctk.CTkFrame):
    """
    Frame utama setelah login.
    Berisi sidebar navigasi dan area konten.

    Sidebar dinamis berdasarkan role user:
        - User     : Feed, Profile, Search, Social, Saved, Settings
        - Moderator: + Violations
        - Admin    : + Manage Users, Analytics
    """

    def __init__(self, master: SocialMediaApp, session: Session,
                 colors: dict, initial_page: str = "feed"):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.master_app   = master
        self.session      = session
        self.colors       = colors
        self.current_page = initial_page
        self.content_frame: Optional[ctk.CTkFrame] = None
        self._build_layout()
        self.navigate(initial_page)

    def _build_layout(self):
        """Bangun layout utama: sidebar kiri + area konten kanan."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(
            self, fg_color=self.colors["bg_secondary"],
            width=250, corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self._build_sidebar()

        # --- AREA KONTEN ---
        self.content_area = ctk.CTkFrame(
            self, fg_color=self.colors["bg_primary"], corner_radius=0
        )
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def _build_sidebar(self):
        """
        Bangun sidebar navigasi dinamis sesuai role.
        Modul 4: Percabangan — menu berbeda per role
        """
        self.sidebar.grid_rowconfigure(15, weight=1)

        # Logo / Brand
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(25, 5))
        
        ctk.CTkLabel(
            logo_frame, text="🌐", font=ctk.CTkFont(size=28)
        ).pack(side="left")
        ctk.CTkLabel(
            logo_frame, text="SocialHub",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(side="left", padx=5)

        # Separator
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=self.colors["border"]
        ).grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 15))

        # Info user login
        user = self.session.user
        badge = logic.get_badge_for_karma(user.karma)
        
        user_frame = ctk.CTkFrame(self.sidebar, fg_color=self.colors["bg_card"], corner_radius=10)
        user_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        user_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            user_frame, text=f"@{user.username}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")
        
        ctk.CTkLabel(
            user_frame,
            text=f"{badge}",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["accent2"]
        ).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="w")

        # Separator
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=self.colors["border"]
        ).grid(row=3, column=0, sticky="ew", padx=15)

        # Definisi menu berdasarkan role
        # Modul 7: List — daftar menu navigasi
        base_menu = [
            ("🏠  Feed",         "feed"),
            ("👤  Profil",       "profile"),
            ("🔍  Cari",         "search"),
            ("👥  Sosial",       "social"),
            ("🔖  Tersimpan",    "saved"),
            ("🏘️  Komunitas",   "community"),
        ]
        mod_menu = [
            ("🛡️  Moderasi",    "moderation"),
        ]
        admin_menu = [
            ("👑  Kelola User",  "admin_users"),
            ("📊  Analitik",     "analytics"),
        ]

        # Modul 4: Percabangan — tambahkan menu sesuai role
        all_menu = base_menu[:]
        if user.role in ("moderator", "admin"):
            all_menu += mod_menu
        if user.role == "admin":
            all_menu += admin_menu

        # Render tombol navigasi
        self.nav_buttons = {}
        for i, (label, page) in enumerate(all_menu, start=4):
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                fg_color="transparent",
                hover_color=self.colors["bg_card"],
                text_color=self.colors["text_primary"],
                font=ctk.CTkFont(size=13),
                height=40,
                corner_radius=8,
                command=lambda p=page: self.navigate(p)
            )
            btn.grid(row=i, column=0, padx=12, pady=2, sticky="ew")
            self.nav_buttons[page] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, height=1, fg_color="transparent").grid(row=len(all_menu)+4, column=0, sticky="ew")

        # Separator bawah
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=self.colors["border"]
        ).grid(row=len(all_menu)+5, column=0, sticky="sew", padx=15, pady=10)

        # Tombol Toggle Theme
        ctk.CTkButton(
            self.sidebar,
            text="🌙 Dark / ☀️ Light",
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["accent2"],
            command=self.master_app.toggle_theme,
            height=38,
            corner_radius=8
        ).grid(row=len(all_menu)+6, column=0, padx=12, pady=5, sticky="ew")

        # Tombol Logout
        ctk.CTkButton(
            self.sidebar, text="🚪  Logout",
            fg_color=self.colors["danger"],
            hover_color="#B91C1C",
            command=self.master_app.do_logout,
            height=38,
            corner_radius=8
        ).grid(row=len(all_menu)+7, column=0, padx=12, pady=(5, 20), sticky="ew")

    def navigate(self, page: str):
        """
        Navigasi ke halaman tertentu tanpa restart aplikasi.
        Modul 4: Percabangan — routing ke frame yang tepat
        """
        # Highlight tombol aktif
        for p, btn in self.nav_buttons.items():
            if p == page:
                btn.configure(fg_color=self.colors["accent"], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.colors["text_primary"])

        # Hapus konten lama
        if self.content_frame:
            self.content_frame.destroy()

        # Mapping halaman ke class frame (Modul 7: Dictionary)
        page_map = {
            "feed":        FeedPage,
            "profile":     ProfilePage,
            "search":      SearchPage,
            "social":      SocialPage,
            "saved":       SavedPage,
            "community":   CommunityPage,
            "moderation":  ModerationPage,
            "admin_users": AdminUsersPage,
            "analytics":   AnalyticsPage,
        }

        # Modul 4: Percabangan — tampilkan frame yang sesuai
        if page in page_map:
            frame_class = page_map[page]
            self.content_frame = frame_class(
                self.content_area, self.session, self.colors, self
            )
            self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.current_page = page


# =============================================================================
# HELPER: POST CARD WIDGET
# =============================================================================

class PostCard(ctk.CTkFrame):
    """
    Widget kartu postingan yang dapat digunakan di halaman mana pun.
    Menampilkan konten, interaksi (like, comment, save, react), dan info user.
    """

    def __init__(self, master, post: dict, session: Session, colors: dict,
                 on_refresh: Optional[Callable] = None):
        """
        Args:
            master    : Parent widget
            post      : Dictionary data postingan
            session   : Sesi login aktif
            colors    : Dictionary warna tema
            on_refresh: Callback untuk refresh parent setelah aksi
        """
        super().__init__(master, fg_color=colors["bg_card"],
                         corner_radius=12, border_width=1,
                         border_color=colors["border"])
        self.post       = post
        self.session    = session
        self.colors     = colors
        self.on_refresh = on_refresh
        self._build()

    def _build(self):
        """Bangun tampilan kartu postingan."""
        self.grid_columnconfigure(0, weight=1)
        
        # Padding terpisah untuk menghindari konflik
        header_padding = {"padx": 15}
        content_padding = {"padx": 15, "pady": 5}
        action_padding = {"padx": 15}

        # Header: avatar + username + waktu + score
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", **header_padding, pady=(12, 5))
        header.grid_columnconfigure(1, weight=1)

        # Avatar dengan inisial dan background warna
        avatar_text = self.post.get("username", "?")[0].upper()
        avatar = ctk.CTkLabel(
            header, text=avatar_text,
            width=40, height=40,
            fg_color=self.colors["accent2"],
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=20
        )
        avatar.grid(row=0, column=0, rowspan=2, padx=(0, 12))

        ctk.CTkLabel(
            header, text=f"@{self.post.get('username', '')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"], anchor="w"
        ).grid(row=0, column=1, sticky="w")

        # Format waktu
        created_at = self.post.get("created_at", "")
        ctk.CTkLabel(
            header, text=f"🕐 {created_at[:16]}",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"], anchor="w"
        ).grid(row=1, column=1, sticky="w")

        # Score badge
        score = self.post.get("score", 0)
        score_frame = ctk.CTkFrame(header, fg_color=self.colors["warning"], corner_radius=15)
        score_frame.grid(row=0, column=2, rowspan=2, padx=5)
        ctk.CTkLabel(
            score_frame, text=f"⭐ {score:.0f}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFFFFF"
        ).pack(padx=8, pady=2)

        # Isi postingan
        content = self.post.get("content", "")
        ctk.CTkLabel(
            self, text=content, wraplength=500,
            justify="left", anchor="w",
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="ew", **content_padding)

        # Tombol aksi: Like, Comment, Save, React
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.grid(row=2, column=0, sticky="ew", **action_padding, pady=(5, 12))

        post_id = self.post.get("post_id", 0)
        uid     = self.session.user.user_id

        # Status like & save
        is_liked = db.get_like_status(post_id, uid)
        is_saved = db.get_save_status(post_id, uid)

        likes    = self.post.get("likes", 0)
        comments = self.post.get("comments", 0)
        saves    = self.post.get("saves", 0)

        like_color = self.colors["danger"] if is_liked else self.colors["text_secondary"]
        save_color = self.colors["success"] if is_saved else self.colors["text_secondary"]

        # Tombol Like
        like_btn = ctk.CTkButton(
            action_bar,
            text=f"❤️ {likes}",
            width=80, height=32,
            fg_color="transparent",
            text_color=like_color,
            hover_color=self.colors["bg_secondary"],
            corner_radius=16,
            command=lambda: self._toggle_like(post_id)
        )
        like_btn.pack(side="left", padx=3)

        # Tombol Comment
        ctk.CTkButton(
            action_bar,
            text=f"💬 {comments}",
            width=80, height=32,
            fg_color="transparent",
            text_color=self.colors["text_secondary"],
            hover_color=self.colors["bg_secondary"],
            corner_radius=16,
            command=lambda: self._open_comments(post_id)
        ).pack(side="left", padx=3)

        # Tombol Save
        ctk.CTkButton(
            action_bar,
            text=f"🔖 {saves}",
            width=80, height=32,
            fg_color="transparent",
            text_color=save_color,
            hover_color=self.colors["bg_secondary"],
            corner_radius=16,
            command=lambda: self._toggle_save(post_id)
        ).pack(side="left", padx=3)

        # Tombol Reaksi
        ctk.CTkButton(
            action_bar,
            text="😊 Reaksi",
            width=90, height=32,
            fg_color="transparent",
            text_color=self.colors["text_secondary"],
            hover_color=self.colors["bg_secondary"],
            corner_radius=16,
            command=lambda: self._open_reactions(post_id)
        ).pack(side="left", padx=3)

        # Tombol hapus post (hanya pemilik atau admin)
        user = self.session.user
        post_owner = self.post.get("user_id", -1)
        if user.user_id == post_owner or user.role == "admin":
            ctk.CTkButton(
                action_bar,
                text="🗑️",
                width=40, height=32,
                fg_color="transparent",
                text_color=self.colors["danger"],
                hover_color=self.colors["bg_secondary"],
                corner_radius=16,
                command=lambda: self._delete_post(post_id)
            ).pack(side="right", padx=3)

    def _toggle_like(self, post_id: int):
        """Toggle like dan beri karma ke pemilik post."""
        liked, msg = db.toggle_like(post_id, self.session.user.user_id)
        if liked:
            # Beri karma ke pemilik post
            post_owner_id = self.post.get("user_id", 0)
            logic.award_karma(post_owner_id, "post_liked")
        if self.on_refresh:
            self.on_refresh()

    def _toggle_save(self, post_id: int):
        """Toggle save postingan."""
        db.toggle_save(post_id, self.session.user.user_id)
        if self.on_refresh:
            self.on_refresh()

    def _open_comments(self, post_id: int):
        """Buka dialog komentar untuk postingan ini."""
        CommentDialog(self, post_id, self.session, self.colors, self.on_refresh)

    def _open_reactions(self, post_id: int):
        """Buka dialog pilihan reaksi emoji."""
        ReactionDialog(self, post_id, self.session, self.colors)

    def _delete_post(self, post_id: int):
        """Hapus postingan setelah konfirmasi."""
        if self._show_confirmation("Konfirmasi", "Yakin ingin menghapus postingan ini?"):
            success, msg = db.delete_post(post_id)
            if success and self.on_refresh:
                self.on_refresh()
            else:
                self._show_error("Gagal", msg)
    
    def _show_confirmation(self, title: str, message: str) -> bool:
        """Tampilkan dialog konfirmasi yang lebih baik."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x180")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"+{x}+{y}")
        
        result = [False]
        
        ctk.CTkLabel(dialog, text=message, wraplength=300,
                     text_color=self.colors["text_primary"]).pack(pady=30)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Ya", width=80,
                      fg_color=self.colors["danger"],
                      command=lambda: [result.__setitem__(0, True), dialog.destroy()]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Tidak", width=80,
                      fg_color=self.colors["bg_card"],
                      command=dialog.destroy).pack(side="left", padx=10)
        
        self.wait_window(dialog)
        return result[0]
    
    def _show_error(self, title: str, message: str):
        """Tampilkan dialog error yang lebih baik."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"❌ {message}", wraplength=300,
                     text_color=self.colors["danger"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)
    
    def _show_info(self, title: str, message: str):
        """Tampilkan dialog info yang lebih baik."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"✅ {message}", wraplength=300,
                     text_color=self.colors["success"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)


# =============================================================================
# DIALOG: COMMENT (Modal dengan proper focus)
# =============================================================================

class CommentDialog(ctk.CTkToplevel):
    """Dialog untuk melihat dan menambah komentar pada postingan."""

    def __init__(self, master, post_id: int, session: Session,
                 colors: dict, on_refresh: Optional[Callable] = None):
        super().__init__(master)
        self.title(f"💬 Komentar Post #{post_id}")
        self.geometry("550x550")
        self.post_id    = post_id
        self.session    = session
        self.colors     = colors
        self.on_refresh = on_refresh
        self.configure(fg_color=colors["bg_primary"])
        
        # Make dialog modal
        self.transient(master)
        self.grab_set()
        self.focus_force()
        
        # Center on screen
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 550) // 2
        y = master.winfo_y() + (master.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        
        self._build()
        
        # Bind escape to close
        self.bind("<Escape>", lambda e: self.destroy())

    def _build(self):
        """Bangun tampilan dialog komentar."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Scroll frame untuk daftar komentar
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=self.colors["bg_secondary"],
            label_text=f"💬 Komentar"
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        scroll.grid_columnconfigure(0, weight=1)

        self._load_comments(scroll)

        # Form tambah komentar
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        input_frame.grid_columnconfigure(0, weight=1)

        self.comment_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Tulis komentar...",
            fg_color=self.colors["bg_card"], height=40
        )
        self.comment_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.comment_entry.bind("<Return>", lambda e: self._submit_comment())

        ctk.CTkButton(
            input_frame, text="Kirim", width=80, height=40,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._submit_comment
        ).grid(row=0, column=1)

    def _load_comments(self, scroll_frame):
        """Muat dan tampilkan semua komentar."""
        comments = db.get_comments_by_post(self.post_id)

        if not comments:
            ctk.CTkLabel(
                scroll_frame, text="💭 Belum ada komentar. Jadilah yang pertama!",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=12)
            ).pack(pady=30)
            return

        # Modul 5: Perulangan — render setiap komentar
        for comment in comments:
            card = ctk.CTkFrame(scroll_frame, fg_color=self.colors["bg_card"], corner_radius=10)
            card.pack(fill="x", pady=4, padx=5)
            card.grid_columnconfigure(0, weight=1)

            # Header komentar
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 2))
            header_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                header_frame, text=f"@{comment['username']}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["accent"]
            ).grid(row=0, column=0, sticky="w")
            
            ctk.CTkLabel(
                header_frame, text=comment["created_at"][:16],
                font=ctk.CTkFont(size=9),
                text_color=self.colors["text_secondary"]
            ).grid(row=0, column=1, padx=10)

            ctk.CTkLabel(
                card, text=comment["content"],
                wraplength=450, anchor="w", justify="left",
                text_color=self.colors["text_primary"],
                font=ctk.CTkFont(size=12)
            ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))

            # Tombol hapus komentar (pemilik atau admin)
            user = self.session.user
            if user.user_id == comment["user_id"] or user.role == "admin":
                ctk.CTkButton(
                    card, text="🗑️", width=30, height=25,
                    fg_color="transparent",
                    text_color=self.colors["danger"],
                    hover_color=self.colors["bg_secondary"],
                    command=lambda cid=comment["comment_id"]: self._delete_comment(cid)
                ).grid(row=0, column=1, padx=5, pady=5)

    def _submit_comment(self):
        """Kirim komentar baru."""
        content = self.comment_entry.get().strip()
        if not content:
            return

        success, msg = db.create_comment(self.post_id, self.session.user.user_id, content)
        if success:
            # Beri karma untuk komentator
            logic.award_karma(self.session.user.user_id, "commented")
            self.comment_entry.delete(0, "end")
            # Refresh dialog
            self.destroy()
            if self.on_refresh:
                self.on_refresh()

    def _delete_comment(self, comment_id: int):
        """Hapus komentar."""
        if self._show_confirmation("Hapus Komentar", "Yakin ingin menghapus komentar ini?"):
            db.delete_comment(comment_id, self.post_id)
            self.destroy()
            if self.on_refresh:
                self.on_refresh()
    
    def _show_confirmation(self, title: str, message: str) -> bool:
        """Tampilkan dialog konfirmasi yang lebih baik."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        result = [False]
        
        ctk.CTkLabel(dialog, text=message, wraplength=300,
                     text_color=self.colors["text_primary"]).pack(pady=30)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Ya", width=80,
                      fg_color=self.colors["danger"],
                      command=lambda: [result.__setitem__(0, True), dialog.destroy()]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Tidak", width=80,
                      fg_color=self.colors["bg_card"],
                      command=dialog.destroy).pack(side="left", padx=10)
        
        self.wait_window(dialog)
        return result[0]


# =============================================================================
# DIALOG: REACTION (Modal)
# =============================================================================

class ReactionDialog(ctk.CTkToplevel):
    """Dialog untuk memilih reaksi emoji pada postingan."""

    EMOJIS = ["❤️", "😂", "😮", "😢", "👏", "🔥", "🎉", "👍"]
    EMOJI_NAMES = ["Love", "Laugh", "Wow", "Sad", "Clap", "Fire", "Party", "Thumbs Up"]

    def __init__(self, master, post_id: int, session: Session, colors: dict):
        super().__init__(master)
        self.title("Pilih Reaksi")
        self.geometry("450x250")
        self.post_id = post_id
        self.session = session
        self.colors  = colors
        self.configure(fg_color=colors["bg_primary"])
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 450) // 2
        y = master.winfo_y() + (master.winfo_height() - 250) // 2
        self.geometry(f"+{x}+{y}")
        
        self._build()
        self.bind("<Escape>", lambda e: self.destroy())

    def _build(self):
        """Bangun tampilan dialog reaksi."""
        ctk.CTkLabel(self, text="Pilih reaksimu:",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack()

        # Modul 5: Perulangan — render tombol emoji
        for i, (emoji, name) in enumerate(zip(self.EMOJIS, self.EMOJI_NAMES)):
            btn = ctk.CTkButton(
                btn_frame, text=f"{emoji}\n{name}",
                width=50, height=60,
                font=ctk.CTkFont(size=18),
                fg_color=self.colors["bg_card"],
                hover_color=self.colors["accent"],
                text_color=self.colors["text_primary"],
                command=lambda e=emoji: self._react(e)
            )
            btn.grid(row=0, column=i, padx=3, pady=5)

        # Tampilkan reaksi yang sudah ada
        reactions = db.get_reactions_by_post(self.post_id)
        if reactions:
            react_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], corner_radius=10)
            react_frame.pack(pady=15, padx=20, fill="x")
            
            ctk.CTkLabel(react_frame, text="📊 Reaksi Populer:",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=self.colors["text_secondary"]).pack(anchor="w", padx=10, pady=(5, 0))
            
            react_text = "  ".join([f"{r['emoji']} {r['count']}" for r in reactions[:5]])
            ctk.CTkLabel(react_frame, text=react_text,
                         font=ctk.CTkFont(size=14),
                         text_color=self.colors["text_primary"]).pack(pady=5, padx=10)

    def _react(self, emoji: str):
        """Kirim reaksi dan tutup dialog."""
        db.add_reaction(self.post_id, self.session.user.user_id, emoji)
        self.destroy()


# =============================================================================
# PAGE: FEED
# =============================================================================

class FeedPage(ctk.CTkFrame):
    """
    Halaman feed utama dengan ranking algorithm.
    Menampilkan semua postingan diurutkan berdasarkan score.
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan halaman feed."""
        # Header
        header = ctk.CTkFrame(self, fg_color=self.colors["bg_secondary"], height=70, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header, text="🏠 Feed",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=15, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=15, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="✏️ Buat Post", width=110, height=38,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._open_create_post
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="🔄 Refresh", width=100, height=38,
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["accent2"],
            command=self._refresh
        ).pack(side="left", padx=5)

        # Sidebar trending hashtags + main feed
        content_area = ctk.CTkFrame(self, fg_color="transparent")
        content_area.grid(row=1, column=0, sticky="nsew")
        content_area.grid_rowconfigure(0, weight=1)
        content_area.grid_columnconfigure(0, weight=3)
        content_area.grid_columnconfigure(1, weight=1)

        # Feed scroll area
        self.feed_scroll = ctk.CTkScrollableFrame(
            content_area, fg_color="transparent"
        )
        self.feed_scroll.grid(row=0, column=0, sticky="nsew", padx=(15, 10), pady=10)
        self.feed_scroll.grid_columnconfigure(0, weight=1)

        # Panel trending di kanan
        self.trending_panel = ctk.CTkFrame(
            content_area, fg_color=self.colors["bg_secondary"],
            width=260, corner_radius=12
        )
        self.trending_panel.grid(row=0, column=1, sticky="ns", padx=(0, 15), pady=10)
        self.trending_panel.grid_propagate(False)

        self._load_feed()
        self._load_trending()

    def _load_feed(self):
        """
        Muat dan render semua postingan (diurutkan oleh score).
        Modul 5: Perulangan — iterasi daftar post
        """
        # Hapus post lama
        for widget in self.feed_scroll.winfo_children():
            widget.destroy()

        posts = db.get_all_posts()

        if not posts:
            empty_frame = ctk.CTkFrame(self.feed_scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(
                empty_frame, text="📭 Belum ada postingan.\nJadilah yang pertama! 🚀",
                font=ctk.CTkFont(size=16),
                text_color=self.colors["text_secondary"]
            ).pack()
            ctk.CTkButton(
                empty_frame, text="✏️ Buat Postingan", width=150,
                fg_color=self.colors["accent"],
                command=self._open_create_post
            ).pack(pady=15)
            return

        # Render setiap postingan sebagai kartu
        # Modul 5: Perulangan — render card per post
        for post in posts:
            card = PostCard(
                self.feed_scroll, post, self.session,
                self.colors, on_refresh=self._refresh
            )
            card.pack(fill="x", pady=6, padx=5)

    def _load_trending(self):
        """Muat dan tampilkan top 5 trending hashtags."""
        for widget in self.trending_panel.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.trending_panel, text="🔥 Trending",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["accent"]
        ).pack(pady=(15, 10), padx=15, anchor="w")

        trending = logic.get_top_trending(5)

        if not trending:
            ctk.CTkLabel(
                self.trending_panel, text="Belum ada trending",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)
        else:
            # Modul 5: Perulangan — tampilkan tiap hashtag
            for i, tag in enumerate(trending, 1):
                frame = ctk.CTkFrame(
                    self.trending_panel, fg_color=self.colors["bg_card"],
                    corner_radius=8
                )
                frame.pack(fill="x", padx=12, pady=4)
                
                number_label = ctk.CTkLabel(
                    frame, text=f"#{i}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors["accent2"],
                    width=35
                )
                number_label.pack(side="left", padx=8, pady=8)
                
                text_frame = ctk.CTkFrame(frame, fg_color="transparent")
                text_frame.pack(side="left", fill="x", expand=True, pady=8)
                
                ctk.CTkLabel(
                    text_frame,
                    text=f"#{tag['tag']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=self.colors["text_primary"],
                    anchor="w"
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    text_frame,
                    text=f"{tag['frequency']}× digunakan",
                    font=ctk.CTkFont(size=10),
                    text_color=self.colors["text_secondary"],
                    anchor="w"
                ).pack(anchor="w")

    def _refresh(self):
        """Refresh feed dan trending."""
        self._load_feed()
        self._load_trending()

    def _open_create_post(self):
        """Buka dialog untuk membuat postingan baru."""
        CreatePostDialog(self, self.session, self.colors, self._refresh)


# =============================================================================
# DIALOG: CREATE POST (Modal)
# =============================================================================

class CreatePostDialog(ctk.CTkToplevel):
    """Dialog untuk membuat postingan baru."""

    def __init__(self, master, session: Session, colors: dict, on_success: Callable):
        super().__init__(master)
        self.title("Buat Postingan Baru")
        self.geometry("550x450")
        self.session    = session
        self.colors     = colors
        self.on_success = on_success
        self.configure(fg_color=colors["bg_primary"])
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 550) // 2
        y = master.winfo_y() + (master.winfo_height() - 450) // 2
        self.geometry(f"+{x}+{y}")
        
        self._build()
        self.bind("<Escape>", lambda e: self.destroy())

    def _build(self):
        """Bangun form pembuatan post."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="✏️ Buat Postingan Baru",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, pady=20)

        self.content_box = ctk.CTkTextbox(
            self, height=180,
            fg_color=self.colors["bg_card"],
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(size=13)
        )
        self.content_box.grid(row=1, column=0, sticky="nsew", padx=25, pady=5)
        self.content_box.insert("0.0", "Tulis sesuatu... Gunakan #hashtag!")

        ctk.CTkLabel(
            self,
            text="💡 Tips: Gunakan #hashtag untuk trending!\n"
                 "🚫 Filter otomatis akan mengganti kata tidak pantas.",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=2, column=0, pady=10)

        self.msg_label = ctk.CTkLabel(self, text="", text_color=self.colors["danger"])
        self.msg_label.grid(row=3, column=0)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=(0, 20))

        ctk.CTkButton(
            btn_frame, text="Publikasikan 🚀", width=160, height=40,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._submit
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["accent2"],
            command=self.destroy
        ).pack(side="left", padx=8)

    def _submit(self):
        """Proses dan kirim postingan baru."""
        content = self.content_box.get("0.0", "end").strip()

        # Validasi konten kosong
        if not content or content == "Tulis sesuatu... Gunakan #hashtag!":
            self.msg_label.configure(text="⚠ Konten tidak boleh kosong.")
            return

        success, message, post_id = logic.process_new_post(
            self.session.user.user_id, content
        )

        if success:
            self.destroy()
            self.on_success()
        else:
            self.msg_label.configure(text=f"❌ {message}")


# =============================================================================
# PAGE: PROFILE
# =============================================================================

class ProfilePage(ctk.CTkFrame):
    """
    Halaman profil pengguna yang sedang login.
    Menampilkan info profil, statistik, karma, dan postingan pribadi.
    Memungkinkan edit profil (CRUD Update pada User).
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan halaman profil."""
        user = self.session.user

        # Refresh data user dari database
        fresh_user = db.get_user_by_id(user.user_id)
        if fresh_user:
            self.session.user = fresh_user
            user = fresh_user

        # Header profil
        profile_header = ctk.CTkFrame(
            self, fg_color=self.colors["bg_secondary"], height=200, corner_radius=0
        )
        profile_header.grid(row=0, column=0, sticky="ew")
        profile_header.grid_columnconfigure(1, weight=1)
        profile_header.grid_propagate(False)

        # Avatar besar dengan gradient effect
        avatar_frame = ctk.CTkFrame(
            profile_header, fg_color=self.colors["accent2"],
            width=100, height=100, corner_radius=50
        )
        avatar_frame.grid(row=0, column=0, rowspan=3, padx=30, pady=25)
        avatar_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            avatar_frame, text=user.username[0].upper(),
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Info user
        badge = logic.get_badge_for_karma(user.karma)
        follow_data = db.get_follow_counts(user.user_id)

        ctk.CTkLabel(
            profile_header,
            text=f"@{user.username}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=1, sticky="w", padx=10, pady=(25, 5))

        ctk.CTkLabel(
            profile_header,
            text=f"{badge}  •  {user.role.capitalize()}",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["accent2"]
        ).grid(row=1, column=1, sticky="w", padx=10)

        ctk.CTkLabel(
            profile_header,
            text=f"📧 {user.email}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        ).grid(row=2, column=1, sticky="w", padx=10)

        # Statistik
        stats_frame = ctk.CTkFrame(profile_header, fg_color=self.colors["bg_card"], corner_radius=10)
        stats_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=25, sticky="n")
        
        stats = [
            ("⭐ Karma", str(user.karma)),
            ("👥 Followers", str(follow_data['followers'])),
            ("➕ Following", str(follow_data['following'])),
        ]
        
        for i, (label, value) in enumerate(stats):
            ctk.CTkLabel(
                stats_frame, text=label,
                font=ctk.CTkFont(size=10),
                text_color=self.colors["text_secondary"]
            ).grid(row=i, column=0, padx=15, pady=(8, 0))
            ctk.CTkLabel(
                stats_frame, text=value,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=self.colors["accent"]
            ).grid(row=i, column=1, padx=10, pady=(8, 0))

        ctk.CTkButton(
            stats_frame, text="✏️ Edit Profil",
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            height=32, width=100,
            command=self._edit_profile
        ).grid(row=3, column=0, columnspan=2, pady=(10, 8), padx=10)

        # Bio section
        bio_frame = ctk.CTkFrame(profile_header, fg_color=self.colors["bg_card"], corner_radius=10)
        bio_frame.grid(row=0, column=3, rowspan=3, padx=20, pady=25, sticky="nsew")
        
        ctk.CTkLabel(
            bio_frame, text="📝 Bio",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w", padx=12, pady=(10, 5))
        
        ctk.CTkLabel(
            bio_frame, text=user.bio or "Belum ada bio. Klik Edit Profil untuk menambahkan.",
            wraplength=200,
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        ).pack(padx=12, pady=(0, 10))

        # Progress karma ke badge berikutnya
        progress_frame = ctk.CTkFrame(profile_header, fg_color=self.colors["bg_card"], corner_radius=10)
        progress_frame.grid(row=0, column=4, rowspan=3, padx=(0, 30), pady=25, sticky="n")
        
        current, target, next_badge = logic.get_karma_progress(user.karma)
        progress = min(1.0, current / target) if target > 0 else 1.0
        
        ctk.CTkLabel(
            progress_frame, text=f"🎯 Progress ke {next_badge}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=(10, 5), padx=10)
        
        progress_bar = ctk.CTkProgressBar(
            progress_frame, width=180, height=10,
            progress_color=self.colors["success"]
        )
        progress_bar.pack(pady=5, padx=10)
        progress_bar.set(progress)
        
        ctk.CTkLabel(
            progress_frame,
            text=f"{current} / {target} karma",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_secondary"]
        ).pack(pady=(0, 10), padx=10)

        # Postingan pribadi
        ctk.CTkLabel(
            self, text="📝 Postingan Saya",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=1, column=0, sticky="w", padx=25, pady=(15, 5))

        self.post_scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.post_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.post_scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._load_my_posts()

    def _load_my_posts(self):
        """Muat postingan milik user yang login."""
        posts = db.get_posts_by_user(self.session.user.user_id)

        if not posts:
            ctk.CTkLabel(
                self.post_scroll,
                text="📭 Kamu belum membuat postingan apapun.",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=13)
            ).pack(pady=40)
            return

        for post in posts:
            card = PostCard(
                self.post_scroll, post, self.session,
                self.colors, on_refresh=self._load_my_posts
            )
            card.pack(fill="x", pady=6)

    def _edit_profile(self):
        """Buka dialog edit profil (CRUD Update User)."""
        EditProfileDialog(self, self.session, self.colors, self._rebuild)

    def _rebuild(self):
        """Rebuild halaman profil setelah edit."""
        for w in self.winfo_children():
            w.destroy()
        self._build()


# =============================================================================
# DIALOG: EDIT PROFILE (Modal)
# =============================================================================

class EditProfileDialog(ctk.CTkToplevel):
    """Dialog untuk mengedit profil pengguna."""

    def __init__(self, master, session: Session, colors: dict, on_success: Callable):
        super().__init__(master)
        self.title("Edit Profil")
        self.geometry("450x350")
        self.session    = session
        self.colors     = colors
        self.on_success = on_success
        self.configure(fg_color=colors["bg_primary"])
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 450) // 2
        y = master.winfo_y() + (master.winfo_height() - 350) // 2
        self.geometry(f"+{x}+{y}")
        
        self._build()
        self.bind("<Escape>", lambda e: self.destroy())

    def _build(self):
        """Bangun form edit profil."""
        user = self.session.user
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="✏️ Edit Profil",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, pady=20)

        ctk.CTkLabel(self, text="Email:",
                     text_color=self.colors["text_secondary"]).grid(
            row=1, column=0, sticky="w", padx=35)
        self.email_entry = ctk.CTkEntry(
            self, width=380, height=40,
            fg_color=self.colors["bg_card"]
        )
        self.email_entry.insert(0, user.email)
        self.email_entry.grid(row=2, column=0, padx=35, pady=(2, 15))

        ctk.CTkLabel(self, text="Bio:",
                     text_color=self.colors["text_secondary"]).grid(
            row=3, column=0, sticky="w", padx=35)
        self.bio_entry = ctk.CTkTextbox(
            self, width=380, height=100,
            fg_color=self.colors["bg_card"]
        )
        self.bio_entry.insert("0.0", user.bio or "")
        self.bio_entry.grid(row=4, column=0, padx=35, pady=(2, 15))

        self.msg_label = ctk.CTkLabel(self, text="", text_color=self.colors["danger"])
        self.msg_label.grid(row=5, column=0)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="Simpan Perubahan", width=160, height=40,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._save
        ).pack(side="left", padx=8)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color=self.colors["bg_card"],
            command=self.destroy
        ).pack(side="left", padx=8)

    def _save(self):
        """Simpan perubahan profil ke database."""
        email = self.email_entry.get().strip()
        bio   = self.bio_entry.get("0.0", "end").strip()

        valid, msg = logic.validate_email(email)
        if not valid:
            self.msg_label.configure(text=f"⚠ {msg}")
            return

        success, message = db.update_user(self.session.user.user_id, bio, email)
        if success:
            self.session.user.email = email
            self.session.user.bio   = bio
            self.destroy()
            self.on_success()
        else:
            self.msg_label.configure(text=f"❌ {message}")


# =============================================================================
# PAGE: SEARCH (Dengan loading state)
# =============================================================================

class SearchPage(ctk.CTkFrame):
    """
    Halaman pencarian cerdas (Bonus: Smart Search).
    Mendukung partial match dan case-insensitive untuk users, posts, hashtags.
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan halaman pencarian."""
        # Header
        ctk.CTkLabel(
            self, text="🔍 Pencarian Cerdas",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=(20, 10), sticky="w")

        # Form pencarian
        search_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_secondary"], height=80, corner_radius=12)
        search_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=5)
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_propagate(False)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Cari user, postingan, atau #hashtag...",
            fg_color=self.colors["bg_card"], height=45,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=17)
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        ctk.CTkButton(
            search_frame, text="🔍 Cari", width=100, height=45,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._do_search
        ).grid(row=0, column=1, padx=(0, 20), pady=17)

        # Area hasil pencarian
        self.result_scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.result_scroll.grid(row=2, column=0, sticky="nsew", padx=25, pady=10)
        self.result_scroll.grid_columnconfigure(0, weight=1)

        self._show_welcome()

    def _show_welcome(self):
        """Tampilkan pesan selamat datang di halaman pencarian."""
        for w in self.result_scroll.winfo_children():
            w.destroy()
        
        welcome_frame = ctk.CTkFrame(self.result_scroll, fg_color="transparent")
        welcome_frame.pack(expand=True, fill="both", pady=60)
        
        ctk.CTkLabel(
            welcome_frame,
            text="🔍",
            font=ctk.CTkFont(size=64),
        ).pack()
        
        ctk.CTkLabel(
            welcome_frame,
            text="Cari Apa Hari Ini?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=10)
        
        ctk.CTkLabel(
            welcome_frame,
            text="Cari pengguna, postingan, atau hashtag dengan kata kunci apapun",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=12)
        ).pack()
        
        ctk.CTkLabel(
            welcome_frame,
            text="💡 Contoh: 'python', 'alice', '#coding'",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(size=11)
        ).pack(pady=10)

    def _show_loading(self):
        """Tampilkan indikator loading."""
        for w in self.result_scroll.winfo_children():
            w.destroy()
        
        ctk.CTkLabel(
            self.result_scroll,
            text="⏳ Mencari...",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        ).pack(pady=50)

    def _do_search(self):
        """Jalankan pencarian dan tampilkan hasil."""
        query = self.search_entry.get().strip()
        if not query:
            self._show_welcome()
            return

        self._show_loading()
        self.update_idletasks()

        results = logic.smart_search(query)

        # Hapus hasil lama
        for w in self.result_scroll.winfo_children():
            w.destroy()

        any_result = False

        # Tampilkan hasil Users
        if results["users"]:
            any_result = True
            section = ctk.CTkFrame(self.result_scroll, fg_color="transparent")
            section.pack(fill="x", pady=(0, 15))
            
            ctk.CTkLabel(
                section, text="👤 Pengguna",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors["accent"]
            ).pack(anchor="w", pady=(0, 8))

            # Modul 5: Perulangan — render tiap user
            for user in results["users"]:
                self._render_user_card(user)

        # Tampilkan hasil Posts
        if results["posts"]:
            any_result = True
            section = ctk.CTkFrame(self.result_scroll, fg_color="transparent")
            section.pack(fill="x", pady=(0, 15))
            
            ctk.CTkLabel(
                section, text="📝 Postingan",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors["accent"]
            ).pack(anchor="w", pady=(0, 8))

            for post in results["posts"]:
                card = PostCard(
                    section, post, self.session,
                    self.colors, on_refresh=self._do_search
                )
                card.pack(fill="x", pady=4)

        # Tampilkan hasil Hashtags
        if results["hashtags"]:
            any_result = True
            section = ctk.CTkFrame(self.result_scroll, fg_color="transparent")
            section.pack(fill="x", pady=(0, 15))
            
            ctk.CTkLabel(
                section, text="🏷️ Hashtag",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors["accent"]
            ).pack(anchor="w", pady=(0, 8))
            
            tags_frame = ctk.CTkFrame(section, fg_color=self.colors["bg_card"], corner_radius=10)
            tags_frame.pack(fill="x")
            
            for tag in results["hashtags"]:
                tag_frame = ctk.CTkFrame(tags_frame, fg_color="transparent")
                tag_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(
                    tag_frame,
                    text=f"#{tag['tag']}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=self.colors["accent2"]
                ).pack(side="left")
                
                ctk.CTkLabel(
                    tag_frame,
                    text=f"{tag['frequency']} postingan",
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors["text_secondary"]
                ).pack(side="right")

        if not any_result:
            ctk.CTkLabel(
                self.result_scroll,
                text=f"😕 Tidak ada hasil untuk '{query}'",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).pack(pady=60)

    def _render_user_card(self, user):
        """Render kartu info pengguna hasil pencarian."""
        card = ctk.CTkFrame(
            self.result_scroll, fg_color=self.colors["bg_card"],
            corner_radius=10
        )
        card.pack(fill="x", pady=4)
        card.grid_columnconfigure(1, weight=1)

        # Avatar
        ctk.CTkLabel(
            card, text=user.username[0].upper(),
            width=45, height=45,
            fg_color=self.colors["accent2"],
            text_color="white",
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=22
        ).grid(row=0, column=0, rowspan=2, padx=12, pady=8)

        ctk.CTkLabel(
            card, text=f"@{user.username}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=1, sticky="w", padx=8, pady=(8, 0))

        badge = logic.get_badge_for_karma(user.karma)
        ctk.CTkLabel(
            card, text=f"{badge}  |  Karma: {user.karma}",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 8))

        # Tombol follow (jika bukan diri sendiri)
        if user.user_id != self.session.user.user_id:
            is_followed = db.is_following(self.session.user.user_id, user.user_id)
            follow_text  = "✓ Following" if is_followed else "+ Follow"
            follow_color = self.colors["success"] if is_followed else self.colors["accent"]

            ctk.CTkButton(
                card, text=follow_text, width=90, height=32,
                fg_color=follow_color,
                corner_radius=16,
                command=lambda uid=user.user_id: self._toggle_follow(uid)
            ).grid(row=0, column=2, rowspan=2, padx=10, pady=8)

            ctk.CTkButton(
                card, text="👋 Teman", width=80, height=32,
                fg_color=self.colors["accent2"],
                corner_radius=16,
                command=lambda uid=user.user_id: self._send_friend_req(uid)
            ).grid(row=0, column=3, rowspan=2, padx=(0, 12), pady=8)

    def _toggle_follow(self, target_id: int):
        """Toggle follow/unfollow pengguna."""
        followed, msg = db.toggle_follow(self.session.user.user_id, target_id)
        if followed:
            logic.award_karma(target_id, "followed")
        self._do_search()

    def _send_friend_req(self, target_id: int):
        """Kirim permintaan pertemanan."""
        success, msg = db.send_friend_request(self.session.user.user_id, target_id)
        self._show_info("Info", msg)
    
    def _show_info(self, title: str, message: str):
        """Tampilkan dialog info."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"✅ {message}", wraplength=300,
                     text_color=self.colors["success"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)


# =============================================================================
# PAGE: SOCIAL (Follow & Friend Request)
# =============================================================================

class SocialPage(ctk.CTkFrame):
    """
    Halaman aktivitas sosial:
        - Daftar following/followers
        - Permintaan pertemanan masuk
        - Kelola follow
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan halaman sosial."""
        ctk.CTkLabel(
            self, text="👥 Aktivitas Sosial",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=(20, 10), sticky="w")

        tab = ctk.CTkTabview(
            self,
            fg_color=self.colors["bg_secondary"],
            segmented_button_fg_color=self.colors["bg_card"],
            segmented_button_selected_color=self.colors["accent"],
            segmented_button_selected_hover_color=self.colors["accent_hover"],
        )
        tab.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        tab.add("📨 Permintaan Teman")
        tab.add("👥 Semua Pengguna")

        self._build_friend_requests(tab.tab("📨 Permintaan Teman"))
        self._build_all_users(tab.tab("👥 Semua Pengguna"))

    def _build_friend_requests(self, parent):
        """Tampilkan permintaan pertemanan yang masuk."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        pending = db.get_pending_requests(self.session.user.user_id)

        if not pending:
            empty_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(
                empty_frame, text="📭 Tidak ada permintaan pertemanan yang masuk.",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=13)
            ).pack()
            return

        for req in pending:
            card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=f"@{req['sender_name']} ingin berteman",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_primary"]
            ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))
            
            ctk.CTkLabel(
                card,
                text=f"📅 {req['created_at'][:16]}",
                font=ctk.CTkFont(size=10),
                text_color=self.colors["text_secondary"]
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, rowspan=2, padx=12, pady=8)

            ctk.CTkButton(
                btn_frame, text="✅ Terima", width=90, height=32,
                fg_color=self.colors["success"],
                hover_color="#0D9488",
                corner_radius=16,
                command=lambda rid=req["request_id"]: self._respond(rid, "accepted")
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                btn_frame, text="❌ Tolak", width=90, height=32,
                fg_color=self.colors["danger"],
                hover_color="#B91C1C",
                corner_radius=16,
                command=lambda rid=req["request_id"]: self._respond(rid, "rejected")
            ).pack(side="left", padx=3)

    def _build_all_users(self, parent):
        """Tampilkan daftar semua pengguna dengan tombol follow."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        users = db.get_all_users()
        current_uid = self.session.user.user_id

        for user in users:
            if user.user_id == current_uid:
                continue  # Skip diri sendiri

            card = ctk.CTkFrame(scroll, fg_color=self.colors["bg_card"], corner_radius=10)
            card.pack(fill="x", pady=4, padx=5)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                card, text=user.username[0].upper(),
                width=40, height=40,
                fg_color=self.colors["accent2"],
                text_color="white",
                font=ctk.CTkFont(size=16, weight="bold"),
                corner_radius=20
            ).grid(row=0, column=0, rowspan=2, padx=12, pady=8)

            badge = logic.get_badge_for_karma(user.karma)
            ctk.CTkLabel(
                card,
                text=f"@{user.username}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_primary"]
            ).grid(row=0, column=1, sticky="w", padx=8, pady=(8, 0))
            
            ctk.CTkLabel(
                card,
                text=f"{badge}  •  Karma: {user.karma}",
                font=ctk.CTkFont(size=10),
                text_color=self.colors["text_secondary"]
            ).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 8))

            is_followed = db.is_following(current_uid, user.user_id)
            follow_text  = "✓ Following" if is_followed else "+ Follow"
            follow_color = self.colors["success"] if is_followed else self.colors["accent"]

            ctk.CTkButton(
                card, text=follow_text, width=90, height=32,
                fg_color=follow_color,
                corner_radius=16,
                command=lambda uid=user.user_id: self._toggle_follow_refresh(uid)
            ).grid(row=0, column=2, rowspan=2, padx=8, pady=8)

            ctk.CTkButton(
                card, text="👋", width=45, height=32,
                fg_color=self.colors["accent2"],
                corner_radius=16,
                command=lambda uid=user.user_id: self._friend_req(uid)
            ).grid(row=0, column=3, rowspan=2, padx=(0, 12), pady=8)

    def _respond(self, request_id: int, action: str):
        """Respons permintaan pertemanan."""
        success, msg = db.respond_friend_request(request_id, action)
        self._show_info("Info", msg)
        # Rebuild halaman
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _toggle_follow_refresh(self, target_id: int):
        """Toggle follow dan refresh halaman."""
        followed, msg = db.toggle_follow(self.session.user.user_id, target_id)
        if followed:
            logic.award_karma(target_id, "followed")
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _friend_req(self, target_id: int):
        """Kirim permintaan pertemanan."""
        success, msg = db.send_friend_request(self.session.user.user_id, target_id)
        self._show_info("Info", msg)
    
    def _show_info(self, title: str, message: str):
        """Tampilkan dialog info."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"✅ {message}", wraplength=300,
                     text_color=self.colors["success"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)


# =============================================================================
# PAGE: SAVED POSTS
# =============================================================================

class SavedPage(ctk.CTkFrame):
    """Halaman postingan yang disimpan pengguna."""

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan halaman saved posts."""
        ctk.CTkLabel(
            self, text="🔖 Postingan Tersimpan",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=(20, 10), sticky="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        scroll.grid_columnconfigure(0, weight=1)

        saved_posts = db.get_saved_posts(self.session.user.user_id)

        if not saved_posts:
            empty_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=60)
            ctk.CTkLabel(
                empty_frame, text="📭",
                font=ctk.CTkFont(size=48),
            ).pack()
            ctk.CTkLabel(
                empty_frame,
                text="Kamu belum menyimpan postingan apapun.",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).pack(pady=10)
            ctk.CTkLabel(
                empty_frame,
                text="Klik 🔖 pada postingan untuk menyimpannya.",
                text_color=self.colors["accent"],
                font=ctk.CTkFont(size=12)
            ).pack()
            return

        for post in saved_posts:
            card = PostCard(
                scroll, post, self.session,
                self.colors, on_refresh=self._refresh
            )
            card.pack(fill="x", pady=6)

    def _refresh(self):
        """Refresh halaman."""
        for w in self.winfo_children():
            w.destroy()
        self._build()


# =============================================================================
# PAGE: COMMUNITY
# =============================================================================

class CommunityPage(ctk.CTkFrame):
    """
    Halaman manajemen komunitas/hashtag.
    CRUD penuh: Create, Read, Update, Delete komunitas.
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan halaman komunitas."""
        # Header dengan tombol tambah
        header = ctk.CTkFrame(
            self, fg_color=self.colors["bg_secondary"], height=70, corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header, text="🏘️ Komunitas",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=15, sticky="w")

        ctk.CTkButton(
            header, text="+ Buat Komunitas", width=140, height=38,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._create_community
        ).grid(row=0, column=1, padx=15, pady=15)

        # Daftar komunitas
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        scroll.grid_columnconfigure(0, weight=1)

        communities = db.get_all_communities()

        if not communities:
            empty_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(
                empty_frame, text="🏘️",
                font=ctk.CTkFont(size=48),
            ).pack()
            ctk.CTkLabel(
                empty_frame, text="Belum ada komunitas. Buat yang pertama!",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).pack(pady=10)
            return

        for comm in communities:
            self._render_community_card(scroll, comm)

    def _render_community_card(self, parent, comm: dict):
        """Render kartu komunitas."""
        card = ctk.CTkFrame(
            parent, fg_color=self.colors["bg_card"],
            corner_radius=12, border_width=1,
            border_color=self.colors["border"]
        )
        card.pack(fill="x", pady=6)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=f"🏘️ {comm['name']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            card,
            text=comm["description"] or "Tidak ada deskripsi",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 4))

        ctk.CTkLabel(
            card,
            text=f"👤 {comm['member_count']} anggota  |  📝 {comm['post_count']} post  |  📅 Dibuat oleh @{comm['creator_name']}",
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=10)
        ).grid(row=2, column=0, sticky="w", padx=15, pady=(0, 12))

        # Tombol edit/hapus jika creator atau admin
        user = self.session.user
        if user.user_id == comm["creator_id"] or user.role == "admin":
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, rowspan=3, padx=15, pady=10)

            ctk.CTkButton(
                btn_frame, text="✏️ Edit", width=75, height=30,
                fg_color=self.colors["accent2"],
                corner_radius=15,
                command=lambda c=comm: self._edit_community(c)
            ).pack(pady=3)

            ctk.CTkButton(
                btn_frame, text="🗑️ Hapus", width=75, height=30,
                fg_color=self.colors["danger"],
                hover_color="#B91C1C",
                corner_radius=15,
                command=lambda cid=comm["community_id"]: self._delete_community(cid)
            ).pack(pady=3)

    def _create_community(self):
        """Buka dialog buat komunitas baru."""
        CommunityDialog(self, None, self.session, self.colors, self._refresh)

    def _edit_community(self, comm: dict):
        """Buka dialog edit komunitas."""
        CommunityDialog(self, comm, self.session, self.colors, self._refresh)

    def _delete_community(self, community_id: int):
        """Hapus komunitas setelah konfirmasi."""
        if self._show_confirmation("Konfirmasi", "Yakin ingin menghapus komunitas ini?"):
            success, msg = db.delete_community(community_id)
            if success:
                self._refresh()
            else:
                self._show_error("Error", msg)
    
    def _refresh(self):
        """Refresh halaman komunitas."""
        for w in self.winfo_children():
            w.destroy()
        self._build()
    
    def _show_confirmation(self, title: str, message: str) -> bool:
        """Tampilkan dialog konfirmasi."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        result = [False]
        
        ctk.CTkLabel(dialog, text=message, wraplength=300,
                     text_color=self.colors["text_primary"]).pack(pady=30)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Ya", width=80,
                      fg_color=self.colors["danger"],
                      command=lambda: [result.__setitem__(0, True), dialog.destroy()]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Tidak", width=80,
                      fg_color=self.colors["bg_card"],
                      command=dialog.destroy).pack(side="left", padx=10)
        
        self.wait_window(dialog)
        return result[0]
    
    def _show_error(self, title: str, message: str):
        """Tampilkan dialog error."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"❌ {message}", wraplength=300,
                     text_color=self.colors["danger"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)


# =============================================================================
# DIALOG: COMMUNITY (Modal)
# =============================================================================

class CommunityDialog(ctk.CTkToplevel):
    """Dialog untuk membuat atau mengedit komunitas."""

    def __init__(self, master, community: Optional[dict], session: Session,
                 colors: dict, on_success: Callable):
        super().__init__(master)
        is_edit = community is not None
        self.title("Edit Komunitas" if is_edit else "Buat Komunitas Baru")
        self.geometry("450x320")
        self.community  = community
        self.session    = session
        self.colors     = colors
        self.on_success = on_success
        self.configure(fg_color=colors["bg_primary"])
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 450) // 2
        y = master.winfo_y() + (master.winfo_height() - 320) // 2
        self.geometry(f"+{x}+{y}")
        
        self._build(is_edit)
        self.bind("<Escape>", lambda e: self.destroy())

    def _build(self, is_edit: bool):
        """Bangun form komunitas."""
        self.grid_columnconfigure(0, weight=1)

        title_text = "✏️ Edit Komunitas" if is_edit else "➕ Buat Komunitas Baru"
        ctk.CTkLabel(
            self, text=title_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, pady=20)

        ctk.CTkLabel(self, text="Nama Komunitas:",
                     text_color=self.colors["text_secondary"]).grid(
            row=1, column=0, sticky="w", padx=35)
        self.name_entry = ctk.CTkEntry(self, width=380, height=40,
                                        fg_color=self.colors["bg_card"])
        if is_edit:
            self.name_entry.insert(0, self.community["name"])
        self.name_entry.grid(row=2, column=0, padx=35, pady=(2, 15))

        ctk.CTkLabel(self, text="Deskripsi:",
                     text_color=self.colors["text_secondary"]).grid(
            row=3, column=0, sticky="w", padx=35)
        self.desc_entry = ctk.CTkTextbox(self, width=380, height=80,
                                          fg_color=self.colors["bg_card"])
        if is_edit:
            self.desc_entry.insert("0.0", self.community["description"] or "")
        self.desc_entry.grid(row=4, column=0, padx=35, pady=(2, 15))

        self.msg_label = ctk.CTkLabel(self, text="", text_color=self.colors["danger"])
        self.msg_label.grid(row=5, column=0)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, pady=15)
        
        btn_text = "Simpan" if is_edit else "Buat Komunitas"
        ctk.CTkButton(
            btn_frame, text=btn_text, width=160, height=40,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._save
        ).pack(side="left", padx=8)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color=self.colors["bg_card"],
            command=self.destroy
        ).pack(side="left", padx=8)

    def _save(self):
        """Simpan komunitas (create atau update)."""
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get("0.0", "end").strip()

        if not name:
            self.msg_label.configure(text="⚠ Nama komunitas tidak boleh kosong.")
            return

        if self.community:
            success, msg = db.update_community(
                self.community["community_id"], name, desc
            )
        else:
            success, msg = db.create_community(name, desc, self.session.user.user_id)

        if success:
            self.destroy()
            self.on_success()
        else:
            self.msg_label.configure(text=f"❌ {msg}")


# =============================================================================
# PAGE: MODERATION (Moderator + Admin) - Perbaikan warna
# =============================================================================

class ModerationPage(ctk.CTkFrame):
    """
    Halaman moderasi konten.
    Menampilkan log pelanggaran dan kontrol moderasi.
    Hanya bisa diakses oleh Moderator dan Admin.
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan halaman moderasi."""
        ctk.CTkLabel(
            self, text="🛡️ Moderasi Konten",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=(20, 10), sticky="w")

        scroll = ctk.CTkScrollableFrame(
            self, fg_color=self.colors["bg_secondary"],
            label_text="📋 Log Pelanggaran Konten",
            label_font=ctk.CTkFont(size=14, weight="bold")
        )
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        scroll.grid_columnconfigure(0, weight=1)

        logs = db.get_all_violation_logs()

        if not logs:
            empty_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(
                empty_frame, text="✅",
                font=ctk.CTkFont(size=48),
            ).pack()
            ctk.CTkLabel(
                empty_frame, text="Tidak ada pelanggaran konten yang tercatat.",
                text_color=self.colors["success"],
                font=ctk.CTkFont(size=14)
            ).pack(pady=10)
            return

        # Modul 5: Perulangan — render tiap log
        for log in logs:
            card = ctk.CTkFrame(
                scroll, fg_color=self.colors["bg_card"],
                corner_radius=10, border_width=1,
                border_color=self.colors["warning"]
            )
            card.pack(fill="x", pady=6, padx=5)

            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=12, pady=(10, 5))
            
            ctk.CTkLabel(
                header_frame,
                text=f"⚠️",
                font=ctk.CTkFont(size=14),
                text_color=self.colors["warning"]
            ).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(
                header_frame,
                text=f"@{log['username']}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["accent"]
            ).pack(side="left")
            
            ctk.CTkLabel(
                header_frame,
                text=f"Post #{log['post_id']}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors["text_secondary"]
            ).pack(side="left", padx=(8, 0))
            
            ctk.CTkLabel(
                header_frame,
                text=f"📅 {log['created_at'][:16]}",
                font=ctk.CTkFont(size=10),
                text_color=self.colors["text_secondary"]
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=f"Original : {log['original'][:100]}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors["text_secondary"]
            ).pack(anchor="w", padx=12, pady=(0, 4))

            ctk.CTkLabel(
                card,
                text=f"Filtered : {log['filtered'][:100]}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors["accent"]
            ).pack(anchor="w", padx=12, pady=(0, 10))


# =============================================================================
# PAGE: ADMIN — MANAGE USERS (Dengan perbaikan warna)
# =============================================================================

class AdminUsersPage(ctk.CTkFrame):
    """
    Halaman manajemen pengguna (khusus Admin).
    Mendukung CRUD penuh pada entitas User.
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan manajemen pengguna."""
        header = ctk.CTkFrame(
            self, fg_color=self.colors["bg_secondary"], height=70, corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header, text="👑 Kelola Pengguna",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=15, sticky="w")

        ctk.CTkButton(
            header, text="+ Tambah User", width=140, height=38,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._add_user
        ).grid(row=0, column=1, padx=15, pady=15)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        scroll.grid_columnconfigure(0, weight=1)

        users = db.get_all_users()

        # Header tabel dengan desain lebih baik
        header_row = ctk.CTkFrame(scroll, fg_color=self.colors["accent2"], corner_radius=8)
        header_row.pack(fill="x", pady=(0, 5))
        
        cols = ["Username", "Email", "Role", "Karma", "Badge", "Status", "Aksi"]
        weights = [2, 3, 1, 1, 2, 1, 2]

        for j, (col, w) in enumerate(zip(cols, weights)):
            header_row.grid_columnconfigure(j, weight=w)
            ctk.CTkLabel(
                header_row, text=col,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=j, padx=10, pady=8, sticky="w")

        # Render baris user (Modul 5: Perulangan)
        for i, user in enumerate(users):
            row_fg = self.colors["bg_secondary"] if i % 2 == 0 else self.colors["bg_card"]
            row = ctk.CTkFrame(scroll, fg_color=row_fg, corner_radius=6)
            row.pack(fill="x", pady=2)
            for j, w in enumerate(weights):
                row.grid_columnconfigure(j, weight=w)

            status_text  = "Aktif" if user.is_active else "Nonaktif"
            status_color = self.colors["success"] if user.is_active else self.colors["danger"]
            badge_color = self._get_badge_color(user.badge)

            data_cells = [
                (f"@{user.username}", self.colors["text_primary"]),
                (user.email,          self.colors["text_secondary"]),
                (user.role,           self.colors["info"]),
                (str(user.karma),     self.colors["warning"]),
                (user.badge,          badge_color),
                (status_text,         status_color),
            ]

            for j, (text, color) in enumerate(data_cells):
                ctk.CTkLabel(
                    row, text=text,
                    font=ctk.CTkFont(size=11),
                    text_color=color
                ).grid(row=0, column=j, padx=10, pady=8, sticky="w")

            # Tombol aksi (hapus/nonaktifkan)
            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.grid(row=0, column=6, padx=8, pady=4)

            if user.user_id != self.session.user.user_id:
                ctk.CTkButton(
                    action_frame, text="🗑️ Nonaktif", width=95, height=28,
                    fg_color=self.colors["danger"],
                    hover_color="#B91C1C",
                    font=ctk.CTkFont(size=10),
                    corner_radius=14,
                    command=lambda uid=user.user_id: self._deactivate(uid)
                ).pack(side="left", padx=2)

    def _get_badge_color(self, badge: str) -> str:
        """Dapatkan warna untuk badge."""
        badge_colors = {
            "Social Star": "#F59E0B",
            "Influencer": "#EF4444",
            "Active User": "#10B981",
            "Beginner": "#6B7280",
        }
        return badge_colors.get(badge, self.colors["text_secondary"])

    def _add_user(self):
        """Buka dialog tambah pengguna baru (oleh admin)."""
        AddUserDialog(self, self.session, self.colors, self._refresh)

    def _deactivate(self, user_id: int):
        """Nonaktifkan pengguna setelah konfirmasi."""
        if self._show_confirmation("Konfirmasi", "Yakin ingin menonaktifkan pengguna ini?"):
            success, msg = db.delete_user(user_id)
            if success:
                self._refresh()
            else:
                self._show_error("Error", msg)
    
    def _refresh(self):
        """Refresh halaman."""
        for w in self.winfo_children():
            w.destroy()
        self._build()
    
    def _show_confirmation(self, title: str, message: str) -> bool:
        """Tampilkan dialog konfirmasi."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        result = [False]
        
        ctk.CTkLabel(dialog, text=message, wraplength=300,
                     text_color=self.colors["text_primary"]).pack(pady=30)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Ya", width=80,
                      fg_color=self.colors["danger"],
                      command=lambda: [result.__setitem__(0, True), dialog.destroy()]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Tidak", width=80,
                      fg_color=self.colors["bg_card"],
                      command=dialog.destroy).pack(side="left", padx=10)
        
        self.wait_window(dialog)
        return result[0]
    
    def _show_error(self, title: str, message: str):
        """Tampilkan dialog error."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"❌ {message}", wraplength=300,
                     text_color=self.colors["danger"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)


# =============================================================================
# DIALOG: ADD USER (Admin) - Modal
# =============================================================================

class AddUserDialog(ctk.CTkToplevel):
    """Dialog untuk admin menambah pengguna baru."""

    def __init__(self, master, session: Session, colors: dict, on_success: Callable):
        super().__init__(master)
        self.title("Tambah Pengguna Baru")
        self.geometry("450x400")
        self.session    = session
        self.colors     = colors
        self.on_success = on_success
        self.configure(fg_color=colors["bg_primary"])
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 450) // 2
        y = master.winfo_y() + (master.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")
        
        self._build()
        self.bind("<Escape>", lambda e: self.destroy())

    def _build(self):
        """Bangun form tambah user."""
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="➕ Tambah Pengguna Baru",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, pady=20)

        fields = [
            ("Username",  "add_username", ""),
            ("Email",     "add_email",    ""),
            ("Password",  "add_password", ""),
        ]

        for i, (label, attr, placeholder) in enumerate(fields, start=1):
            ctk.CTkLabel(self, text=f"{label}:",
                         text_color=self.colors["text_secondary"]).grid(
                row=i*2-1, column=0, sticky="w", padx=35)
            show = "•" if "password" in attr else ""
            entry = ctk.CTkEntry(
                self, width=380, height=40,
                fg_color=self.colors["bg_card"],
                show=show, placeholder_text=placeholder
            )
            entry.grid(row=i*2, column=0, padx=35, pady=(2, 10))
            setattr(self, attr, entry)

        ctk.CTkLabel(self, text="Role:",
                     text_color=self.colors["text_secondary"]).grid(
            row=7, column=0, sticky="w", padx=35)
        self.role_var = ctk.StringVar(value="user")
        ctk.CTkOptionMenu(
            self, values=["user", "moderator", "admin"],
            variable=self.role_var,
            fg_color=self.colors["bg_card"],
            button_color=self.colors["accent"],
            width=380
        ).grid(row=8, column=0, padx=35, pady=(2, 15))

        self.msg_label = ctk.CTkLabel(self, text="", text_color=self.colors["danger"])
        self.msg_label.grid(row=9, column=0)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=10, column=0, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="Tambah Pengguna", width=160, height=40,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._save
        ).pack(side="left", padx=8)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color=self.colors["bg_card"],
            command=self.destroy
        ).pack(side="left", padx=8)

    def _save(self):
        """Simpan pengguna baru."""
        username = self.add_username.get().strip()
        email    = self.add_email.get().strip()
        password = self.add_password.get()
        role     = self.role_var.get()

        # Validasi semua field
        for label, value, validator in [
            ("Username", username, logic.validate_username),
            ("Email",    email,    logic.validate_email),
            ("Password", password, logic.validate_password),
        ]:
            valid, msg = validator(value)
            if not valid:
                self.msg_label.configure(text=f"⚠ {msg}")
                return

        success, message = db.create_user(username, password, email, role)
        if success:
            self.destroy()
            self.on_success()
        else:
            self.msg_label.configure(text=f"❌ {message}")


# =============================================================================
# PAGE: ANALYTICS DASHBOARD (Dengan perbaikan tampilan)
# =============================================================================

class AnalyticsPage(ctk.CTkFrame):
    """
    Dashboard analitik (khusus Admin).
    Menampilkan: engagement score per post, trending hashtags,
    user activity summary. Mendukung export TXT dan CSV.
    """

    def __init__(self, master, session: Session, colors: dict, nav_frame=None):
        super().__init__(master, fg_color=colors["bg_primary"])
        self.session   = session
        self.colors    = colors
        self.nav_frame = nav_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        """Bangun tampilan dashboard analitik."""
        # Header dengan tombol export
        header = ctk.CTkFrame(
            self, fg_color=self.colors["bg_secondary"], height=70, corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header, text="📊 Dashboard Analitik",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, padx=25, pady=15, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=15, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="📄 Export TXT", width=120, height=38,
            fg_color=self.colors["info"],
            hover_color="#0891B2",
            command=self._export_txt
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="📊 Export CSV", width=120, height=38,
            fg_color=self.colors["success"],
            hover_color="#0D9488",
            command=self._export_csv
        ).pack(side="left", padx=5)

        # Tab analitik
        tab = ctk.CTkTabview(
            self,
            fg_color=self.colors["bg_secondary"],
            segmented_button_fg_color=self.colors["bg_card"],
            segmented_button_selected_color=self.colors["accent"],
            segmented_button_selected_hover_color=self.colors["accent_hover"],
        )
        tab.grid(row=1, column=0, sticky="nsew", padx=25, pady=(10, 20))
        tab.add("🏆 Engagement")
        tab.add("🔥 Trending")
        tab.add("👥 User Activity")

        self._build_engagement_tab(tab.tab("🏆 Engagement"))
        self._build_trending_tab(tab.tab("🔥 Trending"))
        self._build_user_activity_tab(tab.tab("👥 User Activity"))

    def _build_engagement_tab(self, parent):
        """Tampilkan tabel engagement score per post."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        data = db.get_engagement_analytics()

        if not data:
            empty_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(
                empty_frame, text="📊",
                font=ctk.CTkFont(size=48),
            ).pack()
            ctk.CTkLabel(
                empty_frame, text="Belum ada data engagement.",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).pack(pady=10)
            return

        # Header tabel
        hdr = ctk.CTkFrame(scroll, fg_color=self.colors["accent2"], corner_radius=8)
        hdr.pack(fill="x", pady=(0, 5))
        cols   = ["#", "Username", "Konten", "Likes", "Comments", "Saves", "Score"]
        weights = [0, 1, 4, 1, 1, 1, 1]
        for j, (col, w) in enumerate(zip(cols, weights)):
            hdr.grid_columnconfigure(j, weight=w)
            ctk.CTkLabel(
                hdr, text=col,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            ).grid(row=0, column=j, padx=10, pady=8, sticky="w")

        # Render baris data (Modul 5: Perulangan)
        for i, item in enumerate(data, 1):
            row_fg = self.colors["bg_secondary"] if i % 2 == 0 else self.colors["bg_card"]
            row = ctk.CTkFrame(scroll, fg_color=row_fg, corner_radius=6)
            row.pack(fill="x", pady=1)
            for j, w in enumerate(weights):
                row.grid_columnconfigure(j, weight=w)

            cells = [
                str(i),
                f"@{item['username']}",
                item["content_preview"][:35] + "..." if len(item["content_preview"]) > 35 else item["content_preview"],
                str(item["likes"]),
                str(item["comments"]),
                str(item["saves"]),
                str(item["engagement_score"]),
            ]
            colors_list = [
                self.colors["text_secondary"],
                self.colors["accent"],
                self.colors["text_primary"],
                self.colors["info"],
                self.colors["success"],
                self.colors["warning"],
                self.colors["accent"],
            ]
            for j, (cell, col) in enumerate(zip(cells, colors_list)):
                ctk.CTkLabel(
                    row, text=cell,
                    font=ctk.CTkFont(size=11),
                    text_color=col
                ).grid(row=0, column=j, padx=10, pady=6, sticky="w")

    def _build_trending_tab(self, parent):
        """Tampilkan top trending hashtags dengan bar chart sederhana."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        trending = db.get_trending_hashtags(10)

        if not trending:
            empty_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(
                empty_frame, text="🔥",
                font=ctk.CTkFont(size=48),
            ).pack()
            ctk.CTkLabel(
                empty_frame, text="Belum ada hashtag yang digunakan.",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).pack(pady=10)
            return

        max_freq = max(t["frequency"] for t in trending) if trending else 1

        ctk.CTkLabel(
            scroll, text="🔥 Top 10 Trending Hashtags",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=(15, 20))

        for i, tag in enumerate(trending, 1):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=20)
            row.grid_columnconfigure(2, weight=1)

            # Nomor urut dengan background warna
            num_bg = self.colors["accent2"] if i <= 3 else self.colors["bg_card"]
            ctk.CTkLabel(
                row, text=f"#{i:02d}",
                width=45, height=30,
                fg_color=num_bg,
                corner_radius=15,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white" if i <= 3 else self.colors["text_primary"]
            ).grid(row=0, column=0, padx=(0, 12))

            # Nama hashtag
            ctk.CTkLabel(
                row, text=f"#{tag['tag']}",
                width=150, anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["accent"]
            ).grid(row=0, column=1, padx=(0, 10))

            # Bar progress
            bar_ratio = tag["frequency"] / max_freq
            bar = ctk.CTkProgressBar(row, width=250, height=10, 
                                      progress_color=self.colors["accent"])
            bar.set(bar_ratio)
            bar.grid(row=0, column=2, sticky="w")

            # Angka frekuensi
            ctk.CTkLabel(
                row, text=f"{tag['frequency']}×",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors["warning"]
            ).grid(row=0, column=3, padx=(10, 0))

    def _build_user_activity_tab(self, parent):
        """Tampilkan ringkasan aktivitas per pengguna."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        users = db.get_user_activity_summary()

        if not users:
            empty_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            ctk.CTkLabel(
                empty_frame, text="👥",
                font=ctk.CTkFont(size=48),
            ).pack()
            ctk.CTkLabel(
                empty_frame, text="Tidak ada data user.",
                text_color=self.colors["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).pack(pady=10)
            return

        # Header
        hdr = ctk.CTkFrame(scroll, fg_color=self.colors["accent2"], corner_radius=8)
        hdr.pack(fill="x", pady=(0, 5))
        cols   = ["Username", "Badge", "Karma", "Posts", "Comments", "Followers"]
        widths = [2, 2, 1, 1, 1, 1]
        for j, (col, w) in enumerate(zip(cols, widths)):
            hdr.grid_columnconfigure(j, weight=w)
            ctk.CTkLabel(
                hdr, text=col,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            ).grid(row=0, column=j, padx=10, pady=8, sticky="w")

        for i, user in enumerate(users, 1):
            row_fg = self.colors["bg_secondary"] if i % 2 == 0 else self.colors["bg_card"]
            row = ctk.CTkFrame(scroll, fg_color=row_fg, corner_radius=6)
            row.pack(fill="x", pady=1)
            for j, w in enumerate(widths):
                row.grid_columnconfigure(j, weight=w)

            badge_color = self._get_badge_color(user["badge"])
            cells = [
                f"@{user['username']}",
                user["badge"],
                str(user["karma"]),
                str(user["total_posts"]),
                str(user["total_comments"]),
                str(user["followers"]),
            ]
            cell_colors = [
                self.colors["text_primary"],
                badge_color,
                self.colors["warning"],
                self.colors["info"],
                self.colors["success"],
                self.colors["accent"],
            ]
            for j, (cell, color) in enumerate(zip(cells, cell_colors)):
                ctk.CTkLabel(
                    row, text=cell,
                    font=ctk.CTkFont(size=11),
                    text_color=color
                ).grid(row=0, column=j, padx=10, pady=6, sticky="w")

    def _get_badge_color(self, badge: str) -> str:
        """Dapatkan warna untuk badge."""
        badge_colors = {
            "Social Star": "#F59E0B",
            "Influencer": "#EF4444",
            "Active User": "#10B981",
            "Beginner": "#6B7280",
        }
        return badge_colors.get(badge, self.colors["text_secondary"])

    def _export_txt(self):
        """Export laporan ke file TXT."""
        success, msg = logic.export_analytics_txt()
        if success:
            self._show_info("✅ Export Berhasil", msg)
        else:
            self._show_error("❌ Export Gagal", msg)

    def _export_csv(self):
        """Export laporan ke file CSV."""
        success, msg = logic.export_analytics_csv()
        if success:
            self._show_info("✅ Export Berhasil", msg)
        else:
            self._show_error("❌ Export Gagal", msg)
    
    def _show_info(self, title: str, message: str):
        """Tampilkan dialog info."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"✅ {message}", wraplength=350,
                     text_color=self.colors["success"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)
    
    def _show_error(self, title: str, message: str):
        """Tampilkan dialog error."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.configure(fg_color=self.colors["bg_primary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"❌ {message}", wraplength=350,
                     text_color=self.colors["danger"]).pack(pady=40)
        
        ctk.CTkButton(dialog, text="OK", width=100,
                      fg_color=self.colors["accent"],
                      command=dialog.destroy).pack(pady=10)
        
        self.wait_window(dialog)