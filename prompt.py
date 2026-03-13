import customtkinter as ctk
from datetime import datetime
import random
import json
import os
import threading

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# ── Paths ────────────────────────────────────────────────────────────────────
CONFIG_FILE  = os.path.expanduser("~/journal/.reflect_config")
JOURNAL_FILE = os.path.expanduser("~/journal/entries.json")

# ── Colors (matching web app) ─────────────────────────────────────────────────
CREAM      = "#fdf6ec"
CARD_BG    = "#fff8f0"
TAN        = "#e8d5bb"
BROWN      = "#b08a60"
DARK       = "#2e231a"
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


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def get_supabase(config):
    """Authenticate and return (client, user_id) or (None, None) on failure."""
    url   = config.get("supabase_url")
    key   = config.get("supabase_key")
    email = config.get("email")
    pwd   = config.get("password")
    if not (url and key and email and pwd):
        return None, None
    try:
        client = create_client(url, key)
        res = client.auth.sign_in_with_password({"email": email, "password": pwd})
        return client, res.user.id if res.user else None
    except Exception as e:
        print(f"[reflect] supabase auth error: {e}")
        return None, None


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
        print(f"[reflect] supabase insert error: {e}")


def push_skip_to_supabase(client, user_id, now):
    try:
        client.table("activity_tracker").upsert(
            {"user_id": user_id, "last_popup_shown": now.isoformat()},
            on_conflict="user_id",
        ).execute()
    except Exception as e:
        print(f"[reflect] supabase skip error: {e}")


def show_prompt():
    question    = random.choice(QUESTIONS)
    prompted_at = datetime.now()
    first_key   = [None]

    # Auth in background so the window opens immediately
    sb = [None, None]  # [client, user_id]
    auth_thread = None
    if SUPABASE_AVAILABLE:
        def _auth():
            config = load_config()
            sb[0], sb[1] = get_supabase(config)
        auth_thread = threading.Thread(target=_auth, daemon=True)
        auth_thread.start()

    # ── Window setup ─────────────────────────────────────────────────────────
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

    # ── Card ─────────────────────────────────────────────────────────────────
    card = ctk.CTkFrame(root, fg_color=CARD_BG, corner_radius=20,
                        border_width=1, border_color=TAN)
    card.pack(fill="both", expand=True, padx=2, pady=2)

    # Header
    ctk.CTkLabel(
        card, text="✦  a moment to reflect",
        text_color=BROWN,
        font=ctk.CTkFont(family="Georgia", size=12),
        fg_color="transparent",
    ).pack(pady=(26, 0))

    # Question
    ctk.CTkLabel(
        card, text=question,
        text_color=DARK,
        font=ctk.CTkFont(family="Georgia", size=17, weight="bold"),
        wraplength=430, justify="center", fg_color="transparent",
    ).pack(pady=(12, 0), padx=28)

    # Textarea
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

    # ── Actions ───────────────────────────────────────────────────────────────
    def submit(event=None):
        answer = answer_box.get("1.0", "end").strip()
        if not answer:
            return
        submitted_at  = datetime.now()
        typing_secs   = (
            (submitted_at - first_key[0]).total_seconds()
            if first_key[0] else None
        )
        entry = {
            "timestamp":      submitted_at.isoformat(),
            "question":       question,
            "answer":         answer,
            "word_count":     len(answer.split()),
            "prompted_at":    prompted_at.isoformat(),
            "submitted_at":   submitted_at.isoformat(),
            "typing_seconds": round(typing_secs, 2) if typing_secs else None,
            "skipped":        False,
        }
        save_local(entry)
        # Wait for auth thread (max 5s) then push
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

    # ── Buttons ───────────────────────────────────────────────────────────────
    btn_row = ctk.CTkFrame(card, fg_color="transparent")
    btn_row.pack(pady=(14, 24))

    ctk.CTkButton(
        btn_row, text="Skip",
        fg_color="transparent", text_color=BROWN,
        hover_color=TAN, border_width=0,
        font=ctk.CTkFont(family="Helvetica Neue", size=13),
        width=80, height=36, command=skip,
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        btn_row, text="Save  ↵",
        fg_color=ACCENT, text_color="white",
        hover_color=ACCENT_HVR, border_width=0,
        font=ctk.CTkFont(family="Helvetica Neue", size=13, weight="bold"),
        width=110, height=36, command=submit,
    ).pack(side="left")

    root.mainloop()


if __name__ == "__main__":
    show_prompt()
