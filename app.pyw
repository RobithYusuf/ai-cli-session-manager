import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import shutil
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

_IS_MAC = sys.platform == "darwin"
_FONT_UI = "San Francisco" if _IS_MAC else "Segoe UI"
_FONT_MONO = "Menlo" if _IS_MAC else "Consolas"
_RIGHT_CLICK = "<Button-2>" if _IS_MAC else "<Button-3>"


class SessionCleaner:
    STRINGS = {
        "id": {
            "size": "Ukuran", "blank": "Kosong", "showing": "Ditampilkan",
            "selected": "Dipilih", "search": "Cari:", "time": "Waktu:",
            "sort_label": "Urut:", "group_label": "Group:",
            "all": "Semua", "today": "Hari ini", "yesterday": "Kemarin",
            "7d": "7 hari", "30d": "30 hari", "90d": "90 hari", ">90d": "> 90 hari",
            "newest": "Terbaru", "oldest": "Terlama", "a_z": "A-Z", "z_a": "Z-A",
            "no_group": "Tanpa Group", "date": "Tanggal", "month": "Bulan", "age": "Umur",
            "col_date": "Tanggal", "col_title": "Judul Percakapan",
            "col_first_chat": "Chat Pertama",
            "col_size": "Ukuran", "col_age": "Umur",
            "select_all": "Pilih Semua", "deselect": "Batal Pilih",
            "invert": "Balik Pilihan", "select_blank": "Pilih Kosong",
            "sel_7d": "Pilih > 7 hari", "sel_30d": "Pilih > 30 hari",
            "sel_90d": "Pilih > 90 hari",
            "del_blank": "Hapus Session Kosong", "del_selected": "Hapus Yang Dipilih",
            "loading": "Memuat...", "loading_sessions": "Memuat session...",
            "x_of_y": "{shown} dari {total} session",
            "preview": "Preview Session",
            "preview_hint": "Pilih session untuk melihat preview",
            "preview_click": "Klik session untuk melihat isi percakapan...",
            "n_selected": "{n} session dipilih",
            "no_title": "(tidak ada judul)",
            "no_msg": "(tidak ada pesan)", "no_msg_ua": "(tidak ada pesan user/assistant)",
            "no_msg_file": "(tidak ada pesan user/assistant dalam file ini)",
            "empty_file": "(file kosong atau tidak bisa dibaca)",
            "more_msg": "... masih ada pesan lainnya dalam session ini",
            "load_more": "Muat Lebih Banyak ({n} tersisa)",
            "showing_of": "Menampilkan {shown} dari {total} pesan",
            "error_read": "Error membaca file: {e}",
            "no_session_age": "Tidak ada session lebih dari {days} hari.",
            "blank_found": "Ditemukan {n} session kosong/blank.\nUkuran total: {size}\n\nKriteria: file 0 bytes, tidak ada pesan,\natau hanya 'New Session' tanpa percakapan.",
            "blank_title": "Session Kosong",
            "no_blank": "Tidak ada session kosong/blank.",
            "del_blank_confirm": "Hapus {n} session kosong ({src})?\nUkuran: {size}\n\nKriteria:\n  - File 0 bytes\n  - Tidak ada pesan user/assistant\n  - 'New Session' tanpa percakapan",
            "done": "Selesai",
            "del_blank_done": "{n} session kosong dihapus.\nDibebaskan: {size}{extra}",
            "empty_dirs": "\n+ {n} folder kosong dihapus",
            "warn": "Peringatan", "warn_select": "Pilih session yang ingin dihapus.",
            "and_more": "... dan {n} lainnya",
            "del_confirm_title": "Konfirmasi Hapus",
            "del_confirm": "Hapus {n} session ({src})?\nUkuran: {size}\n\n{preview}",
            "del_done": "{n} session dihapus.\nDibebaskan: {size}",
            "n_session": "{n} session",
            "other": "Lainnya",
            "day": "hari", "week": "minggu", "month_u": "bulan", "year": "tahun",
            "this_week": "Minggu ini", "this_month": "Bulan ini",
            "1_3m": "1-3 bulan lalu", "3_6m": "3-6 bulan lalu",
            "6_12m": "6-12 bulan lalu", ">1y": "> 1 tahun lalu",
            "open_session": "Buka Session",
            "open_session_tip": "Buka terminal dan resume session ini",
            "open_no_support": "Resume session tidak tersedia untuk {src}",
            "open_no_dir": "Folder project tidak ditemukan:\n{path}",
            "open_factory_info": "Droid akan dibuka di folder project.\nKetik /sessions untuk memilih session.",
            "open_opencode_info": "OpenCode akan dibuka di folder project.",
            "copied_sid": "Session ID disalin ke clipboard",
            "rename_title": "Rename Judul",
            "rename_prompt": "Masukkan judul baru:",
            "rename_success": "Judul berhasil diubah",
            "rename_no_support": "Rename tidak tersedia untuk Codex CLI",
        },
        "en": {
            "size": "Size", "blank": "Blank", "showing": "Showing",
            "selected": "Selected", "search": "Search:", "time": "Time:",
            "sort_label": "Sort:", "group_label": "Group:",
            "all": "All", "today": "Today", "yesterday": "Yesterday",
            "7d": "7 days", "30d": "30 days", "90d": "90 days", ">90d": "> 90 days",
            "newest": "Newest", "oldest": "Oldest", "a_z": "A-Z", "z_a": "Z-A",
            "no_group": "No Group", "date": "Date", "month": "Month", "age": "Age",
            "col_date": "Date", "col_title": "Conversation Title",
            "col_first_chat": "First Chat",
            "col_size": "Size", "col_age": "Age",
            "select_all": "Select All", "deselect": "Deselect",
            "invert": "Invert Selection", "select_blank": "Select Blank",
            "sel_7d": "Select > 7 days", "sel_30d": "Select > 30 days",
            "sel_90d": "Select > 90 days",
            "del_blank": "Delete Blank Sessions", "del_selected": "Delete Selected",
            "loading": "Loading...", "loading_sessions": "Loading sessions...",
            "x_of_y": "{shown} of {total} sessions",
            "preview": "Session Preview",
            "preview_hint": "Select a session to preview",
            "preview_click": "Click a session to view the conversation...",
            "n_selected": "{n} sessions selected",
            "no_title": "(no title)",
            "no_msg": "(no messages)", "no_msg_ua": "(no user/assistant messages)",
            "no_msg_file": "(no user/assistant messages in this file)",
            "empty_file": "(empty or unreadable file)",
            "more_msg": "... more messages in this session",
            "load_more": "Load More ({n} remaining)",
            "showing_of": "Showing {shown} of {total} messages",
            "error_read": "Error reading file: {e}",
            "no_session_age": "No sessions older than {days} days.",
            "blank_found": "Found {n} blank sessions.\nTotal size: {size}\n\nCriteria: 0 byte files, no messages,\nor 'New Session' without conversation.",
            "blank_title": "Blank Sessions",
            "no_blank": "No blank sessions found.",
            "del_blank_confirm": "Delete {n} blank sessions ({src})?\nSize: {size}\n\nCriteria:\n  - 0 byte files\n  - No user/assistant messages\n  - 'New Session' without conversation",
            "done": "Done",
            "del_blank_done": "{n} blank sessions deleted.\nFreed: {size}{extra}",
            "empty_dirs": "\n+ {n} empty folders deleted",
            "warn": "Warning", "warn_select": "Select sessions to delete.",
            "and_more": "... and {n} more",
            "del_confirm_title": "Confirm Delete",
            "del_confirm": "Delete {n} sessions ({src})?\nSize: {size}\n\n{preview}",
            "del_done": "{n} sessions deleted.\nFreed: {size}",
            "n_session": "{n} sessions",
            "other": "Other",
            "day": "days", "week": "weeks", "month_u": "months", "year": "years",
            "this_week": "This Week", "this_month": "This Month",
            "1_3m": "1-3 months ago", "3_6m": "3-6 months ago",
            "6_12m": "6-12 months ago", ">1y": "> 1 year ago",
            "open_session": "Open Session",
            "open_session_tip": "Open terminal and resume this session",
            "open_no_support": "Resume session not available for {src}",
            "open_no_dir": "Project folder not found:\n{path}",
            "open_factory_info": "Droid will open in the project folder.\nType /sessions to select a session.",
            "open_opencode_info": "OpenCode will open in the project folder.",
            "copied_sid": "Session ID copied to clipboard",
            "rename_title": "Rename Title",
            "rename_prompt": "Enter new title:",
            "rename_success": "Title renamed successfully",
            "rename_no_support": "Rename not available for Codex CLI",
        },
    }

    # ══════════════════════════════════════════════════════════════
    # ── Initialization & Config ──
    # ══════════════════════════════════════════════════════════════

    def __init__(self, root):
        self.root = root
        self.root.title("AI CLI Session Manager")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#0e0e10")

        self.all_sessions = []
        self.filtered_sessions = []
        self.projects = set()
        self.project_colors = {}
        self.session_map = {}
        self.current_source = "factory"
        self.current_lang = "id"

        self.SOURCES = {
            "factory": {
                "label": "Factory (Droid)",
                "dir": os.path.join(os.path.expanduser("~"), ".factory", "sessions"),
                "accent": "#00d4aa",
            },
            "claude": {
                "label": "Claude Code",
                "dir": os.path.join(os.path.expanduser("~"), ".claude", "projects"),
                "accent": "#d4a574",
            },
            "codex": {
                "label": "Codex CLI",
                "dir": os.path.join(os.path.expanduser("~"), ".codex", "sessions"),
                "accent": "#61afef",
            },
            "opencode": {
                "label": "OpenCode",
                "dir": os.path.join(os.path.expanduser("~"), ".local", "share", "opencode", "storage"),
                "accent": "#c678dd",
            },
        }

        self.COLOR_PALETTE = [
            "#00d4aa", "#e06c75", "#61afef", "#c678dd", "#e5c07b",
            "#56b6c2", "#d19a66", "#98c379", "#be5046", "#5c6370",
            "#ff6b81", "#7bed9f", "#70a1ff", "#ffa502", "#a29bfe",
            "#fd79a8", "#00cec9", "#fab1a0", "#81ecec", "#dfe6e9",
        ]

        self.setup_styles()
        self.build_ui()
        self._apply_language()
        self.load_all_sessions()

    def t(self, key):
        return self.STRINGS[self.current_lang].get(key, key)

    def _key_from_display(self, display, keys):
        for k in keys:
            if self.t(k) == display:
                return k
        return display

    # ══════════════════════════════════════════════════════════════
    # ── UI Setup & Styles ──
    # ══════════════════════════════════════════════════════════════

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        self.colors = {
            "bg": "#0e0e10",
            "surface": "#1a1a2e",
            "surface2": "#16213e",
            "border": "#2a2a4a",
            "text": "#e0e0e0",
            "dim": "#888899",
            "accent": "#00d4aa",
            "danger": "#e94560",
            "warn": "#f0a500",
            "group_bg": "#0f3460",
            "preview_bg": "#12121a",
            "preview_user": "#61afef",
            "preview_asst": "#98c379",
            "preview_sys": "#888899",
        }
        c = self.colors

        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["text"], font=(_FONT_UI, 10))
        style.configure("Title.TLabel", background=c["bg"], foreground=c["accent"], font=(_FONT_UI, 15, "bold"))
        style.configure("Dim.TLabel", background=c["bg"], foreground=c["dim"], font=(_FONT_UI, 9))

        style.configure("TButton", font=(_FONT_UI, 8), padding=(6, 3),
                        background=c["border"], foreground=c["text"])
        style.map("TButton", background=[("active", "#3a3a5a")])

        style.configure("Accent.TButton", font=(_FONT_UI, 8, "bold"), padding=(6, 3),
                        background=c["accent"], foreground="#000")
        style.map("Accent.TButton", background=[("active", "#00b894")])

        style.configure("Danger.TButton", font=(_FONT_UI, 9, "bold"), padding=(8, 4),
                        background=c["danger"], foreground="#fff")
        style.map("Danger.TButton", background=[("active", "#c0392b")])

        style.configure("Warn.TButton", font=(_FONT_UI, 8, "bold"), padding=(6, 3),
                        background=c["warn"], foreground="#000")
        style.map("Warn.TButton", background=[("active", "#d48b00")])

        style.configure("TCombobox", font=(_FONT_UI, 9), fieldbackground=c["surface"],
                        background=c["surface"], foreground=c["text"])

        style.configure("Treeview",
                        background=c["surface"], foreground=c["text"], fieldbackground=c["surface"],
                        font=(_FONT_UI, 9), rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading",
                        background=c["group_bg"], foreground=c["text"],
                        font=(_FONT_UI, 9, "bold"), borderwidth=0)
        style.map("Treeview.Heading",
                  background=[("active", c["border"])],
                  foreground=[("active", c["accent"])])
        style.map("Treeview",
                  background=[("selected", c["danger"])],
                  foreground=[("selected", "#ffffff")])

    def build_ui(self):
        # Header with source selector
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=16, pady=(12, 6))

        self.title_label = ttk.Label(header, text="AI CLI Session Manager", style="Title.TLabel")
        self.title_label.pack(side="left")

        # Language toggle
        self.lang_btn = tk.Button(header, text="EN", font=(_FONT_UI, 8, "bold"),
                                  padx=6, pady=2, cursor="hand2",
                                  command=self._toggle_language)
        self.lang_btn.pack(side="right", padx=(8, 0))

        # Source selector
        src_frame = tk.Frame(header, bg=self.colors["bg"])
        src_frame.pack(side="right")

        ttk.Label(src_frame, text="Source:", style="Dim.TLabel").pack(side="left", padx=(0, 6))

        self.source_buttons = {}
        for key, info in self.SOURCES.items():
            btn = tk.Button(src_frame, text=info["label"], font=(_FONT_UI, 9, "bold"),
                            padx=12, pady=4, cursor="hand2",
                            command=lambda k=key: self._switch_source(k))
            btn.pack(side="left", padx=(0, 2))
            self.source_buttons[key] = btn

        self._update_source_buttons()

        # Stats bar
        stats_frame = tk.Frame(self.root, bg=self.colors["surface"],
                               highlightbackground=self.colors["border"], highlightthickness=1)
        stats_frame.pack(fill="x", padx=16, pady=(0, 6))

        self.stat_total = self._stat(stats_frame, "Total", "0")
        self.stat_projects = self._stat(stats_frame, "Project", "0")
        self.stat_size = self._stat(stats_frame, "size", "0 MB")
        self.stat_blank = self._stat(stats_frame, "blank", "0")
        self.stat_showing = self._stat(stats_frame, "showing", "0")
        self.stat_selected = self._stat(stats_frame, "selected", "0")

        # Toolbar
        tb1 = ttk.Frame(self.root)
        tb1.pack(fill="x", padx=16, pady=(0, 2))

        self.lbl_search = ttk.Label(tb1, text=self.t("search"), style="Dim.TLabel")
        self.lbl_search.pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.apply_filters)
        tk.Entry(tb1, textvariable=self.search_var, width=20,
                 bg=self.colors["surface2"], fg=self.colors["text"],
                 insertbackground=self.colors["text"], font=(_FONT_UI, 9),
                 borderwidth=0, highlightthickness=1,
                 highlightcolor=self.colors["accent"],
                 highlightbackground=self.colors["border"]).pack(side="left", padx=(4, 8), ipady=3)

        ttk.Label(tb1, text="Project:", style="Dim.TLabel").pack(side="left")
        self.project_var = tk.StringVar(value=self.t("all"))

        # Searchable project entry
        self.project_entry = tk.Entry(tb1, textvariable=self.project_var, width=18,
                 bg=self.colors["surface2"], fg=self.colors["text"],
                 insertbackground=self.colors["text"], font=(_FONT_UI, 9),
                 borderwidth=0, highlightthickness=1,
                 highlightcolor=self.colors["accent"],
                 highlightbackground=self.colors["border"])
        self.project_entry.pack(side="left", padx=(4, 0), ipady=3)
        self.project_entry.bind("<KeyRelease>", self._on_project_search)
        self.project_entry.bind("<FocusIn>", self._on_project_focus_in)
        self.project_entry.bind("<Escape>", lambda e: self._close_project_dropdown())

        self.project_listbox_frame = None
        self.project_listbox = None
        self._all_projects_list = []

        self.project_count_label = ttk.Label(tb1, text="", style="Dim.TLabel")
        self.project_count_label.pack(side="left", padx=(2, 8))

        self.lbl_time = ttk.Label(tb1, text=self.t("time"), style="Dim.TLabel")
        self.lbl_time.pack(side="left")
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(tb1, textvariable=self.date_var, width=10, state="readonly")
        self.date_combo.pack(side="left", padx=(4, 8))
        self.date_var.trace_add("write", self.apply_filters)

        self.lbl_sort = ttk.Label(tb1, text=self.t("sort_label"), style="Dim.TLabel")
        self.lbl_sort.pack(side="left")
        self.sort_var = tk.StringVar()
        self.sort_combo = ttk.Combobox(tb1, textvariable=self.sort_var, width=8, state="readonly")
        self.sort_combo.pack(side="left", padx=(4, 8))
        self.sort_var.trace_add("write", self.apply_filters)

        self.lbl_group = ttk.Label(tb1, text=self.t("group_label"), style="Dim.TLabel")
        self.lbl_group.pack(side="left")
        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(tb1, textvariable=self.group_var, width=10, state="readonly")
        self.group_combo.pack(side="left", padx=(4, 0))
        self.group_var.trace_add("write", self.apply_filters)

        self._update_combo_values()

        # PanedWindow (tree + preview)
        self.paned = tk.PanedWindow(self.root, orient="vertical", bg=self.colors["bg"],
                                     sashwidth=6, sashrelief="flat", borderwidth=0)
        self.paned.pack(fill="both", expand=True, padx=16, pady=(6, 6))

        # Treeview
        tree_frame = ttk.Frame(self.paned)
        self.paned.add(tree_frame, minsize=200)

        cols = ("source", "project", "date", "title", "first_chat", "model", "size", "age")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="tree headings",
                                 selectmode="extended")

        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("source", text="Source", command=lambda: self._sort_click("source"))
        self.tree.heading("project", text="Project", command=lambda: self._sort_click("project"))
        self.tree.heading("date", text=self.t("col_date"), command=lambda: self._sort_click("date"))
        self.tree.heading("title", text=self.t("col_title"), command=lambda: self._sort_click("title"))
        self.tree.heading("first_chat", text=self.t("col_first_chat"))
        self.tree.heading("model", text="Model", command=lambda: self._sort_click("model"))
        self.tree.heading("size", text=self.t("col_size"), command=lambda: self._sort_click("size"))
        self.tree.heading("age", text=self.t("col_age"), command=lambda: self._sort_click("age"))

        self.tree.column("#0", width=30, minwidth=30, stretch=False)
        self.tree.column("source", width=0, minwidth=0, stretch=False)
        self.tree.column("project", width=110, minwidth=70)
        self.tree.column("date", width=120, minwidth=100, stretch=False)
        self.tree.column("title", width=220, minwidth=120)
        self.tree.column("first_chat", width=180, minwidth=100)
        self.tree.column("model", width=170, minwidth=100)
        self.tree.column("size", width=65, minwidth=50, stretch=False, anchor="e")
        self.tree.column("age", width=75, minwidth=55, stretch=False, anchor="e")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind(_RIGHT_CLICK, self._on_tree_right_click)

        self.tree.tag_configure("group", background=self.colors["group_bg"],
                                foreground=self.colors["accent"],
                                font=(_FONT_UI, 10, "bold"))

        # Preview
        preview_frame = tk.Frame(self.paned, bg=self.colors["preview_bg"],
                                  highlightbackground=self.colors["border"], highlightthickness=1)
        self.paned.add(preview_frame, minsize=80)

        preview_header = tk.Frame(preview_frame, bg=self.colors["surface"])
        preview_header.pack(fill="x")

        self.preview_title_label = tk.Label(preview_header, text=self.t("preview"),
                                            bg=self.colors["surface"], fg=self.colors["accent"],
                                            font=(_FONT_UI, 10, "bold"), anchor="w", padx=10, pady=4)
        self.preview_title_label.pack(side="left", fill="x", expand=True)

        self.preview_info_label = tk.Label(preview_header, text="",
                                           bg=self.colors["surface"], fg=self.colors["dim"],
                                           font=(_FONT_UI, 8), anchor="e", padx=10)
        self.preview_info_label.pack(side="right")

        # Preview body container (text + load more button)
        preview_body = tk.Frame(preview_frame, bg=self.colors["preview_bg"])
        preview_body.pack(fill="both", expand=True)

        self.preview_text = tk.Text(preview_body, wrap="word", height=5,
                                    bg=self.colors["preview_bg"], fg=self.colors["text"],
                                    font=(_FONT_MONO, 9), borderwidth=0,
                                    insertbackground=self.colors["text"],
                                    padx=12, pady=8, state="disabled",
                                    selectbackground=self.colors["border"],
                                    selectforeground=self.colors["text"],
                                    spacing1=1, spacing3=1)
        preview_sb = ttk.Scrollbar(preview_body, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_sb.set)
        preview_sb.pack(side="right", fill="y")
        self.preview_text.pack(fill="both", expand=True)

        # Load more button (hidden by default)
        self.preview_loadmore_frame = tk.Frame(preview_frame, bg=self.colors["surface2"])
        self.preview_loadmore_btn = tk.Button(self.preview_loadmore_frame,
            text="Load More Messages", font=(_FONT_UI, 8, "bold"),
            bg=self.colors["border"], fg=self.colors["text"],
            activebackground=self.colors["accent"], activeforeground="#000",
            padx=16, pady=3, cursor="hand2", borderwidth=0,
            command=self._load_more_preview)
        self.preview_loadmore_btn.pack(pady=4)
        self.preview_msg_count_label = tk.Label(self.preview_loadmore_frame, text="",
            bg=self.colors["surface2"], fg=self.colors["dim"], font=(_FONT_UI, 7))
        self.preview_msg_count_label.pack()

        # Preview pagination state
        self._preview_page = 0
        self._preview_page_size = 20
        self._preview_messages = []
        self._preview_current_sid = None
        self._preview_total_available = 0

        self.preview_text.tag_configure("role_user", foreground=self.colors["preview_user"],
                                        font=(_FONT_MONO, 9, "bold"))
        self.preview_text.tag_configure("role_assistant", foreground=self.colors["preview_asst"],
                                        font=(_FONT_MONO, 9, "bold"))
        self.preview_text.tag_configure("role_system", foreground=self.colors["preview_sys"],
                                        font=(_FONT_MONO, 9, "bold"))
        self.preview_text.tag_configure("content", foreground=self.colors["text"],
                                        font=(_FONT_MONO, 9), lmargin1=20, lmargin2=20)
        self.preview_text.tag_configure("content_truncated", foreground="#7a7a8a",
                                        font=(_FONT_MONO, 8, "italic"), lmargin1=20, lmargin2=20)
        self.preview_text.tag_configure("separator", foreground="#2a2a3a",
                                        font=(_FONT_MONO, 6))
        self.preview_text.tag_configure("meta", foreground=self.colors["dim"],
                                        font=(_FONT_MONO, 8, "italic"))
        self.preview_text.tag_configure("msg_number", foreground="#555566",
                                        font=(_FONT_MONO, 8))

        # Bottom bar
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=16, pady=(0, 12))

        btn_row = ttk.Frame(bottom)
        btn_row.pack(fill="x")

        self.btn_select_all = ttk.Button(btn_row, text=self.t("select_all"), command=self.select_all)
        self.btn_select_all.pack(side="left", padx=(0, 2))
        self.btn_deselect = ttk.Button(btn_row, text=self.t("deselect"), command=self.deselect_all)
        self.btn_deselect.pack(side="left", padx=(0, 2))
        self.btn_invert = ttk.Button(btn_row, text=self.t("invert"), command=self.invert_selection)
        self.btn_invert.pack(side="left", padx=(0, 2))

        tk.Frame(btn_row, width=1, bg=self.colors["border"]).pack(side="left", fill="y", padx=5, pady=2)

        self.btn_sel_blank = ttk.Button(btn_row, text=self.t("select_blank"), style="Warn.TButton",
                   command=self.select_blank)
        self.btn_sel_blank.pack(side="left", padx=(0, 2))
        self.btn_sel_7d = ttk.Button(btn_row, text=self.t("sel_7d"), command=lambda: self.select_by_age(7))
        self.btn_sel_7d.pack(side="left", padx=(0, 2))
        self.btn_sel_30d = ttk.Button(btn_row, text=self.t("sel_30d"), command=lambda: self.select_by_age(30))
        self.btn_sel_30d.pack(side="left", padx=(0, 2))
        self.btn_sel_90d = ttk.Button(btn_row, text=self.t("sel_90d"), command=lambda: self.select_by_age(90))
        self.btn_sel_90d.pack(side="left", padx=(0, 2))

        tk.Frame(btn_row, width=1, bg=self.colors["border"]).pack(side="left", fill="y", padx=5, pady=2)

        self.btn_del_blank = ttk.Button(btn_row, text=self.t("del_blank"), style="Warn.TButton",
                   command=self.delete_blank_sessions)
        self.btn_del_blank.pack(side="left", padx=(0, 2))
        self.btn_open_session = ttk.Button(btn_row, text=self.t("open_session"), style="Accent.TButton",
                   command=self._open_selected_session)
        self.btn_open_session.pack(side="left", padx=(0, 2))
        ttk.Button(btn_row, text="Refresh", style="Accent.TButton",
                   command=self.refresh).pack(side="left", padx=(0, 2))

        self.btn_del_selected = ttk.Button(btn_row, text=self.t("del_selected"), style="Danger.TButton",
                   command=self.delete_selected)
        self.btn_del_selected.pack(side="right")

        self.status_label = ttk.Label(btn_row, text=self.t("loading"), style="Dim.TLabel")
        self.status_label.pack(side="right", padx=12)

    def _switch_source(self, source):
        if source == self.current_source:
            return
        self.current_source = source
        self._update_source_buttons()
        self.search_var.set("")
        self.project_var.set(self.t("all"))
        self.date_var.set(self.t("all"))
        self.load_all_sessions()

    def _update_source_buttons(self):
        c = self.colors
        accent = self.SOURCES[self.current_source]["accent"]
        for key, btn in self.source_buttons.items():
            if key == self.current_source:
                btn.config(bg=self.SOURCES[key]["accent"], fg="#000", relief="sunken")
            else:
                btn.config(bg=c["border"], fg=c["text"], relief="raised")
        self.title_label.config(foreground=accent)

    # ══════════════════════════════════════════════════════════════
    # ── Searchable Project Dropdown ──
    # ══════════════════════════════════════════════════════════════

    def _on_project_focus_in(self, event):
        self.project_entry.select_range(0, "end")
        self._show_project_dropdown()

    def _on_project_search(self, event):
        if event.keysym in ("Return", "Tab"):
            self._select_project_from_entry()
            self._close_project_dropdown()
            return
        if event.keysym in ("Escape", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return
        if event.keysym == "Down" and self.project_listbox:
            self.project_listbox.focus_set()
            if self.project_listbox.size() > 0:
                self.project_listbox.selection_set(0)
            return
        self._show_project_dropdown()

    def _show_project_dropdown(self):
        typed = self.project_var.get().lower()
        all_label = self.t("all")
        matches = [all_label]
        for p in self._all_projects_list:
            if typed and typed != all_label.lower() and typed not in p.lower():
                continue
            matches.append(p)

        if self.project_listbox_frame:
            self._close_project_dropdown()

        if not matches:
            return

        self.project_listbox_frame = tk.Frame(self.root, bg=self.colors["border"])

        x = self.project_entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.project_entry.winfo_rooty() - self.root.winfo_rooty() + self.project_entry.winfo_height()
        w = max(self.project_entry.winfo_width(), 250)
        h = min(len(matches) * 20 + 4, 300)

        self.project_listbox_frame.place(x=x, y=y, width=w, height=h)
        self.project_listbox_frame.lift()

        self.project_listbox = tk.Listbox(self.project_listbox_frame,
            bg=self.colors["surface2"], fg=self.colors["text"],
            font=(_FONT_UI, 9), borderwidth=0, highlightthickness=0,
            selectbackground=self.colors["accent"], selectforeground="#000",
            activestyle="none")

        sb = ttk.Scrollbar(self.project_listbox_frame, orient="vertical",
                           command=self.project_listbox.yview)
        self.project_listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.project_listbox.pack(fill="both", expand=True)

        for m in matches:
            self.project_listbox.insert("end", m)

        self.project_listbox.bind("<ButtonRelease-1>", self._on_project_listbox_click)
        self.project_listbox.bind("<Return>", self._on_project_listbox_click)
        self.project_listbox.bind("<Escape>", lambda e: self._close_project_dropdown())

        self.root.bind("<Button-1>", self._on_click_outside_dropdown, add="+")

    def _on_project_listbox_click(self, event):
        sel = self.project_listbox.curselection()
        if sel:
            value = self.project_listbox.get(sel[0])
            self.project_var.set(value)
            self._close_project_dropdown()
            self.apply_filters()

    def _on_click_outside_dropdown(self, event):
        if self.project_listbox_frame:
            w = event.widget
            if w != self.project_entry and w != self.project_listbox:
                self._close_project_dropdown()
                self._select_project_from_entry()

    def _close_project_dropdown(self):
        if self.project_listbox_frame:
            self.project_listbox_frame.destroy()
            self.project_listbox_frame = None
            self.project_listbox = None
        try:
            self.root.unbind("<Button-1>")
        except:
            pass

    def _select_project_from_entry(self):
        typed = self.project_var.get()
        if typed == self.t("all") or typed in self._all_projects_list:
            self.apply_filters()
            return
        # Try partial match
        lower = typed.lower()
        for p in self._all_projects_list:
            if lower == p.lower():
                self.project_var.set(p)
                self.apply_filters()
                return
        # No match, reset to all
        self.project_var.set(self.t("all"))
        self.apply_filters()

    # ══════════════════════════════════════════════════════════════
    # ── Language & Localization ──
    # ══════════════════════════════════════════════════════════════

    def _toggle_language(self):
        self.current_lang = "en" if self.current_lang == "id" else "id"
        self._apply_language()
        self.load_all_sessions()

    def _update_combo_values(self):
        self._date_keys = ["all", "today", "yesterday", "7d", "30d", "90d", ">90d"]
        self._sort_keys = ["newest", "oldest", "a_z", "z_a", "size", "project"]
        self._group_keys = ["no_group", "project", "date", "month", "age"]
        self.date_combo["values"] = [self.t(k) for k in self._date_keys]
        self.sort_combo["values"] = [self.t(k) for k in self._sort_keys]
        self.group_combo["values"] = [self.t(k) for k in self._group_keys]
        self.date_var.set(self.t("all"))
        self.sort_var.set(self.t("newest"))
        self.group_var.set(self.t("no_group"))

    def _apply_language(self):
        self.lang_btn.config(text="ID" if self.current_lang == "en" else "EN",
                             bg=self.colors["accent"] if self.current_lang == "en" else self.colors["border"],
                             fg="#000" if self.current_lang == "en" else self.colors["text"])
        self._update_combo_values()
        self.project_var.set(self.t("all"))
        self.lbl_search.config(text=self.t("search"))
        self.lbl_time.config(text=self.t("time"))
        self.lbl_sort.config(text=self.t("sort_label"))
        self.lbl_group.config(text=self.t("group_label"))
        self.tree.heading("date", text=self.t("col_date"))
        self.tree.heading("title", text=self.t("col_title"))
        self.tree.heading("first_chat", text=self.t("col_first_chat"))
        self.tree.heading("size", text=self.t("col_size"))
        self.tree.heading("age", text=self.t("col_age"))
        self.preview_title_label.config(text=self.t("preview"))
        self.preview_info_label.config(text=self.t("preview_hint"))
        self.btn_select_all.config(text=self.t("select_all"))
        self.btn_deselect.config(text=self.t("deselect"))
        self.btn_invert.config(text=self.t("invert"))
        self.btn_sel_blank.config(text=self.t("select_blank"))
        self.btn_sel_7d.config(text=self.t("sel_7d"))
        self.btn_sel_30d.config(text=self.t("sel_30d"))
        self.btn_sel_90d.config(text=self.t("sel_90d"))
        self.btn_del_blank.config(text=self.t("del_blank"))
        self.btn_open_session.config(text=self.t("open_session"))
        self.btn_del_selected.config(text=self.t("del_selected"))
        for w in (self.stat_size, self.stat_blank, self.stat_showing, self.stat_selected):
            lbl = w.master.winfo_children()[1]
            if hasattr(lbl, "_lang_key"):
                lbl.config(text=self.t(lbl._lang_key))

    def _stat(self, parent, label_key, value):
        f = tk.Frame(parent, bg=self.colors["surface"], padx=16, pady=6)
        f.pack(side="left", fill="both", expand=True)
        v = tk.Label(f, text=value, bg=self.colors["surface"], fg=self.colors["accent"],
                     font=(_FONT_UI, 13, "bold"))
        v.pack(anchor="w")
        display = self.t(label_key) if label_key in self.STRINGS["id"] else label_key
        lbl = tk.Label(f, text=display, bg=self.colors["surface"], fg=self.colors["dim"],
                 font=(_FONT_UI, 8))
        lbl.pack(anchor="w")
        lbl._lang_key = label_key
        return v

    # ══════════════════════════════════════════════════════════════
    # ── Helpers & Formatting ──
    # ══════════════════════════════════════════════════════════════

    def fmt_size(self, b):
        if b < 1024: return f"{b} B"
        if b < 1048576: return f"{b/1024:.1f} KB"
        return f"{b/1048576:.1f} MB"

    def fmt_age(self, dt):
        days = (datetime.now() - dt).days
        if days == 0: return self.t("today")
        if days == 1: return self.t("yesterday")
        if days < 7: return f"{days} {self.t('day')}"
        if days < 30: return f"{days//7} {self.t('week')}"
        if days < 365: return f"{days//30} {self.t('month_u')}"
        return f"{days//365} {self.t('year')}"

    def get_project_name(self, folder_name):
        if not folder_name:
            return "(root)"
        name = folder_name
        for prefix in ["-C-laragon-www-MYPROJECT-", "-C-laragon-www-WORK-",
                       "-D-Obsidian-", "-C-laragon-www-", "-C-",
                       "C--laragon-www-MYPROJECT-", "C--laragon-www-WORK-",
                       "D--Obsidian-", "C--laragon-www-", "C--"]:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        return name

    def get_age_group(self, dt):
        days = (datetime.now() - dt).days
        if days == 0: return self.t("today")
        if days == 1: return self.t("yesterday")
        if days <= 7: return self.t("this_week")
        if days <= 30: return self.t("this_month")
        if days <= 90: return self.t("1_3m")
        if days <= 180: return self.t("3_6m")
        if days <= 365: return self.t("6_12m")
        return self.t(">1y")

    def _assign_project_colors(self):
        self.project_colors = {}
        for i, p in enumerate(sorted(self.projects)):
            self.project_colors[p] = self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]
        self.project_colors["(root)"] = self.colors["dim"]

    # ══════════════════════════════════════════════════════════════
    # ── Session Loading & Parsing ──
    # ══════════════════════════════════════════════════════════════

    def load_all_sessions(self):
        self.all_sessions = []
        self.projects = set()
        self.session_map = {}

        self.status_label.config(text=self.t("loading_sessions"))
        self.root.update_idletasks()

        if self.current_source == "factory":
            self._load_factory_sessions()
        elif self.current_source == "claude":
            self._load_claude_sessions()
        elif self.current_source == "codex":
            self._load_codex_sessions()
        elif self.current_source == "opencode":
            self._load_opencode_sessions()

        self._assign_project_colors()

        total_size = sum(s["size"] for s in self.all_sessions)
        blank_count = sum(1 for s in self.all_sessions if s.get("is_blank"))
        self.stat_total.config(text=str(len(self.all_sessions)))
        self.stat_projects.config(text=str(len(self.projects)))
        self.stat_size.config(text=self.fmt_size(total_size))
        self.stat_blank.config(text=str(blank_count))

        self._all_projects_list = sorted(self.projects)
        # Count sessions per project
        proj_counts = {}
        for s in self.all_sessions:
            p = s["project"]
            proj_counts[p] = proj_counts.get(p, 0) + 1
        self._project_counts = proj_counts

        self.apply_filters()

    # ── Factory (Droid) ─────────────────────────────────────────

    def _load_factory_sessions(self):
        session_dir = self.SOURCES["factory"]["dir"]
        if not os.path.exists(session_dir):
            return

        # Root-level sessions
        for f in os.listdir(session_dir):
            if f.endswith(".jsonl"):
                fp = os.path.join(session_dir, f)
                s = self._parse_factory_session(fp, "")
                if s:
                    self.all_sessions.append(s)
                    self.session_map[s["id"]] = s

        # Folder-level sessions
        for folder in os.listdir(session_dir):
            folder_path = os.path.join(session_dir, folder)
            if not os.path.isdir(folder_path):
                continue
            project = self.get_project_name(folder)
            self.projects.add(project)
            for f in os.listdir(folder_path):
                if f.endswith(".jsonl"):
                    fp = os.path.join(folder_path, f)
                    s = self._parse_factory_session(fp, folder)
                    if s:
                        self.all_sessions.append(s)
                        self.session_map[s["id"]] = s

    def _parse_factory_session(self, filepath, folder_name):
        try:
            sid = os.path.basename(filepath).replace(".jsonl", "")
            mtime = os.path.getmtime(filepath)
            size = os.path.getsize(filepath)
            model = ""
            settings = filepath.replace(".jsonl", ".settings.json")
            if os.path.exists(settings):
                size += os.path.getsize(settings)
                try:
                    with open(settings, "r", encoding="utf-8") as sf:
                        sdata = json.load(sf)
                    model = sdata.get("model", "")
                except:
                    pass

            no_title = self.t("no_title")
            title = no_title
            first_chat = ""
            line_count = 0
            msg_count = 0
            first_user_msg = ""
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, raw_line in enumerate(f):
                        line_count += 1
                        if i == 0:
                            raw_line = raw_line.strip()
                            if raw_line:
                                data = json.loads(raw_line)
                                raw_title = data.get("title", "")
                                session_title = data.get("sessionTitle", "")
                                if session_title:
                                    title = session_title[:150]
                                    first_chat = raw_title[:150] if raw_title else ""
                                elif raw_title:
                                    title = raw_title[:150]
                        if line_count > 50:
                            msg_count = 99
                            break
                        try:
                            entry = json.loads(raw_line.strip())
                            if entry.get("type") == "message" and isinstance(entry.get("message"), dict):
                                r = entry["message"].get("role", "")
                                if r in ("user", "assistant"):
                                    msg_count += 1
                                if r == "user" and not first_user_msg:
                                    content = entry["message"].get("content", "")
                                    if isinstance(content, list):
                                        for part in content:
                                            if isinstance(part, dict) and part.get("type") == "text":
                                                content = part.get("text", "")
                                                break
                                        else:
                                            content = ""
                                    if isinstance(content, str):
                                        clean = content.strip()
                                        if clean and not clean.startswith("<system-reminder>"):
                                            first_user_msg = clean[:150]
                        except:
                            pass
            except:
                pass

            if title == no_title and first_user_msg:
                title = first_user_msg
            if not first_chat and first_user_msg:
                first_chat = first_user_msg

            is_blank = (size == 0 or msg_count == 0 or
                        (title.lower() in ("new session", no_title.lower()) and msg_count <= 1))

            dt = datetime.fromtimestamp(mtime)
            project = self.get_project_name(folder_name)

            return {
                "id": sid, "filepath": filepath, "folder": folder_name,
                "source": "factory", "project": project,
                "mtime": mtime, "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                "date_date": dt.strftime("%Y-%m-%d"), "date_month": dt.strftime("%Y-%m"),
                "date_obj": dt, "title": title, "first_chat": first_chat,
                "model": model,
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": [], "is_blank": is_blank,
            }
        except:
            return None

    # ── Claude Code ────────────────────────────────────────────

    def _load_claude_sessions(self):
        projects_dir = self.SOURCES["claude"]["dir"]
        if not os.path.exists(projects_dir):
            return

        for folder in os.listdir(projects_dir):
            folder_path = os.path.join(projects_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            project = self.get_project_name(folder)
            self.projects.add(project)

            # Try to use sessions-index.json for faster title lookup
            index_data = {}
            idx_path = os.path.join(folder_path, "sessions-index.json")
            if os.path.exists(idx_path):
                try:
                    with open(idx_path, "r", encoding="utf-8") as f:
                        idx = json.load(f)
                    for entry in idx.get("entries", []):
                        sid = entry.get("sessionId", "")
                        index_data[sid] = entry
                except:
                    pass

            for f in os.listdir(folder_path):
                if not f.endswith(".jsonl"):
                    continue
                fp = os.path.join(folder_path, f)
                sid = f.replace(".jsonl", "")
                s = self._parse_claude_session(fp, folder, project, index_data.get(sid))
                if s:
                    self.all_sessions.append(s)
                    self.session_map[s["id"]] = s

    def _parse_claude_session(self, filepath, folder_name, project, index_entry):
        try:
            sid = os.path.basename(filepath).replace(".jsonl", "")
            mtime = os.path.getmtime(filepath)
            size = os.path.getsize(filepath)

            # Collect associated files (subfolder with same name)
            extra_files = []
            sub_dir = filepath.replace(".jsonl", "")
            if os.path.isdir(sub_dir):
                for root_d, dirs, files in os.walk(sub_dir):
                    for fn in files:
                        efp = os.path.join(root_d, fn)
                        extra_files.append(efp)
                        size += os.path.getsize(efp)

            no_title = self.t("no_title")
            title = no_title
            first_chat = ""
            msg_count = 0
            model = ""
            has_real_user_msg = False
            if index_entry:
                fp_text = index_entry.get("firstPrompt", "")
                summary_text = index_entry.get("summary", "")
                if fp_text and (self._is_claude_command(fp_text) or fp_text == "No prompt"):
                    fp_text = ""
                if isinstance(summary_text, str) and summary_text.strip():
                    title = summary_text.strip()[:150]
                    first_chat = fp_text[:150] if fp_text else ""
                    has_real_user_msg = True
                elif fp_text:
                    title = fp_text[:150]
                    first_chat = fp_text[:150]
                    has_real_user_msg = True
                msg_count = index_entry.get("messageCount", 0)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        data = json.loads(line)
                        if data.get("type") == "assistant" and not model:
                            msg = data.get("message", {})
                            if isinstance(msg, dict):
                                model = msg.get("model", "")
                            if index_entry:
                                break
                        if not index_entry:
                            if data.get("type") in ("user", "human", "assistant"):
                                msg_count += 1
                                if data.get("type") in ("user", "human") and (title == no_title or not first_chat):
                                    msg = data.get("message", {})
                                    if isinstance(msg, dict):
                                        content = msg.get("content", "")
                                        if isinstance(content, list):
                                            for p in content:
                                                if isinstance(p, dict) and p.get("type") == "text":
                                                    content = p.get("text", "")
                                                    break
                                            else:
                                                content = ""
                                        if isinstance(content, str):
                                            clean = content.strip()
                                            if clean and not self._is_claude_command(clean):
                                                has_real_user_msg = True
                                                if title == no_title:
                                                    title = clean[:150]
                                                if not first_chat:
                                                    first_chat = clean[:150]
            except:
                pass

            is_blank = (size == 0 or
                        (msg_count == 0 and os.path.getsize(filepath) < 100) or
                        (not has_real_user_msg and title == no_title) or
                        (title.lower().startswith("[request interrupted") and msg_count <= 2))

            dt = datetime.fromtimestamp(mtime)

            return {
                "id": f"cc_{sid}", "filepath": filepath, "folder": folder_name,
                "source": "claude", "project": project,
                "mtime": mtime, "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                "date_date": dt.strftime("%Y-%m-%d"), "date_month": dt.strftime("%Y-%m"),
                "date_obj": dt, "title": title, "first_chat": first_chat or title,
                "model": model,
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": extra_files, "is_blank": is_blank,
            }
        except:
            return None

    # ── Codex CLI ────────────────────────────────────────────────

    def _load_codex_sessions(self):
        session_dir = self.SOURCES["codex"]["dir"]
        if not os.path.exists(session_dir):
            return
        for root_d, dirs, files in os.walk(session_dir):
            for f in files:
                if not f.endswith(".jsonl"):
                    continue
                fp = os.path.join(root_d, f)
                s = self._parse_codex_session(fp)
                if s:
                    self.all_sessions.append(s)
                    self.session_map[s["id"]] = s

    def _parse_codex_session(self, filepath):
        try:
            sid = os.path.basename(filepath).replace(".jsonl", "")
            mtime = os.path.getmtime(filepath)
            size = os.path.getsize(filepath)

            no_title = self.t("no_title")
            title = no_title
            project = "(unknown)"
            model = ""
            msg_count = 0
            codex_session_id = ""
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except:
                            continue
                        t = entry.get("type", "")
                        payload = entry.get("payload", {})
                        if not isinstance(payload, dict):
                            continue
                        if t == "session_meta":
                            codex_session_id = payload.get("id", "")
                            cwd = payload.get("cwd", "")
                            if cwd:
                                project = self.get_project_name(
                                    cwd.replace("\\", "-").replace("/", "-").replace(":", "").lstrip("-"))
                        elif t == "turn_context" and not model:
                            model = payload.get("model", "")
                        elif t == "event_msg":
                            msg_text = payload.get("message", "")
                            if msg_text and title == no_title:
                                clean = msg_text.strip()
                                marker = "My request for Codex:\n"
                                idx = clean.find(marker)
                                if idx != -1:
                                    clean = clean[idx + len(marker):].strip()
                                elif clean.startswith("<") or clean.startswith("#"):
                                    clean = ""
                                if clean:
                                    title = clean[:150]
                            msg_count += 1
                        elif t == "response_item":
                            role = payload.get("role", "")
                            if role in ("user", "assistant"):
                                msg_count += 1
            except:
                pass

            self.projects.add(project)
            is_blank = (size == 0 or msg_count == 0)
            dt = datetime.fromtimestamp(mtime)

            return {
                "id": "cx_" + sid, "filepath": filepath, "folder": "",
                "source": "codex", "project": project,
                "codex_session_id": codex_session_id or sid,
                "mtime": mtime, "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                "date_date": dt.strftime("%Y-%m-%d"), "date_month": dt.strftime("%Y-%m"),
                "date_obj": dt, "title": title, "first_chat": title,
                "model": model,
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": [], "is_blank": is_blank,
            }
        except:
            return None

    # ── OpenCode ──────────────────────────────────────────────────

    def _load_opencode_sessions(self):
        base = self.SOURCES["opencode"]["dir"]
        session_dir = os.path.join(base, "session")
        msg_dir = os.path.join(base, "message")
        if not os.path.exists(session_dir):
            return

        for proj_folder in os.listdir(session_dir):
            proj_path = os.path.join(session_dir, proj_folder)
            if not os.path.isdir(proj_path):
                continue
            for f in os.listdir(proj_path):
                if not f.endswith(".json"):
                    continue
                fp = os.path.join(proj_path, f)
                s = self._parse_opencode_session(fp, base, msg_dir)
                if s:
                    self.all_sessions.append(s)
                    self.session_map[s["id"]] = s

    def _parse_opencode_session(self, filepath, base_dir, msg_dir):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            sid = data.get("id", "")
            title = data.get("title", self.t("no_title"))
            directory = data.get("directory", "")
            time_info = data.get("time", {})
            created = time_info.get("created", 0)
            updated = time_info.get("updated", created)

            project = self.get_project_name(
                directory.replace("\\", "-").replace("/", "-").replace(":", "").lstrip("-")) if directory else "(unknown)"
            self.projects.add(project)

            # Calculate size: session file + messages + parts
            size = os.path.getsize(filepath)
            msg_session_dir = os.path.join(msg_dir, sid)
            extra_files = [filepath]
            msg_count = 0
            first_user_msg = ""
            first_user_created = float("inf")

            if os.path.isdir(msg_session_dir):
                for mf in os.listdir(msg_session_dir):
                    mfp = os.path.join(msg_session_dir, mf)
                    extra_files.append(mfp)
                    size += os.path.getsize(mfp)
                    if mf.endswith(".json"):
                        try:
                            with open(mfp, "r", encoding="utf-8") as mfh:
                                md = json.load(mfh)
                            role = md.get("role", "")
                            if role in ("user", "assistant"):
                                msg_count += 1
                            # Grab first user message text
                            if role == "user":
                                mc = md.get("time", {}).get("created", 0)
                                if mc < first_user_created:
                                    mid = md.get("id", "")
                                    pdir = os.path.join(base_dir, "part", mid)
                                    if os.path.isdir(pdir):
                                        for pf in sorted(os.listdir(pdir)):
                                            pfp = os.path.join(pdir, pf)
                                            try:
                                                with open(pfp, "r", encoding="utf-8") as ph:
                                                    pd = json.load(ph)
                                                if pd.get("type") == "text" and pd.get("text"):
                                                    first_user_msg = pd["text"].strip()[:150]
                                                    first_user_created = mc
                                                    break
                                            except:
                                                pass
                            # Also count parts for size
                            part_dir = os.path.join(base_dir, "part", md.get("id", ""))
                            if os.path.isdir(part_dir):
                                for pf in os.listdir(part_dir):
                                    pfp = os.path.join(part_dir, pf)
                                    extra_files.append(pfp)
                                    size += os.path.getsize(pfp)
                        except:
                            pass

            is_blank = msg_count == 0
            dt = datetime.fromtimestamp(updated / 1000) if updated > 1e12 else datetime.fromtimestamp(updated)

            return {
                "id": "oc_" + sid, "filepath": filepath, "folder": "",
                "source": "opencode", "project": project,
                "mtime": dt.timestamp(), "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                "date_date": dt.strftime("%Y-%m-%d"), "date_month": dt.strftime("%Y-%m"),
                "date_obj": dt, "title": title or self.t("no_title"),
                "first_chat": first_user_msg or "",
                "model": "",
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": extra_files, "is_blank": is_blank,
            }
        except:
            return None

    # ══════════════════════════════════════════════════════════════
    # ── Filtering & Sorting ──
    # ══════════════════════════════════════════════════════════════

    def apply_filters(self, *args):
        if not hasattr(self, 'tree'):
            return
        search = self.search_var.get().lower()
        project_filter = self.project_var.get()
        date_filter = self._key_from_display(self.date_var.get(), self._date_keys)
        sort_mode = self._key_from_display(self.sort_var.get(), self._sort_keys)
        group_mode = self._key_from_display(self.group_var.get(), self._group_keys)

        result = []
        for s in self.all_sessions:
            if search:
                if (search not in s["title"].lower()
                    and search not in s["project"].lower()
                    and search not in s["date_str"]
                    and search not in s.get("model", "").lower()):
                    continue
            if project_filter != self.t("all") and s["project"] != project_filter:
                continue
            days = s["age_days"]
            if date_filter == "today" and days > 0: continue
            elif date_filter == "yesterday" and days != 1: continue
            elif date_filter == "7d" and days > 7: continue
            elif date_filter == "30d" and days > 30: continue
            elif date_filter == "90d" and days > 90: continue
            elif date_filter == ">90d" and days <= 90: continue
            result.append(s)

        if sort_mode == "newest":
            result.sort(key=lambda x: x["mtime"], reverse=True)
        elif sort_mode == "oldest":
            result.sort(key=lambda x: x["mtime"])
        elif sort_mode == "a_z":
            result.sort(key=lambda x: x["title"].lower())
        elif sort_mode == "z_a":
            result.sort(key=lambda x: x["title"].lower(), reverse=True)
        elif sort_mode == "size":
            result.sort(key=lambda x: x["size"], reverse=True)
        elif sort_mode == "project":
            result.sort(key=lambda x: (x["project"].lower(), -x["mtime"]))

        self.filtered_sessions = result

        # Update project count label
        pf = project_filter
        if pf and pf != self.t("all"):
            cnt = self._project_counts.get(pf, 0)
            self.project_count_label.config(text=f"({cnt})")
        else:
            self.project_count_label.config(text=f"({len(self._all_projects_list)} projects)")

        self.render_tree(group_mode)

    def _sort_click(self, col):
        mapping = {"project": "project", "date": "newest", "title": "a_z",
                   "size": "size", "age": "oldest"}
        current = self._key_from_display(self.sort_var.get(), self._sort_keys)
        target = mapping.get(col, "newest")
        if col == "date":
            target = "oldest" if current == "newest" else "newest"
        elif col == "title":
            target = "z_a" if current == "a_z" else "a_z"
        self.sort_var.set(self.t(target))

    def render_tree(self, group_mode="no_group"):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.stat_showing.config(text=str(len(self.filtered_sessions)))
        self.stat_selected.config(text="0")

        # Hide source column (single source view)
        self.tree.column("source", width=0, minwidth=0, stretch=False)

        for project, color in self.project_colors.items():
            tag = f"proj_{hash(project)}"
            self.tree.tag_configure(tag, foreground=color)

        self.tree.tag_configure("blank", foreground="#555566")

        if group_mode == "no_group":
            for s in self.filtered_sessions:
                tag = f"proj_{hash(s['project'])}"
                tags = (tag, "blank") if s.get("is_blank") else (tag,)
                self.tree.insert("", "end", iid=s["id"],
                               values=("", s["project"], s["date_str"], s["title"],
                                       s.get("first_chat", ""), s.get("model", ""),
                                       s["size_str"], s["age_str"]),
                               tags=tags)
        else:
            groups = defaultdict(list)
            for s in self.filtered_sessions:
                if group_mode == "project":
                    key = s["project"]
                elif group_mode == "date":
                    key = s["date_date"]
                elif group_mode == "month":
                    key = s["date_month"]
                elif group_mode == "age":
                    key = s["age_group"]
                else:
                    key = self.t("other")
                groups[key].append(s)

            if group_mode == "age":
                order = [self.t("today"), self.t("yesterday"), self.t("this_week"),
                         self.t("this_month"), self.t("1_3m"), self.t("3_6m"),
                         self.t("6_12m"), self.t(">1y")]
                sorted_keys = [k for k in order if k in groups]
            elif group_mode in ("date", "month"):
                sorted_keys = sorted(groups.keys(), reverse=True)
            else:
                sorted_keys = sorted(groups.keys())

            for gidx, key in enumerate(sorted_keys):
                items = groups[key]
                total = self.fmt_size(sum(s["size"] for s in items))
                gid = f"__group_{gidx}"

                self.tree.insert("", "end", iid=gid, text="",
                               values=("", f"{key}", self.t("n_session").format(n=len(items)), "", "", "", total, ""),
                               tags=("group",), open=True)

                for s in items:
                    tag = f"proj_{hash(s['project'])}"
                    tags = (tag, "blank") if s.get("is_blank") else (tag,)
                    self.tree.insert(gid, "end", iid=s["id"],
                                   values=("", s["project"], s["date_str"], s["title"],
                                           s.get("first_chat", ""), s.get("model", ""),
                                           s["size_str"], s["age_str"]),
                                   tags=tags)

        self.status_label.config(
            text=self.t("x_of_y").format(shown=len(self.filtered_sessions), total=len(self.all_sessions)))
        self._clear_preview()

    # ══════════════════════════════════════════════════════════════
    # ── Selection & Preview ──
    # ══════════════════════════════════════════════════════════════

    def on_select(self, event):
        selected = self.tree.selection()
        count = sum(1 for s in selected if not s.startswith("__group_"))
        self.stat_selected.config(text=str(count))

        real = [s for s in selected if not s.startswith("__group_")]
        if len(real) == 1:
            self._show_preview(real[0])
        elif len(real) > 1:
            self._show_multi_preview(real)
        else:
            self._clear_preview()

    def _clear_preview(self):
        self.preview_title_label.config(text=self.t("preview"), fg=self.colors["accent"])
        self.preview_info_label.config(text=self.t("preview_hint"))
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("end", self.t("preview_click"), "meta")
        self.preview_text.config(state="disabled")
        self.preview_loadmore_frame.pack_forget()
        self._preview_messages = []
        self._preview_current_sid = None
        self._preview_page = 0

    def _show_multi_preview(self, sids):
        self.preview_loadmore_frame.pack_forget()
        self._preview_messages = []
        self._preview_current_sid = None
        self.preview_title_label.config(text=self.t("n_selected").format(n=len(sids)), fg=self.colors["accent"])
        total_size = sum(self.session_map[s]["size"] for s in sids if s in self.session_map)
        self.preview_info_label.config(text=f"Total: {self.fmt_size(total_size)}")

        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")
        for i, sid in enumerate(sids[:15]):
            s = self.session_map.get(sid)
            if not s:
                continue
            color = self.project_colors.get(s["project"], self.colors["text"])
            tag_name = f"multi_{hash(s['project'])}"
            self.preview_text.tag_configure(tag_name, foreground=color, font=(_FONT_MONO, 9, "bold"))
            self.preview_text.insert("end", f"[{s['project']}] ", tag_name)
            self.preview_text.insert("end", f"{s['title']}\n", "content")
            self.preview_text.insert("end", f"  {s['date_str']}  |  {s['size_str']}  |  {s['age_str']}\n", "meta")
            if i < len(sids) - 1:
                self.preview_text.insert("end", "\n")
        if len(sids) > 15:
            self.preview_text.insert("end", f"\n{self.t('and_more').format(n=len(sids) - 15)}\n", "meta")
        self.preview_text.config(state="disabled")

    def _is_claude_command(self, text):
        prefixes = ("<local-command", "<command-name>", "<command-message>",
                     "<command-args>", "<local-command-stdout>", "<local-command-stderr>",
                     "<local-command-caveat>")
        return any(text.startswith(p) for p in prefixes) or text.startswith("<system-reminder>")

    # ══════════════════════════════════════════════════════════════
    # ── Open / Resume Session (Cross-Platform) ──
    # ══════════════════════════════════════════════════════════════

    def _try_resolve_path(self, base, segments):
        if not segments:
            return base if os.path.isdir(base) else None
        # Try longest match first (greedy) to avoid partial prefix matches
        # e.g. "svelte-obfuscation" should match before "svelte"
        for i in range(len(segments), 0, -1):
            candidate = os.path.join(base, "-".join(segments[:i]))
            if os.path.isdir(candidate):
                result = self._try_resolve_path(candidate, segments[i:])
                if result:
                    return result
        return base if os.path.isdir(base) else None

    def _resolve_project_dir(self, session):
        source = session.get("source", "")
        folder = session.get("folder", "")
        if source == "claude" and folder:
            parts = folder.split("--", 1)
            if len(parts) == 2:
                drive = parts[0] + ":/"
                segments = parts[1].split("-")
                return self._try_resolve_path(drive, segments)
        elif source == "factory" and folder:
            stripped = folder.lstrip("-")
            parts = stripped.split("-", 1)
            if len(parts) == 2:
                drive = parts[0] + ":/"
                segments = parts[1].split("-")
                return self._try_resolve_path(drive, segments)
        elif source == "codex":
            fp = session.get("filepath", "")
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        data = json.loads(line)
                        if data.get("type") == "session_meta":
                            cwd = data.get("payload", {}).get("cwd", "")
                            if cwd and os.path.isdir(cwd):
                                return cwd
                        break
            except:
                pass
        elif source == "opencode":
            fp = session.get("filepath", "")
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cwd = data.get("directory", "") or data.get("cwd", "") or data.get("working_directory", "")
                if cwd and os.path.isdir(cwd):
                    return cwd
            except:
                pass
        return None

    def _get_session_id(self, session):
        sid = session.get("id", "")
        for prefix in ("cc_", "cx_", "oc_"):
            if sid.startswith(prefix):
                return sid[len(prefix):]
        return sid

    def _open_in_terminal(self, cmd_args, cwd):
        """Open a command in a new terminal window, cross-platform."""
        import sys, shlex
        platform = sys.platform

        if platform == "win32":
            subprocess.Popen(
                ["cmd", "/c", "start", "", "cmd", "/k"] + cmd_args,
                cwd=cwd, shell=False
            )
        elif platform == "darwin":
            cmd_str = " ".join(shlex.quote(a) for a in cmd_args)
            cwd_q = shlex.quote(cwd)
            # Try iTerm2 first, fall back to Terminal.app
            iterm_script = (
                f'tell application "iTerm"\n'
                f'  create window with default profile\n'
                f'  tell current session of current window\n'
                f'    write text "cd {cwd_q} && {cmd_str}"\n'
                f'  end tell\n'
                f'end tell'
            )
            terminal_script = (
                f'tell application "Terminal"\n'
                f'  do script "cd {cwd_q} && {cmd_str}"\n'
                f'  activate\n'
                f'end tell'
            )
            # Check if iTerm2 is installed
            iterm_path = "/Applications/iTerm.app"
            if os.path.isdir(iterm_path):
                subprocess.Popen(["osascript", "-e", iterm_script])
            else:
                subprocess.Popen(["osascript", "-e", terminal_script])
        else:
            # Linux: try common terminal emulators
            cmd_str = " ".join(shlex.quote(a) for a in cmd_args)
            cwd_q = shlex.quote(cwd)
            bash_cmd = f"cd {cwd_q} && {cmd_str}; exec bash"
            terminals = [
                ["x-terminal-emulator", "-e", f"bash -c '{bash_cmd}'"],
                ["gnome-terminal", "--", "bash", "-c", bash_cmd],
                ["konsole", "-e", "bash", "-c", bash_cmd],
                ["xfce4-terminal", "-e", f"bash -c '{bash_cmd}'"],
                ["xterm", "-e", f"bash -c '{bash_cmd}'"],
            ]
            for term_cmd in terminals:
                try:
                    subprocess.Popen(term_cmd)
                    return
                except FileNotFoundError:
                    continue
            messagebox.showwarning(self.t("warn"),
                "No supported terminal emulator found.\n"
                f"Run manually: cd {cwd} && {cmd_str}")

    def _show_open_dialog(self, session, callback):
        """Show modal dialog with options before opening a session."""
        source = session.get("source", "")
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("open_session"))
        dlg.configure(bg=self.colors["surface"])
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        # Center on parent
        dlg.update_idletasks()
        w, h = 380, 180
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        title = session.get("title", "")[:60]
        tk.Label(dlg, text=f"Resume: {title}", font=(_FONT_UI, 9, "bold"),
                 bg=self.colors["surface"], fg=self.colors["text"],
                 wraplength=350).pack(padx=16, pady=(12, 4))

        opts = {}
        if source == "claude":
            opts["skip_permissions"] = tk.BooleanVar(value=False)
            tk.Checkbutton(dlg, text="--dangerously-skip-permissions",
                           variable=opts["skip_permissions"],
                           bg=self.colors["surface"], fg="#e06060",
                           selectcolor=self.colors["surface2"],
                           activebackground=self.colors["surface"],
                           activeforeground="#e06060",
                           font=(_FONT_MONO, 9)).pack(padx=20, anchor="w", pady=(8, 0))
            tk.Label(dlg, text="⚠ Skip all permission prompts (use with caution)",
                     bg=self.colors["surface"], fg=self.colors["dim"],
                     font=(_FONT_UI, 7, "italic")).pack(padx=36, anchor="w")

        btn_frame = tk.Frame(dlg, bg=self.colors["surface"])
        btn_frame.pack(pady=(16, 12))
        tk.Button(btn_frame, text=self.t("open_session"), font=(_FONT_UI, 9, "bold"),
                  bg=self.colors["accent"], fg="#000", padx=20, pady=4, borderwidth=0,
                  cursor="hand2",
                  command=lambda: [dlg.destroy(), callback(opts)]).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Cancel", font=(_FONT_UI, 9),
                  bg=self.colors["border"], fg=self.colors["text"], padx=16, pady=4,
                  borderwidth=0, cursor="hand2",
                  command=dlg.destroy).pack(side="left", padx=4)

    def _open_session(self, session):
        source = session.get("source", "")
        sid = self._get_session_id(session)
        project_dir = self._resolve_project_dir(session)
        src_label = self.SOURCES.get(source, {}).get("label", source)

        if source == "claude":
            cwd = project_dir or os.path.expanduser("~")
            def do_open(opts):
                cmd = ["claude", "--resume", sid]
                if opts.get("skip_permissions") and opts["skip_permissions"].get():
                    cmd.append("--dangerously-skip-permissions")
                self._open_in_terminal(cmd, cwd)
            self._show_open_dialog(session, do_open)
            return
        elif source == "codex":
            codex_sid = session.get("codex_session_id", sid)
            cwd = project_dir or os.path.expanduser("~")
            self._open_in_terminal(["codex", "resume", codex_sid], cwd)
        elif source == "factory":
            cwd = project_dir
            if not cwd:
                messagebox.showwarning(self.t("warn"),
                    self.t("open_no_dir").format(path=session.get("folder", "")))
                return
            self._open_in_terminal(["droid", "--resume", sid], cwd)
        elif source == "opencode":
            cwd = project_dir
            if not cwd:
                messagebox.showwarning(self.t("warn"),
                    self.t("open_no_dir").format(path=session.get("folder", "")))
                return
            self._open_in_terminal(["opencode", "-s", sid], cwd)
        else:
            messagebox.showinfo(self.t("warn"),
                self.t("open_no_support").format(src=src_label))

    def _open_selected_session(self):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        s = self.session_map.get(iid)
        if not s:
            return
        self._open_session(s)

    def _on_tree_double_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        s = self.session_map.get(iid)
        if not s:
            return
        self._open_session(s)

    def _on_tree_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        s = self.session_map.get(iid)
        if not s:
            return

        menu = tk.Menu(self.root, tearoff=0,
                       bg=self.colors["surface"], fg=self.colors["text"],
                       activebackground=self.colors["accent"], activeforeground="#000",
                       font=(_FONT_UI, 9))
        menu.add_command(label=self.t("open_session"),
                         command=lambda: self._open_session(s))
        menu.add_command(label=self.t("rename_title"),
                         command=lambda: self._rename_session(s))
        menu.add_command(label="Copy Session ID",
                         command=lambda: self._copy_session_id(s))
        menu.add_separator()
        menu.add_command(label=self.t("del_selected"),
                         command=self.delete_selected)
        menu.tk_popup(event.x_root, event.y_root)

    def _copy_session_id(self, session):
        sid = self._get_session_id(session)
        self.root.clipboard_clear()
        self.root.clipboard_append(sid)
        self.status_label.config(text=self.t("copied_sid"))

    def _ask_rename(self, current_title):
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("rename_title"))
        dlg.configure(bg=self.colors["bg"])
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        w, h = 500, 150
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        result = {"value": None}

        tk.Label(dlg, text=self.t("rename_prompt"),
                 bg=self.colors["bg"], fg=self.colors["text"],
                 font=(_FONT_UI, 10)).pack(padx=20, pady=(16, 6), anchor="w")

        entry = tk.Entry(dlg, font=(_FONT_UI, 11), width=50,
                         bg=self.colors["surface2"], fg=self.colors["text"],
                         insertbackground=self.colors["text"],
                         borderwidth=0, highlightthickness=1,
                         highlightcolor=self.colors["accent"],
                         highlightbackground=self.colors["border"])
        entry.pack(padx=20, ipady=6, fill="x")
        entry.insert(0, current_title)
        entry.select_range(0, "end")
        entry.focus_set()

        btn_frame = tk.Frame(dlg, bg=self.colors["bg"])
        btn_frame.pack(pady=(12, 16), padx=20, fill="x")

        def on_ok(*_):
            result["value"] = entry.get().strip()
            dlg.destroy()

        def on_cancel(*_):
            dlg.destroy()

        tk.Button(btn_frame, text="OK", font=(_FONT_UI, 9, "bold"),
                  bg=self.colors["accent"], fg="#000", padx=20, pady=4,
                  cursor="hand2", command=on_ok).pack(side="right", padx=(6, 0))
        tk.Button(btn_frame, text="Cancel", font=(_FONT_UI, 9),
                  bg=self.colors["border"], fg=self.colors["text"], padx=20, pady=4,
                  cursor="hand2", command=on_cancel).pack(side="right")

        entry.bind("<Return>", on_ok)
        entry.bind("<Escape>", on_cancel)

        dlg.wait_window()
        return result["value"]

    # ══════════════════════════════════════════════════════════════
    # ── Rename Session ──
    # ══════════════════════════════════════════════════════════════

    def _rename_session(self, session):
        source = session.get("source", "")
        if source == "codex":
            messagebox.showinfo(self.t("warn"), self.t("rename_no_support"))
            return

        new_title = self._ask_rename(session.get("title", ""))
        if not new_title:
            return

        try:
            if source == "factory":
                self._rename_factory(session, new_title)
            elif source == "claude":
                self._rename_claude(session, new_title)
            elif source == "opencode":
                self._rename_opencode(session, new_title)

            session["title"] = new_title
            # Update treeview
            iid = session["id"]
            if self.tree.exists(iid):
                vals = list(self.tree.item(iid, "values"))
                vals[3] = new_title  # title is index 3
                self.tree.item(iid, values=vals)
            self.status_label.config(text=self.t("rename_success"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _rename_factory(self, session, new_title):
        filepath = session["filepath"]
        lines = []
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines:
            first = json.loads(lines[0])
            first["sessionTitle"] = new_title
            first["isSessionTitleManuallySet"] = True
            lines[0] = json.dumps(first, ensure_ascii=False) + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def _rename_claude(self, session, new_title):
        sid = self._get_session_id(session)
        folder = session.get("folder", "")
        projects_dir = self.SOURCES["claude"]["dir"]
        idx_path = os.path.join(projects_dir, folder, "sessions-index.json")
        if os.path.exists(idx_path):
            with open(idx_path, "r", encoding="utf-8") as f:
                idx = json.load(f)
            for entry in idx.get("entries", []):
                if entry.get("sessionId") == sid:
                    entry["summary"] = new_title
                    break
            with open(idx_path, "w", encoding="utf-8") as f:
                json.dump(idx, f, ensure_ascii=False, indent=2)
        else:
            raise FileNotFoundError(f"sessions-index.json not found for {folder}")

    def _rename_opencode(self, session, new_title):
        filepath = session["filepath"]
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["title"] = new_title
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ══════════════════════════════════════════════════════════════
    # ── Chat Preview & Pagination ──
    # ══════════════════════════════════════════════════════════════

    def _extract_content_text(self, content):
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, dict):
                    t = part.get("type", "")
                    if t == "text":
                        parts.append(part.get("text", ""))
                    elif t == "thinking":
                        pass
                    elif t == "tool_use":
                        parts.append(f"[tool: {part.get('name', '?')}]")
                    elif t == "tool_result":
                        parts.append("[tool result]")
                elif isinstance(part, str):
                    parts.append(part)
            return "\n".join(parts)
        return str(content) if content else ""

    def _show_preview(self, sid):
        s = self.session_map.get(sid)
        if not s:
            self._clear_preview()
            return

        color = self.project_colors.get(s["project"], self.colors["text"])
        self.preview_title_label.config(text=s["title"], fg=color)
        model_str = s.get("model", "")
        info_parts = [s['project'], s['date_str']]
        if model_str:
            info_parts.append(model_str)
        info_parts.extend([s['size_str'], s['age_str']])
        self.preview_info_label.config(text="  |  ".join(info_parts))

        # Parse all messages once, then paginate
        self._preview_current_sid = sid
        self._preview_page = 0

        if s["source"] == "opencode":
            self._preview_messages = self._parse_opencode_messages(s)
        else:
            self._preview_messages = self._parse_jsonl_messages(s)

        self._preview_total_available = len(self._preview_messages)
        self._render_preview_page(reset=True)

    def _parse_opencode_messages(self, s):
        messages = []
        try:
            base = self.SOURCES["opencode"]["dir"]
            msg_dir = os.path.join(base, "message", s["id"].replace("oc_", ""))
            part_dir = os.path.join(base, "part")

            if not os.path.isdir(msg_dir):
                return messages

            raw = []
            for mf in os.listdir(msg_dir):
                if not mf.endswith(".json"):
                    continue
                mfp = os.path.join(msg_dir, mf)
                try:
                    with open(mfp, "r", encoding="utf-8") as fh:
                        md = json.load(fh)
                    role = md.get("role", "")
                    if role not in ("user", "assistant"):
                        continue
                    created = md.get("time", {}).get("created", 0)
                    msg_id = md.get("id", "")
                    texts = []
                    pdir = os.path.join(part_dir, msg_id)
                    if os.path.isdir(pdir):
                        for pf in sorted(os.listdir(pdir)):
                            pfp = os.path.join(pdir, pf)
                            try:
                                with open(pfp, "r", encoding="utf-8") as ph:
                                    pd = json.load(ph)
                                pt = pd.get("type", "")
                                if pt == "text" and pd.get("text"):
                                    texts.append(pd["text"])
                                elif pt == "tool":
                                    texts.append("[tool: %s]" % pd.get("tool", "?"))
                            except:
                                pass
                    content = "\n".join(texts).strip()
                    if content:
                        raw.append((created, role, content))
                except:
                    pass

            raw.sort(key=lambda x: x[0])
            for _, role, content in raw:
                messages.append({"role": role, "content": content})
        except:
            pass
        return messages

    def _parse_jsonl_messages(self, s):
        messages = []
        try:
            with open(s["filepath"], "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f):
                    if line_num >= 500:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except:
                        continue

                    entry_type = entry.get("type", "")
                    role = ""
                    content = ""

                    if entry_type == "message" and isinstance(entry.get("message"), dict):
                        msg = entry["message"]
                        role = msg.get("role", "")
                        content = self._extract_content_text(msg.get("content", ""))
                    elif entry_type in ("user", "human", "assistant") and isinstance(entry.get("message"), dict):
                        msg = entry["message"]
                        role = msg.get("role", "") or entry_type
                        if role == "human":
                            role = "user"
                        content = self._extract_content_text(msg.get("content", ""))
                    elif entry_type == "event_msg" and isinstance(entry.get("payload"), dict):
                        role = "user"
                        raw = entry["payload"].get("message", "")
                        marker = "My request for Codex:\n"
                        idx = raw.find(marker)
                        content = raw[idx + len(marker):].strip() if idx != -1 else raw.strip()
                    elif entry_type == "response_item" and isinstance(entry.get("payload"), dict):
                        payload = entry["payload"]
                        role = payload.get("role", "")
                        if role in ("developer", "system"):
                            continue
                        content = self._extract_content_text(payload.get("content", ""))
                    elif entry.get("role") and entry.get("content"):
                        role = entry["role"]
                        content = self._extract_content_text(entry["content"])
                    else:
                        continue

                    if not role or role == "system":
                        continue
                    if not content.strip():
                        continue

                    text = self._clean_message_text(content.strip())
                    if not text:
                        continue
                    if self._is_claude_command(text):
                        continue

                    messages.append({"role": role, "content": text})
        except:
            pass
        return messages

    def _clean_message_text(self, text):
        """Strip all <system-reminder>...</system-reminder> blocks from text."""
        import re
        text = re.sub(r'<system-reminder>.*?</system-reminder>', '', text, flags=re.DOTALL).strip()
        return text

    def _render_preview_page(self, reset=False):
        self.preview_text.config(state="normal")

        if reset:
            self.preview_text.delete("1.0", "end")
            self._preview_page = 0

        messages = self._preview_messages
        if not messages:
            self.preview_text.insert("end", self.t("no_msg_file"), "meta")
            self.preview_text.config(state="disabled")
            self.preview_loadmore_frame.pack_forget()
            return

        start = self._preview_page * self._preview_page_size
        end = start + self._preview_page_size
        page_msgs = messages[start:end]
        total = len(messages)

        for i, msg in enumerate(page_msgs):
            msg_num = start + i + 1
            role = msg["role"]
            text = msg["content"]

            role_tag = f"role_{role}" if role in ("user", "assistant") else "role_system"
            role_label = {"user": "USER", "assistant": "ASSISTANT"}.get(role, role.upper())
            role_icon = "\u25b6" if role == "user" else "\u25c0"

            self.preview_text.insert("end", f"#{msg_num} ", "msg_number")
            self.preview_text.insert("end", f"{role_icon} {role_label}\n", role_tag)

            # Show more text but truncate very long messages
            max_len = 800
            if len(text) > max_len:
                self.preview_text.insert("end", text[:max_len], "content")
                remaining = len(text) - max_len
                self.preview_text.insert("end", f"\n    ... [{remaining} chars more]\n", "content_truncated")
            else:
                self.preview_text.insert("end", f"{text}\n", "content")

            if msg_num < total:
                self.preview_text.insert("end", "\u2500" * 40 + "\n", "separator")

        shown = min(end, total)
        has_more = end < total

        # Update info label with message count
        s = self.session_map.get(self._preview_current_sid)
        if s:
            model_str = s.get("model", "")
            info_parts = [s['project'], s['date_str']]
            if model_str:
                info_parts.append(model_str)
            info_parts.extend([s['size_str'], f"{shown}/{total} msgs"])
            self.preview_info_label.config(text="  |  ".join(info_parts))

        if has_more:
            remaining = total - shown
            self.preview_loadmore_btn.config(
                text=self.t("load_more").format(n=remaining))
            self.preview_msg_count_label.config(
                text=self.t("showing_of").format(shown=shown, total=total))
            self.preview_loadmore_frame.pack(fill="x", side="bottom")
        else:
            self.preview_loadmore_frame.pack_forget()

        self.preview_text.config(state="disabled")

        if reset:
            self.preview_text.yview_moveto(0)

    def _load_more_preview(self):
        self._preview_page += 1
        # Scroll position before appending
        self.preview_text.config(state="normal")
        # Remove trailing newline if any for clean append
        self.preview_text.config(state="disabled")
        self._render_preview_page(reset=False)

    def _delete_opencode_extras(self, s):
        base = self.SOURCES["opencode"]["dir"]
        sid = s["id"].replace("oc_", "")
        # Delete message folder and part folders
        msg_dir = os.path.join(base, "message", sid)
        if os.path.isdir(msg_dir):
            # First delete parts for each message
            for mf in os.listdir(msg_dir):
                if mf.endswith(".json"):
                    try:
                        with open(os.path.join(msg_dir, mf), "r", encoding="utf-8") as fh:
                            mid = json.load(fh).get("id", "")
                        if mid:
                            part_d = os.path.join(base, "part", mid)
                            if os.path.isdir(part_d):
                                shutil.rmtree(part_d)
                    except:
                        pass
            try: shutil.rmtree(msg_dir)
            except: pass
        # Delete session_diff
        diff_f = os.path.join(base, "session_diff", sid + ".json")
        if os.path.exists(diff_f):
            try: os.remove(diff_f)
            except: pass

    # ══════════════════════════════════════════════════════════════
    # ── Delete & Bulk Actions ──
    # ══════════════════════════════════════════════════════════════

    def _get_session_items(self):
        items = []
        for item in self.tree.get_children():
            if item.startswith("__group_"):
                items.extend(self.tree.get_children(item))
            else:
                items.append(item)
        return items

    def select_all(self):
        items = self._get_session_items()
        self.tree.selection_set(items)
        self.stat_selected.config(text=str(len(items)))

    def deselect_all(self):
        self.tree.selection_remove(*self.tree.selection())
        self.stat_selected.config(text="0")
        self._clear_preview()

    def invert_selection(self):
        all_items = set(self._get_session_items())
        selected = set(s for s in self.tree.selection() if not s.startswith("__group_"))
        new = list(all_items - selected)
        self.tree.selection_set(new)
        self.stat_selected.config(text=str(len(new)))

    def select_by_age(self, days):
        to_select = [s["id"] for s in self.filtered_sessions if s["age_days"] > days]
        if to_select:
            self.tree.selection_set(to_select)
            self.stat_selected.config(text=str(len(to_select)))
        else:
            messagebox.showinfo("Info", self.t("no_session_age").format(days=days))

    def select_blank(self):
        to_select = [s["id"] for s in self.filtered_sessions if s.get("is_blank")]
        if to_select:
            self.tree.selection_set(to_select)
            self.stat_selected.config(text=str(len(to_select)))
            total_size = sum(s["size"] for s in self.filtered_sessions if s.get("is_blank"))
            messagebox.showinfo(self.t("blank_title"),
                self.t("blank_found").format(n=len(to_select), size=self.fmt_size(total_size)))
        else:
            messagebox.showinfo("Info", self.t("no_blank"))

    def delete_blank_sessions(self):
        blanks = [s for s in self.all_sessions if s.get("is_blank")]
        if not blanks:
            messagebox.showinfo("Info", self.t("no_blank"))
            return

        total_size = sum(s["size"] for s in blanks)
        src_label = self.SOURCES[self.current_source]["label"]
        msg = self.t("del_blank_confirm").format(n=len(blanks), src=src_label, size=self.fmt_size(total_size))

        if not messagebox.askyesno(self.t("del_blank"), msg, icon="warning"):
            return

        deleted = 0
        for s in blanks:
            try:
                os.remove(s["filepath"])
                deleted += 1
            except:
                pass
            if s["source"] == "factory":
                settings = s["filepath"].replace(".jsonl", ".settings.json")
                if os.path.exists(settings):
                    try: os.remove(settings)
                    except: pass
            elif s["source"] == "claude":
                sub_dir = s["filepath"].replace(".jsonl", "")
                if os.path.isdir(sub_dir):
                    try: shutil.rmtree(sub_dir)
                    except: pass
            elif s["source"] == "opencode":
                self._delete_opencode_extras(s)

        # Also clean up empty folders
        base_dir = self.SOURCES[self.current_source]["dir"]
        empty_dirs = 0
        if os.path.exists(base_dir):
            for dirpath, dirnames, filenames in os.walk(base_dir, topdown=False):
                if dirpath == base_dir:
                    continue
                if not os.listdir(dirpath):
                    try:
                        os.rmdir(dirpath)
                        empty_dirs += 1
                    except:
                        pass

        extra = self.t("empty_dirs").format(n=empty_dirs) if empty_dirs else ""
        messagebox.showinfo(self.t("done"),
                           self.t("del_blank_done").format(n=deleted, size=self.fmt_size(total_size), extra=extra))
        self.refresh()

    def refresh(self):
        self.load_all_sessions()

    def delete_selected(self):
        raw = self.tree.selection()
        selected = [s for s in raw if not s.startswith("__group_")]
        if not selected:
            messagebox.showwarning(self.t("warn"), self.t("warn_select"))
            return

        total_size = 0
        lines = []
        for sid in selected:
            s = self.session_map.get(sid)
            if s:
                lines.append(f"  {s['date_str']}  {s['title'][:45]}")
                total_size += s["size"]

        preview = "\n".join(lines[:10])
        if len(lines) > 10:
            preview += f"\n  {self.t('and_more').format(n=len(lines) - 10)}"

        src_label = self.SOURCES[self.current_source]["label"]
        msg = self.t("del_confirm").format(n=len(selected), src=src_label,
                                           size=self.fmt_size(total_size), preview=preview)

        if not messagebox.askyesno(self.t("del_confirm_title"), msg, icon="warning"):
            return

        deleted = 0
        for sid in selected:
            s = self.session_map.get(sid)
            if not s:
                continue
            try:
                os.remove(s["filepath"])
                deleted += 1
            except:
                pass

            # Delete associated files
            if s["source"] == "factory":
                settings = s["filepath"].replace(".jsonl", ".settings.json")
                if os.path.exists(settings):
                    try: os.remove(settings)
                    except: pass
            elif s["source"] == "claude":
                sub_dir = s["filepath"].replace(".jsonl", "")
                if os.path.isdir(sub_dir):
                    try: shutil.rmtree(sub_dir)
                    except: pass
                for ef in s.get("extra_files", []):
                    if os.path.exists(ef):
                        try: os.remove(ef)
                        except: pass
            elif s["source"] == "opencode":
                self._delete_opencode_extras(s)

        messagebox.showinfo(self.t("done"),
                           self.t("del_done").format(n=deleted, size=self.fmt_size(total_size)))

        sel_set = set(selected)
        self.all_sessions = [s for s in self.all_sessions if s["id"] not in sel_set]
        self.filtered_sessions = [s for s in self.filtered_sessions if s["id"] not in sel_set]
        for sid in selected:
            self.session_map.pop(sid, None)
        self.apply_filters()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except:
        pass
    if _IS_MAC:
        root.lift()
        root.attributes("-topmost", True)
        root.after(100, lambda: root.attributes("-topmost", False))
    app = SessionCleaner(root)
    root.mainloop()
