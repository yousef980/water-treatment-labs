import tkinter as tk
import customtkinter as ctk
from aqualabs.ui.theme import COLORS
from aqualabs.modules.jar_test import JarTestModule
from aqualabs.modules.chlorination import ChlorinationModule
from aqualabs.modules.suspended_solids import SuspendedSolidsModule
from aqualabs.modules.iron_manganese import IronManganeseModule
from aqualabs.modules.nitrate_adsorption import NitrateAdsorptionModule
from aqualabs.modules.lime_soda import LimeSodaModule
from aqualabs.modules.gram_staining import GramStainingModule
from aqualabs.modules.surface_hygiene import SurfaceHygieneModule
from aqualabs.modules.water_quality import WaterQualityModule

class AquaLabsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AQUALABS v4.0 — Water Treatment Suite")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        self.configure(fg_color=COLORS["bg"])
        
        self.modules = {
            'JarTest': JarTestModule,
            'Chlorination': ChlorinationModule,
            'SuspendedSolids': SuspendedSolidsModule,
            'IronManganese': IronManganeseModule,
            'NitrateAdsorption': NitrateAdsorptionModule,
            'LimeSoda': LimeSodaModule,
            'GramStaining': GramStainingModule,
            'SurfaceHygiene': SurfaceHygieneModule,
            'WaterQuality': WaterQualityModule,
        }
        
        self.current_module = None
        self.current_frame = None
        self._build_layout()
        self.navigate('JarTest')
    
    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=COLORS["surface"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="AQUALABS", font=("Consolas", 24, "bold"), text_color=COLORS["text"]).pack(padx=20, pady=(30, 2), anchor="w")
        
        # Navigation buttons
        self._nav_btns = {}
        for key, module_class in self.modules.items():
            # Instantiate with None to get metadata
            m = module_class(None, None)
            metadata = m.get_metadata()
            btn = ctk.CTkButton(
                self.sidebar, 
                text=metadata['title'], 
                anchor="w", 
                fg_color="transparent", 
                text_color=COLORS["text"], 
                command=lambda k=key: self.navigate(k)
            )
            btn.pack(fill="x", padx=15, pady=5)
            self._nav_btns[key] = btn
        
        # Workspace
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def navigate(self, key):
        if self.current_frame:
            self.current_frame.destroy()
        
        module_class = self.modules[key]
        self.current_module = module_class(self.workspace, COLORS)
        
        self.current_frame = ctk.CTkFrame(self.workspace, fg_color="transparent")
        self.current_frame.pack(expand=True, fill="both")
        
        # Left: controls, Right: display
        ctrl = ctk.CTkFrame(self.current_frame, width=280, fg_color=COLORS["card"], corner_radius=20)
        ctrl.pack(side="left", fill="y", padx=(0, 20))
        
        disp = ctk.CTkFrame(self.current_frame, fg_color=COLORS["card"], corner_radius=20)
        disp.pack(side="left", expand=True, fill="both")
        
        self.current_module.build_controls(ctrl)
        self.current_module.render_result(disp)

def main():
    app = AquaLabsApp()
    app.mainloop()

if __name__ == "__main__":
    main()
