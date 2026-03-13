#!/usr/bin/env python3
"""Review today's (or all) journal entries in a scrollable window."""

import json
import os
import sys
import customtkinter as ctk
from datetime import datetime, date

JOURNAL_FILE = os.path.expanduser("~/journal/entries.json")


def load_entries(filter_date=None):
    if not os.path.exists(JOURNAL_FILE):
        return []
    with open(JOURNAL_FILE, "r") as f:
        entries = json.load(f)
    if filter_date:
        entries = [e for e in entries
                   if e["timestamp"].startswith(filter_date.isoformat())]
    return entries


def format_time(iso, all_entries=False):
    dt = datetime.fromisoformat(iso)
    if all_entries:
        return dt.strftime("%b %-d  ·  %-I:%M %p")
    return dt.strftime("%-I:%M %p")


def show_review(all_entries=False):
    if all_entries:
        entries = load_entries()
        title_suffix = "All Entries"
    else:
        entries = load_entries(filter_date=date.today())
        title_suffix = date.today().strftime("%B %d, %Y")

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title("")
    root.resizable(False, False)

    window_width, window_height = 560, 520
    ptr_x = root.winfo_pointerx()
    ptr_y = root.winfo_pointery()
    x = ptr_x - window_width // 2
    y = ptr_y - window_height // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(fg_color="#fdf6ec")
    root.lift()
    root.attributes("-topmost", True)
    root.after(500, lambda: root.attributes("-topmost", False))

    # Header
    header = ctk.CTkLabel(
        root,
        text="✦  a moment to reflect",
        text_color="#b08a60",
        font=ctk.CTkFont(family="Georgia", size=12, slant="italic"),
    )
    header.pack(pady=(24, 2))

    title_label = ctk.CTkLabel(
        root,
        text=title_suffix,
        text_color="#2e231a",
        font=ctk.CTkFont(family="Georgia", size=16, weight="bold"),
    )
    title_label.pack()

    count_label = ctk.CTkLabel(
        root,
        text=f"{len(entries)} entr{'y' if len(entries) == 1 else 'ies'}",
        text_color="#b08a60",
        font=ctk.CTkFont(family="Helvetica", size=11),
    )
    count_label.pack(pady=(2, 10))

    # Scrollable area
    scroll = ctk.CTkScrollableFrame(
        root,
        fg_color="#fdf6ec",
        scrollbar_button_color="#e0ccb0",
        scrollbar_button_hover_color="#c8a880",
        corner_radius=0,
    )
    scroll.pack(fill="both", expand=True, padx=20, pady=(0, 12))

    if not entries:
        empty = ctk.CTkLabel(
            scroll,
            text="No entries yet today.\nCheck back after your first prompt!",
            text_color="#b08a60",
            font=ctk.CTkFont(family="Georgia", size=13, slant="italic"),
            justify="center",
        )
        empty.pack(pady=60)
    else:
        for entry in reversed(entries):
            card = ctk.CTkFrame(
                scroll,
                fg_color="#fff8f0",
                border_color="#e0ccb0",
                border_width=1,
                corner_radius=10,
            )
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(
                card,
                text=format_time(entry["timestamp"], all_entries),
                text_color="#b08a60",
                font=ctk.CTkFont(family="Helvetica", size=10),
                anchor="w",
            ).pack(anchor="w", padx=14, pady=(10, 0))

            ctk.CTkLabel(
                card,
                text=entry["question"],
                text_color="#5a4030",
                font=ctk.CTkFont(family="Georgia", size=12, slant="italic"),
                wraplength=480,
                justify="left",
                anchor="w",
            ).pack(anchor="w", padx=14, pady=(2, 4))

            ctk.CTkLabel(
                card,
                text=entry["answer"],
                text_color="#2e231a",
                font=ctk.CTkFont(family="Baskerville", size=13),
                wraplength=480,
                justify="left",
                anchor="w",
            ).pack(anchor="w", padx=14, pady=(0, 12))

    # Buttons
    btn_text = "View All Entries" if not all_entries else "View Today Only"

    def toggle():
        root.destroy()
        show_review(all_entries=not all_entries)

    btn_frame = ctk.CTkFrame(root, fg_color="transparent")
    btn_frame.pack(pady=(0, 20))

    ctk.CTkButton(
        btn_frame,
        text=btn_text,
        command=toggle,
        fg_color="#c8855a",
        hover_color="#b0724a",
        text_color="white",
        font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
        width=140,
        height=34,
        corner_radius=8,
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        btn_frame,
        text="Close",
        command=root.destroy,
        fg_color="transparent",
        text_color="#b08a60",
        hover_color="#f0e6d6",
        border_width=0,
        font=ctk.CTkFont(family="Helvetica", size=13),
        width=80,
        height=34,
        corner_radius=8,
    ).pack(side="left", padx=6)

    root.mainloop()


if __name__ == "__main__":
    all_flag = "--all" in sys.argv
    show_review(all_entries=all_flag)
