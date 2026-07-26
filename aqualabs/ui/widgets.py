import customtkinter as ctk
from aqualabs.ui.theme import COLORS

class ResultBanner(ctk.CTkFrame):
    """Reusable widget for displaying analysis results or errors."""
    def __init__(self, master, status="success", title="", details="", **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=8, **kwargs)
        
        color = COLORS["green"] if status == "success" else COLORS["red"]
        
        if title:
            ctk.CTkLabel(
                self, text=title, font=("Segoe UI", 18, "bold"), text_color=color
            ).pack(pady=(10, 5))
            
        if details:
            # Details might have multiple lines, so we split them or just display
            ctk.CTkLabel(
                self, text=details, font=("Segoe UI", 12), text_color=COLORS["text"], justify="center"
            ).pack(pady=(0, 10))
