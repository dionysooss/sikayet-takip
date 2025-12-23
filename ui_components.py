import customtkinter as ctk
import tkinter as tk
from animation_utils import AnimationController, interpolate_color

class PremiumButton(ctk.CTkButton):
    """
    Hover ve Click efektlerine sahip Premium Buton.
    PERFORMANS OPTİMİZASYONU: Renk geçiş animasyonu kaldırıldı
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.default_color = kwargs.get("fg_color", "#3B8ED0")
        if self.default_color == "transparent":
            self.hover_color = kwargs.get("hover_color", "#E5E5E5")
            self.default_color = "transparent"
        else:
            self.hover_color = kwargs.get("hover_color", self.default_color)
            
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.is_hovering = False

    def on_enter(self, event):
        """Hover - Anlık renk değişimi (animasyon yok)"""
        self.is_hovering = True
        if self.default_color != "transparent":
            self.configure(fg_color=self.hover_color)

    def on_leave(self, event):
        """Hover bitti - Anlık renk değişimi"""
        self.is_hovering = False
        if self.default_color != "transparent":
            self.configure(fg_color=self.default_color)

    def on_click(self, event):
        """Tıklama efekti"""
        self.configure(border_width=2, border_color="white")

    def on_release(self, event):
        """Tıklama bitti"""
        self.configure(border_width=0)


class ToastNotification(ctk.CTkToplevel):
    """
    Ekranın altında veya üstünde beliren, kendini otomatik kapatan bildirim.
    """
    def __init__(self, master, title, message, icon="✅", color="#27ae60"):
        super().__init__(master)
        
        self.overrideredirect(True) # Pencere kenarlarını kaldır
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0) # Başlangıçta görünmez
        
        # Tasarım
        self.configure(fg_color=color)
        self.geometry("300x80")
        
        # İçerik
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(self.frame, text=icon, font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        
        msg_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        msg_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(msg_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="white", anchor="w").pack(fill="x")
        ctk.CTkLabel(msg_frame, text=message, font=ctk.CTkFont(size=12), text_color="white", anchor="w").pack(fill="x")
        
        # Pozisyonlama (Sağ Alt Köşe)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - 320
        y = screen_height - 150
        self.geometry(f"+{x}+{y}")
        
        # Giriş Animasyonu
        self.animate_in()
        
    def animate_in(self):
        """Fade in ve hafif yukarı kayma"""
        def step(alpha, y_offset):
            if alpha >= 0.95:
                # Bekle ve sonra kapat
                self.after(3000, self.animate_out)
                return
            
            new_alpha = alpha + 0.05
            self.attributes("-alpha", new_alpha)
            
            # Hafif yukarı kay
            current_y = int(self.geometry().split('+')[2])
            self.geometry(f"+{self.geometry().split('+')[1]}+{current_y - 1}")
            
            self.after(20, lambda: step(new_alpha, y_offset))
            
        step(0.0, 0)

    def animate_out(self):
        """Fade out"""
        def step(alpha):
            if alpha <= 0.05:
                self.destroy()
                return
            
            self.attributes("-alpha", alpha - 0.05)
            self.after(20, lambda: step(alpha - 0.05))
            
        step(0.95)


class SkeletonCard(ctk.CTkFrame):
    """
    Yükleniyor efekti veren boş kart (Skeleton Loading).
    PERFORMANS OPTİMİZASYONU: Animasyon kaldırıldı (CPU tasarrufu)
    """
    def __init__(self, master, width=280, height=150, **kwargs):
        super().__init__(master, width=width, height=height, fg_color=("gray90", "gray25"), **kwargs)
        self.pack_propagate(False)
        
        # Statik skeleton parçaları (animasyon yok!)
        # Başlık barı
        b1 = ctk.CTkFrame(self, height=20, width=150, fg_color=("gray80", "gray35"), corner_radius=5)
        b1.place(x=15, y=15)
        
        # Alt satırlar
        b2 = ctk.CTkFrame(self, height=15, width=200, fg_color=("gray85", "gray40"), corner_radius=5)
        b2.place(x=15, y=50)
        
        b3 = ctk.CTkFrame(self, height=15, width=180, fg_color=("gray85", "gray40"), corner_radius=5)
        b3.place(x=15, y=75)
        
        # Animasyon kaldırıldı - statik gösterge
