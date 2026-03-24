#!/usr/bin/env python3
"""Shows a popup with a journaling question and saves the response.
Syncs last popup time across devices via Supabase."""

import json
import os
import random
import requests
import customtkinter as ctk
from datetime import datetime, timezone

# ─── REPLACE THESE ────────────────────────────────────────────────
SUPABASE_URL = "https://opilhmterqutsdgdasjz.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9waWxobXRlcnF1dHNkZ2Rhc2p6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMzNjM4OTUsImV4cCI6MjA4ODkzOTg5NX0.yC2ajoHQyo3gCEDXgDenxOj5juwbbxFqK1R78s55JTI"
# ──────────────────────────────────────────────────────────────────

HOURS_BETWEEN_POPUPS = 2
JOURNAL_FILE = os.path.expanduser("~/journal/entries.json")

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
}

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


def get_last_popup_time():
    """Fetch the last popup timestamp from Supabase."""
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/activity_tracker?select=last_popup_shown&limit=1",
            headers=HEADERS,
        )
        data = res.json()
        if data:
            return datetime.fromisoformat(data[0]["last_popup_shown"])
    except Exception as e:
        print(f"Error fetching from Supabase: {e}")
    return None


def update_last_popup_time():
    """Update the last popup timestamp in Supabase to now."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        # Update the first (only) row
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/activity_tracker?id=gt.0",
            headers=HEADERS,
            json={"last_popup_shown": now},
        )
    except Exception as e:
        print(f"Error updating Supabase: {e}")


def should_show_popup():
    """Return True if 2+ hours have passed since the last popup on any device."""
    last = get_last_popup_time()
    if last is None:
        return True
    now = datetime.now(timezone.utc)
    # Make sure last is timezone-aware
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    hours_passed = (now - last).total_seconds() / 3600
    return hours_passed >= HOURS_BETWEEN_POPUPS


def load_entries():
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as f:
            return json.load(f)
    return []


def save_entry(question, answer):
    os.makedirs(os.path.dirname(JOURNAL_FILE), exist_ok=True)
    entries = load_entries()
    entries.append({
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
    })
    with open(JOURNAL_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def show_prompt():
    question = random.choice(QUESTIONS)

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title("")
    root.resizable(False, False)
    root.configure(fg_color="#fdf6ec")

    root.update_idletasks()

    window_width, window_height = 500, 340
    ptr_x = root.winfo_pointerx()
    ptr_y = root.winfo_pointery()
    x = ptr_x - window_width // 2
    y = ptr_y - window_height // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.lift()
    root.focus_force()
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))

    # Header
    header = ctk.CTkLabel(
        root,
        text="✦  a moment to ground",
        text_color="#b08a60",
        font=ctk.CTkFont(family="Georgia", size=12, slant="italic"),
    )
    header.pack(pady=(24, 6))

    # Question
    q_label = ctk.CTkLabel(
        root,
        text=question,
        text_color="#2e231a",
        font=ctk.CTkFont(family="Georgia", size=15, weight="bold"),
        wraplength=440,
        justify="center",
    )
    q_label.pack(padx=24, pady=(0, 14))

    # Text box
    answer_box = ctk.CTkTextbox(
        root,
        height=100,
        font=ctk.CTkFont(family="Helvetica", size=13),
        fg_color="#fff8f0",
        text_color="#2e231a",
        border_color="#e0ccb0",
        border_width=1,
        corner_radius=10,
        wrap="word",
    )
    answer_box.pack(padx=24, fill="x")
    answer_box.focus_set()

    def submit(event=None):
        answer = answer_box.get("1.0", "end").strip()
        if answer:
            save_entry(question, answer)
        update_last_popup_time()
        root.destroy()

    def skip():
        update_last_popup_time()  # still counts as seen, resets the 2hr timer
        root.destroy()

    # Buttons
    btn_frame = ctk.CTkFrame(root, fg_color="transparent")
    btn_frame.pack(pady=(14, 20))

    skip_btn = ctk.CTkButton(
        btn_frame,
        text="Skip",
        command=skip,
        fg_color="transparent",
        text_color="#b08a60",
        hover_color="#f0e6d6",
        border_width=0,
        font=ctk.CTkFont(family="Helvetica", size=13),
        width=80,
        height=34,
        corner_radius=8,
    )
    skip_btn.pack(side="left", padx=6)

    save_btn = ctk.CTkButton(
        btn_frame,
        text="Save  ↵",
        command=submit,
        fg_color="#c8855a",
        hover_color="#b0724a",
        text_color="white",
        font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
        width=100,
        height=34,
        corner_radius=8,
    )
    save_btn.pack(side="left", padx=6)

    root.bind("<Command-Return>", submit)
    root.bind("<Control-Return>", submit)

    root.mainloop()


if __name__ == "__main__":
    if should_show_popup():
        show_prompt()
    else:
        print("Not time yet — popup skipped.")