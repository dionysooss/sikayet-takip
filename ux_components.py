"""
Gelişmiş Kullanıcı Deneyimi Bileşenleri
Modern ve kullanıcı dostu UI widget'ları
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import re
from datetime import datetime


class TarihSecici(ctk.CTkFrame):
    """Modern tarih seçici widget"""
    
    def __init__(self, parent, etiket="Tarih", **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        # Etiket
        ctk.CTkLabel(
            self, 
            text=etiket, 
            font=ctk.CTkFont(size=12, weight="bold"), 
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        # Tarih seçici container
        date_container = ctk.CTkFrame(self, fg_color=("#F9FAFB", "#374151"), corner_radius=8)
        date_container.pack(fill="x")
        
        # DateEntry widget
        self.date_entry = DateEntry(
            date_container,
            width=25,
            background='#3498db',
            foreground='white',
            borderwidth=0,
            date_pattern='dd.mm.yyyy',
            font=('Arial', 12),
            **kwargs
        )
        self.date_entry.pack(padx=10, pady=8, fill="x")
        
    def get(self):
        """Tarihi dd.mm.yyyy formatında döndür"""
        return self.date_entry.get()
    
    def set_date(self, date_str):
        """Tarihi ayarla (dd.mm.yyyy veya yyyy-mm-dd formatında)"""
        try:
            if '-' in date_str:
                # yyyy-mm-dd formatı
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                # dd.mm.yyyy formatı
                date_obj = datetime.strptime(date_str, '%d.%m.%Y')
            
            self.date_entry.set_date(date_obj)
        except:
            pass


class TelefonGirisi(ctk.CTkFrame):
    """Otomatik formatlanan telefon girişi"""
    
    def __init__(self, parent, etiket="Telefon", **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        # Etiket
        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            label_frame, 
            text=etiket, 
            font=ctk.CTkFont(size=12, weight="bold"), 
            anchor="w"
        ).pack(side="left")
        
        # Durum ikonu
        self.status_label = ctk.CTkLabel(
            label_frame,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="e"
        )
        self.status_label.pack(side="right")
        
        # Entry
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="0555 123 45 67",
            height=35,
            **kwargs
        )
        self.entry.pack(fill="x")
        
        # Otomatik formatlama
        self.entry.bind('<KeyRelease>', self._formatla)
        self.entry.bind('<FocusOut>', self._validate)
        
    def _formatla(self, event=None):
        """Telefonu otomatik formatla"""
        # Sadece rakamları al
        text = ''.join(filter(str.isdigit, self.entry.get()))
        
        # Maksimum 11 hane
        if len(text) > 11:
            text = text[:11]
        
        # Formatla
        if len(text) >= 10:
            if text.startswith('0'):
                # 0555 123 45 67 formatı
                formatted = f"{text[:4]} {text[4:7]} {text[7:9]} {text[9:11]}"
            else:
                # 555 123 45 67 formatı
                formatted = f"{text[:3]} {text[3:6]} {text[6:8]} {text[8:10]}"
            
            # Entry'yi güncelle
            cursor_pos = self.entry.index(tk.INSERT)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, formatted.strip())
            
    def _validate(self, event=None):
        """Telefon numarasını doğrula"""
        text = ''.join(filter(str.isdigit, self.entry.get()))
        
        if not text:
            self.status_label.configure(text="", text_color="gray")
        elif len(text) >= 10:
            self.status_label.configure(text="✓", text_color="green")
        else:
            self.status_label.configure(text="❌ En az 10 hane", text_color="red")
    
    def get(self):
        """Telefon numarasını döndür"""
        return self.entry.get()
    
    def delete(self, start, end):
        """Entry'yi temizle"""
        self.entry.delete(start, end)
    
    def insert(self, index, text):
        """Entry'ye metin ekle"""
        self.entry.insert(index, text)
        self._formatla()


class TCKimlikGirisi(ctk.CTkFrame):
    """TC Kimlik numarası girişi ve validasyonu"""
    
    def __init__(self, parent, etiket="TC Kimlik No", **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        # Etiket
        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            label_frame, 
            text=etiket, 
            font=ctk.CTkFont(size=12, weight="bold"), 
            anchor="w"
        ).pack(side="left")
        
        # Durum ikonu
        self.status_label = ctk.CTkLabel(
            label_frame,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="e"
        )
        self.status_label.pack(side="right")
        
        # Entry
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="11 Haneli TC Kimlik",
            height=35,
            **kwargs
        )
        self.entry.pack(fill="x")
        
        # Sadece rakam girişi
        self.entry.bind('<KeyRelease>', self._validate)
        
    def _validate(self, event=None):
        """TC Kimlik numarasını doğrula"""
        tc = self.entry.get().strip()
        
        if not tc:
            self.status_label.configure(text="", text_color="gray")
            return
        
        # Sadece rakam kontrolü
        if not tc.isdigit():
            self.status_label.configure(text="❌ Sadece rakam", text_color="red")
            # Rakam olmayanları sil
            self.entry.delete(0, tk.END)
            self.entry.insert(0, ''.join(filter(str.isdigit, tc)))
            return
        
        # 11 hane kontrolü
        if len(tc) > 11:
            self.entry.delete(11, tk.END)
            tc = tc[:11]
        
        if len(tc) < 11:
            self.status_label.configure(text=f"❌ {11-len(tc)} hane eksik", text_color="orange")
            return
        
        # TC Kimlik algoritması
        if self._tc_kimlik_dogrula(tc):
            self.status_label.configure(text="✓ Geçerli", text_color="green")
        else:
            self.status_label.configure(text="❌ Geçersiz TC", text_color="red")
    
    def _tc_kimlik_dogrula(self, tc):
        """TC Kimlik numarası algoritması"""
        if len(tc) != 11 or not tc.isdigit():
            return False
        
        # İlk hane 0 olamaz
        if tc[0] == '0':
            return False
        
        # 10. hane kontrolü
        odd_sum = sum(int(tc[i]) for i in range(0, 9, 2))
        even_sum = sum(int(tc[i]) for i in range(1, 8, 2))
        if (odd_sum * 7 - even_sum) % 10 != int(tc[9]):
            return False
        
        # 11. hane kontrolü
        if sum(int(tc[i]) for i in range(10)) % 10 != int(tc[10]):
            return False
        
        return True
    
    def get(self):
        """TC Kimlik numarasını döndür"""
        return self.entry.get()
    
    def delete(self, start, end):
        """Entry'yi temizle"""
        self.entry.delete(start, end)
    
    def insert(self, index, text):
        """Entry'ye metin ekle"""
        self.entry.insert(index, text)
        self._validate()


class EmailGirisi(ctk.CTkFrame):
    """E-posta girişi ve validasyonu"""
    
    def __init__(self, parent, etiket="E-posta", **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        # Etiket
        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            label_frame, 
            text=etiket, 
            font=ctk.CTkFont(size=12, weight="bold"), 
            anchor="w"
        ).pack(side="left")
        
        # Durum ikonu
        self.status_label = ctk.CTkLabel(
            label_frame,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="e"
        )
        self.status_label.pack(side="right")
        
        # Entry
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="ornek@email.com",
            height=35,
            **kwargs
        )
        self.entry.pack(fill="x")
        
        # Validasyon
        self.entry.bind('<FocusOut>', self._validate)
        self.entry.bind('<KeyRelease>', self._validate)
        
    def _validate(self, event=None):
        """E-posta adresini doğrula"""
        email = self.entry.get().strip()
        
        if not email:
            self.status_label.configure(text="", text_color="gray")
            return
        
        # E-posta regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            self.status_label.configure(text="✓", text_color="green")
        else:
            self.status_label.configure(text="❌ Geçersiz", text_color="red")
    
    def get(self):
        """E-posta adresini döndür"""
        return self.entry.get()
    
    def delete(self, start, end):
        """Entry'yi temizle"""
        self.entry.delete(start, end)
    
    def insert(self, index, text):
        """Entry'ye metin ekle"""
        self.entry.insert(index, text)
        self._validate()


class LoadingSpinner(ctk.CTkFrame):
    """Yükleme animasyonu"""
    
    def __init__(self, parent, text="Yükleniyor..."):
        super().__init__(
            parent,
            fg_color=("white", "gray17"),
            corner_radius=15
        )
        
        # Spinner ikonu
        self.spinner_label = ctk.CTkLabel(
            self,
            text="⏳",
            font=ctk.CTkFont(size=48)
        )
        self.spinner_label.pack(pady=(30, 10))
        
        # Metin
        self.text_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=14)
        )
        self.text_label.pack(pady=(0, 30))
        
        # Animasyon
        self.is_animating = True
        self._animate()
    
    def _animate(self):
        """Spinner animasyonu"""
        if not self.is_animating:
            return
        
        current = self.spinner_label.cget("text")
        icons = ["⏳", "⌛"]
        next_icon = icons[(icons.index(current) + 1) % len(icons)]
        self.spinner_label.configure(text=next_icon)
        
        self.after(500, self._animate)
    
    def stop(self):
        """Animasyonu durdur"""
        self.is_animating = False
    
    def update_text(self, text):
        """Metin güncelle"""
        self.text_label.configure(text=text)


class Breadcrumb(ctk.CTkFrame):
    """Navigasyon breadcrumb"""
    
    def __init__(self, parent, path):
        """
        path: [{"text": "Ana Sayfa", "command": func}, ...]
        """
        super().__init__(parent, fg_color="transparent")
        
        for i, item in enumerate(path):
            # Ayırıcı
            if i > 0:
                ctk.CTkLabel(
                    self,
                    text="›",
                    font=ctk.CTkFont(size=14),
                    text_color=("gray50", "gray60")
                ).pack(side="left", padx=5)
            
            # Breadcrumb item
            is_last = (i == len(path) - 1)
            
            if is_last:
                # Son item - tıklanamaz
                ctk.CTkLabel(
                    self,
                    text=item["text"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#1a1a2e", "white")
                ).pack(side="left")
            else:
                # Tıklanabilir item
                btn = ctk.CTkButton(
                    self,
                    text=item["text"],
                    command=item.get("command"),
                    fg_color="transparent",
                    hover_color=("gray90", "gray30"),
                    text_color=("#3498db", "#5dade2"),
                    font=ctk.CTkFont(size=14),
                    width=0,
                    height=25
                )
                btn.pack(side="left")


class ProgressBar(ctk.CTkFrame):
    """İlerleme çubuğu"""
    
    def __init__(self, parent, max_value=100):
        super().__init__(parent, fg_color="transparent")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self,
            mode="determinate",
            height=20
        )
        self.progress.pack(fill="x", pady=(0, 5))
        self.progress.set(0)
        
        # Yüzde etiketi
        self.label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=12)
        )
        self.label.pack()
        
        self.max_value = max_value
    
    def set(self, value):
        """İlerlemeyi ayarla (0-max_value arası)"""
        percentage = value / self.max_value
        self.progress.set(percentage)
        self.label.configure(text=f"{int(percentage * 100)}%")
    
    def increment(self, amount=1):
        """İlerlemeyi artır"""
        current = self.progress.get() * self.max_value
        self.set(current + amount)


class EmptyState(ctk.CTkFrame):
    """Boş durum göstergesi"""
    
    def __init__(self, parent, icon="📭", title="Henüz veri yok", 
                 message="", action_text=None, action_command=None):
        super().__init__(parent, fg_color="transparent")
        
        # İkon
        ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=64)
        ).pack(pady=(50, 20))
        
        # Başlık
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 10))
        
        # Mesaj
        if message:
            ctk.CTkLabel(
                self,
                text=message,
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray60")
            ).pack(pady=(0, 20))
        
        # Aksiyon butonu
        if action_text and action_command:
            ctk.CTkButton(
                self,
                text=action_text,
                command=action_command,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=20)


if __name__ == "__main__":
    # Test
    app = ctk.CTk()
    app.geometry("600x800")
    
    frame = ctk.CTkScrollableFrame(app)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Tarih seçici
    tarih = TarihSecici(frame, "Sefer Tarihi")
    tarih.pack(fill="x", pady=10)
    
    # Telefon girişi
    telefon = TelefonGirisi(frame, "Telefon Numarası")
    telefon.pack(fill="x", pady=10)
    
    # TC Kimlik
    tc = TCKimlikGirisi(frame, "TC Kimlik No")
    tc.pack(fill="x", pady=10)
    
    # E-posta
    email = EmailGirisi(frame, "E-posta Adresi")
    email.pack(fill="x", pady=10)
    
    # Breadcrumb
    breadcrumb = Breadcrumb(frame, [
        {"text": "Ana Sayfa", "command": lambda: print("Ana Sayfa")},
        {"text": "Şikayetler", "command": lambda: print("Şikayetler")},
        {"text": "Detay"}
    ])
    breadcrumb.pack(fill="x", pady=20)
    
    # Progress bar
    progress = ProgressBar(frame, max_value=100)
    progress.pack(fill="x", pady=10)
    progress.set(45)
    
    # Empty state
    empty = EmptyState(
        frame,
        icon="📭",
        title="Henüz şikayet yok",
        message="Yeni şikayet eklemek için butona tıklayın",
        action_text="Yeni Şikayet Ekle",
        action_command=lambda: print("Yeni şikayet")
    )
    empty.pack(fill="both", expand=True, pady=20)
    
    app.mainloop()
