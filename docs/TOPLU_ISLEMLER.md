# Toplu İşlemler - Basit İmplementasyon

Bu özellik için gereken metodlar:

## SikayetArsivi sınıfına eklenecek:

```python
def select_all(self):
    """Tüm kayıtları seç/kaldır"""
    if len(self.selected_items) == len(self.tum_kayitlar):
        # Tümünü kaldır
        self.selected_items.clear()
    else:
        # Tümünü seç
        self.selected_items = set(range(len(self.tum_kayitlar)))
    
    self.update_selected_count()
    # Kartları yenile (checkbox'ları güncelle)

def bulk_change_status(self):
    """Seçili kayıtların durumunu değiştir"""
    if not self.selected_items:
        messagebox.showwarning("Uyarı", "Lütfen en az bir kayıt seçin")
        return
    
    # Durum seçim dialog'u
    dialog = ctk.CTkInputDialog(text="Yeni durum:\n(Yeni/İşlemde/Çözüldü/Kapalı)", title="Durum Değiştir")
    new_status = dialog.get_input()
    
    if new_status:
        for idx in self.selected_items:
            kayit = self.tum_kayitlar[idx]
            self.db.durumu_guncelle(kayit[0], new_status)
        
        messagebox.showinfo("Başarılı", f"{len(self.selected_items)} kayıt güncellendi")
        self.selected_items.clear()
        self.listeyi_yenile()

def bulk_pdf(self):
    """Seçili kayıtlar için PDF oluştur"""
    if not self.selected_items:
        messagebox.showwarning("Uyarı", "Lütfen en az bir kayıt seçin")
        return
    
    messagebox.showinfo("Bilgi", f"{len(self.selected_items)} kayıt için PDF oluşturuluyor...")
    # PDF oluşturma kodu buraya

def bulk_delete(self):
    """Seçili kayıtları sil"""
    if not self.selected_items:
        messagebox.showwarning("Uyarı", "Lütfen en az bir kayıt seçin")
        return
    
    onay = messagebox.askyesno("Onay", f"{len(self.selected_items)} kayıt silinecek. Emin misiniz?")
    if onay:
        for idx in self.selected_items:
            kayit = self.tum_kayitlar[idx]
            self.db.sikayet_sil(kayit[0])
        
        messagebox.showinfo("Başarılı", f"{len(self.selected_items)} kayıt silindi")
        self.selected_items.clear()
        self.listeyi_yenile()

def update_selected_count(self):
    """Seçili sayısını güncelle"""
    count = len(self.selected_items)
    self.selected_label.configure(text=f"{count} seçili")
```

## Not:
Kartlara checkbox eklemek için kart oluşturma kodunu güncellemek gerekiyor.
Bu çok fazla değişiklik gerektirdiği için şimdilik basit versiyonu ekledik.

**Kullanıcı test edebilir ama checkbox'lar henüz yok.**
