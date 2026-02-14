import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import shutil
from datetime import datetime, timedelta
from collections import defaultdict


class SessionCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Session Cleaner")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#0e0e10")

        self.all_sessions = []
        self.filtered_sessions = []
        self.projects = set()
        self.project_colors = {}
        self.session_map = {}
        self.current_source = "factory"

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
        self.load_all_sessions()

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
        style.configure("TLabel", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=c["bg"], foreground=c["accent"], font=("Segoe UI", 15, "bold"))
        style.configure("Dim.TLabel", background=c["bg"], foreground=c["dim"], font=("Segoe UI", 9))

        style.configure("TButton", font=("Segoe UI", 9), padding=(10, 5),
                        background=c["border"], foreground=c["text"])
        style.map("TButton", background=[("active", "#3a3a5a")])

        style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 5),
                        background=c["accent"], foreground="#000")
        style.map("Accent.TButton", background=[("active", "#00b894")])

        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 7),
                        background=c["danger"], foreground="#fff")
        style.map("Danger.TButton", background=[("active", "#c0392b")])

        style.configure("Warn.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 5),
                        background=c["warn"], foreground="#000")
        style.map("Warn.TButton", background=[("active", "#d48b00")])

        style.configure("TCombobox", font=("Segoe UI", 9), fieldbackground=c["surface"],
                        background=c["surface"], foreground=c["text"])

        style.configure("Treeview",
                        background=c["surface"], foreground=c["text"], fieldbackground=c["surface"],
                        font=("Segoe UI", 9), rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading",
                        background=c["group_bg"], foreground=c["text"],
                        font=("Segoe UI", 9, "bold"), borderwidth=0)
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

        self.title_label = ttk.Label(header, text="Session Cleaner", style="Title.TLabel")
        self.title_label.pack(side="left")

        # Source selector
        src_frame = tk.Frame(header, bg=self.colors["bg"])
        src_frame.pack(side="right")

        ttk.Label(src_frame, text="Source:", style="Dim.TLabel").pack(side="left", padx=(0, 6))

        self.source_buttons = {}
        for key, info in self.SOURCES.items():
            btn = tk.Button(src_frame, text=info["label"], font=("Segoe UI", 9, "bold"),
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
        self.stat_size = self._stat(stats_frame, "Ukuran", "0 MB")
        self.stat_blank = self._stat(stats_frame, "Kosong", "0")
        self.stat_showing = self._stat(stats_frame, "Ditampilkan", "0")
        self.stat_selected = self._stat(stats_frame, "Dipilih", "0")

        # Toolbar
        tb1 = ttk.Frame(self.root)
        tb1.pack(fill="x", padx=16, pady=(0, 2))

        ttk.Label(tb1, text="Cari:", style="Dim.TLabel").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.apply_filters)
        tk.Entry(tb1, textvariable=self.search_var, width=28,
                 bg=self.colors["surface2"], fg=self.colors["text"],
                 insertbackground=self.colors["text"], font=("Segoe UI", 9),
                 borderwidth=0, highlightthickness=1,
                 highlightcolor=self.colors["accent"],
                 highlightbackground=self.colors["border"]).pack(side="left", padx=(4, 12), ipady=3)

        ttk.Label(tb1, text="Project:", style="Dim.TLabel").pack(side="left")
        self.project_var = tk.StringVar(value="Semua")
        self.project_combo = ttk.Combobox(tb1, textvariable=self.project_var, width=25, state="readonly")
        self.project_combo.pack(side="left", padx=(4, 12))
        self.project_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        ttk.Label(tb1, text="Waktu:", style="Dim.TLabel").pack(side="left")
        self.date_var = tk.StringVar(value="Semua")
        ttk.Combobox(tb1, textvariable=self.date_var, width=12,
                     values=["Semua", "Hari ini", "Kemarin", "7 hari", "30 hari",
                             "90 hari", "> 90 hari"],
                     state="readonly").pack(side="left", padx=(4, 12))
        self.date_var.trace("w", self.apply_filters)

        ttk.Label(tb1, text="Urut:", style="Dim.TLabel").pack(side="left")
        self.sort_var = tk.StringVar(value="Terbaru")
        ttk.Combobox(tb1, textvariable=self.sort_var, width=10,
                     values=["Terbaru", "Terlama", "A-Z", "Z-A", "Ukuran", "Project"],
                     state="readonly").pack(side="left", padx=(4, 12))
        self.sort_var.trace("w", self.apply_filters)

        ttk.Label(tb1, text="Group:", style="Dim.TLabel").pack(side="left")
        self.group_var = tk.StringVar(value="Tanpa Group")
        ttk.Combobox(tb1, textvariable=self.group_var, width=12,
                     values=["Tanpa Group", "Project", "Tanggal", "Bulan", "Umur"],
                     state="readonly").pack(side="left", padx=(4, 0))
        self.group_var.trace("w", self.apply_filters)

        # PanedWindow (tree + preview)
        self.paned = tk.PanedWindow(self.root, orient="vertical", bg=self.colors["bg"],
                                     sashwidth=6, sashrelief="flat", borderwidth=0)
        self.paned.pack(fill="both", expand=True, padx=16, pady=(6, 6))

        # Treeview
        tree_frame = ttk.Frame(self.paned)
        self.paned.add(tree_frame, minsize=200)

        cols = ("source", "project", "date", "title", "size", "age")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="tree headings",
                                 selectmode="extended")

        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("source", text="Source", command=lambda: self._sort_click("source"))
        self.tree.heading("project", text="Project", command=lambda: self._sort_click("project"))
        self.tree.heading("date", text="Tanggal", command=lambda: self._sort_click("date"))
        self.tree.heading("title", text="Judul Percakapan", command=lambda: self._sort_click("title"))
        self.tree.heading("size", text="Ukuran", command=lambda: self._sort_click("size"))
        self.tree.heading("age", text="Umur", command=lambda: self._sort_click("age"))

        self.tree.column("#0", width=30, minwidth=30, stretch=False)
        self.tree.column("source", width=0, minwidth=0, stretch=False)
        self.tree.column("project", width=160, minwidth=100)
        self.tree.column("date", width=130, minwidth=110, stretch=False)
        self.tree.column("title", width=400, minwidth=200)
        self.tree.column("size", width=70, minwidth=50, stretch=False, anchor="e")
        self.tree.column("age", width=80, minwidth=60, stretch=False, anchor="e")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.tree.tag_configure("group", background=self.colors["group_bg"],
                                foreground=self.colors["accent"],
                                font=("Segoe UI", 10, "bold"))

        # Preview
        preview_frame = tk.Frame(self.paned, bg=self.colors["preview_bg"],
                                  highlightbackground=self.colors["border"], highlightthickness=1)
        self.paned.add(preview_frame, minsize=80)

        preview_header = tk.Frame(preview_frame, bg=self.colors["surface"])
        preview_header.pack(fill="x")

        self.preview_title_label = tk.Label(preview_header, text="Preview Session",
                                            bg=self.colors["surface"], fg=self.colors["accent"],
                                            font=("Segoe UI", 10, "bold"), anchor="w", padx=10, pady=4)
        self.preview_title_label.pack(side="left", fill="x", expand=True)

        self.preview_info_label = tk.Label(preview_header, text="",
                                           bg=self.colors["surface"], fg=self.colors["dim"],
                                           font=("Segoe UI", 8), anchor="e", padx=10)
        self.preview_info_label.pack(side="right")

        self.preview_text = tk.Text(preview_frame, wrap="word", height=5,
                                    bg=self.colors["preview_bg"], fg=self.colors["text"],
                                    font=("Consolas", 9), borderwidth=0,
                                    insertbackground=self.colors["text"],
                                    padx=10, pady=6, state="disabled",
                                    selectbackground=self.colors["border"],
                                    selectforeground=self.colors["text"])
        preview_sb = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_sb.set)
        preview_sb.pack(side="right", fill="y")
        self.preview_text.pack(fill="both", expand=True)

        self.preview_text.tag_configure("role_user", foreground=self.colors["preview_user"],
                                        font=("Consolas", 9, "bold"))
        self.preview_text.tag_configure("role_assistant", foreground=self.colors["preview_asst"],
                                        font=("Consolas", 9, "bold"))
        self.preview_text.tag_configure("role_system", foreground=self.colors["preview_sys"],
                                        font=("Consolas", 9, "bold"))
        self.preview_text.tag_configure("content", foreground=self.colors["text"],
                                        font=("Consolas", 9))
        self.preview_text.tag_configure("separator", foreground=self.colors["border"],
                                        font=("Consolas", 8))
        self.preview_text.tag_configure("meta", foreground=self.colors["dim"],
                                        font=("Consolas", 8, "italic"))

        # Bottom bar
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=16, pady=(0, 12))

        btn_row = ttk.Frame(bottom)
        btn_row.pack(fill="x")

        ttk.Button(btn_row, text="Pilih Semua", command=self.select_all).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="Batal Pilih", command=self.deselect_all).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="Balik Pilihan", command=self.invert_selection).pack(side="left", padx=(0, 3))

        tk.Frame(btn_row, width=1, bg=self.colors["border"]).pack(side="left", fill="y", padx=8, pady=2)

        ttk.Button(btn_row, text="Pilih Kosong", style="Warn.TButton",
                   command=self.select_blank).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="Pilih > 7 hari", command=lambda: self.select_by_age(7)).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="Pilih > 30 hari", command=lambda: self.select_by_age(30)).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="Pilih > 90 hari", command=lambda: self.select_by_age(90)).pack(side="left", padx=(0, 3))

        tk.Frame(btn_row, width=1, bg=self.colors["border"]).pack(side="left", fill="y", padx=8, pady=2)

        ttk.Button(btn_row, text="Hapus Session Kosong", style="Warn.TButton",
                   command=self.delete_blank_sessions).pack(side="left", padx=(0, 3))
        ttk.Button(btn_row, text="Refresh", style="Accent.TButton",
                   command=self.refresh).pack(side="left", padx=(0, 3))

        ttk.Button(btn_row, text="Hapus Yang Dipilih", style="Danger.TButton",
                   command=self.delete_selected).pack(side="right")

        self.status_label = ttk.Label(btn_row, text="Memuat...", style="Dim.TLabel")
        self.status_label.pack(side="right", padx=12)

    def _switch_source(self, source):
        if source == self.current_source:
            return
        self.current_source = source
        self._update_source_buttons()
        self.search_var.set("")
        self.project_var.set("Semua")
        self.date_var.set("Semua")
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

    def _stat(self, parent, label, value):
        f = tk.Frame(parent, bg=self.colors["surface"], padx=16, pady=6)
        f.pack(side="left", fill="both", expand=True)
        v = tk.Label(f, text=value, bg=self.colors["surface"], fg=self.colors["accent"],
                     font=("Segoe UI", 13, "bold"))
        v.pack(anchor="w")
        tk.Label(f, text=label, bg=self.colors["surface"], fg=self.colors["dim"],
                 font=("Segoe UI", 8)).pack(anchor="w")
        return v

    def fmt_size(self, b):
        if b < 1024: return f"{b} B"
        if b < 1048576: return f"{b/1024:.1f} KB"
        return f"{b/1048576:.1f} MB"

    def fmt_age(self, dt):
        days = (datetime.now() - dt).days
        if days == 0: return "Hari ini"
        if days == 1: return "Kemarin"
        if days < 7: return f"{days} hari"
        if days < 30: return f"{days//7} minggu"
        if days < 365: return f"{days//30} bulan"
        return f"{days//365} tahun"

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
        if days == 0: return "Hari ini"
        if days == 1: return "Kemarin"
        if days <= 7: return "Minggu ini"
        if days <= 30: return "Bulan ini"
        if days <= 90: return "1-3 bulan lalu"
        if days <= 180: return "3-6 bulan lalu"
        if days <= 365: return "6-12 bulan lalu"
        return "> 1 tahun lalu"

    def _assign_project_colors(self):
        self.project_colors = {}
        for i, p in enumerate(sorted(self.projects)):
            self.project_colors[p] = self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]
        self.project_colors["(root)"] = self.colors["dim"]

    # ── Loading ──

    def load_all_sessions(self):
        self.all_sessions = []
        self.projects = set()
        self.session_map = {}

        self.status_label.config(text="Memuat session...")
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

        project_list = ["Semua"] + sorted(self.projects)
        self.project_combo["values"] = project_list

        self.apply_filters()

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
            settings = filepath.replace(".jsonl", ".settings.json")
            if os.path.exists(settings):
                size += os.path.getsize(settings)

            title = "(tidak ada judul)"
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
                                if data.get("title"):
                                    title = data["title"][:150]
                                elif data.get("sessionTitle"):
                                    title = data["sessionTitle"][:150]
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

            if title == "(tidak ada judul)" and first_user_msg:
                title = first_user_msg

            is_blank = (size == 0 or msg_count == 0 or
                        (title.lower() in ("new session", "(tidak ada judul)") and msg_count <= 1))

            dt = datetime.fromtimestamp(mtime)
            project = self.get_project_name(folder_name)

            return {
                "id": sid, "filepath": filepath, "folder": folder_name,
                "source": "factory", "project": project,
                "mtime": mtime, "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                "date_date": dt.strftime("%Y-%m-%d"), "date_month": dt.strftime("%Y-%m"),
                "date_obj": dt, "title": title,
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": [], "is_blank": is_blank,
            }
        except:
            return None

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

            title = "(tidak ada judul)"
            msg_count = 0
            if index_entry:
                fp_text = index_entry.get("firstPrompt", "")
                if fp_text:
                    title = fp_text[:150]
                msg_count = index_entry.get("messageCount", 0)
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            data = json.loads(line)
                            if data.get("type") in ("user", "human", "assistant"):
                                msg_count += 1
                                if data.get("type") in ("user", "human") and title == "(tidak ada judul)":
                                    msg = data.get("message", {})
                                    if isinstance(msg, dict):
                                        content = msg.get("content", "")
                                        if isinstance(content, str) and content.strip():
                                            title = content.strip()[:150]
                except:
                    pass

            is_blank = (size == 0 or msg_count == 0 or
                        (title.lower().startswith("[request interrupted") and msg_count <= 2))

            dt = datetime.fromtimestamp(mtime)

            return {
                "id": f"cc_{sid}", "filepath": filepath, "folder": folder_name,
                "source": "claude", "project": project,
                "mtime": mtime, "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                "date_date": dt.strftime("%Y-%m-%d"), "date_month": dt.strftime("%Y-%m"),
                "date_obj": dt, "title": title,
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": extra_files, "is_blank": is_blank,
            }
        except:
            return None

    # ── Codex CLI ──

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

            title = "(tidak ada judul)"
            project = "(unknown)"
            msg_count = 0
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
                            cwd = payload.get("cwd", "")
                            if cwd:
                                project = self.get_project_name(
                                    cwd.replace("\\", "-").replace("/", "-").replace(":", "").lstrip("-"))
                        elif t == "event_msg":
                            msg_text = payload.get("message", "")
                            if msg_text and title == "(tidak ada judul)":
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
                "mtime": mtime, "date_str": dt.strftime("%Y-%m-%d %H:%M"),
                "date_date": dt.strftime("%Y-%m-%d"), "date_month": dt.strftime("%Y-%m"),
                "date_obj": dt, "title": title,
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": [], "is_blank": is_blank,
            }
        except:
            return None

    # ── OpenCode ──

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
            title = data.get("title", "(tidak ada judul)")
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

            if os.path.isdir(msg_session_dir):
                for mf in os.listdir(msg_session_dir):
                    mfp = os.path.join(msg_session_dir, mf)
                    extra_files.append(mfp)
                    size += os.path.getsize(mfp)
                    if mf.endswith(".json"):
                        try:
                            with open(mfp, "r", encoding="utf-8") as mfh:
                                md = json.load(mfh)
                            if md.get("role") in ("user", "assistant"):
                                msg_count += 1
                            # Also count parts
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
                "date_obj": dt, "title": title or "(tidak ada judul)",
                "size": size, "size_str": self.fmt_size(size),
                "age_str": self.fmt_age(dt),
                "age_days": (datetime.now() - dt).days,
                "age_group": self.get_age_group(dt),
                "extra_files": extra_files, "is_blank": is_blank,
            }
        except:
            return None

    # ── Filtering ──

    def apply_filters(self, *args):
        search = self.search_var.get().lower()
        project_filter = self.project_var.get()
        date_filter = self.date_var.get()
        sort_mode = self.sort_var.get()
        group_mode = self.group_var.get()

        result = []
        for s in self.all_sessions:
            if search:
                if (search not in s["title"].lower()
                    and search not in s["project"].lower()
                    and search not in s["date_str"]):
                    continue
            if project_filter != "Semua" and s["project"] != project_filter:
                continue
            days = s["age_days"]
            if date_filter == "Hari ini" and days > 0: continue
            elif date_filter == "Kemarin" and days != 1: continue
            elif date_filter == "7 hari" and days > 7: continue
            elif date_filter == "30 hari" and days > 30: continue
            elif date_filter == "90 hari" and days > 90: continue
            elif date_filter == "> 90 hari" and days <= 90: continue
            result.append(s)

        if sort_mode == "Terbaru":
            result.sort(key=lambda x: x["mtime"], reverse=True)
        elif sort_mode == "Terlama":
            result.sort(key=lambda x: x["mtime"])
        elif sort_mode == "A-Z":
            result.sort(key=lambda x: x["title"].lower())
        elif sort_mode == "Z-A":
            result.sort(key=lambda x: x["title"].lower(), reverse=True)
        elif sort_mode == "Ukuran":
            result.sort(key=lambda x: x["size"], reverse=True)
        elif sort_mode == "Project":
            result.sort(key=lambda x: (x["project"].lower(), -x["mtime"]))

        self.filtered_sessions = result
        self.render_tree(group_mode)

    def _sort_click(self, col):
        mapping = {"project": "Project", "date": "Terbaru", "title": "A-Z",
                   "size": "Ukuran", "age": "Terlama"}
        current = self.sort_var.get()
        target = mapping.get(col, "Terbaru")
        if col == "date":
            target = "Terlama" if current == "Terbaru" else "Terbaru"
        elif col == "title":
            target = "Z-A" if current == "A-Z" else "A-Z"
        self.sort_var.set(target)

    def render_tree(self, group_mode="Tanpa Group"):
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

        if group_mode == "Tanpa Group":
            for s in self.filtered_sessions:
                tag = f"proj_{hash(s['project'])}"
                tags = (tag, "blank") if s.get("is_blank") else (tag,)
                self.tree.insert("", "end", iid=s["id"],
                               values=("", s["project"], s["date_str"], s["title"],
                                       s["size_str"], s["age_str"]),
                               tags=tags)
        else:
            groups = defaultdict(list)
            for s in self.filtered_sessions:
                if group_mode == "Project":
                    key = s["project"]
                elif group_mode == "Tanggal":
                    key = s["date_date"]
                elif group_mode == "Bulan":
                    key = s["date_month"]
                elif group_mode == "Umur":
                    key = s["age_group"]
                else:
                    key = "Lainnya"
                groups[key].append(s)

            if group_mode == "Umur":
                order = ["Hari ini", "Kemarin", "Minggu ini", "Bulan ini",
                         "1-3 bulan lalu", "3-6 bulan lalu", "6-12 bulan lalu", "> 1 tahun lalu"]
                sorted_keys = [k for k in order if k in groups]
            elif group_mode in ("Tanggal", "Bulan"):
                sorted_keys = sorted(groups.keys(), reverse=True)
            else:
                sorted_keys = sorted(groups.keys())

            for gidx, key in enumerate(sorted_keys):
                items = groups[key]
                total = self.fmt_size(sum(s["size"] for s in items))
                gid = f"__group_{gidx}"

                self.tree.insert("", "end", iid=gid, text="",
                               values=("", f"{key}", f"{len(items)} session", "", total, ""),
                               tags=("group",), open=True)

                for s in items:
                    tag = f"proj_{hash(s['project'])}"
                    tags = (tag, "blank") if s.get("is_blank") else (tag,)
                    self.tree.insert(gid, "end", iid=s["id"],
                                   values=("", s["project"], s["date_str"], s["title"],
                                           s["size_str"], s["age_str"]),
                                   tags=tags)

        self.status_label.config(
            text=f"{len(self.filtered_sessions)} dari {len(self.all_sessions)} session")
        self._clear_preview()

    # ── Selection ──

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
        self.preview_title_label.config(text="Preview Session", fg=self.colors["accent"])
        self.preview_info_label.config(text="Pilih session untuk melihat preview")
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("end", "Klik session untuk melihat isi percakapan...", "meta")
        self.preview_text.config(state="disabled")

    def _show_multi_preview(self, sids):
        self.preview_title_label.config(text=f"{len(sids)} session dipilih", fg=self.colors["accent"])
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
            self.preview_text.tag_configure(tag_name, foreground=color, font=("Consolas", 9, "bold"))
            self.preview_text.insert("end", f"[{s['project']}] ", tag_name)
            self.preview_text.insert("end", f"{s['title']}\n", "content")
            self.preview_text.insert("end", f"  {s['date_str']}  |  {s['size_str']}  |  {s['age_str']}\n", "meta")
            if i < len(sids) - 1:
                self.preview_text.insert("end", "\n")
        if len(sids) > 15:
            self.preview_text.insert("end", f"\n... dan {len(sids) - 15} session lainnya\n", "meta")
        self.preview_text.config(state="disabled")

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
        self.preview_info_label.config(
            text=f"{s['project']}  |  {s['date_str']}  |  {s['size_str']}  |  {s['age_str']}")

        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")

        if s["source"] == "opencode":
            self._preview_opencode(s)
        else:
            self._preview_jsonl(s)

        self.preview_text.config(state="disabled")
        self.preview_text.yview_moveto(0)

    def _preview_opencode(self, s):
        try:
            base = self.SOURCES["opencode"]["dir"]
            msg_dir = os.path.join(base, "message", s["id"].replace("oc_", ""))
            part_dir = os.path.join(base, "part")

            if not os.path.isdir(msg_dir):
                self.preview_text.insert("end", "(tidak ada pesan)", "meta")
                return

            # Load messages sorted by creation time
            messages = []
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
                    # Load text parts
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
                        messages.append((created, role, content))
                except:
                    pass

            messages.sort(key=lambda x: x[0])
            msg_count = 0
            for _, role, content in messages:
                text = content[:400] + "..." if len(content) > 400 else content
                role_tag = "role_user" if role == "user" else "role_assistant"
                role_label = "USER" if role == "user" else "ASSISTANT"
                self.preview_text.insert("end", f"[{role_label}] ", role_tag)
                self.preview_text.insert("end", f"{text}\n", "content")
                self.preview_text.insert("end", "-" * 50 + "\n", "separator")
                msg_count += 1
                if msg_count >= 15:
                    self.preview_text.insert("end",
                        "\n... masih ada pesan lainnya dalam session ini\n", "meta")
                    break

            if msg_count == 0:
                self.preview_text.insert("end", "(tidak ada pesan user/assistant)", "meta")

        except Exception as e:
            self.preview_text.insert("end", f"Error: {e}", "meta")

    def _preview_jsonl(self, s):

        try:
            entries = []
            with open(s["filepath"], "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f):
                    if line_num >= 200:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except:
                        continue

            if not entries:
                self.preview_text.insert("end", "(file kosong atau tidak bisa dibaca)", "meta")
                return

            msg_count = 0
            for entry in entries:
                entry_type = entry.get("type", "")
                role = ""
                content = ""

                # Factory format: {type:"message", message:{role, content}}
                if entry_type == "message" and isinstance(entry.get("message"), dict):
                    msg = entry["message"]
                    role = msg.get("role", "")
                    content = self._extract_content_text(msg.get("content", ""))

                # Claude Code format: {type:"user"/"assistant", message:{role, content}}
                elif entry_type in ("user", "human", "assistant") and isinstance(entry.get("message"), dict):
                    msg = entry["message"]
                    role = msg.get("role", "") or entry_type
                    if role == "human":
                        role = "user"
                    content = self._extract_content_text(msg.get("content", ""))

                # Codex CLI format: {type:"event_msg", payload:{message}} or {type:"response_item", payload:{role, content}}
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

                # Generic format: {role, content} at root
                elif entry.get("role") and entry.get("content"):
                    role = entry["role"]
                    content = self._extract_content_text(entry["content"])

                else:
                    continue

                if not role or role == "system":
                    continue
                if not content.strip():
                    continue

                text = content.strip()
                # Strip system-reminder tags
                if text.startswith("<system-reminder>"):
                    end_tag = "</system-reminder>"
                    idx = text.find(end_tag)
                    if idx != -1:
                        text = text[idx + len(end_tag):].strip()
                if not text:
                    continue

                if len(text) > 400:
                    text = text[:400] + "..."

                role_tag = f"role_{role}" if role in ("user", "assistant") else "role_system"
                role_label = {"user": "USER", "assistant": "ASSISTANT"}.get(role, role.upper())

                self.preview_text.insert("end", f"[{role_label}] ", role_tag)
                self.preview_text.insert("end", f"{text}\n", "content")
                self.preview_text.insert("end", "-" * 50 + "\n", "separator")

                msg_count += 1
                if msg_count >= 15:
                    self.preview_text.insert("end",
                        f"\n... masih ada pesan lainnya dalam session ini\n", "meta")
                    break

            if msg_count == 0:
                self.preview_text.insert("end", "(tidak ada pesan user/assistant dalam file ini)", "meta")

        except Exception as e:
            self.preview_text.insert("end", f"Error membaca file: {e}", "meta")

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

    # ── Actions ──

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
            messagebox.showinfo("Info", f"Tidak ada session lebih dari {days} hari.")

    def select_blank(self):
        to_select = [s["id"] for s in self.filtered_sessions if s.get("is_blank")]
        if to_select:
            self.tree.selection_set(to_select)
            self.stat_selected.config(text=str(len(to_select)))
            total_size = sum(s["size"] for s in self.filtered_sessions if s.get("is_blank"))
            messagebox.showinfo("Session Kosong",
                f"Ditemukan {len(to_select)} session kosong/blank.\n"
                f"Ukuran total: {self.fmt_size(total_size)}\n\n"
                f"Kriteria: file 0 bytes, tidak ada pesan,\n"
                f"atau hanya 'New Session' tanpa percakapan.")
        else:
            messagebox.showinfo("Info", "Tidak ada session kosong/blank.")

    def delete_blank_sessions(self):
        blanks = [s for s in self.all_sessions if s.get("is_blank")]
        if not blanks:
            messagebox.showinfo("Info", "Tidak ada session kosong/blank.")
            return

        total_size = sum(s["size"] for s in blanks)
        src_label = self.SOURCES[self.current_source]["label"]
        msg = (f"Hapus {len(blanks)} session kosong ({src_label})?\n"
               f"Ukuran: {self.fmt_size(total_size)}\n\n"
               f"Kriteria:\n"
               f"  - File 0 bytes\n"
               f"  - Tidak ada pesan user/assistant\n"
               f"  - 'New Session' tanpa percakapan")

        if not messagebox.askyesno("Hapus Session Kosong", msg, icon="warning"):
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

        extra = f"\n+ {empty_dirs} folder kosong dihapus" if empty_dirs else ""
        messagebox.showinfo("Selesai",
                           f"{deleted} session kosong dihapus.\n"
                           f"Dibebaskan: {self.fmt_size(total_size)}{extra}")
        self.refresh()

    def refresh(self):
        self.load_all_sessions()

    def delete_selected(self):
        raw = self.tree.selection()
        selected = [s for s in raw if not s.startswith("__group_")]
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih session yang ingin dihapus.")
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
            preview += f"\n  ... dan {len(lines) - 10} lainnya"

        src_label = self.SOURCES[self.current_source]["label"]
        msg = (f"Hapus {len(selected)} session ({src_label})?\n"
               f"Ukuran: {self.fmt_size(total_size)}\n\n{preview}")

        if not messagebox.askyesno("Konfirmasi Hapus", msg, icon="warning"):
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

        messagebox.showinfo("Selesai",
                           f"{deleted} session dihapus.\n"
                           f"Dibebaskan: {self.fmt_size(total_size)}")

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
    app = SessionCleaner(root)
    root.mainloop()
