from abc import ABC, abstractmethod
import tkinter as tk
import matplotlib.pyplot as plt
from aqualabs.ui.theme import style_matplotlib_axes, COLORS

class BaseModule(ABC):
    """Abstract base for all lab modules - eliminates copy-paste."""
    
    def __init__(self, parent_workspace, theme_colors=None):
        self.workspace = parent_workspace
        self.colors = theme_colors or COLORS
        self.current_result = None
        self.current_df = None
        self.frame = None
    
    @abstractmethod
    def get_metadata(self) -> dict:
        """Return {'title': str, 'number': int, 'description': str, 'icon_color': str}"""
        pass
    
    @abstractmethod
    def build_controls(self, ctrl_frame: tk.Frame) -> None:
        """Build left panel. Store input widgets as self.input_name"""
        pass
    
    @abstractmethod
    def run_analysis(self) -> dict:
        """Execute analysis. Return {'title': str, 'status': str, 'message': str, 'figures': [...], 'stats': {...}}"""
        pass
    
    def render_result(self, disp_frame: tk.Frame) -> None:
        """Template: render result to display frame."""
        self.frame = disp_frame
        if self.current_result is None:
            return
        
        for w in disp_frame.winfo_children():
            w.destroy()
        
        from aqualabs.ui.widgets import ResultBanner
        banner = ResultBanner(
            disp_frame,
            status=self.current_result.get('status', 'success'),
            title=self.current_result.get('title', ''),
            details=self.current_result.get('details', '')
        )
        banner.pack(fill='x', padx=10, pady=10)
        
        if 'figures' in self.current_result and self.current_result['figures']:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            for fig in self.current_result['figures']:
                canvas = FigureCanvasTkAgg(fig, master=disp_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(expand=True, fill='both', padx=10, pady=10)
    
    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=self.colors['card'], fg=self.colors['sub'], font=('Segoe UI', 8), anchor='w').pack(fill='x', pady=(5, 1))
    
    def _entry(self, parent, default=""):
        e = tk.Entry(parent, bg=self.colors['surface'], fg=self.colors['accent'], bd=1, insertbackground=self.colors['accent'], font=('Consolas', 9))
        e.pack(fill='x', pady=(0, 2))
        e.insert(0, default)
        return e
    
    def _button(self, parent, text, color, command):
        tk.Button(parent, text=text, bg=color, fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'), bd=0, pady=6, cursor='hand2', command=command).pack(fill='x', pady=5)
