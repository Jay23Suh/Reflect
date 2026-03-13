#!/usr/bin/env python3
"""
reflect — desktop journaling popup
First run: shows setup/login screen + installs LaunchAgent
Subsequent runs: shows journal prompt
"""

import customtkinter as ctk
from datetime import datetime
import random
import json
import os
import sys
import subprocess
import threading

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# ── Config paths ──────────────────────────────────────────────────────────────
SUPABASE_URL  = "https://opilhmterqutsdgdasjz.supabase.co"
SUPABASE_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waWxobXRlcnF1dHNkZ2Rhc2p6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMzNjM4OTUsImV4cCI6MjA4ODkzOTg5NX0.yC2ajoHQyo3gCEDXgDenxOj5juwbbxFqK1R78s55JTI"

CONFIG_FILE  = os.path.expanduser("~/.reflect_config")
JOURNAL_FILE = os.path.expanduser("~/.reflect_entries.json")
PLIST_PATH   = os.path.expanduser("~/Library/LaunchAgents/com.reflect.prompt.plist")

# ── Colors (matching web app) ─────────────────────────────────────────────────
CREAM      = "#fdf6ec"
CARD_BG    = "#fff8f0"
TAN        = "#e8d5bb"
BROWN      = "#b08a60"
DARK       = "#2e231a"
MUTED      = "#9a8070"
ACCENT     = "#c8855a"
ACCENT_HVR = "#b0724a"

# ── Questions ─────────────────────────────────────────────────────────────────
QUESTIONS = [
    "What's something you're grateful for right now?",
    "What's one small win you had today?",
    "Who made you smile recently, and why?",
    "What's something you're looking forward to?",
    "What's a moment from today you want to remember?",
    "What's something kind you did or witnessed today?",
    "What gave you energy today?",
    "What's one thing you learned today?",
    "What made today different from yesterday?",
    "What's something beautiful you noticed today?",
    "What are you proud of yourself for?",
    "What's a challenge you handled well recently?",
    "Who are you thinking about fondly right now?",
    "What's a simple pleasure you enjoyed today?",
    "What's something you're excited about?",
    "What did you do today that felt meaningful?",
    "What's something that made you laugh lately?",
    "What's a goal you're making progress on?",
    "What's something you're looking forward to tomorrow?",
    "What's a strength you used today?",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(email, password):
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "supabase_url": SUPABASE_URL,
            "supabase_key": SUPABASE_KEY,
            "email": email,
            "password": password,
        }, f, indent=2)

def get_executable_path():
    """Return the path to use in the LaunchAgent — works for both .app and raw script."""
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller bundle
        return sys.executable
    else:
        # Running as plain Python script
        return f"{sys.executable} {os.path.abspath(__file__)}"

def install_launch_agent():
    exe = get_executable_path()
    if getattr(sys, 'frozen', False):
        program_args = f"""
  <array>
    <string>{exe}</string>
  </array>"""
    else:
        parts = exe.split(" ", 1)
        program_args = f"""
  <array>
    <string>{parts[0]}</string>
    <string>{parts[1]}</string>
  </array>"""

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.reflect.prompt</string>
  <key>ProgramArguments</key>{program_args}
  <key>StartInterval</key>
  <integer>7200</integer>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>{os.path.expanduser("~/.reflect.log")}</string>
  <key>StandardErrorPath</key>
  <string>{os.path.expanduser("~/.reflect.log")}</string>
</dict>
</plist>"""

    os.makedirs(os.path.dirname(PLIST_PATH), exist_ok=True)
    # Unload existing if present
    subprocess.run(["launchctl", "unload", PLIST_PATH],
                   capture_output=True)
    with open(PLIST_PATH, "w") as f:
        f.write(plist)
    subprocess.run(["launchctl", "load", PLIST_PATH],
                   capture_output=True)

def get_supabase(email, password):
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        return client, res.user.id if res.user else None, None
    except Exception as e:
        return None, None, str(e)

def signup_supabase(name, email, password):
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"name": name}},
        })
        if res.user:
            return client, res.user.id, None
        return None, None, "Sign up failed — check your email to confirm."
    except Exception as e:
        return None, None, str(e)

def load_entries():
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE) as f:
            return json.load(f)
    return []

def save_local(entry):
    entries = load_entries()
    entries.append(entry)
    with open(JOURNAL_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def push_to_supabase(client, user_id, question, answer, submitted_at):
    try:
        client.table("journal_entries").insert({
            "user_id": user_id,
            "question": question,
            "answer": answer,
        }).execute()
        client.table("activity_tracker").upsert(
            {"user_id": user_id, "last_popup_shown": submitted_at.isoformat()},
            on_conflict="user_id",
        ).execute()
    except Exception as e:
        print(f"[reflect] supabase error: {e}")

def push_skip_to_supabase(client, user_id, now):
    try:
        client.table("activity_tracker").upsert(
            {"user_id": user_id, "last_popup_shown": now.isoformat()},
            on_conflict="user_id",
        ).execute()
    except Exception as e:
        print(f"[reflect] supabase skip error: {e}")


# ── Setup window ──────────────────────────────────────────────────────────────

def show_setup():
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.title("reflect — setup")
    root.configure(fg_color=CREAM)
    root.resizable(False, False)

    W, H = 440, 520
    root.geometry(f"{W}x{H}")
    root.eval('tk::PlaceWindow . center')

    is_login = [False]  # start in sign-up mode

    card = ctk.CTkFrame(root, fg_color=CARD_BG, corner_radius=20,
                        border_width=1, border_color=TAN)
    card.pack(fill="both", expand=True, padx=16, pady=16)

    # Header
    ctk.CTkLabel(card, text="✦", text_color=BROWN,
                 font=ctk.CTkFont(family="Georgia", size=28),
                 fg_color="transparent").pack(pady=(32, 0))
    ctk.CTkLabel(card, text="reflect", text_color=DARK,
                 font=ctk.CTkFont(family="Georgia", size=26),
                 fg_color="transparent").pack(pady=(4, 0))
    ctk.CTkLabel(card, text="your daily journaling companion",
                 text_color=MUTED,
                 font=ctk.CTkFont(family="Georgia", size=13),
                 fg_color="transparent").pack(pady=(4, 24))

    # Form fields
    input_opts = dict(
        width=320, height=42,
        fg_color="#fffaf4", border_color=TAN, border_width=1,
        corner_radius=10,
        font=ctk.CTkFont(family="Helvetica Neue", size=13),
        text_color=DARK,
    )

    name_entry = ctk.CTkEntry(card, placeholder_text="your name", **input_opts)
    name_entry.pack(pady=(0, 10))

    email_entry = ctk.CTkEntry(card, placeholder_text="your email", **input_opts)
    email_entry.pack(pady=(0, 10))

    pass_entry = ctk.CTkEntry(card, placeholder_text="password", show="•", **input_opts)
    pass_entry.pack(pady=(0, 10))

    msg_label = ctk.CTkLabel(card, text="", text_color=ACCENT,
                             font=ctk.CTkFont(size=12),
                             fg_color="transparent", wraplength=300)
    msg_label.pack(pady=(0, 6))

    submit_btn = ctk.CTkButton(
        card, text="create account",
        fg_color=ACCENT, text_color="white", hover_color=ACCENT_HVR,
        font=ctk.CTkFont(family="Helvetica Neue", size=14, weight="bold"),
        width=320, height=44, corner_radius=10,
    )
    submit_btn.pack(pady=(0, 10))

    toggle_btn = ctk.CTkButton(
        card, text="already have an account? sign in",
        fg_color="transparent", text_color=BROWN,
        hover_color=TAN, border_width=0,
        font=ctk.CTkFont(family="Helvetica Neue", size=12),
        width=320, height=32,
    )
    toggle_btn.pack()

    def toggle():
        is_login[0] = not is_login[0]
        if is_login[0]:
            name_entry.pack_forget()
            submit_btn.configure(text="sign in")
            toggle_btn.configure(text="don't have an account? sign up")
        else:
            name_entry.pack(before=email_entry, pady=(0, 10))
            submit_btn.configure(text="create account")
            toggle_btn.configure(text="already have an account? sign in")

    toggle_btn.configure(command=toggle)

    def on_submit():
        name  = name_entry.get().strip()
        email = email_entry.get().strip()
        pwd   = pass_entry.get().strip()

        if not email or not pwd:
            msg_label.configure(text="please fill in all fields")
            return
        if not is_login[0] and not name:
            msg_label.configure(text="please enter your name")
            return

        submit_btn.configure(text="...", state="disabled")
        msg_label.configure(text="")

        def _do():
            if is_login[0]:
                client, uid, err = get_supabase(email, pwd)
            else:
                client, uid, err = signup_supabase(name, email, pwd)

            if err or not uid:
                root.after(0, lambda: [
                    msg_label.configure(text=err or "something went wrong"),
                    submit_btn.configure(
                        text="sign in" if is_login[0] else "create account",
                        state="normal"
                    )
                ])
                return

            save_config(email, pwd)
            install_launch_agent()

            root.after(0, lambda: show_success(root, card))

        threading.Thread(target=_do, daemon=True).start()

    submit_btn.configure(command=on_submit)
    pass_entry.bind("<Return>", lambda e: on_submit())

    root.mainloop()


def show_success(root, card):
    for w in card.winfo_children():
        w.destroy()

    ctk.CTkLabel(card, text="✦", text_color=ACCENT,
                 font=ctk.CTkFont(family="Georgia", size=36),
                 fg_color="transparent").pack(pady=(60, 0))
    ctk.CTkLabel(card, text="you're all set",
                 text_color=DARK,
                 font=ctk.CTkFont(family="Georgia", size=22),
                 fg_color="transparent").pack(pady=(12, 0))
    ctk.CTkLabel(card,
                 text="reflect will prompt you every 2 hours.\nyour first prompt is coming up.",
                 text_color=MUTED,
                 font=ctk.CTkFont(family="Georgia", size=13),
                 justify="center", fg_color="transparent").pack(pady=(10, 0))

    root.after(3000, root.destroy)


# ── Journal popup ─────────────────────────────────────────────────────────────

def show_prompt():
    question    = random.choice(QUESTIONS)
    prompted_at = datetime.now()
    first_key   = [None]

    # Auth in background
    sb = [None, None]
    auth_thread = None
    if SUPABASE_AVAILABLE:
        def _auth():
            config = load_config()
            email = config.get("email")
            pwd   = config.get("password")
            if email and pwd:
                client, uid, _ = get_supabase(email, pwd)
                sb[0], sb[1] = client, uid
        auth_thread = threading.Thread(target=_auth, daemon=True)
        auth_thread.start()

    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.title("")
    root.configure(fg_color=CREAM)
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    W, H = 520, 368
    px, py = root.winfo_pointerx(), root.winfo_pointery()
    root.geometry(f"{W}x{H}+{px - W // 2}+{py - H // 2}")
    root.lift()
    root.focus_force()

    card = ctk.CTkFrame(root, fg_color=CARD_BG, corner_radius=20,
                        border_width=1, border_color=TAN)
    card.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(card, text="✦  a moment to reflect",
                 text_color=BROWN,
                 font=ctk.CTkFont(family="Georgia", size=12),
                 fg_color="transparent").pack(pady=(26, 0))

    ctk.CTkLabel(card, text=question,
                 text_color=DARK,
                 font=ctk.CTkFont(family="Georgia", size=17, weight="bold"),
                 wraplength=430, justify="center",
                 fg_color="transparent").pack(pady=(12, 0), padx=28)

    answer_box = ctk.CTkTextbox(
        card, height=100, width=450,
        fg_color="#fffaf4", border_color=TAN, border_width=1,
        corner_radius=10,
        font=ctk.CTkFont(family="Helvetica Neue", size=13),
        text_color=DARK,
    )
    answer_box.pack(pady=(16, 0), padx=28)
    answer_box.focus_set()

    def on_key(_event=None):
        if first_key[0] is None:
            first_key[0] = datetime.now()
    answer_box.bind("<Key>", on_key)

    def submit(event=None):
        answer = answer_box.get("1.0", "end").strip()
        if not answer:
            return
        submitted_at = datetime.now()
        typing_secs  = (
            (submitted_at - first_key[0]).total_seconds()
            if first_key[0] else None
        )
        save_local({
            "timestamp":      submitted_at.isoformat(),
            "question":       question,
            "answer":         answer,
            "word_count":     len(answer.split()),
            "prompted_at":    prompted_at.isoformat(),
            "submitted_at":   submitted_at.isoformat(),
            "typing_seconds": round(typing_secs, 2) if typing_secs else None,
            "skipped":        False,
        })
        if auth_thread:
            auth_thread.join(timeout=5)
        if sb[0] and sb[1]:
            push_to_supabase(sb[0], sb[1], question, answer, submitted_at)
        root.destroy()

    def skip():
        now = datetime.now()
        save_local({
            "timestamp":   now.isoformat(),
            "question":    question,
            "skipped":     True,
            "prompted_at": prompted_at.isoformat(),
        })
        if auth_thread:
            auth_thread.join(timeout=5)
        if sb[0] and sb[1]:
            push_skip_to_supabase(sb[0], sb[1], now)
        root.destroy()

    answer_box.bind("<Command-Return>", submit)

    btn_row = ctk.CTkFrame(card, fg_color="transparent")
    btn_row.pack(pady=(14, 24))

    ctk.CTkButton(btn_row, text="Skip",
                  fg_color="transparent", text_color=BROWN,
                  hover_color=TAN, border_width=0,
                  font=ctk.CTkFont(family="Helvetica Neue", size=13),
                  width=80, height=36, command=skip).pack(side="left", padx=(0, 8))

    ctk.CTkButton(btn_row, text="Save  ↵",
                  fg_color=ACCENT, text_color="white",
                  hover_color=ACCENT_HVR, border_width=0,
                  font=ctk.CTkFont(family="Helvetica Neue", size=13, weight="bold"),
                  width=110, height=36, command=submit).pack(side="left")

    root.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE):
        show_setup()
    else:
        show_prompt()
