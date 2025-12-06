import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import subprocess
import platform

# İşletim sistemi belirleme
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

def dosya_ac(dosya_yolu):
    """Platform bağımsız dosya açma fonksiyonu"""
    try:
        if IS_WINDOWS:
            os.startfile(dosya_yolu)
        elif IS_MAC:
            subprocess.run(["open", dosya_yolu], check=True)
        elif IS_LINUX:
            subprocess.run(["xdg-open", dosya_yolu], check=True)
    except Exception as e:
        print(f"Dosya açılırken hata: {e}")

# Messagebox'ı her zaman en üstte göster
def show_message(msg_type, title, message, parent=None):
    """Messagebox'ı her zaman görünür şekilde göster"""
    if parent:
        try:
            parent.lift()
            parent.focus_force()
        except:
            pass
    
    if msg_type == "info":
        return messagebox.showinfo(title, message, parent=parent)
    elif msg_type == "warning":
        return messagebox.showwarning(title, message, parent=parent)
    elif msg_type == "error":
        return messagebox.showerror(title, message, parent=parent)
    elif msg_type == "yesno":
        return messagebox.askyesno(title, message, parent=parent)
from veritabani_hybrid import VeritabaniYonetici
from PIL import Image, ImageTk
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

# Modern arayüz ayarları
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class YeniSikayetPenceresi(ctk.CTkFrame):
    def __init__(self, parent, db_yonetici, callback_yenile, duzenlenecek_kayit=None, controller=None):
        super().__init__(parent, fg_color=("white", "gray17"))
        self.parent = parent
        self.controller = controller
        self.db = db_yonetici
        self.callback_yenile = callback_yenile
        self.duzenlenecek_kayit = duzenlenecek_kayit
        
        # Üst başlık çubuğu
        baslik_text = f"✏️ Şikayet Düzenle - {duzenlenecek_kayit[1]}" if duzenlenecek_kayit else "➕ Yeni Şikayet Ekle"
        
        header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=("gray95", "gray25"))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkButton(header, text="← Geri", command=self.geri_don, 
                      width=80, height=35, corner_radius=8, fg_color="transparent", 
                      text_color=("#1a1a2e", "white"), hover_color=("gray90", "gray30"),
                      font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=12)
        
        ctk.CTkLabel(header, text=baslik_text, font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10, pady=15)
        
        # Ana Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        # --- YOLCU BİLGİLERİ ---
        self.baslik_olustur("Yolcu Bilgileri")
        
        self.entry_yolcu = self.form_alani_olustur("Ad Soyad *", "Örn: Ahmet Yılmaz")
        
        # Telefon ve E-posta yan yana
        row_iletisim = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_iletisim.pack(fill="x", pady=(0, 10))
        
        self.entry_telefon = self.form_alani_olustur("Telefon *", "0555 123 45 67", parent=row_iletisim, side="left", padding=(0, 5))
        self.entry_eposta = self.form_alani_olustur("E-posta", "ornek@email.com", parent=row_iletisim, side="right", padding=(5, 0))

        # --- SEFER BİLGİLERİ ---
        self.baslik_olustur("Sefer Bilgileri")
        
        # Güzergah ve Tarih yan yana
        row_sefer1 = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_sefer1.pack(fill="x", pady=(0, 10))
        self.entry_guzergah = self.form_alani_olustur("Güzergah *", "Örn: İstanbul - Ankara", parent=row_sefer1, side="left", padding=(0, 5))
        self.entry_tarih = self.form_alani_olustur("Sefer Tarihi *", "gg.aa.yyyy", parent=row_sefer1, side="right", padding=(5, 0))
        
        # Plaka ve PNR yan yana
        row_sefer2 = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        row_sefer2.pack(fill="x", pady=(0, 10))
        self.entry_plaka = self.form_alani_olustur("Otobüs Plakası", "Örn: 34 ABC 123", parent=row_sefer2, side="left", padding=(0, 5))
        self.entry_pnr = self.form_alani_olustur("PNR Numarası", "PNR No", parent=row_sefer2, side="right", padding=(5, 0))

        # Satın Alınan Yer (Şube/Platform)
        satin_alma_yerleri = [
            "Şube - Merkez Terminal",
            "Şube - Otogar",
            "Şube - Acente",
            "Online - Web Sitesi",
            "Online - Mobil Uygulama",
            "Online - obilet.com",
            "Online - enuygun.com",
            "Online - biletall.com",
            "Telefon - Çağrı Merkezi",
            "Diğer"
        ]
        self.combo_satin_alinan_yer = self.combo_alani_olustur("Bilet Satın Alınan Yer", satin_alma_yerleri)
        
        # Diğer seçeneği için manuel giriş kutusu (başlangıçta gizli)
        self.diger_satin_alinan_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.entry_diger_satin_alinan = ctk.CTkEntry(self.diger_satin_alinan_frame, placeholder_text="Satın alınan yeri yazınız...", height=35)
        self.entry_diger_satin_alinan.pack(fill="x")
        # Başlangıçta gizle
        self.diger_satin_alinan_frame.pack_forget()
        
        # Combo değişikliğini izle
        self.combo_satin_alinan_yer.configure(command=self.satin_alinan_degisti)

        # --- ŞİKAYET DETAYLARI ---
        self.baslik_olustur("Şikayet Detayları")
        
        sikayet_turleri = [
            "Personel Davranışı", 
            "Rötar / Sefer İptali", 
            "Bagaj Hasarı", 
            "Bagaj Karışıklığı", 
            "Hijyen ve Temizlik", 
            "İkram Hizmetleri", 
            "Abonelik ve Puan İşlemleri",
            "Hatalı Çekim ve İade",
            "Elektronik Bilet İşlemleri",
            "Diğer"
        ]
        
        self.combo_tur = self.combo_alani_olustur("Şikayet Türü *", sikayet_turleri)
        
        # Başvurulan Yer (Şikayetin yapıldığı platform)
        basvuru_yerleri = [
            "Şikayetvar",
            "CİMER",
            "BTK",
            "Tüketici Hakem Heyeti",
            "WhatsApp Hattı",
            "Sosyal Medya - Twitter/X",
            "Sosyal Medya - Instagram",
            "Sosyal Medya - Facebook",
            "Google Yorumları",
            "E-posta",
            "Çağrı Merkezi",
            "Şube/Terminal",
            "Diğer"
        ]
        self.combo_basvurulan_yer = self.combo_alani_olustur("Başvurulan Yer", basvuru_yerleri)
        
        # Diğer seçeneği için manuel giriş kutusu (başlangıçta gizli)
        self.diger_basvurulan_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.entry_diger_basvurulan = ctk.CTkEntry(self.diger_basvurulan_frame, placeholder_text="Başvurulan yeri yazınız...", height=35)
        self.entry_diger_basvurulan.pack(fill="x")
        # Başlangıçta gizle
        self.diger_basvurulan_frame.pack_forget()
        
        # Combo değişikliğini izle
        self.combo_basvurulan_yer.configure(command=self.basvurulan_degisti)
        
        # Bilet Ücreti
        self.entry_bilet_ucreti = self.form_alani_olustur("Bilet Ücreti (TL)", "Örn: 450")
        
        # Öncelik
        self.combo_oncelik = self.combo_alani_olustur("Öncelik *", ["Düşük", "Orta", "Yüksek", "Acil"])
        self.combo_oncelik.set("Orta")
        
        # Açıklama
        ctk.CTkLabel(self.scroll_frame, text="Şikayet Açıklaması *", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(5, 5))
        self.text_sikayet = ctk.CTkTextbox(self.scroll_frame, height=120, border_width=1, border_color="gray")
        self.text_sikayet.pack(fill="x", pady=(0, 20))
        
        # --- BUTONLAR ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20, side="bottom", padx=20)
        
        btn_text = "💾 Değişiklikleri Kaydet" if duzenlenecek_kayit else "💾 Şikayeti Kaydet"
        
        # Kaydet Butonu (Yeşil - Mavi kaldırıldı)
        ctk.CTkButton(btn_frame, text=btn_text, command=self.kaydet, height=45, 
                      font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2CC985", hover_color="#229C68").pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # İptal Butonu (Beyaz/Gri)
        ctk.CTkButton(btn_frame, text="İptal", command=self.geri_don, height=45, width=100,
                      font=ctk.CTkFont(size=14), fg_color="white", text_color="black", hover_color="#F3F4F6", border_width=1, border_color="#D1D5DB").pack(side="right")

        # Eğer düzenleme modundaysak verileri doldur
        if duzenlenecek_kayit:
            # Pencere tam yüklendikten sonra verileri doldur
            self.after(300, self.verileri_doldur)

    def verileri_doldur(self):
        try:
            k = self.duzenlenecek_kayit
            if not k:
                print("HATA: duzenlenecek_kayit boş!")
                return
            
            print(f"=== VERİLER DOLDURULUYOR ===")
            print(f"Yolcu: '{k[2]}', Tarih: '{k[3]}', Güzergah: '{k[4]}'")

            # Yolcu Adı - index 2
            if k[2]:
                self.entry_yolcu.delete(0, "end")
                self.entry_yolcu.insert(0, str(k[2]))
            
            # Seyahat Tarihi - index 3
            if k[3]:
                self.entry_tarih.delete(0, "end")
                self.entry_tarih.insert(0, str(k[3]))
            
            # Güzergah - index 4
            if k[4]:
                self.entry_guzergah.delete(0, "end")
                self.entry_guzergah.insert(0, str(k[4]))
            
            # PNR - index 5
            if k[5]:
                self.entry_pnr.delete(0, "end")
                self.entry_pnr.insert(0, str(k[5]))
            
            # Telefon - index 11
            if len(k) > 11 and k[11]:
                self.entry_telefon.delete(0, "end")
                self.entry_telefon.insert(0, str(k[11]))
            
            # Eposta - index 12
            if len(k) > 12 and k[12]:
                self.entry_eposta.delete(0, "end")
                self.entry_eposta.insert(0, str(k[12]))
            
            # Plaka - index 13
            if len(k) > 13 and k[13]:
                self.entry_plaka.delete(0, "end")
                self.entry_plaka.insert(0, str(k[13]))
            
            # Şikayet Türü - index 14
            if len(k) > 14 and k[14]:
                self.combo_tur.set(str(k[14]))
            
            # Öncelik - index 16
            if len(k) > 16 and k[16]:
                self.combo_oncelik.set(str(k[16]))
            
            # Satın Alınan Yer - index 17
            if len(k) > 17 and k[17]:
                satin_alinan = str(k[17])
                # Eğer "Diğer: ..." formatındaysa
                if satin_alinan.startswith("Diğer:"):
                    self.combo_satin_alinan_yer.set("Diğer")
                    self.diger_satin_alinan_frame.pack(fill="x", pady=(0, 10), after=self.combo_satin_alinan_yer.master)
                    diger_metin = satin_alinan.replace("Diğer:", "").strip()
                    self.entry_diger_satin_alinan.delete(0, "end")
                    self.entry_diger_satin_alinan.insert(0, diger_metin)
                else:
                    self.combo_satin_alinan_yer.set(satin_alinan)
            
            # Başvurulan Yer - index 18
            if len(k) > 18 and k[18]:
                basvurulan = str(k[18])
                # Eğer "Diğer: ..." formatındaysa
                if basvurulan.startswith("Diğer:"):
                    self.combo_basvurulan_yer.set("Diğer")
                    self.diger_basvurulan_frame.pack(fill="x", pady=(0, 10), after=self.combo_basvurulan_yer.master)
                    diger_metin = basvurulan.replace("Diğer:", "").strip()
                    self.entry_diger_basvurulan.delete(0, "end")
                    self.entry_diger_basvurulan.insert(0, diger_metin)
                else:
                    self.combo_basvurulan_yer.set(basvurulan)
            
            # Bilet Ücreti - index 19
            if len(k) > 19 and k[19]:
                self.entry_bilet_ucreti.delete(0, "end")
                self.entry_bilet_ucreti.insert(0, str(k[19]))
                
            # Şikayet Detayı - index 8
            if k[8]:
                self.text_sikayet.delete("1.0", "end")
                self.text_sikayet.insert("1.0", str(k[8]))
            
            print("=== VERİLER DOLDURULDU ===")
            
            # Focus'u ilk alana ver (placeholder'ı gizlemek için)
            self.entry_yolcu.focus_set()
            self.update()
                
        except Exception as e:
            print(f"!!! HATA: {e}")
            import traceback
            traceback.print_exc()

    def satin_alinan_degisti(self, secim):
        """Satın alınan yer 'Diğer' seçildiğinde manuel giriş kutusunu göster"""
        if secim == "Diğer":
            self.diger_satin_alinan_frame.pack(fill="x", pady=(0, 10), after=self.combo_satin_alinan_yer.master)
        else:
            self.diger_satin_alinan_frame.pack_forget()
            self.entry_diger_satin_alinan.delete(0, "end")

    def basvurulan_degisti(self, secim):
        """Başvurulan yer 'Diğer' seçildiğinde manuel giriş kutusunu göster"""
        if secim == "Diğer":
            self.diger_basvurulan_frame.pack(fill="x", pady=(0, 10), after=self.combo_basvurulan_yer.master)
        else:
            self.diger_basvurulan_frame.pack_forget()
            self.entry_diger_basvurulan.delete(0, "end")

    def baslik_olustur(self, metin):
        ctk.CTkLabel(self.scroll_frame, text=metin, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x", pady=(20, 10))

    def form_alani_olustur(self, etiket, placeholder, parent=None, side=None, padding=None):
        target_frame = parent if parent else self.scroll_frame
        
        container = ctk.CTkFrame(target_frame, fg_color="transparent")
        if side:
            container.pack(side=side, fill="x", expand=True, padx=padding)
        else:
            container.pack(fill="x", pady=(0, 10))
            
        ctk.CTkLabel(container, text=etiket, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 5))
        entry = ctk.CTkEntry(container, placeholder_text=placeholder, height=35)
        entry.pack(fill="x")
        return entry

    def combo_alani_olustur(self, etiket, degerler, parent=None, side=None, padding=None):
        target_frame = parent if parent else self.scroll_frame
        
        container = ctk.CTkFrame(target_frame, fg_color="transparent")
        if side:
            container.pack(side=side, fill="x", expand=True, padx=padding)
        else:
            container.pack(fill="x", pady=(0, 10))
            
        ctk.CTkLabel(container, text=etiket, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", pady=(0, 5))
        
        if "Seçiniz" not in degerler:
            degerler = ["Seçiniz"] + degerler

        # CTkOptionMenu kullan - her yerden tıklanabilir
        dd = ctk.CTkOptionMenu(
            container, 
            values=degerler, 
            height=45, 
            corner_radius=12,
            fg_color=("#F9FAFB", "#374151"),
            button_color=("#E5E7EB", "#4B5563"),
            button_hover_color=("#D1D5DB", "#6B7280"),
            dropdown_fg_color=("white", "#374151"),
            dropdown_hover_color=("#F3F4F6", "#4B5563"),
            text_color=("#111827", "#F9FAFB"),
            font=ctk.CTkFont(size=14, weight="bold"),
            dropdown_font=ctk.CTkFont(size=13),
            anchor="center"
        )
        dd.pack(fill="x")
        dd.set("Seçiniz")
        
        return dd

    def kaydet(self):
        yolcu = self.entry_yolcu.get().strip()
        telefon = self.entry_telefon.get().strip()
        eposta = self.entry_eposta.get().strip()
        guzergah = self.entry_guzergah.get().strip()
        tarih = self.entry_tarih.get().strip()
        plaka = self.entry_plaka.get().strip()
        pnr = self.entry_pnr.get().strip()
        tur = self.combo_tur.get()
        oncelik = self.combo_oncelik.get()
        detay = self.text_sikayet.get("1.0", tk.END).strip()
        satin_alinan_yer = self.combo_satin_alinan_yer.get()
        
        # Eğer "Diğer" seçildiyse manuel girişi kullan
        if satin_alinan_yer == "Diğer":
            diger_yer = self.entry_diger_satin_alinan.get().strip()
            if diger_yer:
                satin_alinan_yer = f"Diğer: {diger_yer}"
        
        if satin_alinan_yer == "Seçiniz":
            satin_alinan_yer = ""
        
        # Başvurulan yer
        basvurulan_yer = self.combo_basvurulan_yer.get()
        
        # Eğer "Diğer" seçildiyse manuel girişi kullan
        if basvurulan_yer == "Diğer":
            diger_basvuru = self.entry_diger_basvurulan.get().strip()
            if diger_basvuru:
                basvurulan_yer = f"Diğer: {diger_basvuru}"
        
        if basvurulan_yer == "Seçiniz":
            basvurulan_yer = ""
        
        # Bilet ücreti
        bilet_ucreti = self.entry_bilet_ucreti.get().strip()

        # Zorunlu alan kontrolü
        if not yolcu or not detay:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Eksik Bilgi", "Lütfen zorunlu alanları doldurunuz.", parent=self)
            return
        
        # Tarih formatı kontrolü (gg.aa.yyyy veya yyyy-mm-dd)
        if tarih:
            import re
            tarih_pattern1 = r'^\d{2}\.\d{2}\.\d{4}$'  # gg.aa.yyyy
            tarih_pattern2 = r'^\d{4}-\d{2}-\d{2}$'    # yyyy-mm-dd
            if not (re.match(tarih_pattern1, tarih) or re.match(tarih_pattern2, tarih)):
                self.lift()
                self.focus_force()
                messagebox.showwarning("Hatalı Tarih", "Tarih formatı hatalı!\nDoğru format: gg.aa.yyyy veya yyyy-mm-dd", parent=self)
                return
        
        # Telefon formatı kontrolü (en az 10 rakam)
        if telefon:
            telefon_temiz = ''.join(filter(str.isdigit, telefon))
            if len(telefon_temiz) < 10:
                self.lift()
                self.focus_force()
                messagebox.showwarning("Hatalı Telefon", "Telefon numarası en az 10 haneli olmalıdır.", parent=self)
                return
        
        # E-posta formatı kontrolü
        if eposta:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, eposta):
                self.lift()
                self.focus_force()
                messagebox.showwarning("Hatalı E-posta", "E-posta adresi geçersiz!", parent=self)
                return
        
        # Çift şikayet kontrolü (sadece yeni kayıtlarda)
        if not self.duzenlenecek_kayit and yolcu and tarih and guzergah:
            self.db.imlec.execute("""
                SELECT sikayet_no FROM sikayetler 
                WHERE yolcu_adi = ? AND seyahat_tarihi = ? AND guzergah = ?
            """, (yolcu, tarih, guzergah))
            benzer = self.db.imlec.fetchone()
            if benzer:
                self.lift()
                self.focus_force()
                devam = messagebox.askyesno(
                    "Benzer Şikayet Bulundu",
                    f"Bu yolcu için aynı tarih ve güzergahta başka bir şikayet mevcut:\n{benzer[0]}\n\nYine de kaydetmek istiyor musunuz?"
                )
                if not devam:
                    return

        # İletişim bilgisini birleştir (Eski yapı uyumluluğu için)
        iletisim = f"{telefon} / {eposta}"
        
        if self.duzenlenecek_kayit:
            # Güncelleme
            self.db.sikayet_guncelle(
                id=self.duzenlenecek_kayit[0],
                yolcu_adi=yolcu,
                seyahat_tarihi=tarih,
                guzergah=guzergah,
                pnr=pnr,
                iletisim=iletisim,
                platform="Uygulama",
                sikayet_detay=detay,
                telefon=telefon,
                eposta=eposta,
                plaka=plaka,
                sikayet_turu=tur,
                lokasyon="",
                oncelik=oncelik,
                satin_alinan_yer=satin_alinan_yer,
                basvurulan_yer=basvurulan_yer,
                bilet_ucreti=bilet_ucreti
            )
            mesaj = "Şikayet başarıyla güncellendi."
            
            # İşlem kaydı
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                self.db.islem_kaydet(
                    kullanici_id=self.controller.aktif_kullanici.get('id'),
                    kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                    islem_turu="ŞİKAYET GÜNCELLEME",
                    islem_detay=f"{yolcu} - {tur}",
                    ilgili_kayit_id=self.duzenlenecek_kayit[0],
                    ilgili_kayit_no=self.duzenlenecek_kayit[1]
                )
                # Şikayet işlemleri tablosuna da ekle
                self.db.sikayet_islemi_ekle(
                    sikayet_id=self.duzenlenecek_kayit[0],
                    kullanici_id=self.controller.aktif_kullanici.get('id'),
                    kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                    islem_turu="GÜNCELLEME",
                    aciklama=f"Şikayet bilgileri güncellendi"
                )
        else:
            # Yeni Kayıt
            self.db.sikayet_ekle(
                yolcu_adi=yolcu,
                seyahat_tarihi=tarih,
                guzergah=guzergah,
                pnr=pnr,
                iletisim=iletisim,
                platform="Uygulama", # Varsayılan
                sikayet_detay=detay,
                telefon=telefon,
                eposta=eposta,
                plaka=plaka,
                sikayet_turu=tur,
                lokasyon="",
                oncelik=oncelik,
                satin_alinan_yer=satin_alinan_yer,
                basvurulan_yer=basvurulan_yer,
                bilet_ucreti=bilet_ucreti
            )
            mesaj = "Şikayet başarıyla kaydedildi."
            
            # Son eklenen şikayet ID ve numarasını al
            self.db.imlec.execute("SELECT id, sikayet_no FROM sikayetler ORDER BY id DESC LIMIT 1")
            son_sikayet = self.db.imlec.fetchone()
            sikayet_id = son_sikayet[0] if son_sikayet else None
            sikayet_no = son_sikayet[1] if son_sikayet else ""
            
            # İşlem kaydı
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                self.db.islem_kaydet(
                    kullanici_id=self.controller.aktif_kullanici.get('id'),
                    kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                    islem_turu="YENİ ŞİKAYET",
                    islem_detay=f"{yolcu} - {tur}",
                    ilgili_kayit_no=sikayet_no
                )
                # Şikayet işlemleri tablosuna da ekle
                if sikayet_id:
                    self.db.sikayet_islemi_ekle(
                        sikayet_id=sikayet_id,
                        kullanici_id=self.controller.aktif_kullanici.get('id'),
                        kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                        islem_turu="OLUŞTURULDU",
                        aciklama=f"Şikayet kaydı oluşturuldu"
                    )
        
        self.callback_yenile()
        self.geri_don()
    
    def geri_don(self):
        """Şikayet arşivine geri dön"""
        if self.controller:
            self.controller.show_frame("SikayetArsivi")

class AnaEkran(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("white", "gray17"))
        self.controller = controller
        
        # Grid layout for centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top user bar
        self.grid_rowconfigure(1, weight=1)  # Center content
        self.grid_rowconfigure(2, weight=0)  # Bottom spacer (weight=0 olmalı)
        
        # --- ÜST KULLANICI BARI ---
        self.user_bar = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color=("gray90", "gray25"))
        self.user_bar.grid(row=0, column=0, sticky="ew")
        
        # Kullanıcı bilgisi (sol taraf)
        self.user_info_frame = ctk.CTkFrame(self.user_bar, fg_color="transparent")
        self.user_info_frame.pack(side="left", padx=20, pady=10)
        
        self.user_icon_label = ctk.CTkLabel(self.user_info_frame, text="👤", font=ctk.CTkFont(size=20))
        self.user_icon_label.pack(side="left", padx=(0, 5))
        
        self.user_name_label = ctk.CTkLabel(self.user_info_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.user_name_label.pack(side="left")
        
        self.user_role_label = ctk.CTkLabel(self.user_info_frame, text="", font=ctk.CTkFont(size=12), text_color=("gray50", "gray60"))
        self.user_role_label.pack(side="left", padx=(10, 0))
        
        # Oturum Kapat butonu (sağ taraf)
        self.logout_btn = ctk.CTkButton(
            self.user_bar, 
            text="🚪 Oturum Kapat", 
            command=controller.cikis_yap, 
            width=140, 
            height=32,
            fg_color="#FF4D4D", 
            hover_color="#CC0000",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.logout_btn.pack(side="right", padx=20, pady=10)
        
        # Tema değiştirme butonu (sağ taraf)
        self.tema_btn = ctk.CTkButton(
            self.user_bar,
            text="🌙",
            command=self.tema_degistir,
            width=35,
            height=32,
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            font=ctk.CTkFont(size=16)
        )
        self.tema_btn.pack(side="right", padx=(0, 10), pady=10)
        self.tema_guncelle()
        
        # Bağlantı durumu göstergesi (sağ taraf - logout butonunun yanı)
        self.baglanti_frame = ctk.CTkFrame(self.user_bar, fg_color="transparent")
        self.baglanti_frame.pack(side="right", padx=(0, 10), pady=10)
        
        self.baglanti_label = ctk.CTkLabel(
            self.baglanti_frame, 
            text="", 
            font=ctk.CTkFont(size=11)
        )
        self.baglanti_label.pack(side="left", padx=(0, 5))
        
        self.senkronize_btn = ctk.CTkButton(
            self.baglanti_frame,
            text="🔄",
            command=self.senkronize_et,
            width=30,
            height=28,
            fg_color=("#3498db", "#2980b9"),
            hover_color=("#2980b9", "#1a5276"),
            font=ctk.CTkFont(size=14)
        )
        self.senkronize_btn.pack(side="left")
        
        # Bağlantı durumunu güncelle
        self.after(1000, self.baglanti_durumu_guncelle)
        
        # --- ORTA PANEL ---
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=1, column=0)
        
        # Logo
        if os.path.exists("logo.png"):
            try:
                pil_image = Image.open("logo.png")
                aspect_ratio = pil_image.width / pil_image.height
                new_height = 150
                new_width = int(new_height * aspect_ratio)
                
                self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))
                ctk.CTkLabel(self.center_frame, text="", image=self.logo_image).pack(pady=20)
            except Exception as e:
                print(f"Logo error: {e}")

        ctk.CTkLabel(self.center_frame, text="ŞİKAYET TAKİP SİSTEMİ", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=10)
        
        # Buttons
        btn_font = ctk.CTkFont(size=16, weight="bold")
        
        ctk.CTkButton(self.center_frame, text="ŞİKAYET ARŞİVİ", command=lambda: controller.show_frame("SikayetArsivi"), width=300, height=50, font=btn_font).pack(pady=10)
        ctk.CTkButton(self.center_frame, text="YENİ ŞİKAYET EKLE", command=controller.yeni_sikayet_ac, width=300, height=50, font=btn_font, fg_color="#2CC985", hover_color="#229C68").pack(pady=10)
        ctk.CTkButton(self.center_frame, text="🗑️ ÇÖP KUTUSU", command=self.cop_kutusu_ac, width=300, height=50, font=btn_font, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=10)
        ctk.CTkButton(self.center_frame, text="AYARLAR", command=lambda: controller.show_frame("Ayarlar"), width=300, height=50, font=btn_font, fg_color="#1F6AA5", hover_color="#144870").pack(pady=10)
    
    def cop_kutusu_ac(self):
        """Çöp kutusu penceresini aç"""
        CopKutusuPenceresi(self.controller, self.controller.db)
        
    def baglanti_durumu_guncelle(self):
        """Bağlantı durumunu güncelle"""
        try:
            durum = self.controller.db.baglanti_durumu()
            if durum["online"]:
                if durum["bekleyen"] > 0:
                    self.baglanti_label.configure(text=f"☁️ Çevrimiçi ({durum['bekleyen']} bekliyor)", text_color="#f39c12")
                else:
                    self.baglanti_label.configure(text="☁️ Çevrimiçi", text_color="#27ae60")
            else:
                self.baglanti_label.configure(text=f"📴 Çevrimdışı ({durum['bekleyen']} bekliyor)", text_color="#e74c3c")
        except:
            self.baglanti_label.configure(text="❓ Bilinmiyor", text_color="#95a5a6")
        
        # Her 30 saniyede bir güncelle
        self.after(30000, self.baglanti_durumu_guncelle)
    
    def senkronize_et(self):
        """Manuel senkronizasyon"""
        try:
            self.senkronize_btn.configure(state="disabled", text="⏳")
            self.update()
            
            if self.controller.db.yeniden_baglan():
                show_message("info", "Senkronizasyon", "✅ Veriler başarıyla senkronize edildi!", self)
            else:
                show_message("warning", "Senkronizasyon", "📴 İnternet bağlantısı yok. Veriler yerel olarak kaydedildi.", self)
            
            self.baglanti_durumu_guncelle()
        except Exception as e:
            show_message("error", "Hata", f"Senkronizasyon hatası: {e}", self)
        finally:
            self.senkronize_btn.configure(state="normal", text="🔄")
    
    def tema_degistir(self):
        """Karanlık/Aydınlık mod geçişi"""
        mevcut_mod = ctk.get_appearance_mode()
        if mevcut_mod == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
        self.tema_guncelle()
    
    def tema_guncelle(self):
        """Tema butonunun ikonunu güncelle"""
        mevcut_mod = ctk.get_appearance_mode()
        if mevcut_mod == "Dark":
            self.tema_btn.configure(text="☀️")
        else:
            self.tema_btn.configure(text="🌙")
    
    def kullanici_bilgisi_guncelle(self, kullanici):
        """Kullanıcı bilgilerini güncelle"""
        if kullanici:
            ad_soyad = kullanici.get("ad_soyad", "") or kullanici.get("kullanici_adi", "")
            rol = kullanici.get("rol", "kullanici")
            rol_text = "Yönetici" if rol == "admin" else "Kullanıcı"
            
            self.user_name_label.configure(text=ad_soyad)
            self.user_role_label.configure(text=f"({rol_text})")


class SikayetDetayPenceresi(ctk.CTkFrame):
    """Şikayet detaylarını ve yapılan işlemleri gösteren frame"""
    def __init__(self, parent, db, kayit, controller=None):
        super().__init__(parent, fg_color=("white", "gray17"))
        self.parent = parent
        self.controller = controller
        self.db = db
        self.kayit = kayit
        self.kayit_id = kayit[0]
        
        # Üst başlık çubuğu
        header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=("gray95", "gray25"))
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkButton(header, text="← Geri", command=self.geri_don, 
                      width=80, height=35, corner_radius=8, fg_color="transparent", 
                      text_color=("#1a1a2e", "white"), hover_color=("gray90", "gray30"),
                      font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=12)
        
        ctk.CTkLabel(header, text=f"📋 Şikayet Detayı - {kayit[1]}", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10, pady=15)
        
        # Ana TabView
        self.tabview = ctk.CTkTabview(self, width=760, height=650)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sekme 1: Şikayet Bilgileri
        self.tab_bilgi = self.tabview.add("📋 Şikayet Bilgileri")
        self.bilgi_sekmesi_olustur()
        
        # Sekme 2: Yapılan İşlemler
        self.tab_islemler = self.tabview.add("📝 Yapılan İşlemler")
        self.islemler_sekmesi_olustur()
        
        # Sekme 3: Dosyalar/Ekler
        self.tab_dosyalar = self.tabview.add("📎 Dosyalar")
        self.dosyalar_sekmesi_olustur()
        
        # Sekme 4: Notlar
        self.tab_notlar = self.tabview.add("💬 Notlar")
        self.notlar_sekmesi_olustur()
        
        # Sekme 5: Etiketler
        self.tab_etiketler = self.tabview.add("🏷️ Etiketler")
        self.etiketler_sekmesi_olustur()
        
        # Sekme 6: Hatırlatıcılar
        self.tab_hatirlaticilar = self.tabview.add("🔔 Hatırlatıcılar")
        self.hatirlaticilar_sekmesi_olustur()
    
    def bilgi_sekmesi_olustur(self):
        """Şikayet bilgilerini gösteren sekme"""
        frame = ctk.CTkScrollableFrame(self.tab_bilgi, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        ctk.CTkLabel(frame, text=f"📋 {self.kayit[1]}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))
        
        # Bilgi kartı
        bilgi_frame = ctk.CTkFrame(frame, fg_color=("gray95", "gray25"), corner_radius=10)
        bilgi_frame.pack(fill="x", pady=(0, 15))
        
        bilgiler = [
            ("Şikayet No:", self.kayit[1]),
            ("Yolcu:", self.kayit[2]),
            ("Telefon:", self.kayit[11] if len(self.kayit) > 11 else "-"),
            ("E-posta:", self.kayit[12] if len(self.kayit) > 12 else "-"),
            ("Seyahat Tarihi:", self.kayit[3]),
            ("Güzergah:", self.kayit[4]),
            ("PNR:", self.kayit[5]),
            ("Plaka:", self.kayit[13] if len(self.kayit) > 13 else "-"),
            ("Platform:", self.kayit[7]),
            ("Kayıt Tarihi:", self.kayit[9]),
            ("Şikayet Türü:", self.kayit[14] if len(self.kayit) > 14 else "-"),
            ("Öncelik:", self.kayit[16] if len(self.kayit) > 16 else "-"),
            ("Satın Alınan Yer:", self.kayit[17] if len(self.kayit) > 17 else "-"),
            ("Başvurulan Yer:", self.kayit[18] if len(self.kayit) > 18 else "-"),
            ("Bilet Ücreti:", (str(self.kayit[19]) + " TL") if len(self.kayit) > 19 and self.kayit[19] else "-"),
            ("Durum:", self.kayit[10]),
        ]

        for baslik, deger in bilgiler:
            satir = ctk.CTkFrame(bilgi_frame, fg_color="transparent")
            satir.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(satir, text=baslik, font=ctk.CTkFont(weight="bold"), width=130, anchor="w").pack(side="left")
            
            # Kopyalanabilir Entry oluştur
            deger_str = str(deger or "-")
            
            # Durum için renkli gösterim
            if baslik == "Durum:":
                durum = deger_str if deger_str != "-" else "Yeni"
                if durum == "Çözüldü":
                    renk = "#27ae60"
                elif durum == "İşlemde":
                    renk = "#f39c12"
                else:
                    renk = "#e74c3c"
                entry = ctk.CTkEntry(satir, fg_color="transparent", border_width=0, text_color=renk, font=ctk.CTkFont(weight="bold"))
                entry.insert(0, durum)
                entry.configure(state="readonly")
                entry.pack(side="left", fill="x", expand=True)
            # Öncelik için renkli gösterim
            elif baslik == "Öncelik:":
                oncelik = deger_str
                if oncelik == "Acil":
                    renk = "#e74c3c"
                elif oncelik == "Yüksek":
                    renk = "#e67e22"
                elif oncelik == "Orta":
                    renk = "#f39c12"
                else:
                    renk = "#27ae60"
                entry = ctk.CTkEntry(satir, fg_color="transparent", border_width=0, text_color=renk, font=ctk.CTkFont(weight="bold"))
                entry.insert(0, oncelik)
                entry.configure(state="readonly")
                entry.pack(side="left", fill="x", expand=True)
            else:
                entry = ctk.CTkEntry(satir, fg_color="transparent", border_width=0)
                entry.insert(0, deger_str)
                entry.configure(state="readonly")
                entry.pack(side="left", fill="x", expand=True)

        # Şikayet Açıklaması
        ctk.CTkLabel(frame, text="Şikayet Açıklaması:", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(15, 5), anchor="w")
        
        text_area = ctk.CTkTextbox(frame, height=150, corner_radius=10)
        text_area.insert("1.0", self.kayit[8] or "")
        text_area.pack(fill="x", pady=(0, 10))
        # Metin seçilebilir ve kopyalanabilir olacak, ancak düzenlenemeyecek
        text_area.bind("<Key>", lambda e: "break" if e.keysym not in ["c", "C", "a", "A"] or not (e.state & 0x4) else None)
    
    def geri_don(self):
        """Şikayet arşivine geri dön"""
        if self.controller:
            self.controller.show_frame("SikayetArsivi")
    
    def islemler_sekmesi_olustur(self):
        """Yapılan işlemler sekmesi"""
        # Üst panel - İşlem ekleme
        ust_frame = ctk.CTkFrame(self.tab_islemler, fg_color=("gray95", "gray25"), corner_radius=10)
        ust_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ust_frame, text="Yeni İşlem Ekle", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        # İşlem türü seçimi
        tur_frame = ctk.CTkFrame(ust_frame, fg_color="transparent")
        tur_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(tur_frame, text="İşlem Türü:", width=100, anchor="w").pack(side="left")
        self.combo_islem_turu = ctk.CTkComboBox(
            tur_frame, 
            values=["Not Ekleme", "Telefon Görüşmesi", "E-posta Gönderildi", "Yolcu ile İletişim", 
                   "İlgili Birime İletildi", "Araştırma Yapıldı", "Çözüm Önerisi Sunuldu",
                   "Tazminat/İade İşlemi", "Özür Mektubu Gönderildi", "Diğer"],
            width=250,
            height=35,
            state="readonly"
        )
        self.combo_islem_turu.set("Not Ekleme")
        self.combo_islem_turu.pack(side="left", padx=10)
        
        # Açıklama
        ctk.CTkLabel(ust_frame, text="Açıklama:", anchor="w").pack(anchor="w", padx=15, pady=(10, 5))
        self.text_aciklama = ctk.CTkTextbox(ust_frame, height=80, corner_radius=8)
        self.text_aciklama.pack(fill="x", padx=15, pady=(0, 10))
        
        # Ekle butonu
        ctk.CTkButton(
            ust_frame, 
            text="➕ İşlem Ekle", 
            command=self.islem_ekle,
            fg_color="#2CC985", hover_color="#229C68",
            height=40, width=150
        ).pack(pady=(0, 15))
        
        # İşlem listesi başlığı
        ctk.CTkLabel(self.tab_islemler, text="Yapılan İşlemler Geçmişi:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(5, 5))
        
        # İşlem listesi frame
        self.islem_liste_frame = ctk.CTkScrollableFrame(self.tab_islemler, fg_color="transparent", height=280)
        self.islem_liste_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # İşlemleri yükle
        self.islemleri_listele()
    
    def islem_ekle(self):
        """Yeni işlem ekle"""
        islem_turu = self.combo_islem_turu.get()
        aciklama = self.text_aciklama.get("1.0", "end").strip()
        
        if not aciklama:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen bir açıklama girin.", parent=self)
            return
        
        # Kullanıcı bilgisi
        kullanici_id = None
        kullanici_adi = "Sistem"
        if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
            kullanici_id = self.controller.aktif_kullanici.get('id')
            kullanici_adi = self.controller.aktif_kullanici.get('kullanici_adi')
        
        # İşlemi kaydet
        self.db.sikayet_islemi_ekle(
            sikayet_id=self.kayit_id,
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            islem_turu=islem_turu,
            aciklama=aciklama
        )
        
        # Genel işlem geçmişine de kaydet
        sikayet_no = self.kayit[1]
        self.db.islem_kaydet(
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            islem_turu="ŞİKAYET İŞLEMİ",
            islem_detay=f"{islem_turu}: {aciklama[:50]}...",
            ilgili_kayit_id=self.kayit_id,
            ilgili_kayit_no=sikayet_no
        )
        
        # Formu temizle
        self.text_aciklama.delete("1.0", "end")
        self.combo_islem_turu.set("Not Ekleme")
        
        # Listeyi yenile
        self.islemleri_listele()
        
        self.lift()
        self.focus_force()
    
    def islem_sonrasi_pdf_olustur(self, islem_turu, aciklama, kullanici_adi):
        """İşlem sonrası A5 formatında PDF oluştur"""
        import os
        import datetime
        from tkinter import filedialog
        
        try:
            from reportlab.lib.pagesizes import A5
            from reportlab.pdfgen import canvas
            from reportlab.lib.colors import HexColor
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.utils import ImageReader
        except ImportError:
            messagebox.showerror("Hata", "PDF oluşturmak için reportlab kütüphanesi gerekli!", parent=self)
            return
        
        # Dosya kaydetme dialogu
        tarih_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        varsayilan_ad = f"Islem_{self.kayit[1]}_{tarih_str}.pdf"
        
        dosya_yolu = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Dosyası", "*.pdf")],
            initialfile=varsayilan_ad,
            title="İşlem Raporunu Kaydet"
        )
        
        if not dosya_yolu:
            return
        
        try:
            c = canvas.Canvas(dosya_yolu, pagesize=A5)
            width, height = A5
            
            # Renkler
            primary_color = HexColor("#0d1b2a")
            accent_color = HexColor("#1b4965")
            text_color = HexColor("#1b263b")
            light_gray = HexColor("#f8f9fa")
            border_color = HexColor("#dee2e6")
            white = HexColor("#ffffff")
            green_color = HexColor("#27ae60")
            
            # Font ayarları
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                pdfmetrics.registerFont(TTFont('ArialBold', 'arialbd.ttf'))
                font_name = 'Arial'
                bold_font = 'ArialBold'
            except:
                font_name = 'Helvetica'
                bold_font = 'Helvetica-Bold'
            
            # ===== HEADER =====
            c.setFillColor(white)
            c.rect(0, height - 70, width, 70, fill=True, stroke=False)
            
            c.setStrokeColor(border_color)
            c.setLineWidth(1)
            c.line(20, height - 72, width - 20, height - 72)
            
            # Logo
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            if os.path.exists(logo_path):
                try:
                    logo = ImageReader(logo_path)
                    c.drawImage(logo, 20, height - 58, width=80, height=45, preserveAspectRatio=True, mask='auto')
                except:
                    pass
            
            # Başlık
            c.setFillColor(text_color)
            c.setFont(bold_font, 16)
            c.drawRightString(width - 25, height - 30, "İŞLEM RAPORU")
            
            c.setFont(font_name, 9)
            c.setFillColor(HexColor("#6c757d"))
            c.drawRightString(width - 25, height - 45, f"Ref: {self.kayit[1]}")
            
            # ===== ŞİKAYET BİLGİLERİ =====
            y = height - 95
            
            c.setFillColor(accent_color)
            c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
            c.setFillColor(white)
            c.setFont(bold_font, 11)
            c.drawString(30, y + 3, "ŞİKAYET BİLGİLERİ")
            y -= 30
            
            c.setFillColor(light_gray)
            c.roundRect(20, y - 85, width - 40, 90, 5, fill=True, stroke=False)
            
            c.setFillColor(text_color)
            c.setFont(bold_font, 9)
            c.drawString(30, y - 5, "Şikayet No:")
            c.setFont(font_name, 9)
            c.drawString(100, y - 5, str(self.kayit[1] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(220, y - 5, "Kayıt Tarihi:")
            c.setFont(font_name, 9)
            c.drawString(290, y - 5, str(self.kayit[9] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 20, "Yolcu:")
            c.setFont(font_name, 9)
            c.drawString(100, y - 20, str(self.kayit[2] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(220, y - 20, "Güzergah:")
            c.setFont(font_name, 9)
            c.drawString(290, y - 20, str(self.kayit[4] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 35, "Telefon:")
            c.setFont(font_name, 9)
            telefon = str(self.kayit[11]) if len(self.kayit) > 11 and self.kayit[11] else "-"
            c.drawString(100, y - 35, telefon)
            
            c.setFont(bold_font, 9)
            c.drawString(220, y - 35, "PNR:")
            c.setFont(font_name, 9)
            c.drawString(290, y - 35, str(self.kayit[5] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 50, "Satın Alınan Yer:")
            c.setFont(font_name, 9)
            satin_alinan = str(self.kayit[17]) if len(self.kayit) > 17 and self.kayit[17] else "-"
            c.drawString(120, y - 50, satin_alinan)
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 65, "Başvurulan Yer:")
            c.setFont(font_name, 9)
            basvurulan = str(self.kayit[18]) if len(self.kayit) > 18 and self.kayit[18] else "-"
            c.drawString(120, y - 65, basvurulan)
            
            c.setFont(bold_font, 9)
            c.drawString(220, y - 50, "Bilet Ücreti:")
            c.setFont(font_name, 9)
            bilet_ucreti = str(self.kayit[19]) if len(self.kayit) > 19 and self.kayit[19] else "-"
            if bilet_ucreti and bilet_ucreti != "-":
                bilet_ucreti = f"{bilet_ucreti} TL"
            c.drawString(290, y - 50, bilet_ucreti)
            
            y -= 110
            
            # ===== YENİ EKLENEN İŞLEM =====
            c.setFillColor(green_color)
            c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
            c.setFillColor(white)
            c.setFont(bold_font, 11)
            c.drawString(30, y + 3, "YENİ EKLENEN İŞLEM")
            y -= 30
            
            c.setFillColor(light_gray)
            c.roundRect(20, y - 70, width - 40, 75, 5, fill=True, stroke=False)
            
            c.setFillColor(text_color)
            c.setFont(bold_font, 9)
            c.drawString(30, y - 5, "İşlem Türü:")
            c.setFont(font_name, 9)
            c.drawString(100, y - 5, islem_turu)
            
            c.setFont(bold_font, 9)
            c.drawString(220, y - 5, "Tarih:")
            c.setFont(font_name, 9)
            c.drawString(270, y - 5, datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 20, "İşlemi Yapan:")
            c.setFont(font_name, 9)
            c.drawString(110, y - 20, kullanici_adi)
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 35, "Açıklama:")
            c.setFont(font_name, 9)
            
            # Açıklamayı satırlara böl
            from reportlab.lib.utils import simpleSplit
            aciklama_satirlar = simpleSplit(aciklama, font_name, 9, width - 120)
            aciklama_kisaltilmis = aciklama_satirlar[0] if aciklama_satirlar else "-"
            if len(aciklama_satirlar) > 1:
                aciklama_kisaltilmis += "..."
            c.drawString(90, y - 35, aciklama_kisaltilmis)
            
            y -= 100
            
            # ===== TÜM İŞLEM GEÇMİŞİ =====
            # Şikayete ait tüm işlemleri getir
            tum_islemler = self.db.sikayet_islemlerini_getir(self.kayit_id)
            
            if tum_islemler and len(tum_islemler) > 0:
                c.setFillColor(HexColor("#8e44ad"))  # Mor renk
                c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
                c.setFillColor(white)
                c.setFont(bold_font, 11)
                c.drawString(30, y + 3, f"TÜM İŞLEM GEÇMİŞİ ({len(tum_islemler)} kayıt)")
                y -= 30
                
                # İşlem listesi
                for i, islem in enumerate(tum_islemler[:5]):  # Max 5 işlem göster
                    # id, tarih, kullanici_adi, islem_turu, aciklama
                    islem_tarih = islem[1] if len(islem) > 1 else "-"
                    islem_kullanici = islem[2] if len(islem) > 2 else "-"
                    islem_tur = islem[3] if len(islem) > 3 else "-"
                    islem_aciklama = islem[4] if len(islem) > 4 else "-"
                    
                    # Alternatif arka plan rengi
                    if i % 2 == 0:
                        c.setFillColor(light_gray)
                    else:
                        c.setFillColor(white)
                    c.roundRect(20, y - 28, width - 40, 30, 3, fill=True, stroke=False)
                    
                    c.setFillColor(text_color)
                    
                    # İşlem türü ikonu
                    ikon_map = {
                        "Not Ekleme": "📝",
                        "Telefon Görüşmesi": "📞",
                        "E-posta Gönderildi": "📧",
                        "Yolcu ile İletişim": "👤",
                        "İlgili Birime İletildi": "📤",
                        "Araştırma Yapıldı": "🔍",
                        "Çözüm Önerisi Sunuldu": "💡",
                        "Tazminat/İade İşlemi": "💰",
                        "Özür Mektubu Gönderildi": "✉️",
                        "Diğer": "📌"
                    }
                    
                    c.setFont(bold_font, 8)
                    c.drawString(25, y - 8, f"• {islem_tur}")
                    
                    c.setFont(font_name, 7)
                    c.setFillColor(HexColor("#6c757d"))
                    c.drawString(25, y - 18, f"  {islem_tarih} - {islem_kullanici}")
                    
                    # Açıklama (kısaltılmış)
                    c.setFillColor(text_color)
                    c.setFont(font_name, 7)
                    aciklama_kisalt = str(islem_aciklama)[:60] + "..." if len(str(islem_aciklama)) > 60 else str(islem_aciklama)
                    c.drawString(150, y - 13, aciklama_kisalt)
                    
                    y -= 32
                
                # Daha fazla işlem varsa not ekle
                if len(tum_islemler) > 5:
                    c.setFillColor(HexColor("#6c757d"))
                    c.setFont(font_name, 8)
                    c.drawString(30, y - 5, f"... ve {len(tum_islemler) - 5} işlem daha")
                    y -= 20
            
            # ===== FOOTER =====
            c.setStrokeColor(border_color)
            c.setLineWidth(0.5)
            c.line(20, 40, width - 20, 40)
            
            c.setFillColor(HexColor("#6c757d"))
            c.setFont(font_name, 7)
            c.drawString(20, 25, f"Bu belge {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} tarihinde oluşturulmuştur.")
            c.drawRightString(width - 20, 25, "İsperia Şikayet Takip Sistemi")
            
            c.save()
            
            # PDF'yi otomatik aç
            os.startfile(dosya_yolu)
            
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulamadı: {e}", parent=self)

    def islemleri_listele(self):
        """Şikayete ait işlemleri listele"""
        # Mevcut öğeleri temizle
        for widget in self.islem_liste_frame.winfo_children():
            widget.destroy()
        
        # İşlemleri getir
        islemler = self.db.sikayet_islemlerini_getir(self.kayit_id)
        
        if not islemler:
            ctk.CTkLabel(
                self.islem_liste_frame, 
                text="Henüz işlem kaydı bulunmamaktadır.", 
                text_color="gray",
                font=ctk.CTkFont(size=13)
            ).pack(pady=30)
            return
        
        # İşlem kartları
        for islem in islemler:
            # id, tarih, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum
            islem_id = islem[0]
            tarih = islem[1]
            kullanici = islem[2] or "Sistem"
            islem_turu = islem[3]
            aciklama = islem[4] or ""
            
            # İşlem kartı
            kart = ctk.CTkFrame(self.islem_liste_frame, fg_color=("white", "gray30"), corner_radius=10)
            kart.pack(fill="x", pady=5, padx=5)
            
            # Üst satır: Tarih ve işlem türü
            ust_satir = ctk.CTkFrame(kart, fg_color="transparent")
            ust_satir.pack(fill="x", padx=10, pady=(8, 2))
            
            # İşlem türü ikonu
            ikon_map = {
                "Not Ekleme": "📝",
                "Telefon Görüşmesi": "📞",
                "E-posta Gönderildi": "📧",
                "Yolcu ile İletişim": "👤",
                "İlgili Birime İletildi": "📤",
                "Araştırma Yapıldı": "🔍",
                "Çözüm Önerisi Sunuldu": "💡",
                "Tazminat/İade İşlemi": "💰",
                "Özür Mektubu Gönderildi": "✉️",
                "Diğer": "📌"
            }
            ikon = ikon_map.get(islem_turu, "📌")
            
            ctk.CTkLabel(ust_satir, text=f"{ikon} {islem_turu}", font=ctk.CTkFont(weight="bold", size=13)).pack(side="left")
            ctk.CTkLabel(ust_satir, text=tarih, font=ctk.CTkFont(size=11), text_color="gray").pack(side="right")
            
            # Orta satır: Açıklama
            if aciklama:
                ctk.CTkLabel(kart, text=aciklama, anchor="w", justify="left", wraplength=680).pack(fill="x", padx=10, pady=2)
            
            # Alt satır: Kullanıcı ve sil butonu
            alt_satir = ctk.CTkFrame(kart, fg_color="transparent")
            alt_satir.pack(fill="x", padx=10, pady=(2, 8))
            
            ctk.CTkLabel(alt_satir, text=f"👤 {kullanici}", font=ctk.CTkFont(size=11), text_color="gray").pack(side="left")
            
            # Sil butonu (sadece admin veya işlemi yapan kişi silebilir)
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                if self.controller.aktif_kullanici.get('rol') == 'admin' or self.controller.aktif_kullanici.get('kullanici_adi') == kullanici:
                    ctk.CTkButton(
                        alt_satir, 
                        text="🗑️", 
                        width=30, height=25,
                        fg_color="transparent", 
                        hover_color="#e74c3c",
                        text_color=("gray50", "gray60"),
                        command=lambda iid=islem_id: self.islem_sil(iid)
                    ).pack(side="right")
    
    def islem_sil(self, islem_id):
        """İşlemi sil"""
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", "Bu işlem kaydını silmek istediğinize emin misiniz?", parent=self)
        if onay:
            self.db.sikayet_islemini_sil(islem_id)
            self.islemleri_listele()
    
    # ============== DOSYALAR SEKMESİ ==============
    def dosyalar_sekmesi_olustur(self):
        """Dosya/Fotoğraf ekleme sekmesi"""
        # Üst panel - Dosya ekleme
        ust_frame = ctk.CTkFrame(self.tab_dosyalar, fg_color=("gray95", "gray25"), corner_radius=10)
        ust_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ust_frame, text="📎 Dosya/Fotoğraf Ekle", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 10))
        
        buton_frame = ctk.CTkFrame(ust_frame, fg_color="transparent")
        buton_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            buton_frame,
            text="📷 Fotoğraf Seç",
            command=lambda: self.dosya_sec("image"),
            fg_color="#3498db", hover_color="#2980b9",
            height=35, width=140
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            buton_frame,
            text="📄 Belge Seç",
            command=lambda: self.dosya_sec("document"),
            fg_color="#9b59b6", hover_color="#8e44ad",
            height=35, width=140
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            buton_frame,
            text="📁 Tüm Dosyalar",
            command=lambda: self.dosya_sec("all"),
            fg_color="#1abc9c", hover_color="#16a085",
            height=35, width=140
        ).pack(side="left")
        
        # Dosya listesi başlığı
        ctk.CTkLabel(self.tab_dosyalar, text="Ekli Dosyalar:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(5, 5))
        
        # Dosya listesi
        self.dosya_liste_frame = ctk.CTkScrollableFrame(self.tab_dosyalar, fg_color="transparent", height=300)
        self.dosya_liste_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Dosyaları yükle
        self.dosyalari_listele()
    
    def dosya_sec(self, tip):
        """Dosya seçme diyalogu"""
        from tkinter import filedialog
        
        if tip == "image":
            filetypes = [("Resim Dosyaları", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("Tüm Dosyalar", "*.*")]
        elif tip == "document":
            filetypes = [("Belgeler", "*.pdf *.doc *.docx *.xls *.xlsx *.txt"), ("Tüm Dosyalar", "*.*")]
        else:
            filetypes = [("Tüm Dosyalar", "*.*")]
        
        dosya_yolu = filedialog.askopenfilename(
            title="Dosya Seç",
            filetypes=filetypes
        )
        
        if dosya_yolu:
            self.dosya_yukle(dosya_yolu)
    
    def dosya_yukle(self, dosya_yolu):
        """Dosyayı kaydet"""
        import os
        import shutil
        
        dosya_adi = os.path.basename(dosya_yolu)
        dosya_boyutu = os.path.getsize(dosya_yolu)
        
        # Dosya tipi belirleme
        uzanti = os.path.splitext(dosya_adi)[1].lower()
        if uzanti in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            dosya_tipi = "image"
        elif uzanti in ['.pdf']:
            dosya_tipi = "pdf"
        elif uzanti in ['.doc', '.docx']:
            dosya_tipi = "word"
        elif uzanti in ['.xls', '.xlsx']:
            dosya_tipi = "excel"
        else:
            dosya_tipi = "other"
        
        # Dosyaları saklamak için klasör oluştur
        dosyalar_klasoru = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dosyalar", str(self.kayit_id))
        os.makedirs(dosyalar_klasoru, exist_ok=True)
        
        # Benzersiz dosya adı oluştur
        import time
        yeni_dosya_adi = f"{int(time.time())}_{dosya_adi}"
        hedef_yol = os.path.join(dosyalar_klasoru, yeni_dosya_adi)
        
        # Dosyayı kopyala
        try:
            shutil.copy2(dosya_yolu, hedef_yol)
        except Exception as e:
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", f"Dosya kopyalanamadı: {e}", parent=self)
            return
        
        # Kullanıcı bilgisi
        kullanici_id = None
        kullanici_adi = "Sistem"
        if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
            kullanici_id = self.controller.aktif_kullanici.get('id')
            kullanici_adi = self.controller.aktif_kullanici.get('kullanici_adi')
        
        # Veritabanına kaydet
        self.db.dosya_ekle(
            sikayet_id=self.kayit_id,
            dosya_adi=dosya_adi,
            dosya_yolu=hedef_yol,
            dosya_tipi=dosya_tipi,
            dosya_boyutu=dosya_boyutu,
            yukleyen_id=kullanici_id,
            yukleyen_adi=kullanici_adi
        )
        
        # Listeyi yenile
        self.dosyalari_listele()
    
    def dosyalari_listele(self):
        """Dosyaları listele"""
        for widget in self.dosya_liste_frame.winfo_children():
            widget.destroy()
        
        dosyalar = self.db.dosyalari_getir(self.kayit_id)
        
        if not dosyalar:
            ctk.CTkLabel(
                self.dosya_liste_frame,
                text="Henüz dosya eklenmemiş.",
                text_color="gray",
                font=ctk.CTkFont(size=13)
            ).pack(pady=30)
            return
        
        for dosya in dosyalar:
            # id, dosya_adi, dosya_yolu, dosya_tipi, dosya_boyutu, kullanici_adi, tarih
            dosya_id = dosya[0]
            dosya_adi = dosya[1]
            dosya_yolu = dosya[2]
            dosya_tipi = dosya[3]
            dosya_boyutu = dosya[4]
            kullanici = dosya[5] or "Sistem"
            tarih = dosya[6]
            
            # Dosya kartı
            kart = ctk.CTkFrame(self.dosya_liste_frame, fg_color=("white", "gray30"), corner_radius=10)
            kart.pack(fill="x", pady=5, padx=5)
            
            # İkon belirleme
            ikon_map = {
                "image": "🖼️",
                "pdf": "📕",
                "word": "📘",
                "excel": "📗",
                "other": "📄"
            }
            ikon = ikon_map.get(dosya_tipi, "📄")
            
            # Üst satır
            ust_satir = ctk.CTkFrame(kart, fg_color="transparent")
            ust_satir.pack(fill="x", padx=10, pady=(8, 2))
            
            ctk.CTkLabel(ust_satir, text=f"{ikon} {dosya_adi}", font=ctk.CTkFont(weight="bold", size=13)).pack(side="left")
            
            # Boyut formatlama
            if dosya_boyutu < 1024:
                boyut_str = f"{dosya_boyutu} B"
            elif dosya_boyutu < 1024 * 1024:
                boyut_str = f"{dosya_boyutu / 1024:.1f} KB"
            else:
                boyut_str = f"{dosya_boyutu / (1024 * 1024):.1f} MB"
            
            ctk.CTkLabel(ust_satir, text=boyut_str, font=ctk.CTkFont(size=11), text_color="gray").pack(side="right")
            
            # Alt satır
            alt_satir = ctk.CTkFrame(kart, fg_color="transparent")
            alt_satir.pack(fill="x", padx=10, pady=(2, 8))
            
            ctk.CTkLabel(alt_satir, text=f"👤 {kullanici} • {tarih}", font=ctk.CTkFont(size=11), text_color="gray").pack(side="left")
            
            # Butonlar
            ctk.CTkButton(
                alt_satir,
                text="📂 Aç",
                width=50, height=25,
                fg_color="#3498db", hover_color="#2980b9",
                command=lambda yol=dosya_yolu: self.dosya_ac(yol)
            ).pack(side="right", padx=2)
            
            ctk.CTkButton(
                alt_satir,
                text="🗑️",
                width=30, height=25,
                fg_color="transparent", hover_color="#e74c3c",
                text_color=("gray50", "gray60"),
                command=lambda did=dosya_id, yol=dosya_yolu: self.dosya_sil(did, yol)
            ).pack(side="right", padx=2)
    
    def dosya_ac(self, dosya_yolu):
        """Dosyayı aç"""
        import os
        import subprocess
        import sys
        
        if not os.path.exists(dosya_yolu):
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", "Dosya bulunamadı!", parent=self)
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(dosya_yolu)
            elif sys.platform == "darwin":
                subprocess.run(["open", dosya_yolu])
            else:
                subprocess.run(["xdg-open", dosya_yolu])
        except Exception as e:
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", f"Dosya açılamadı: {e}", parent=self)

    def dosya_sil(self, dosya_id, dosya_yolu):
        """Dosyayı sil"""
        import os
        
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", "Bu dosyayı silmek istediğinize emin misiniz?", parent=self)
        if onay:
            # Veritabanından sil
            self.db.dosya_sil(dosya_id)
            
            # Fiziksel dosyayı sil
            if os.path.exists(dosya_yolu):
                try:
                    os.remove(dosya_yolu)
                except:
                    pass
            
            self.dosyalari_listele()
    
    # ============== NOTLAR SEKMESİ ==============
    def notlar_sekmesi_olustur(self):
        """Not/Yorum ekleme sekmesi"""
        # Üst panel - Not ekleme
        ust_frame = ctk.CTkFrame(self.tab_notlar, fg_color=("gray95", "gray25"), corner_radius=10)
        ust_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ust_frame, text="💬 Yeni Not Ekle", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Not metin alanı
        self.text_not = ctk.CTkTextbox(ust_frame, height=80, corner_radius=8)
        self.text_not.pack(fill="x", padx=15, pady=(5, 10))
        
        # Ekle butonu
        ctk.CTkButton(
            ust_frame,
            text="➕ Not Ekle",
            command=self.not_ekle,
            fg_color="#2CC985", hover_color="#229C68",
            height=40, width=150
        ).pack(pady=(0, 15))
        
        # Not listesi başlığı
        ctk.CTkLabel(self.tab_notlar, text="Notlar:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(5, 5))
        
        # Not listesi
        self.not_liste_frame = ctk.CTkScrollableFrame(self.tab_notlar, fg_color="transparent", height=300)
        self.not_liste_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Notları yükle
        self.notlari_listele()
    
    def not_ekle(self):
        """Yeni not ekle"""
        not_metni = self.text_not.get("1.0", "end").strip()
        
        if not not_metni:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen bir not girin.", parent=self)
            return
        
        # Kullanıcı bilgisi
        kullanici_id = None
        kullanici_adi = "Sistem"
        if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
            kullanici_id = self.controller.aktif_kullanici.get('id')
            kullanici_adi = self.controller.aktif_kullanici.get('kullanici_adi')
        
        # Notu kaydet
        self.db.not_ekle(
            sikayet_id=self.kayit_id,
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            not_metni=not_metni
        )
        
        # Formu temizle
        self.text_not.delete("1.0", "end")
        
        # Listeyi yenile
        self.notlari_listele()
    
    def notlari_listele(self):
        """Notları listele"""
        for widget in self.not_liste_frame.winfo_children():
            widget.destroy()
        
        notlar = self.db.notlari_getir(self.kayit_id)
        
        if not notlar:
            ctk.CTkLabel(
                self.not_liste_frame,
                text="Henüz not eklenmemiş.",
                text_color="gray",
                font=ctk.CTkFont(size=13)
            ).pack(pady=30)
            return
        
        for not_kayit in notlar:
            # id, kullanici_adi, not_metni, tarih
            not_id = not_kayit[0]
            kullanici = not_kayit[1] or "Sistem"
            not_metni = not_kayit[2]
            tarih = not_kayit[3]
            
            # Not kartı
            kart = ctk.CTkFrame(self.not_liste_frame, fg_color=("white", "gray30"), corner_radius=10)
            kart.pack(fill="x", pady=5, padx=5)
            
            # Üst satır
            ust_satir = ctk.CTkFrame(kart, fg_color="transparent")
            ust_satir.pack(fill="x", padx=10, pady=(8, 2))
            
            ctk.CTkLabel(ust_satir, text=f"👤 {kullanici}", font=ctk.CTkFont(weight="bold", size=12)).pack(side="left")
            ctk.CTkLabel(ust_satir, text=tarih, font=ctk.CTkFont(size=11), text_color="gray").pack(side="right")
            
            # Not metni
            ctk.CTkLabel(kart, text=not_metni, anchor="w", justify="left", wraplength=680).pack(fill="x", padx=10, pady=5)
            
            # Alt satır - Sil butonu
            alt_satir = ctk.CTkFrame(kart, fg_color="transparent")
            alt_satir.pack(fill="x", padx=10, pady=(0, 8))
            
            # Sil butonu (sadece admin veya notu yazan silebilir)
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                if self.controller.aktif_kullanici.get('rol') == 'admin' or self.controller.aktif_kullanici.get('kullanici_adi') == kullanici:
                    ctk.CTkButton(
                        alt_satir,
                        text="🗑️ Sil",
                        width=60, height=25,
                        fg_color="transparent", hover_color="#e74c3c",
                        text_color=("gray50", "gray60"),
                        command=lambda nid=not_id: self.not_sil(nid)
                    ).pack(side="right")
    
    def not_sil(self, not_id):
        """Notu sil"""
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", "Bu notu silmek istediğinize emin misiniz?", parent=self)
        if onay:
            self.db.not_sil(not_id)
            self.notlari_listele()
    
    # ============== ETİKETLER SEKMESİ ==============
    def etiketler_sekmesi_olustur(self):
        """Etiket sistemi sekmesi"""
        # Üst panel - Yeni etiket ekleme
        ust_frame = ctk.CTkFrame(self.tab_etiketler, fg_color=("gray95", "gray25"), corner_radius=10)
        ust_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ust_frame, text="🏷️ Şikayete Etiket Ekle", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 10))
        
        # Etiket ekleme formu
        form_frame = ctk.CTkFrame(ust_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Etiket:", width=60, anchor="w").pack(side="left")
        self.entry_yeni_etiket = ctk.CTkEntry(form_frame, width=200, placeholder_text="Etiket adı...")
        self.entry_yeni_etiket.pack(side="left", padx=5)
        
        # Renk seçimi
        self.etiket_renkler = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c", "#3498db", "#9b59b6", "#34495e"]
        self.secili_renk = ctk.StringVar(value=self.etiket_renkler[0])
        
        ctk.CTkLabel(form_frame, text="Renk:", width=40, anchor="w").pack(side="left", padx=(10, 0))
        
        renk_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        renk_frame.pack(side="left", padx=5)
        
        for renk in self.etiket_renkler:
            btn = ctk.CTkButton(
                renk_frame,
                text="",
                width=20, height=20,
                fg_color=renk,
                hover_color=renk,
                corner_radius=10,
                command=lambda r=renk: self.secili_renk.set(r)
            )
            btn.pack(side="left", padx=2)
        
        ctk.CTkButton(
            form_frame,
            text="➕ Ekle",
            command=self.etiket_ekle_sikayete,
            fg_color="#2CC985", hover_color="#229C68",
            height=30, width=80
        ).pack(side="left", padx=10)
        
        # Mevcut kullanılmış etiketler başlığı
        ctk.CTkLabel(ust_frame, text="Hızlı Ekle (Daha önce kullanılmış etiketler):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Mevcut etiketler
        self.mevcut_etiket_frame = ctk.CTkScrollableFrame(ust_frame, fg_color="transparent", height=60)
        self.mevcut_etiket_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Şikayete ait etiketler
        ctk.CTkLabel(self.tab_etiketler, text="Bu Şikayetin Etiketleri:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.sikayet_etiket_frame = ctk.CTkScrollableFrame(self.tab_etiketler, fg_color="transparent", height=200)
        self.sikayet_etiket_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Etiketleri yükle
        self.etiketleri_listele()
    
    def etiket_ekle_sikayete(self):
        """Şikayete yeni etiket ekle"""
        etiket_adi = self.entry_yeni_etiket.get().strip()
        
        if not etiket_adi:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen etiket adı girin.", parent=self)
            return
        
        renk = self.secili_renk.get()
        
        # Kullanıcı bilgisi
        ekleyen_id = None
        ekleyen_adi = "Sistem"
        if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
            ekleyen_id = self.controller.aktif_kullanici.get('id')
            ekleyen_adi = self.controller.aktif_kullanici.get('kullanici_adi')
        
        # Etiketi ekle
        sonuc = self.db.etiket_ekle(self.kayit_id, etiket_adi, renk, ekleyen_id, ekleyen_adi)
        
        if sonuc is None:
            self.lift()
            self.focus_force()
            messagebox.showinfo("Bilgi", "Bu etiket zaten şikayete eklenmiş.", parent=self)
            return
        
        # Formu temizle
        self.entry_yeni_etiket.delete(0, "end")
        
        # Listeyi yenile
        self.etiketleri_listele()
    
    def etiketleri_listele(self):
        """Etiketleri listele"""
        # Mevcut etiketleri temizle
        for widget in self.mevcut_etiket_frame.winfo_children():
            widget.destroy()
        for widget in self.sikayet_etiket_frame.winfo_children():
            widget.destroy()
        
        # Tüm benzersiz etiketleri getir (hızlı ekle için)
        tum_etiketler = self.db.tum_etiketleri_getir()
        
        # Şikayetin etiketlerini getir
        sikayet_etiketleri = self.db.etiketleri_getir(self.kayit_id)
        sikayet_etiket_isimleri = [e[1] for e in sikayet_etiketleri]  # etiket adları
        
        if not tum_etiketler:
            ctk.CTkLabel(
                self.mevcut_etiket_frame,
                text="Henüz sistemde etiket kullanılmamış.",
                text_color="gray"
            ).pack(pady=5)
        else:
            # Etiket chip'leri göster (hızlı ekle için)
            row_frame = ctk.CTkFrame(self.mevcut_etiket_frame, fg_color="transparent")
            row_frame.pack(fill="x")
            
            for etiket in tum_etiketler:
                etiket_adi = etiket[0]
                renk = etiket[1]
                
                # Şikayette varsa farklı göster
                ekli = etiket_adi in sikayet_etiket_isimleri
                if ekli:
                    fg = renk
                    text_color = "white"
                else:
                    fg = "transparent"
                    text_color = renk
                
                btn = ctk.CTkButton(
                    row_frame,
                    text=f"🏷️ {etiket_adi}",
                    fg_color=fg,
                    text_color=text_color,
                    hover_color=renk,
                    border_width=2,
                    border_color=renk,
                    corner_radius=15,
                    height=28,
                    command=lambda e=etiket_adi, r=renk, added=ekli: self.hizli_etiket_ekle(e, r, added)
                )
                btn.pack(side="left", padx=3, pady=3)
        
        # Şikayetin etiketlerini göster
        if not sikayet_etiketleri:
            ctk.CTkLabel(
                self.sikayet_etiket_frame,
                text="Bu şikayete henüz etiket eklenmemiş.\nYukarıdan etiket seçebilir veya yeni etiket ekleyebilirsiniz.",
                text_color="gray",
                font=ctk.CTkFont(size=13)
            ).pack(pady=30)
        else:
            etiket_goster_frame = ctk.CTkFrame(self.sikayet_etiket_frame, fg_color="transparent")
            etiket_goster_frame.pack(fill="x", pady=10)
            
            for etiket in sikayet_etiketleri:
                etiket_id = etiket[0]
                etiket_adi = etiket[1]
                renk = etiket[2]
                
                chip_frame = ctk.CTkFrame(etiket_goster_frame, fg_color=renk, corner_radius=15)
                chip_frame.pack(side="left", padx=5, pady=5)
                
                ctk.CTkLabel(
                    chip_frame,
                    text=f"🏷️ {etiket_adi}",
                    text_color="white",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left", padx=(10, 5), pady=5)
                
                ctk.CTkButton(
                    chip_frame,
                    text="✕",
                    width=20, height=20,
                    fg_color="transparent",
                    hover_color="white",
                    text_color="white",
                    corner_radius=10,
                    command=lambda eid=etiket_id: self.etiket_kaldir(eid)
                ).pack(side="left", padx=(0, 5), pady=5)
    
    def hizli_etiket_ekle(self, etiket_adi, renk, eklenmis):
        """Hızlı etiket ekle/kaldır"""
        if eklenmis:
            # Silmek için etiket id'sini bul
            sikayet_etiketleri = self.db.etiketleri_getir(self.kayit_id)
            for e in sikayet_etiketleri:
                if e[1] == etiket_adi:
                    self.db.etiket_sil(e[0])
                    break
        else:
            # Kullanıcı bilgisi
            ekleyen_id = None
            ekleyen_adi = "Sistem"
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                ekleyen_id = self.controller.aktif_kullanici.get('id')
                ekleyen_adi = self.controller.aktif_kullanici.get('kullanici_adi')
            
            self.db.etiket_ekle(self.kayit_id, etiket_adi, renk, ekleyen_id, ekleyen_adi)
        
        self.etiketleri_listele()
    
    def etiket_kaldir(self, etiket_id):
        """Etiketi kaldır"""
        self.db.etiket_sil(etiket_id)
        self.etiketleri_listele()
    
    # ============== HATIRLATICILAR SEKMESİ ==============
    def hatirlaticilar_sekmesi_olustur(self):
        """Hatırlatıcı sekmesi"""
        # Üst panel - Hatırlatıcı ekleme
        ust_frame = ctk.CTkFrame(self.tab_hatirlaticilar, fg_color=("gray95", "gray25"), corner_radius=10)
        ust_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ust_frame, text="🔔 Yeni Hatırlatıcı Ekle", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 10))
        
        # Tarih ve saat
        tarih_frame = ctk.CTkFrame(ust_frame, fg_color="transparent")
        tarih_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(tarih_frame, text="Tarih (GG.AA.YYYY):", width=130, anchor="w").pack(side="left")
        self.entry_hatirlatma_tarih = ctk.CTkEntry(tarih_frame, width=120, placeholder_text="01.01.2025")
        self.entry_hatirlatma_tarih.pack(side="left", padx=5)
        
        ctk.CTkLabel(tarih_frame, text="Saat (SS:DD):", width=90, anchor="w").pack(side="left", padx=(20, 0))
        self.entry_hatirlatma_saat = ctk.CTkEntry(tarih_frame, width=80, placeholder_text="09:00")
        self.entry_hatirlatma_saat.pack(side="left", padx=5)
        
        # Bugün, yarın, hafta sonu hızlı butonları
        hizli_frame = ctk.CTkFrame(ust_frame, fg_color="transparent")
        hizli_frame.pack(fill="x", padx=15, pady=5)
        
        from datetime import datetime, timedelta
        bugun = datetime.now()
        yarin = bugun + timedelta(days=1)
        hafta_sonu = bugun + timedelta(days=(5 - bugun.weekday()) % 7 or 7)
        
        ctk.CTkButton(
            hizli_frame,
            text="📅 Bugün",
            command=lambda: self.hizli_tarih_sec(bugun),
            fg_color="#3498db", hover_color="#2980b9",
            height=28, width=80
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            hizli_frame,
            text="📅 Yarın",
            command=lambda: self.hizli_tarih_sec(yarin),
            fg_color="#9b59b6", hover_color="#8e44ad",
            height=28, width=80
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            hizli_frame,
            text="📅 1 Hafta",
            command=lambda: self.hizli_tarih_sec(bugun + timedelta(days=7)),
            fg_color="#e67e22", hover_color="#d35400",
            height=28, width=80
        ).pack(side="left", padx=3)
        
        # Mesaj
        ctk.CTkLabel(ust_frame, text="Hatırlatma Mesajı:", anchor="w").pack(anchor="w", padx=15, pady=(10, 5))
        self.text_hatirlatma_mesaj = ctk.CTkTextbox(ust_frame, height=60, corner_radius=8)
        self.text_hatirlatma_mesaj.pack(fill="x", padx=15, pady=(0, 10))
        
        # Ekle butonu
        ctk.CTkButton(
            ust_frame,
            text="➕ Hatırlatıcı Ekle",
            command=self.hatirlatici_ekle,
            fg_color="#2CC985", hover_color="#229C68",
            height=40, width=180
        ).pack(pady=(0, 15))
        
        # Hatırlatıcı listesi başlığı
        ctk.CTkLabel(self.tab_hatirlaticilar, text="Aktif Hatırlatıcılar:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(5, 5))
        
        # Hatırlatıcı listesi
        self.hatirlatici_liste_frame = ctk.CTkScrollableFrame(self.tab_hatirlaticilar, fg_color="transparent", height=250)
        self.hatirlatici_liste_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Hatırlatıcıları yükle
        self.hatiraticilar_listele()
    
    def hizli_tarih_sec(self, tarih):
        """Hızlı tarih seçimi"""
        self.entry_hatirlatma_tarih.delete(0, "end")
        self.entry_hatirlatma_tarih.insert(0, tarih.strftime("%d.%m.%Y"))
        self.entry_hatirlatma_saat.delete(0, "end")
        self.entry_hatirlatma_saat.insert(0, "09:00")
    
    def hatirlatici_ekle(self):
        """Yeni hatırlatıcı ekle"""
        tarih_str = self.entry_hatirlatma_tarih.get().strip()
        saat_str = self.entry_hatirlatma_saat.get().strip()
        mesaj = self.text_hatirlatma_mesaj.get("1.0", "end").strip()
        
        if not tarih_str or not saat_str:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen tarih ve saat girin.", parent=self)
            return
        
        if not mesaj:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen hatırlatma mesajı girin.", parent=self)
            return
        
        # Tarih formatını kontrol et
        try:
            from datetime import datetime
            tarih_saat = datetime.strptime(f"{tarih_str} {saat_str}", "%d.%m.%Y %H:%M")
            hatirlatma_tarihi = tarih_saat.strftime("%Y-%m-%d %H:%M:00")
        except ValueError:
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", "Geçersiz tarih/saat formatı!\nTarih: GG.AA.YYYY\nSaat: SS:DD", parent=self)
            return
        
        # Kullanıcı bilgisi
        kullanici_id = None
        kullanici_adi = "Sistem"
        if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
            kullanici_id = self.controller.aktif_kullanici.get('id')
            kullanici_adi = self.controller.aktif_kullanici.get('kullanici_adi')
        
        # Hatırlatıcıyı kaydet
        self.db.hatirlatici_ekle(
            sikayet_id=self.kayit_id,
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            hatirlatma_tarihi=hatirlatma_tarihi,
            mesaj=mesaj
        )
        
        # Formu temizle
        self.entry_hatirlatma_tarih.delete(0, "end")
        self.entry_hatirlatma_saat.delete(0, "end")
        self.text_hatirlatma_mesaj.delete("1.0", "end")
        
        # Listeyi yenile
        self.hatiraticilar_listele()
    
    def hatiraticilar_listele(self):
        """Hatırlatıcıları listele"""
        for widget in self.hatirlatici_liste_frame.winfo_children():
            widget.destroy()
        
        hatirlaticilar = self.db.hatirlaticilari_getir(self.kayit_id, sadece_aktif=False)
        
        if not hatirlaticilar:
            ctk.CTkLabel(
                self.hatirlatici_liste_frame,
                text="Henüz hatırlatıcı eklenmemiş.",
                text_color="gray",
                font=ctk.CTkFont(size=13)
            ).pack(pady=30)
            return
        
        from datetime import datetime
        simdi = datetime.now()
        
        for hatirlatici in hatirlaticilar:
            # id, sikayet_id, kullanici_adi, hatirlatma_tarihi, mesaj, tamamlandi, sikayet_no, yolcu_adi
            hatirlatici_id = hatirlatici[0]
            hatirlatma_tarihi = hatirlatici[3]
            mesaj = hatirlatici[4]
            tamamlandi = hatirlatici[5] if len(hatirlatici) > 5 else 0
            
            # Tarihi parse et
            try:
                hatirlatma_dt = datetime.strptime(str(hatirlatma_tarihi)[:16], "%Y-%m-%d %H:%M")
                tarih_gosterim = hatirlatma_dt.strftime("%d.%m.%Y %H:%M")
                gecmis_mi = hatirlatma_dt < simdi
            except:
                tarih_gosterim = str(hatirlatma_tarihi)
                gecmis_mi = False
            
            # Kart rengi
            if tamamlandi:
                kart_renk = ("#d5f5e3", "#1e4620")  # Yeşil - tamamlandı
            elif gecmis_mi:
                kart_renk = ("#fadbd8", "#641e16")  # Kırmızı - geçmiş
            else:
                kart_renk = ("white", "gray30")  # Normal
            
            # Hatırlatıcı kartı
            kart = ctk.CTkFrame(self.hatirlatici_liste_frame, fg_color=kart_renk, corner_radius=10)
            kart.pack(fill="x", pady=5, padx=5)
            
            # Üst satır
            ust_satir = ctk.CTkFrame(kart, fg_color="transparent")
            ust_satir.pack(fill="x", padx=10, pady=(8, 2))
            
            # Durum ikonu
            if tamamlandi:
                ikon = "✅"
            elif gecmis_mi:
                ikon = "⚠️"
            else:
                ikon = "🔔"
            
            ctk.CTkLabel(ust_satir, text=f"{ikon} {tarih_gosterim}", font=ctk.CTkFont(weight="bold", size=13)).pack(side="left")
            
            # Mesaj
            ctk.CTkLabel(kart, text=mesaj, anchor="w", justify="left", wraplength=680).pack(fill="x", padx=10, pady=5)
            
            # Alt satır - Butonlar
            alt_satir = ctk.CTkFrame(kart, fg_color="transparent")
            alt_satir.pack(fill="x", padx=10, pady=(0, 8))
            
            if not tamamlandi:
                ctk.CTkButton(
                    alt_satir,
                    text="✓ Tamamlandı",
                    width=100, height=25,
                    fg_color="#27ae60", hover_color="#1e8449",
                    command=lambda hid=hatirlatici_id: self.hatirlatici_tamamla(hid)
                ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                alt_satir,
                text="🗑️ Sil",
                width=60, height=25,
                fg_color="transparent", hover_color="#e74c3c",
                text_color=("gray50", "gray60"),
                command=lambda hid=hatirlatici_id: self.hatirlatici_sil(hid)
            ).pack(side="right", padx=2)
    
    def hatirlatici_tamamla(self, hatirlatici_id):
        """Hatırlatıcıyı tamamla"""
        self.db.hatirlatici_tamamla(hatirlatici_id)
        self.hatiraticilar_listele()
    
    def hatirlatici_sil(self, hatirlatici_id):
        """Hatırlatıcıyı sil"""
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", "Bu hatırlatıcıyı silmek istediğinize emin misiniz?", parent=self)
        if onay:
            self.db.hatirlatici_sil(hatirlatici_id)
            self.hatiraticilar_listele()


class SikayetArsivi(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("white", "gray17"))
        self.controller = controller
        self.db = controller.db
        self.tum_kayitlar = []
        
        # Sayfalama ayarları
        self.sayfa_basi_kayit = 12  # Her sayfada 12 kart (4 satır x 3 sütun)
        self.mevcut_sayfa = 1
        self.toplam_sayfa = 1
        self.filtreli_kayitlar = []
        
        # Aktif filtre etiketleri
        self.aktif_durum_filtre = "Tümü"
        self.aktif_oncelik_filtre = "Tümü"
        self.aktif_tur_filtre = "Tümü"
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Kartlar için (row 2 -> 3)
        
        # --- ÜST PANEL ---
        self.ust_panel = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=("white", "gray20"))
        self.ust_panel.grid(row=0, column=0, sticky="ew")
        
        # Back Button
        ctk.CTkButton(self.ust_panel, text="← Geri", command=lambda: controller.show_frame("AnaEkran"), 
                      width=80, height=35, corner_radius=8, fg_color="transparent", 
                      text_color=("#1a1a2e", "white"), hover_color=("gray90", "gray30"),
                      font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=12)
        
        ctk.CTkLabel(self.ust_panel, text="📋 Şikayet Arşivi", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=10)
        
        ctk.CTkButton(self.ust_panel, text="＋ Yeni Şikayet", command=controller.yeni_sikayet_ac, 
                      width=150, height=38, corner_radius=10,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#10b981", hover_color="#059669").pack(side="right", padx=20, pady=11)
        
        # --- ARAMA VE FİLTRE PANELİ (Tek satır) ---
        self.arama_panel = ctk.CTkFrame(self, height=55, corner_radius=12, fg_color=("gray95", "gray25"))
        self.arama_panel.grid(row=1, column=0, sticky="ew", padx=15, pady=(12, 8))
        
        # Arama kutusu (daha geniş ve modern)
        self.entry_arama = ctk.CTkEntry(self.arama_panel, 
                                         placeholder_text="🔍 Ara: isim, telefon, PNR, güzergah...", 
                                         width=350, height=38, corner_radius=10,
                                         font=ctk.CTkFont(size=13))
        self.entry_arama.pack(side="left", padx=12, pady=8)
        self.entry_arama.bind("<KeyRelease>", lambda e: self.filtrele())
        
        # Temizle butonu (minimal)
        ctk.CTkButton(self.arama_panel, text="✕", command=self.filtreleri_temizle, 
                      width=38, height=38, corner_radius=10,
                      fg_color=("gray85", "gray35"), hover_color=("gray75", "gray45"),
                      text_color=("gray50", "gray70"), font=ctk.CTkFont(size=16)).pack(side="left", padx=5)
        
        # İstatistik butonu
        ctk.CTkButton(self.arama_panel, text="📊", command=self.istatistik_goster, 
                      width=42, height=38, corner_radius=10,
                      fg_color="#8b5cf6", hover_color="#7c3aed",
                      font=ctk.CTkFont(size=18)).pack(side="right", padx=12)
        
        # --- MODERN FİLTRE CHIPS (Tek satırda) ---
        self.filtre_panel = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="transparent")
        self.filtre_panel.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        # Tüm filtreler tek satırda - yatay kaydırılabilir
        filtre_scroll = ctk.CTkScrollableFrame(self.filtre_panel, height=48, orientation="horizontal", 
                                                fg_color="transparent")
        filtre_scroll.pack(fill="x", expand=True)
        
        # === DURUM FİLTRELERİ ===
        self.durum_butonlari = {}
        durum_verileri = [
            ("Tümü", "#64748b", "white"),
            ("Yeni", "#ef4444", "white"),
            ("İşlemde", "#f59e0b", "white"),
            ("Çözüldü", "#22c55e", "white")
        ]
        
        # Ayırıcı label
        ctk.CTkLabel(filtre_scroll, text="Durum", font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=("gray60", "gray50")).pack(side="left", padx=(5, 8))
        
        for durum, renk, text_renk in durum_verileri:
            btn = ctk.CTkButton(
                filtre_scroll, 
                text=durum,
                width=70 if durum == "Tümü" else 85,
                height=30,
                corner_radius=15,
                fg_color=renk if durum == "Tümü" else "transparent",
                border_width=2,
                border_color=renk,
                text_color=text_renk if durum == "Tümü" else renk,
                hover_color=renk,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda d=durum: self.durum_filtre_sec(d)
            )
            btn.pack(side="left", padx=3)
            self.durum_butonlari[durum] = btn
        
        # Dikey ayırıcı
        ctk.CTkFrame(filtre_scroll, width=2, height=25, fg_color=("gray80", "gray40")).pack(side="left", padx=10)
        
        # === ÖNCELİK FİLTRELERİ ===
        ctk.CTkLabel(filtre_scroll, text="Öncelik", font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=("gray60", "gray50")).pack(side="left", padx=(5, 8))
        
        self.oncelik_butonlari = {}
        oncelik_verileri = [
            ("Tümü", "#64748b"),
            ("Düşük", "#22c55e"),
            ("Orta", "#eab308"),
            ("Yüksek", "#f97316"),
            ("Acil", "#ef4444")
        ]
        
        for oncelik, renk in oncelik_verileri:
            # Öncelik ikonları
            ikon = {"Tümü": "", "Düşük": "●", "Orta": "●", "Yüksek": "●", "Acil": "🔥"}
            btn = ctk.CTkButton(
                filtre_scroll,
                text=f"{ikon[oncelik]} {oncelik}" if ikon[oncelik] else oncelik,
                height=30,
                corner_radius=15,
                fg_color=renk if oncelik == "Tümü" else "transparent",
                border_width=2,
                border_color=renk,
                text_color="white" if oncelik == "Tümü" else renk,
                hover_color=renk,
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda o=oncelik: self.oncelik_filtre_sec(o)
            )
            btn.pack(side="left", padx=3)
            self.oncelik_butonlari[oncelik] = btn
        
        # Dikey ayırıcı
        ctk.CTkFrame(filtre_scroll, width=2, height=25, fg_color=("gray80", "gray40")).pack(side="left", padx=10)
        
        # === TÜR FİLTRELERİ ===
        ctk.CTkLabel(filtre_scroll, text="Tür", font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=("gray60", "gray50")).pack(side="left", padx=(5, 8))
        
        self.tur_butonlari = {}
        sikayet_turleri = [
            ("Tümü", "#64748b", "📋"),
            ("Personel", "#8b5cf6", "👤"),
            ("Rötar", "#ef4444", "⏰"),
            ("Bagaj", "#f97316", "🧳"),
            ("Hijyen", "#14b8a6", "✨"),
            ("İkram", "#3b82f6", "☕"),
            ("İade", "#ec4899", "💳"),
            ("Bilet", "#6366f1", "🎫"),
            ("Diğer", "#94a3b8", "📝")
        ]
        
        # Tür eşleştirme (kısa isim -> gerçek isim)
        self.tur_eslestirme = {
            "Tümü": "Tümü",
            "Personel": "Personel Davranışı",
            "Rötar": "Rötar / Sefer İptali", 
            "Bagaj": "Bagaj Hasarı",
            "Hijyen": "Hijyen ve Temizlik",
            "İkram": "İkram Hizmetleri",
            "İade": "Hatalı Çekim ve İade",
            "Bilet": "Elektronik Bilet İşlemleri",
            "Diğer": "Diğer"
        }
        
        for tur, renk, ikon in sikayet_turleri:
            btn = ctk.CTkButton(
                filtre_scroll,
                text=f"{ikon} {tur}",
                height=30,
                corner_radius=15,
                fg_color=renk if tur == "Tümü" else "transparent",
                border_width=2,
                border_color=renk,
                text_color="white" if tur == "Tümü" else renk,
                hover_color=renk,
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda t=tur: self.tur_filtre_sec(t)
            )
            btn.pack(side="left", padx=3)
            self.tur_butonlari[tur] = btn
        
        # --- KART PANELİ (Scrollable) ---
        self.kart_panel = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.kart_panel.grid(row=3, column=0, sticky="nswe", padx=15, pady=8)
        self.kart_panel.grid_columnconfigure((0, 1, 2), weight=1)  # 3 sütunlu grid
        
        # --- ALT PANEL (Sayfalama - Modern) ---
        self.alt_panel = ctk.CTkFrame(self, height=50, corner_radius=12, fg_color=("gray95", "gray25"))
        self.alt_panel.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 12))
        
        # Sol: Toplam kayıt bilgisi
        self.kayit_bilgi_label = ctk.CTkLabel(self.alt_panel, text="📊 0 kayıt", font=ctk.CTkFont(size=12))
        self.kayit_bilgi_label.pack(side="left", padx=15, pady=10)
        
        # Orta: Sayfalama kontrolleri
        sayfalama_frame = ctk.CTkFrame(self.alt_panel, fg_color="transparent")
        sayfalama_frame.pack(expand=True)
        
        self.btn_ilk = ctk.CTkButton(sayfalama_frame, text="⏮", width=35, height=32, corner_radius=8, command=lambda: self.sayfaya_git(1))
        self.btn_ilk.pack(side="left", padx=2)
        
        self.btn_onceki = ctk.CTkButton(sayfalama_frame, text="◀", width=35, height=32, corner_radius=8, command=lambda: self.sayfaya_git(self.mevcut_sayfa - 1))
        self.btn_onceki.pack(side="left", padx=2)
        
        self.sayfa_label = ctk.CTkLabel(sayfalama_frame, text="1 / 1", font=ctk.CTkFont(size=13, weight="bold"), width=70)
        self.sayfa_label.pack(side="left", padx=10)
        
        self.btn_sonraki = ctk.CTkButton(sayfalama_frame, text="▶", width=35, height=32, corner_radius=8, command=lambda: self.sayfaya_git(self.mevcut_sayfa + 1))
        self.btn_sonraki.pack(side="left", padx=2)
        
        self.btn_son = ctk.CTkButton(sayfalama_frame, text="⏭", width=35, height=32, corner_radius=8, command=lambda: self.sayfaya_git(self.toplam_sayfa))
        self.btn_son.pack(side="left", padx=2)
        
        # Sağ: Sayfa başı kayıt sayısı
        ctk.CTkLabel(self.alt_panel, text="Göster:", font=ctk.CTkFont(size=11)).pack(side="right", padx=(5, 2), pady=10)
        self.combo_sayfa_basi = ctk.CTkComboBox(self.alt_panel, values=["12", "24", "48", "96"], width=70, height=28, 
                                                 state="readonly", command=self.sayfa_basi_degisti)
        self.combo_sayfa_basi.set("12")
        self.combo_sayfa_basi.pack(side="right", padx=(0, 15), pady=10)
        
        self.listeyi_yenile()
    
    def kart_olustur(self, kayit, row, col):
        """Tek bir şikayet kartı oluştur"""
        # kayit: (id, sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer)
        
        kayit_id = kayit[0]
        sikayet_no = kayit[1] or ""
        yolcu = kayit[2] or "-"
        pnr = kayit[5] or "-"
        durum = kayit[10] or "Yeni"
        telefon = kayit[11] if len(kayit) > 11 and kayit[11] else "-"
        sikayet_turu = kayit[14] if len(kayit) > 14 and kayit[14] else "-"
        oncelik = kayit[16] if len(kayit) > 16 and kayit[16] else "Orta"
        
        # Durum renkleri
        durum_renk = {"Yeni": "#e74c3c", "İşlemde": "#f39c12", "Çözüldü": "#27ae60"}
        oncelik_renk = {"Acil": "#e74c3c", "Yüksek": "#e67e22", "Orta": "#f39c12", "Düşük": "#27ae60"}
        
        # Kart frame
        kart = ctk.CTkFrame(self.kart_panel, corner_radius=12, fg_color=("gray95", "gray25"), border_width=1, border_color=("gray80", "gray40"))
        kart.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        kart.configure(cursor="hand2")
        
        # Üst kısım: Şikayet türü ve durum
        ust = ctk.CTkFrame(kart, fg_color="transparent")
        ust.pack(fill="x", padx=12, pady=(10, 5))
        
        # Şikayet türü etiketi
        tur_label = ctk.CTkLabel(ust, text=sikayet_turu, font=ctk.CTkFont(size=11), 
                                  fg_color=("#3498db", "#2980b9"), corner_radius=5, 
                                  text_color="white", padx=8, pady=2)
        tur_label.pack(side="left")
        
        # Durum etiketi
        durum_label = ctk.CTkLabel(ust, text=durum, font=ctk.CTkFont(size=11, weight="bold"),
                                    fg_color=durum_renk.get(durum, "#95a5a6"), corner_radius=5,
                                    text_color="white", padx=8, pady=2)
        durum_label.pack(side="right")
        
        # Öncelik göstergesi (küçük nokta)
        oncelik_frame = ctk.CTkFrame(ust, width=12, height=12, corner_radius=6, 
                                      fg_color=oncelik_renk.get(oncelik, "#f39c12"))
        oncelik_frame.pack(side="right", padx=(0, 8))
        
        # Orta kısım: İsim Soyisim (büyük)
        ctk.CTkLabel(kart, text=yolcu, font=ctk.CTkFont(size=15, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(5, 2))
        
        # Alt bilgiler: Telefon ve PNR
        alt = ctk.CTkFrame(kart, fg_color="transparent")
        alt.pack(fill="x", padx=12, pady=(2, 10))
        
        ctk.CTkLabel(alt, text=f"📞 {telefon}", font=ctk.CTkFont(size=12), text_color=("gray50", "gray60"), anchor="w").pack(side="left")
        ctk.CTkLabel(alt, text=f"🎫 {pnr}", font=ctk.CTkFont(size=12), text_color=("gray50", "gray60"), anchor="e").pack(side="right")
        
        # Tıklama olayları - tüm karta ve alt elemanlarına bağla
        def on_click(e):
            self.kart_tiklandi(kayit)
        
        def on_double_click(e):
            self.kart_cift_tiklandi(kayit)
        
        # Kartı ve tüm alt elemanlarını tıklanabilir yap
        for widget in [kart, ust, alt, tur_label, durum_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_double_click)
        
        # Kart içindeki label'ları da tıklanabilir yap
        for child in kart.winfo_children():
            child.bind("<Button-1>", on_click)
            child.bind("<Double-Button-1>", on_double_click)
            if hasattr(child, 'winfo_children'):
                for subchild in child.winfo_children():
                    subchild.bind("<Button-1>", on_click)
                    subchild.bind("<Double-Button-1>", on_double_click)
    
    def kart_tiklandi(self, kayit):
        """Karta tek tıklandığında - seçim için (isteğe bağlı)"""
        pass  # İsterseniz seçim efekti ekleyebiliriz
    
    def kart_cift_tiklandi(self, kayit):
        """Karta çift tıklandığında - detay/düzenleme menüsü aç"""
        self.secili_kayit = kayit
        self.islem_menusu_goster(kayit)
    
    def islem_menusu_goster(self, kayit):
        """Sağ tık benzeri işlem menüsü"""
        # Önceki menü varsa kapat
        if hasattr(self, 'aktif_menu') and self.aktif_menu and self.aktif_menu.winfo_exists():
            self.aktif_menu.destroy()
        
        menu = ctk.CTkToplevel(self.controller)
        self.aktif_menu = menu
        menu.title("")
        menu.geometry("220x300")
        menu.resizable(False, False)
        menu.attributes("-topmost", True)
        menu.overrideredirect(True)  # Başlık çubuğunu kaldır
        
        # Ekranın ortasına konumla
        x = self.controller.winfo_x() + self.controller.winfo_width()//2 - 110
        y = self.controller.winfo_y() + self.controller.winfo_height()//2 - 150
        menu.geometry(f"+{x}+{y}")
        
        # Menü çerçevesi
        frame = ctk.CTkFrame(menu, corner_radius=12, fg_color=("white", "gray20"), border_width=2, border_color=("gray70", "gray40"))
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Üst kısım - Başlık ve X butonu
        ust_frame = ctk.CTkFrame(frame, fg_color="transparent")
        ust_frame.pack(fill="x", padx=10, pady=(8, 5))
        
        ctk.CTkLabel(ust_frame, text=f"📋 {kayit[1]}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", expand=True)
        
        # X kapatma butonu
        ctk.CTkButton(ust_frame, text="✕", width=28, height=28, 
                      fg_color="transparent", hover_color=("#E0E0E0", "gray40"),
                      text_color=("gray50", "gray70"), font=ctk.CTkFont(size=14, weight="bold"),
                      command=menu.destroy).pack(side="right")
        
        # Butonlar
        ctk.CTkButton(frame, text="👁️ Detayları Göster", command=lambda: [menu.destroy(), self.detay_goster_kayit(kayit)],
                      width=190, height=34, fg_color="#E59400", hover_color="#B37400").pack(pady=3)
        
        ctk.CTkButton(frame, text="✏️ Düzenle", command=lambda: [menu.destroy(), self.duzenle_kayit(kayit)],
                      width=190, height=34, fg_color="#1F6AA5", hover_color="#144870").pack(pady=3)
        
        ctk.CTkButton(frame, text="🔄 Durum Değiştir", command=lambda: [menu.destroy(), self.durum_degistir_kayit(kayit)],
                      width=190, height=34, fg_color="#2CC985", hover_color="#229C68").pack(pady=3)
        
        ctk.CTkButton(frame, text="📜 İşlem Geçmişi", command=lambda: [menu.destroy(), self.islem_gecmisi_goster_kayit(kayit)],
                      width=190, height=34, fg_color="#9B59B6", hover_color="#7D3C98").pack(pady=3)
        
        ctk.CTkButton(frame, text="📄 PDF İndir", command=lambda: [menu.destroy(), self.pdf_indir_kayit(kayit)],
                      width=190, height=34, fg_color="#3B8ED0", hover_color="#1f538d").pack(pady=3)
        
        ctk.CTkButton(frame, text="🗑️ Sil", command=lambda: [menu.destroy(), self.sil_kayit(kayit)],
                      width=190, height=34, fg_color="#FF4D4D", hover_color="#CC0000").pack(pady=3)
        
        # ESC tuşuyla kapat
        menu.bind("<Escape>", lambda e: menu.destroy())
        
        # Menü dışına tıklayınca kapat
        def disari_tikla_kontrol(event):
            try:
                # Tıklanan widget menünün içinde mi kontrol et
                widget = event.widget
                if not str(widget).startswith(str(menu)):
                    menu.destroy()
            except:
                pass
        
        # Ana pencereye tıklama olayını bağla
        self.controller.bind("<Button-1>", disari_tikla_kontrol, add="+")
        
        # Menü kapandığında olayı kaldır
        def temizle():
            try:
                self.controller.unbind("<Button-1>")
            except:
                pass
        
        menu.bind("<Destroy>", lambda e: temizle())
        menu.focus_set()
    
    def detay_goster_kayit(self, kayit):
        """Detay ekranını aç"""
        self.controller.sikayet_detay_ac(kayit)
    
    def duzenle_kayit(self, kayit):
        """Düzenleme ekranını aç"""
        self.controller.yeni_sikayet_ac(duzenlenecek_kayit=kayit)
    
    def islem_gecmisi_goster_kayit(self, kayit):
        """Bu şikayete ait işlem geçmişini göster"""
        sikayet_id = kayit[0]
        sikayet_no = kayit[1]
        
        # Pencere oluştur
        pencere = ctk.CTkToplevel(self.controller)
        pencere.title(f"İşlem Geçmişi - {sikayet_no}")
        pencere.geometry("600x450")
        pencere.attributes("-topmost", True)
        pencere.resizable(True, True)
        
        # Ekranın ortasına konumla
        x = self.controller.winfo_x() + self.controller.winfo_width()//2 - 300
        y = self.controller.winfo_y() + self.controller.winfo_height()//2 - 225
        pencere.geometry(f"+{x}+{y}")
        
        # Başlık
        baslik_frame = ctk.CTkFrame(pencere, fg_color="transparent")
        baslik_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(baslik_frame, text=f"📜 {sikayet_no} - İşlem Geçmişi", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        ctk.CTkButton(baslik_frame, text="✕ Kapat", width=80, height=30,
                      fg_color="#FF4D4D", hover_color="#CC0000",
                      command=pencere.destroy).pack(side="right")
        
        # İşlem listesi için scroll frame
        liste_frame = ctk.CTkScrollableFrame(pencere, fg_color="transparent")
        liste_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Veritabanından işlemleri al
        islemler = self.db.sikayet_islemlerini_getir(sikayet_id)
        
        if not islemler:
            # Boş durum mesajı
            bos_frame = ctk.CTkFrame(liste_frame, fg_color=("gray90", "gray25"), corner_radius=10)
            bos_frame.pack(fill="x", pady=20, padx=10)
            ctk.CTkLabel(bos_frame, text="📭 Bu şikayet için henüz işlem kaydı bulunmuyor.", 
                        font=ctk.CTkFont(size=14), text_color="gray").pack(pady=30)
        else:
            # İşlemleri listele
            for islem in islemler:
                # islem: (id, tarih, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum)
                islem_id, tarih, kullanici, islem_turu, aciklama, eski_durum, yeni_durum = islem
                
                # İşlem kartı
                kart = ctk.CTkFrame(liste_frame, fg_color=("white", "gray25"), corner_radius=8, 
                                    border_width=1, border_color=("gray80", "gray40"))
                kart.pack(fill="x", pady=5, padx=5)
                
                # Üst satır: İşlem türü ve tarih
                ust = ctk.CTkFrame(kart, fg_color="transparent")
                ust.pack(fill="x", padx=12, pady=(10, 5))
                
                # İşlem türüne göre ikon ve renk
                ikon_renk = {
                    "DURUM DEĞİŞİKLİĞİ": ("🔄", "#2CC985"),
                    "OLUŞTURULDU": ("➕", "#3B8ED0"),
                    "GÜNCELLEME": ("✏️", "#E59400"),
                    "DÜZENLEME": ("✏️", "#E59400"),
                    "SİLİNDİ": ("🗑️", "#FF4D4D"),
                    "NOT EKLENDİ": ("📝", "#9B59B6"),
                }
                ikon, renk = ikon_renk.get(islem_turu, ("📋", "#1F6AA5"))
                
                ctk.CTkLabel(ust, text=f"{ikon} {islem_turu}", 
                            font=ctk.CTkFont(size=13, weight="bold"),
                            text_color=renk).pack(side="left")
                
                ctk.CTkLabel(ust, text=tarih, 
                            font=ctk.CTkFont(size=11),
                            text_color="gray").pack(side="right")
                
                # Alt satır: Kullanıcı ve detaylar
                alt = ctk.CTkFrame(kart, fg_color="transparent")
                alt.pack(fill="x", padx=12, pady=(0, 10))
                
                ctk.CTkLabel(alt, text=f"👤 {kullanici or 'Bilinmiyor'}", 
                            font=ctk.CTkFont(size=11),
                            text_color=("gray40", "gray60")).pack(side="left")
                
                # Durum değişikliği varsa göster
                if eski_durum and yeni_durum:
                    durum_text = f"{eski_durum} → {yeni_durum}"
                    ctk.CTkLabel(alt, text=durum_text, 
                                font=ctk.CTkFont(size=11, weight="bold"),
                                text_color="#2CC985").pack(side="right")
                
                # Açıklama varsa göster
                if aciklama:
                    aciklama_frame = ctk.CTkFrame(kart, fg_color=("gray95", "gray30"), corner_radius=5)
                    aciklama_frame.pack(fill="x", padx=12, pady=(0, 10))
                    ctk.CTkLabel(aciklama_frame, text=aciklama, 
                                font=ctk.CTkFont(size=11),
                                wraplength=500, justify="left").pack(padx=10, pady=8)
        
        # Toplam işlem sayısı
        ctk.CTkLabel(pencere, text=f"Toplam {len(islemler)} işlem", 
                    font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 10))
        
        pencere.focus_set()

    def durum_degistir_kayit(self, kayit):
        """Durum değiştirme dialogu"""
        dialog = ctk.CTkToplevel(self.controller)
        dialog.title("Durum Değiştir")
        dialog.geometry("300x150")
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        
        x = self.controller.winfo_x() + self.controller.winfo_width()//2 - 150
        y = self.controller.winfo_y() + self.controller.winfo_height()//2 - 75
        dialog.geometry(f"+{x}+{y}")
        
        eski_durum = kayit[10] or "Yeni"
        
        ctk.CTkLabel(dialog, text=f"Şikayet: {kayit[1]}", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        combo = ctk.CTkComboBox(dialog, values=["Yeni", "İşlemde", "Çözüldü"], width=200, state="readonly")
        combo.set(eski_durum)
        combo.pack(pady=10)
        
        def kaydet():
            yeni_durum = combo.get()
            if yeni_durum != eski_durum:
                self.db.durumu_guncelle(kayit[0], yeni_durum)
                
                # İşlem geçmişine kaydet
                if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                    self.db.sikayet_islemi_ekle(
                        sikayet_id=kayit[0],
                        kullanici_id=self.controller.aktif_kullanici.get('id'),
                        kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                        islem_turu="DURUM DEĞİŞİKLİĞİ",
                        aciklama=f"Durum değiştirildi",
                        eski_durum=eski_durum,
                        yeni_durum=yeni_durum
                    )
                
                dialog.destroy()
                self.listeyi_yenile()
            else:
                dialog.destroy()
        
        ctk.CTkButton(dialog, text="Kaydet", command=kaydet, fg_color="#2CC985").pack(pady=10)
    
    def pdf_indir_kayit(self, kayit):
        """PDF indir"""
        self.secili_kayit_for_pdf = kayit
        self.pdf_indir_internal(kayit)
    
    def sil_kayit(self, kayit):
        """Şikayeti çöp kutusuna taşı"""
        self.controller.lift()
        self.controller.focus_force()
        onay = messagebox.askyesno("Onay", f"{kayit[1]} numaralı şikayeti çöp kutusuna taşımak istediğinize emin misiniz?", parent=self.controller)
        if onay:
            kullanici_id = None
            kullanici_adi = None
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                kullanici_id = self.controller.aktif_kullanici.get("id")
                kullanici_adi = self.controller.aktif_kullanici.get("kullanici_adi")
            basarili, mesaj = self.db.cop_kutusuna_tasi(kayit[0], kullanici_id, kullanici_adi)
            if basarili:
                messagebox.showinfo("Bilgi", "Şikayet çöp kutusuna taşındı. İstediğiniz zaman geri alabilirsiniz.", parent=self.controller)
            else:
                messagebox.showerror("Hata", mesaj, parent=self.controller)
            self.listeyi_yenile()
    
    def listeyi_yenile(self):
        """Kartları yenile (sayfalama ile)"""
        # Verileri al
        self.tum_kayitlar = self.db.sikayetleri_getir()
        self.filtreli_kayitlar = self.tum_kayitlar.copy()
        self.mevcut_sayfa = 1
        self._sayfalama_guncelle()
    
    def _sayfalama_guncelle(self):
        """Sayfalama bilgilerini güncelle ve kartları göster"""
        # Mevcut kartları temizle
        for widget in self.kart_panel.winfo_children():
            widget.destroy()
        
        toplam_kayit = len(self.filtreli_kayitlar)
        self.toplam_sayfa = max(1, (toplam_kayit + self.sayfa_basi_kayit - 1) // self.sayfa_basi_kayit)
        
        # Sayfa sınırlarını kontrol et
        if self.mevcut_sayfa > self.toplam_sayfa:
            self.mevcut_sayfa = self.toplam_sayfa
        if self.mevcut_sayfa < 1:
            self.mevcut_sayfa = 1
        
        # Bu sayfadaki kayıtları hesapla
        baslangic = (self.mevcut_sayfa - 1) * self.sayfa_basi_kayit
        bitis = baslangic + self.sayfa_basi_kayit
        sayfa_kayitlari = self.filtreli_kayitlar[baslangic:bitis]
        
        # Kartları oluştur
        for i, kayit in enumerate(sayfa_kayitlari):
            row = i // 3
            col = i % 3
            self.kart_olustur(kayit, row, col)
        
        # Sayfalama bilgilerini güncelle
        self.kayit_bilgi_label.configure(text=f"Toplam: {toplam_kayit} kayıt")
        self.sayfa_label.configure(text=f"Sayfa {self.mevcut_sayfa} / {self.toplam_sayfa}")
        
        # Buton durumlarını güncelle
        self.btn_ilk.configure(state="normal" if self.mevcut_sayfa > 1 else "disabled")
        self.btn_onceki.configure(state="normal" if self.mevcut_sayfa > 1 else "disabled")
        self.btn_sonraki.configure(state="normal" if self.mevcut_sayfa < self.toplam_sayfa else "disabled")
        self.btn_son.configure(state="normal" if self.mevcut_sayfa < self.toplam_sayfa else "disabled")
    
    def sayfaya_git(self, sayfa):
        """Belirtilen sayfaya git"""
        if 1 <= sayfa <= self.toplam_sayfa:
            self.mevcut_sayfa = sayfa
            self._sayfalama_guncelle()
    
    def sayfa_basi_degisti(self, deger):
        """Sayfa başı kayıt sayısı değişti"""
        self.sayfa_basi_kayit = int(deger)
        self.mevcut_sayfa = 1
        self._sayfalama_guncelle()
    
    def durum_filtre_sec(self, durum):
        """Durum filtre butonuna tıklandığında"""
        self.aktif_durum_filtre = durum
        self._filtre_butonlarini_guncelle()
        self.filtrele()
    
    def oncelik_filtre_sec(self, oncelik):
        """Öncelik filtre butonuna tıklandığında"""
        self.aktif_oncelik_filtre = oncelik
        self._filtre_butonlarini_guncelle()
        self.filtrele()
    
    def tur_filtre_sec(self, tur):
        """Tür filtre butonuna tıklandığında"""
        self.aktif_tur_filtre = tur
        self._filtre_butonlarini_guncelle()
        self.filtrele()
    
    def _filtre_butonlarini_guncelle(self):
        """Filtre butonlarının görünümünü güncelle"""
        # Durum butonları
        durum_renkleri = {"Tümü": "#64748b", "Yeni": "#ef4444", "İşlemde": "#f59e0b", "Çözüldü": "#22c55e"}
        for durum, btn in self.durum_butonlari.items():
            renk = durum_renkleri.get(durum, "#64748b")
            if durum == self.aktif_durum_filtre:
                btn.configure(fg_color=renk, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=renk)
        
        # Öncelik butonları
        oncelik_renkleri = {"Tümü": "#64748b", "Düşük": "#22c55e", "Orta": "#eab308", "Yüksek": "#f97316", "Acil": "#ef4444"}
        for oncelik, btn in self.oncelik_butonlari.items():
            renk = oncelik_renkleri.get(oncelik, "#64748b")
            if oncelik == self.aktif_oncelik_filtre:
                btn.configure(fg_color=renk, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=renk)
        
        # Tür butonları (kısa isimler)
        tur_renkleri = {
            "Tümü": "#64748b", "Personel": "#8b5cf6", "Rötar": "#ef4444",
            "Bagaj": "#f97316", "Hijyen": "#14b8a6", "İkram": "#3b82f6",
            "İade": "#ec4899", "Bilet": "#6366f1", "Diğer": "#94a3b8"
        }
        for tur, btn in self.tur_butonlari.items():
            renk = tur_renkleri.get(tur, "#64748b")
            if tur == self.aktif_tur_filtre:
                btn.configure(fg_color=renk, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=renk)
    
    def filtrele(self):
        """Arama ve filtreleme işlemi"""
        arama = self.entry_arama.get().strip().lower()
        
        # Verileri her zaman güncel al (kopya sorunu çözümü)
        self.tum_kayitlar = self.db.sikayetleri_getir()
        
        self.filtreli_kayitlar = []
        for kayit in self.tum_kayitlar:
            # Arama filtresi
            if arama:
                yolcu = str(kayit[2] or "").lower()
                pnr = str(kayit[5] or "").lower()
                sikayet_no = str(kayit[1] or "").lower()
                detay = str(kayit[8] or "").lower()
                guzergah = str(kayit[4] or "").lower()
                telefon = str(kayit[11] or "").lower() if len(kayit) > 11 else ""
                eposta = str(kayit[12] or "").lower() if len(kayit) > 12 else ""
                plaka = str(kayit[13] or "").lower() if len(kayit) > 13 else ""
                
                if not (arama in yolcu or arama in pnr or arama in sikayet_no or arama in detay or arama in guzergah or arama in telefon or arama in eposta or arama in plaka):
                    continue
            
            # Durum filtresi
            if self.aktif_durum_filtre != "Tümü":
                if kayit[10] != self.aktif_durum_filtre:
                    continue
            
            # Öncelik filtresi
            if self.aktif_oncelik_filtre != "Tümü":
                oncelik = kayit[16] if len(kayit) > 16 else ""
                if oncelik != self.aktif_oncelik_filtre:
                    continue
            
            # Tür filtresi
            if self.aktif_tur_filtre != "Tümü":
                tur = kayit[14] if len(kayit) > 14 else ""
                if tur != self.aktif_tur_filtre:
                    continue
            
            self.filtreli_kayitlar.append(kayit)
        
        # İlk sayfaya dön ve göster
        self.mevcut_sayfa = 1
        self._sayfalama_guncelle()
    
    def filtreleri_temizle(self):
        """Tüm filtreleri temizle"""
        self.entry_arama.delete(0, "end")
        self.aktif_durum_filtre = "Tümü"
        self.aktif_oncelik_filtre = "Tümü"
        self.aktif_tur_filtre = "Tümü"
        self._filtre_butonlarini_guncelle()
        self.listeyi_yenile()

    def pdf_indir_internal(self, secilen_kayit):

        # Ask for save location
        dosya_yolu = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Dosyası", "*.pdf")],
            initialfile=f"Sikayet_{secilen_kayit[1]}.pdf",
            title="PDF Olarak Kaydet"
        )
        
        if not dosya_yolu:
            return
            
        try:
            from reportlab.lib.colors import HexColor
            
            c = canvas.Canvas(dosya_yolu, pagesize=A5)
            width, height = A5
            
            # Renkler - Modern ve şık palet
            primary_color = HexColor("#0d1b2a")      # Lacivert (header)
            accent_color = HexColor("#1b4965")       # Koyu petrol mavisi (bölüm başlıkları)
            text_color = HexColor("#1b263b")         # Koyu lacivert (metin)
            light_gray = HexColor("#f8f9fa")         # Çok açık gri (kutular)
            border_color = HexColor("#dee2e6")       # Kenarlık gri
            white = HexColor("#ffffff")
            
            # Font ayarları
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                pdfmetrics.registerFont(TTFont('ArialBold', 'arialbd.ttf'))
                font_name = 'Arial'
                bold_font = 'ArialBold'
            except:
                font_name = 'Helvetica'
                bold_font = 'Helvetica-Bold'
            
            # ===== HEADER BÖLÜMÜ =====
            # Üst banner - Beyaz arka plan
            c.setFillColor(white)
            c.rect(0, height - 70, width, 70, fill=True, stroke=False)
            
            # Alt çizgi (ince gri)
            c.setStrokeColor(border_color)
            c.setLineWidth(1)
            c.line(20, height - 72, width - 20, height - 72)
            
            # Logo (sol üst)
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            if os.path.exists(logo_path):
                try:
                    logo = ImageReader(logo_path)
                    c.drawImage(logo, 20, height - 58, width=80, height=45, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    print(f"Logo yüklenemedi: {e}")
            
            # Başlık (sağda)
            c.setFillColor(text_color)
            c.setFont(bold_font, 16)
            c.drawRightString(width - 25, height - 30, "ŞİKAYET DETAY RAPORU")
            
            # Alt başlık - Şikayet No (başlığın altında, sağda)
            c.setFont(font_name, 9)
            c.setFillColor(HexColor("#6c757d"))
            c.drawRightString(width - 25, height - 45, f"Ref: {secilen_kayit[1]}")
            
            # ===== ANA İÇERİK =====
            y = height - 95
            
            # Bilgi Kartı Başlığı
            c.setFillColor(accent_color)
            c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
            c.setFillColor(white)
            c.setFont(bold_font, 11)
            c.drawString(30, y + 3, "YOLCU BİLGİLERİ")
            y -= 30
            
            # Yolcu bilgileri kutusu - 3 satır için yükseklik artırıldı
            c.setFillColor(light_gray)
            c.roundRect(20, y - 55, width - 40, 60, 5, fill=True, stroke=False)
            
            c.setFillColor(text_color)
            c.setFont(bold_font, 9)
            c.drawString(30, y - 5, "Ad Soyad:")
            c.setFont(font_name, 9)
            c.drawString(100, y - 5, str(secilen_kayit[2] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 20, "Telefon:")
            c.setFont(font_name, 9)
            telefon = str(secilen_kayit[11]) if len(secilen_kayit) > 11 and secilen_kayit[11] else "-"
            c.drawString(100, y - 20, telefon)
            
            # E-posta ayrı satırda (tam genişlik)
            c.setFont(bold_font, 9)
            c.drawString(30, y - 35, "E-posta:")
            c.setFont(font_name, 9)
            eposta = str(secilen_kayit[12]) if len(secilen_kayit) > 12 and secilen_kayit[12] else "-"
            c.drawString(100, y - 35, eposta)
            
            y -= 75
            
            # Sefer Bilgileri Başlığı
            c.setFillColor(accent_color)
            c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
            c.setFillColor(white)
            c.setFont(bold_font, 11)
            c.drawString(30, y + 3, "SEFER BİLGİLERİ")
            y -= 30
            
            # Sefer bilgileri kutusu - 5 satır için yükseklik artırıldı
            c.setFillColor(light_gray)
            c.roundRect(20, y - 85, width - 40, 90, 5, fill=True, stroke=False)
            
            c.setFillColor(text_color)
            
            # Sol sütun
            c.setFont(bold_font, 9)
            c.drawString(30, y - 5, "Güzergah:")
            c.setFont(font_name, 9)
            c.drawString(100, y - 5, str(secilen_kayit[4] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 20, "Sefer Tarihi:")
            c.setFont(font_name, 9)
            c.drawString(100, y - 20, str(secilen_kayit[3] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 35, "PNR:")
            c.setFont(font_name, 9)
            c.drawString(100, y - 35, str(secilen_kayit[5] or "-"))
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 50, "Satın Alınan Yer:")
            c.setFont(font_name, 9)
            satin_alinan = str(secilen_kayit[17]) if len(secilen_kayit) > 17 and secilen_kayit[17] else "-"
            c.drawString(120, y - 50, satin_alinan)
            
            c.setFont(bold_font, 9)
            c.drawString(30, y - 65, "Başvurulan Yer:")
            c.setFont(font_name, 9)
            basvurulan = str(secilen_kayit[18]) if len(secilen_kayit) > 18 and secilen_kayit[18] else "-"
            c.drawString(120, y - 65, basvurulan)
            
            # Sağ sütun
            c.setFont(bold_font, 9)
            c.drawString(220, y - 5, "Plaka:")
            c.setFont(font_name, 9)
            plaka = str(secilen_kayit[13]) if len(secilen_kayit) > 13 and secilen_kayit[13] else "-"
            c.drawString(270, y - 5, plaka)
            
            c.setFont(bold_font, 9)
            c.drawString(220, y - 20, "Kayıt Tarihi:")
            c.setFont(font_name, 9)
            c.drawString(290, y - 20, str(secilen_kayit[9] or "-")[:16])
            
            c.setFont(bold_font, 9)
            c.drawString(220, y - 35, "Bilet Ücreti:")
            c.setFont(font_name, 9)
            bilet_ucreti = str(secilen_kayit[19]) if len(secilen_kayit) > 19 and secilen_kayit[19] else "-"
            if bilet_ucreti and bilet_ucreti != "-":
                bilet_ucreti = f"{bilet_ucreti} TL"
            c.drawString(290, y - 35, bilet_ucreti)
            
            y -= 105
            
            # Şikayet Detayları Başlığı
            c.setFillColor(accent_color)
            c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
            c.setFillColor(white)
            c.setFont(bold_font, 11)
            c.drawString(30, y + 3, "ŞİKAYET DETAYLARI")
            y -= 30
            
            # Şikayet bilgileri kutusu
            c.setFillColor(light_gray)
            c.roundRect(20, y - 40, width - 40, 45, 5, fill=True, stroke=False)
            
            c.setFillColor(text_color)
            
            # Şikayet türü
            c.setFont(bold_font, 9)
            c.drawString(30, y - 8, "Şikayet Türü:")
            c.setFont(font_name, 9)
            sikayet_turu = str(secilen_kayit[14]) if len(secilen_kayit) > 14 and secilen_kayit[14] else "-"
            c.drawString(110, y - 8, sikayet_turu)
            
            # Öncelik
            c.setFont(bold_font, 9)
            c.drawString(220, y - 8, "Öncelik:")
            oncelik = str(secilen_kayit[16]) if len(secilen_kayit) > 16 and secilen_kayit[16] else "-"
            
            # Öncelik rengini ayarla
            if oncelik == "Acil":
                c.setFillColor(HexColor("#e74c3c"))
            elif oncelik == "Yüksek":
                c.setFillColor(HexColor("#e67e22"))
            elif oncelik == "Orta":
                c.setFillColor(HexColor("#f39c12"))
            else:
                c.setFillColor(HexColor("#27ae60"))
            c.setFont(bold_font, 9)
            c.drawString(270, y - 8, oncelik)
            c.setFillColor(text_color)
            
            # Durum
            c.setFont(bold_font, 9)
            c.drawString(30, y - 25, "Durum:")
            durum = str(secilen_kayit[10] or "Yeni")
            if durum == "Çözüldü":
                c.setFillColor(HexColor("#27ae60"))
            else:
                c.setFillColor(HexColor("#3498db"))
            c.setFont(bold_font, 9)
            c.drawString(110, y - 25, durum)
            c.setFillColor(text_color)
            
            y -= 60
            
            # Açıklama Başlığı
            c.setFillColor(accent_color)
            c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
            c.setFillColor(white)
            c.setFont(bold_font, 11)
            c.drawString(30, y + 3, "ŞİKAYET AÇIKLAMASI")
            y -= 30
            
            # Açıklama metni hazırlığı
            c.setFillColor(text_color)
            c.setFont(font_name, 9)
            detay_metni = str(secilen_kayit[8] or "Açıklama girilmemiş.")
            
            from reportlab.lib.utils import simpleSplit
            max_width = width - 70
            
            # Tüm satırları hesapla
            tum_satirlar = []
            lines = detay_metni.split('\n')
            for line in lines:
                if line.strip() == "":
                    tum_satirlar.append("")
                else:
                    wrapped_lines = simpleSplit(line, font_name, 9, max_width)
                    tum_satirlar.extend(wrapped_lines)
            
            # Kutu yüksekliğini hesapla (minimum 50, her satır için 14 piksel)
            satir_yuksekligi = 14
            min_kutu_yuksekligi = 50
            hesaplanan_yukseklik = len(tum_satirlar) * satir_yuksekligi + 25
            
            # Mevcut sayfada kalan alan
            footer_yuksekligi = 45
            kalan_alan = y - footer_yuksekligi
            
            # Kutu yüksekliği (kalan alana sığacak şekilde veya hesaplanan)
            kutu_yuksekligi = min(max(hesaplanan_yukseklik, min_kutu_yuksekligi), kalan_alan)
            
            # Açıklama kutusu - açık gri arka plan
            c.setFillColor(light_gray)
            kutu_y = y - kutu_yuksekligi
            c.roundRect(20, kutu_y, width - 40, kutu_yuksekligi, 5, fill=True, stroke=False)
            
            # Açıklama metnini yaz
            c.setFillColor(text_color)
            c.setFont(font_name, 9)
            text_y = y - 15
            sayfa_no = 1
            
            for satir in tum_satirlar:
                if text_y < footer_yuksekligi + 15:
                    # Yeni sayfa gerekiyor
                    # Footer çiz (beyaz arka plan)
                    c.setStrokeColor(border_color)
                    c.setLineWidth(1)
                    c.line(20, 38, width - 20, 38)
                    
                    c.setFillColor(white)
                    c.rect(0, 0, width, 38, fill=True, stroke=False)
                    
                    c.setFillColor(HexColor("#6c757d"))
                    c.setFont(font_name, 7)
                    c.drawString(25, 22, "Bu belge Şikayet Takip Sistemi tarafından otomatik olarak oluşturulmuştur.")
                    c.drawString(25, 10, f"Sayfa {sayfa_no}")
                    c.drawRightString(width - 25, 10, str(secilen_kayit[9])[:16])
                    
                    c.showPage()
                    sayfa_no += 1
                    
                    # Yeni sayfa - önce tam sayfa açık gri arka plan
                    c.setFillColor(light_gray)
                    c.roundRect(20, footer_yuksekligi + 5, width - 40, height - footer_yuksekligi - 60, 5, fill=True, stroke=False)
                    
                    # Yeni sayfa başlığı (beyaz arka plan, tutarlı stil)
                    c.setFillColor(white)
                    c.rect(0, height - 50, width, 50, fill=True, stroke=False)
                    
                    # Alt çizgi
                    c.setStrokeColor(border_color)
                    c.setLineWidth(1)
                    c.line(20, height - 52, width - 20, height - 52)
                    
                    c.setFillColor(text_color)
                    c.setFont(bold_font, 12)
                    c.drawString(25, height - 35, f"ŞİKAYET AÇIKLAMASI (Devam)")
                    
                    c.setFillColor(HexColor("#6c757d"))
                    c.setFont(font_name, 9)
                    c.drawRightString(width - 25, height - 35, f"Ref: {secilen_kayit[1]}")
                    
                    text_y = height - 70
                    c.setFillColor(text_color)
                    c.setFont(font_name, 9)
                
                c.drawString(30, text_y, satir)
                text_y -= satir_yuksekligi
            
            # ===== NOTLAR BÖLÜMÜ =====
            # Şikayete ait tüm notları al (hem sikayet_notlari hem de manuel işlemler)
            sikayet_id = secilen_kayit[0]
            
            # 1. sikayet_notlari tablosundan notları al
            tum_notlar = self.db.notlari_getir(sikayet_id)  # (id, kullanici_adi, not_metni, olusturma_tarihi)
            
            # 2. sikayet_islemleri tablosundan manuel işlemleri al
            tum_islemler = self.db.sikayet_islemlerini_getir(sikayet_id)
            
            # Otomatik logları filtrele, sadece kullanıcının manuel eklediği notları göster
            otomatik_anahtar_kelimeler = [
                "DURUM", "GÜNCELLE", "GUNCELLE", "YENİ", "YENI", "OLUŞTUR", "OLUSTUR",
                "SİL", "SIL", "DOSYA", "ETİKET", "ETIKET", "HATIRLATICI"
            ]
            
            # Birleştirilmiş not listesi oluştur
            islemler = []
            
            # sikayet_notlari'ndan gelen notları ekle (format: tarih, kullanici, tur, aciklama)
            if tum_notlar:
                for not_kayit in tum_notlar:
                    # not_kayit: (id, kullanici_adi, not_metni, olusturma_tarihi)
                    islemler.append((
                        not_kayit[0],           # id
                        not_kayit[3],           # tarih (olusturma_tarihi)
                        not_kayit[1],           # kullanici_adi
                        "NOT",                  # islem_turu
                        not_kayit[2],           # not_metni (aciklama)
                        None,                   # eski_durum
                        None                    # yeni_durum
                    ))
            
            # sikayet_islemleri'nden manuel işlemleri ekle
            if tum_islemler:
                for islem in tum_islemler:
                    islem_turu = islem[3] if len(islem) > 3 else ""
                    islem_turu_upper = islem_turu.upper()
                    # Otomatik işlem mi kontrol et
                    otomatik_mi = False
                    for anahtar in otomatik_anahtar_kelimeler:
                        if anahtar in islem_turu_upper:
                            otomatik_mi = True
                            break
                    if islem_turu and not otomatik_mi:
                        islemler.append(islem)
            
            # Tarihe göre sırala (en yeniden en eskiye)
            islemler.sort(key=lambda x: x[1] if x[1] else "", reverse=True)
            
            if islemler and len(islemler) > 0:
                # İşlemler için yeni sayfa kontrolü
                islem_baslik_yukseklik = 30
                islem_satir_yukseklik = 45
                toplam_islem_yukseklik = islem_baslik_yukseklik + (len(islemler) * islem_satir_yukseklik) + 20
                
                # Mevcut y pozisyonunu güncelle (açıklama kutusunun altı)
                y = text_y - 20
                
                # Yeterli alan yoksa yeni sayfa
                if y - toplam_islem_yukseklik < footer_yuksekligi + 20:
                    # Footer çiz
                    c.setStrokeColor(border_color)
                    c.setLineWidth(1)
                    c.line(20, 38, width - 20, 38)
                    
                    c.setFillColor(white)
                    c.rect(0, 0, width, 38, fill=True, stroke=False)
                    
                    c.setFillColor(HexColor("#6c757d"))
                    c.setFont(font_name, 7)
                    c.drawString(25, 22, "Bu belge Şikayet Takip Sistemi tarafından otomatik olarak oluşturulmuştur.")
                    c.drawString(25, 10, f"Sayfa {sayfa_no}")
                    c.drawRightString(width - 25, 10, str(secilen_kayit[9])[:16])
                    
                    c.showPage()
                    sayfa_no += 1
                    
                    # Yeni sayfa başlığı
                    c.setFillColor(white)
                    c.rect(0, height - 50, width, 50, fill=True, stroke=False)
                    
                    c.setStrokeColor(border_color)
                    c.setLineWidth(1)
                    c.line(20, height - 52, width - 20, height - 52)
                    
                    c.setFillColor(text_color)
                    c.setFont(bold_font, 12)
                    c.drawString(25, height - 35, f"NOTLAR VE İŞLEMLER")
                    
                    c.setFillColor(HexColor("#6c757d"))
                    c.setFont(font_name, 9)
                    c.drawRightString(width - 25, height - 35, f"Ref: {secilen_kayit[1]}")
                    
                    y = height - 75
                
                # Notlar başlığı - accent_color ile uyumlu
                c.setFillColor(accent_color)
                c.rect(20, y - 5, width - 40, 22, fill=True, stroke=False)
                c.setFillColor(white)
                c.setFont(bold_font, 11)
                c.drawString(30, y + 3, f"NOTLAR VE İŞLEMLER ({len(islemler)} kayıt)")
                y -= 35
                
                # Her not için kart
                for islem in islemler:
                    # islem: (id, tarih, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum)
                    islem_tarih = islem[1] if len(islem) > 1 else "-"
                    islem_kullanici = islem[2] if len(islem) > 2 else "-"
                    islem_turu = islem[3] if len(islem) > 3 else "-"
                    islem_aciklama = islem[4] if len(islem) > 4 else "-"
                    
                    # Açıklamayı satırlara böl
                    aciklama_satirlari = []
                    if islem_aciklama:
                        aciklama_text = str(islem_aciklama)
                        max_karakter = 45  # Bir satırda maksimum karakter
                        while len(aciklama_text) > 0:
                            if len(aciklama_text) <= max_karakter:
                                aciklama_satirlari.append(aciklama_text)
                                break
                            else:
                                # Kelime bölünmesini önle
                                kesim = aciklama_text[:max_karakter].rfind(' ')
                                if kesim == -1:
                                    kesim = max_karakter
                                aciklama_satirlari.append(aciklama_text[:kesim])
                                aciklama_text = aciklama_text[kesim:].strip()
                    
                    # Kart yüksekliğini hesapla (satır sayısına göre)
                    satir_sayisi = max(1, len(aciklama_satirlari))
                    kart_yuksekligi = 30 + (satir_sayisi * 12)
                    
                    # Yeni sayfa kontrolü - dinamik yükseklik
                    if y - kart_yuksekligi < footer_yuksekligi + 10:
                        # Footer çiz
                        c.setStrokeColor(border_color)
                        c.setLineWidth(1)
                        c.line(20, 38, width - 20, 38)
                        
                        c.setFillColor(white)
                        c.rect(0, 0, width, 38, fill=True, stroke=False)
                        
                        c.setFillColor(HexColor("#6c757d"))
                        c.setFont(font_name, 7)
                        c.drawString(25, 22, "Bu belge Şikayet Takip Sistemi tarafından otomatik olarak oluşturulmuştur.")
                        c.drawString(25, 10, f"Sayfa {sayfa_no}")
                        c.drawRightString(width - 25, 10, str(secilen_kayit[9])[:16])
                        
                        c.showPage()
                        sayfa_no += 1
                        
                        # Yeni sayfa başlığı
                        c.setFillColor(white)
                        c.rect(0, height - 50, width, 50, fill=True, stroke=False)
                        
                        c.setStrokeColor(border_color)
                        c.setLineWidth(1)
                        c.line(20, height - 52, width - 20, height - 52)
                        
                        c.setFillColor(text_color)
                        c.setFont(bold_font, 12)
                        c.drawString(25, height - 35, f"NOTLAR VE İŞLEMLER (Devam)")
                        
                        c.setFillColor(HexColor("#6c757d"))
                        c.setFont(font_name, 9)
                        c.drawRightString(width - 25, height - 35, f"Ref: {secilen_kayit[1]}")
                        
                        y = height - 75
                    
                    # Not kartı arka planı - dinamik yükseklik
                    c.setFillColor(light_gray)
                    c.roundRect(20, y - kart_yuksekligi + 5, width - 40, kart_yuksekligi, 5, fill=True, stroke=False)
                    
                    # İşlem türü ve tarih - accent_color ile uyumlu
                    c.setFillColor(accent_color)
                    c.setFont(bold_font, 9)
                    c.drawString(30, y - 8, f"• {islem_turu}")
                    
                    c.setFillColor(HexColor("#6c757d"))
                    c.setFont(font_name, 8)
                    c.drawRightString(width - 30, y - 8, str(islem_tarih)[:16])
                    
                    # Kullanıcı
                    c.setFillColor(text_color)
                    c.setFont(font_name, 8)
                    c.drawString(30, y - 20, f"{islem_kullanici}")
                    
                    # Açıklama satırları
                    aciklama_y = y - 20
                    c.setFont(font_name, 8)
                    for satir in aciklama_satirlari:
                        c.drawString(100, aciklama_y, satir)
                        aciklama_y -= 12
                    
                    y -= kart_yuksekligi + 5
            
            # ===== FOOTER =====
            # Üst çizgi (ince gri)
            c.setStrokeColor(border_color)
            c.setLineWidth(1)
            c.line(20, 38, width - 20, 38)
            
            c.setFillColor(white)
            c.rect(0, 0, width, 38, fill=True, stroke=False)
            
            c.setFillColor(HexColor("#6c757d"))
            c.setFont(font_name, 7)
            c.drawString(25, 22, "Bu belge Şikayet Takip Sistemi tarafından otomatik olarak oluşturulmuştur.")
            c.drawString(25, 10, f"Sayfa {sayfa_no}")
            c.drawRightString(width - 25, 10, str(secilen_kayit[9])[:16])
            
            c.save()
            
            # Open the file automatically
            try:
                dosya_ac(dosya_yolu)
            except:
                pass
                
        except Exception as e:
            self.controller.lift()
            self.controller.focus_force()
            messagebox.showerror("Hata", f"PDF oluşturulurken hata: {e}", parent=self.controller)
    
    def istatistik_goster(self):
        """İstatistik penceresini aç"""
        IstatistikPenceresi(self.controller, self.db)


class IstatistikPenceresi(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("📊 Şikayet İstatistikleri")
        self.geometry("700x600")
        self.attributes("-topmost", True)
        
        # Ana scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        ctk.CTkLabel(self.scroll_frame, text="📊 ŞİKAYET İSTATİSTİKLERİ", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))
        
        # Verileri al
        kayitlar = self.db.sikayetleri_getir()
        toplam = len(kayitlar)
        
        if toplam == 0:
            ctk.CTkLabel(self.scroll_frame, text="Henüz kayıtlı şikayet bulunmamaktadır.", font=ctk.CTkFont(size=14)).pack(pady=50)
            return
        
        # Durum istatistikleri
        durum_sayilari = {"Yeni": 0, "İşlemde": 0, "Çözüldü": 0}
        oncelik_sayilari = {"Düşük": 0, "Orta": 0, "Yüksek": 0, "Acil": 0}
        tur_sayilari = {}
        platform_sayilari = {}
        
        for kayit in kayitlar:
            # Durum
            durum = kayit[10] or "Yeni"
            if durum in durum_sayilari:
                durum_sayilari[durum] += 1
            else:
                durum_sayilari[durum] = 1
            
            # Öncelik
            if len(kayit) > 16 and kayit[16]:
                oncelik = kayit[16]
                if oncelik in oncelik_sayilari:
                    oncelik_sayilari[oncelik] += 1
            
            # Şikayet türü
            if len(kayit) > 14 and kayit[14]:
                tur = kayit[14]
                tur_sayilari[tur] = tur_sayilari.get(tur, 0) + 1
            
            # Platform
            if kayit[7]:
                platform = kayit[7]
                platform_sayilari[platform] = platform_sayilari.get(platform, 0) + 1
        
        # === ÖZET KARTLARI ===
        ozet_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        ozet_frame.pack(fill="x", pady=(0, 20))
        
        kartlar = [
            ("📋 TOPLAM", toplam, "#3498db"),
            ("🆕 YENİ", durum_sayilari.get("Yeni", 0), "#e74c3c"),
            ("⏳ İŞLEMDE", durum_sayilari.get("İşlemde", 0), "#f39c12"),
            ("✅ ÇÖZÜLDÜ", durum_sayilari.get("Çözüldü", 0), "#27ae60"),
        ]
        
        for i, (baslik, sayi, renk) in enumerate(kartlar):
            kart = ctk.CTkFrame(ozet_frame, fg_color=renk, corner_radius=10, width=150, height=100)
            kart.pack(side="left", expand=True, fill="x", padx=5)
            kart.pack_propagate(False)
            
            ctk.CTkLabel(kart, text=baslik, font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(pady=(15, 5))
            ctk.CTkLabel(kart, text=str(sayi), font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack()
        
        # === ÖNCELİK DAĞILIMI ===
        self.bolum_baslik("🎯 Öncelik Dağılımı")
        
        oncelik_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "gray25"), corner_radius=10)
        oncelik_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        oncelik_renkler = {"Düşük": "#27ae60", "Orta": "#f39c12", "Yüksek": "#e67e22", "Acil": "#e74c3c"}
        
        for oncelik, sayi in oncelik_sayilari.items():
            if sayi > 0:
                row = ctk.CTkFrame(oncelik_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=5)
                
                ctk.CTkLabel(row, text=oncelik, font=ctk.CTkFont(weight="bold"), width=80, anchor="w").pack(side="left")
                
                # Progress bar
                yuzde = (sayi / toplam) * 100
                bar_frame = ctk.CTkFrame(row, fg_color=("gray80", "gray40"), corner_radius=5, height=20)
                bar_frame.pack(side="left", fill="x", expand=True, padx=10)
                bar_frame.pack_propagate(False)
                
                if yuzde > 0:
                    fill_bar = ctk.CTkFrame(bar_frame, fg_color=oncelik_renkler[oncelik], corner_radius=5)
                    fill_bar.place(relx=0, rely=0, relwidth=yuzde/100, relheight=1)
                
                ctk.CTkLabel(row, text=f"{sayi} (%{yuzde:.1f})", font=ctk.CTkFont(size=12), width=80).pack(side="right")
        
        # === ŞİKAYET TÜRÜ DAĞILIMI ===
        if tur_sayilari:
            self.bolum_baslik("📁 Şikayet Türü Dağılımı")
            
            tur_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "gray25"), corner_radius=10)
            tur_frame.pack(fill="x", pady=(0, 20), padx=5)
            
            # Sırala (en çoktan aza)
            sirali_turler = sorted(tur_sayilari.items(), key=lambda x: x[1], reverse=True)
            
            for tur, sayi in sirali_turler:
                if tur and tur != "Seçiniz":
                    row = ctk.CTkFrame(tur_frame, fg_color="transparent")
                    row.pack(fill="x", padx=15, pady=5)
                    
                    ctk.CTkLabel(row, text=tur[:25], font=ctk.CTkFont(weight="bold"), width=180, anchor="w").pack(side="left")
                    
                    yuzde = (sayi / toplam) * 100
                    bar_frame = ctk.CTkFrame(row, fg_color=("gray80", "gray40"), corner_radius=5, height=20)
                    bar_frame.pack(side="left", fill="x", expand=True, padx=10)
                    bar_frame.pack_propagate(False)
                    
                    if yuzde > 0:
                        fill_bar = ctk.CTkFrame(bar_frame, fg_color="#3498db", corner_radius=5)
                        fill_bar.place(relx=0, rely=0, relwidth=yuzde/100, relheight=1)
                    
                    ctk.CTkLabel(row, text=f"{sayi} (%{yuzde:.1f})", font=ctk.CTkFont(size=12), width=80).pack(side="right")
        
        # === PLATFORM DAĞILIMI ===
        if platform_sayilari:
            self.bolum_baslik("📱 Platform Dağılımı")
            
            platform_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "gray25"), corner_radius=10)
            platform_frame.pack(fill="x", pady=(0, 20), padx=5)
            
            for platform, sayi in platform_sayilari.items():
                row = ctk.CTkFrame(platform_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=5)
                
                ctk.CTkLabel(row, text=platform, font=ctk.CTkFont(weight="bold"), width=120, anchor="w").pack(side="left")
                
                yuzde = (sayi / toplam) * 100
                bar_frame = ctk.CTkFrame(row, fg_color=("gray80", "gray40"), corner_radius=5, height=20)
                bar_frame.pack(side="left", fill="x", expand=True, padx=10)
                bar_frame.pack_propagate(False)
                
                if yuzde > 0:
                    fill_bar = ctk.CTkFrame(bar_frame, fg_color="#9b59b6", corner_radius=5)
                    fill_bar.place(relx=0, rely=0, relwidth=yuzde/100, relheight=1)
                
                ctk.CTkLabel(row, text=f"{sayi} (%{yuzde:.1f})", font=ctk.CTkFont(size=12), width=80).pack(side="right")
        
        # Kapat butonu
        ctk.CTkButton(self.scroll_frame, text="Kapat", command=self.destroy, width=200, height=40).pack(pady=20)
    
    def bolum_baslik(self, text):
        ctk.CTkLabel(self.scroll_frame, text=text, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x", pady=(10, 5), padx=5)


class Ayarlar(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=("white", "gray17"))
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=0, column=0)
        
        ctk.CTkLabel(self.center_frame, text="AYARLAR", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(0, 40))
        
        # Tema Seçimi
        ctk.CTkLabel(self.center_frame, text="Görünüm Modu:", font=ctk.CTkFont(size=16)).pack(pady=(0, 10))
        
        self.seg_tema = ctk.CTkSegmentedButton(self.center_frame, values=["Light", "Dark", "System"], command=self.tema_degistir)
        self.seg_tema.set(ctk.get_appearance_mode())
        self.seg_tema.pack(pady=(0, 40))
        
        # Kullanıcı Yönetimi (Sadece Admin için) - Başlangıçta gizli
        self.btn_kullanici_yonetimi = ctk.CTkButton(
            self.center_frame, 
            text="👥 KULLANICI YÖNETİMİ", 
            command=self.kullanici_yonetimi_ac,
            width=300, height=50, 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1F6AA5", hover_color="#144870"
        )
        # Başlangıçta pack etme, kullanici_gorunumu_guncelle ile kontrol edilecek
        
        # Şifre Değiştir
        self.btn_sifre_degistir = ctk.CTkButton(
            self.center_frame, 
            text="🔐 ŞİFRE DEĞİŞTİR", 
            command=self.sifre_degistir_ac,
            width=300, height=50, 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#E59400", hover_color="#B37400"
        )
        self.btn_sifre_degistir.pack(pady=(0, 20))
        
        # İşlem Geçmişi (Sadece Admin için)
        self.btn_islem_gecmisi = ctk.CTkButton(
            self.center_frame, 
            text="📋 İŞLEM GEÇMİŞİ", 
            command=self.islem_gecmisi_ac,
            width=300, height=50, 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#9b59b6", hover_color="#8e44ad"
        )
        # Başlangıçta pack etme
        
        # Yedekleme Yönetimi
        self.btn_yedekleme = ctk.CTkButton(
            self.center_frame, 
            text="💾 YEDEKLEME YÖNETİMİ", 
            command=self.yedekleme_ac,
            width=300, height=50, 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#27ae60", hover_color="#1e8449"
        )
        self.btn_yedekleme.pack(pady=(0, 20))
        
        # Geri Dön Butonu
        self.btn_geri = ctk.CTkButton(self.center_frame, text="ANA MENÜYE DÖN", command=lambda: controller.show_frame("AnaEkran"), width=300, height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_geri.pack()

    def tema_degistir(self, value):
        ctk.set_appearance_mode(value)
    
    def kullanici_gorunumu_guncelle(self):
        # Admin değilse kullanıcı yönetimi butonunu gizle
        if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
            # Önce tüm butonları gizle
            self.btn_kullanici_yonetimi.pack_forget()
            self.btn_sifre_degistir.pack_forget()
            self.btn_islem_gecmisi.pack_forget()
            self.btn_yedekleme.pack_forget()
            self.btn_geri.pack_forget()
            
            # Admin ise kullanıcı yönetimi ve işlem geçmişi butonlarını göster
            if self.controller.aktif_kullanici.get('rol') == 'admin':
                self.btn_kullanici_yonetimi.pack(pady=(0, 20))
                self.btn_islem_gecmisi.pack(pady=(0, 20))
            
            # Şifre değiştir butonunu yeniden pack et
            self.btn_sifre_degistir.pack(pady=(0, 20))
            
            # Yedekleme butonu (herkes görebilir)
            self.btn_yedekleme.pack(pady=(0, 20))
            
            # Geri dön butonu
            self.btn_geri.pack()
    
    def kullanici_yonetimi_ac(self):
        if self.controller.aktif_kullanici.get('rol') != 'admin':
            self.controller.lift()
            self.controller.focus_force()
            messagebox.showerror("Yetki Hatası", "Bu işlem için admin yetkisi gereklidir.", parent=self.controller)
            return
        KullaniciYonetimi(self.controller, self.controller.db)
    
    def islem_gecmisi_ac(self):
        if self.controller.aktif_kullanici.get('rol') != 'admin':
            self.controller.lift()
            self.controller.focus_force()
            messagebox.showerror("Yetki Hatası", "Bu işlem için admin yetkisi gereklidir.", parent=self.controller)
            return
        IslemGecmisiPenceresi(self.controller, self.controller.db)
    
    def yedekleme_ac(self):
        YedeklemePenceresi(self.controller, self.controller.db)
    
    def sifre_degistir_ac(self):
        SifreDegistir(self.controller, self.controller.db, self.controller.aktif_kullanici)


class CopKutusuPenceresi(ctk.CTkToplevel):
    """Çöp Kutusu - Silinen şikayetleri görüntüleme ve geri yükleme"""
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.controller = parent
        self.db = db
        self.title("🗑️ Çöp Kutusu")
        self.geometry("900x600")
        self.attributes("-topmost", True)
        
        # Üst Panel
        ust_panel = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=("gray95", "gray25"))
        ust_panel.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(ust_panel, text="🗑️ Çöp Kutusu", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=20, pady=20)
        
        # Çöp kutusunu boşalt butonu
        self.btn_bosalt = ctk.CTkButton(
            ust_panel, 
            text="🧹 Tümünü Kalıcı Sil", 
            command=self.cop_kutusunu_bosalt,
            fg_color="#e74c3c", hover_color="#c0392b",
            font=ctk.CTkFont(weight="bold"),
            width=160, height=40
        )
        self.btn_bosalt.pack(side="right", padx=20, pady=20)
        
        # Bilgi paneli
        bilgi_frame = ctk.CTkFrame(self, fg_color=("white", "gray20"))
        bilgi_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(bilgi_frame, text="💡 Silinen şikayetler buraya taşınır. Geri yükleyebilir veya kalıcı olarak silebilirsiniz.", 
                    font=ctk.CTkFont(size=12)).pack(pady=10)
        
        # Tablo Frame
        tablo_frame = ctk.CTkFrame(self, fg_color="transparent")
        tablo_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Tablo
        style = ttk.Style()
        style.configure("CopKutusu.Treeview", rowheight=35, font=("Arial", 10))
        style.configure("CopKutusu.Treeview.Heading", font=("Arial", 11, "bold"))
        
        columns = ("id", "sikayet_no", "yolcu_adi", "guzergah", "durum", "silinme_tarihi", "silen")
        self.tree = ttk.Treeview(tablo_frame, columns=columns, show="headings", selectmode="browse", style="CopKutusu.Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("sikayet_no", text="Şikayet No")
        self.tree.heading("yolcu_adi", text="Yolcu Adı")
        self.tree.heading("guzergah", text="Güzergah")
        self.tree.heading("durum", text="Durum")
        self.tree.heading("silinme_tarihi", text="Silinme Tarihi")
        self.tree.heading("silen", text="Silen Kullanıcı")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("sikayet_no", width=100, anchor="center")
        self.tree.column("yolcu_adi", width=150, anchor="w")
        self.tree.column("guzergah", width=150, anchor="w")
        self.tree.column("durum", width=100, anchor="center")
        self.tree.column("silinme_tarihi", width=140, anchor="center")
        self.tree.column("silen", width=120, anchor="center")
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(tablo_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(tablo_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        
        # Alt buton paneli
        alt_panel = ctk.CTkFrame(self, fg_color="transparent")
        alt_panel.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            alt_panel, 
            text="♻️ Seçileni Geri Yükle", 
            command=self.secili_geri_yukle,
            fg_color="#27ae60", hover_color="#1e8449",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180, height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            alt_panel, 
            text="🗑️ Seçileni Kalıcı Sil", 
            command=self.secili_kalici_sil,
            fg_color="#e74c3c", hover_color="#c0392b",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180, height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            alt_panel, 
            text="🔄 Yenile", 
            command=self.listeyi_yenile,
            fg_color="#3498db", hover_color="#2980b9",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120, height=40
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            alt_panel, 
            text="Kapat", 
            command=self.destroy,
            fg_color="gray", hover_color="gray30",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100, height=40
        ).pack(side="right", padx=5)
        
        # Listeyi yükle
        self.listeyi_yenile()
    
    def listeyi_yenile(self):
        """Çöp kutusundaki kayıtları listele"""
        # Tabloyu temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Verileri getir
        kayitlar = self.db.cop_kutusunu_getir()
        
        for kayit in kayitlar:
            # (id, sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, sikayet_detay, durum, silinme_tarihi, silen_kullanici_adi)
            cop_id = kayit[0]
            sikayet_no = kayit[1] or "-"
            yolcu_adi = kayit[2] or "-"
            guzergah = kayit[4] or "-"
            durum = kayit[6] or "-"
            silinme_tarihi = kayit[7] or "-"
            silen = kayit[8] or "-"
            
            self.tree.insert("", "end", values=(cop_id, sikayet_no, yolcu_adi, guzergah, durum, silinme_tarihi, silen))
        
        # Kayıt sayısını göster
        kayit_sayisi = len(kayitlar)
        if kayit_sayisi == 0:
            self.btn_bosalt.configure(state="disabled")
        else:
            self.btn_bosalt.configure(state="normal")
    
    def secili_geri_yukle(self):
        """Seçili şikayeti geri yükle"""
        selected = self.tree.selection()
        if not selected:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen geri yüklenecek bir kayıt seçin.", parent=self)
            return
        
        item = self.tree.item(selected[0])
        cop_id = item['values'][0]
        sikayet_no = item['values'][1]
        
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", f"{sikayet_no} numaralı şikayeti geri yüklemek istiyor musunuz?", parent=self)
        if onay:
            basarili, mesaj = self.db.cop_kutusundan_geri_al(cop_id)
            if basarili:
                messagebox.showinfo("Başarılı", "Şikayet başarıyla geri yüklendi!", parent=self)
                self.listeyi_yenile()
                # Ana listeyi de yenile
                if hasattr(self.controller, 'frames') and 'SikayetArsivi' in self.controller.frames:
                    self.controller.frames['SikayetArsivi'].listeyi_yenile()
            else:
                messagebox.showerror("Hata", mesaj, parent=self)
    
    def secili_kalici_sil(self):
        """Seçili şikayeti kalıcı olarak sil"""
        selected = self.tree.selection()
        if not selected:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen silinecek bir kayıt seçin.", parent=self)
            return
        
        item = self.tree.item(selected[0])
        cop_id = item['values'][0]
        sikayet_no = item['values'][1]
        
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Dikkat!", f"{sikayet_no} numaralı şikayeti KALICI olarak silmek istiyor musunuz?\n\nBu işlem geri alınamaz!", parent=self)
        if onay:
            basarili, mesaj = self.db.cop_kutusundan_kalici_sil(cop_id)
            if basarili:
                messagebox.showinfo("Başarılı", "Kayıt kalıcı olarak silindi.", parent=self)
                self.listeyi_yenile()
            else:
                messagebox.showerror("Hata", mesaj, parent=self)
    
    def cop_kutusunu_bosalt(self):
        """Çöp kutusunu tamamen boşalt"""
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("DİKKAT!", "Çöp kutusundaki TÜM kayıtlar kalıcı olarak silinecek!\n\nBu işlem geri alınamaz! Devam etmek istiyor musunuz?", parent=self)
        if onay:
            onay2 = messagebox.askyesno("Son Onay", "Emin misiniz? Bu işlem geri alınamaz!", parent=self)
            if onay2:
                basarili, mesaj = self.db.cop_kutusunu_bosalt()
                if basarili:
                    messagebox.showinfo("Başarılı", "Çöp kutusu boşaltıldı.", parent=self)
                    self.listeyi_yenile()
                else:
                    messagebox.showerror("Hata", mesaj, parent=self)


class YedeklemePenceresi(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.controller = parent  # parent aynı zamanda controller
        self.db = db
        self.title("💾 Yedekleme Yönetimi")
        self.geometry("700x550")
        self.attributes("-topmost", True)
        
        # Üst Panel
        ust_panel = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=("gray95", "gray25"))
        ust_panel.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(ust_panel, text="💾 Yedekleme Yönetimi", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=20, pady=20)
        
        # Manuel yedek al butonu
        ctk.CTkButton(
            ust_panel, 
            text="📥 Şimdi Yedek Al", 
            command=self.manuel_yedek_al,
            fg_color="#27ae60", hover_color="#1e8449",
            font=ctk.CTkFont(weight="bold"),
            width=150, height=40
        ).pack(side="right", padx=20, pady=20)
        
        # Bilgi paneli
        bilgi_frame = ctk.CTkFrame(self, fg_color=("white", "gray20"))
        bilgi_frame.pack(fill="x", padx=20, pady=10)
        
        # Son yedek bilgisi
        son_yedek = self.db.son_yedek_tarihi()
        if son_yedek:
            son_yedek_text = f"Son otomatik yedek: {son_yedek}"
        else:
            son_yedek_text = "Henüz otomatik yedek alınmamış"
        
        ctk.CTkLabel(bilgi_frame, text=son_yedek_text, font=ctk.CTkFont(size=13)).pack(pady=10)
        ctk.CTkLabel(bilgi_frame, text="📁 Yedekler 'yedekler' klasöründe saklanır. 30 günden eski yedekler otomatik silinir.", 
                    font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 10))
        
        # Yedek listesi başlığı
        ctk.CTkLabel(self, text="Mevcut Yedekler:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        # Tablo Frame
        tablo_frame = ctk.CTkFrame(self, fg_color="transparent")
        tablo_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Tablo
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=30, font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        columns = ("dosya", "tarih", "tip", "boyut")
        self.tree = ttk.Treeview(tablo_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("dosya", text="Dosya Adı")
        self.tree.heading("tarih", text="Tarih")
        self.tree.heading("tip", text="Tür")
        self.tree.heading("boyut", text="Boyut")
        
        self.tree.column("dosya", width=280)
        self.tree.column("tarih", width=150, anchor="center")
        self.tree.column("tip", width=100, anchor="center")
        self.tree.column("boyut", width=100, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tablo_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Alt Panel
        alt_panel = ctk.CTkFrame(self, height=60, corner_radius=0)
        alt_panel.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkButton(alt_panel, text="Kapat", command=self.destroy, width=100).pack(side="right", padx=20, pady=15)
        
        ctk.CTkButton(
            alt_panel, 
            text="🔄 Geri Yükle", 
            command=self.geri_yukle,
            fg_color="#e67e22", hover_color="#d35400",
            width=120
        ).pack(side="right", padx=5, pady=15)
        
        ctk.CTkButton(
            alt_panel, 
            text="🗑️ Sil", 
            command=self.yedek_sil,
            fg_color="#e74c3c", hover_color="#c0392b",
            width=80
        ).pack(side="right", padx=5, pady=15)
        
        self.listeyi_yenile()
    
    def listeyi_yenile(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        yedekler = self.db.yedekleri_listele()
        
        for yedek in yedekler:
            # Boyutu formatla
            boyut = yedek["boyut"]
            if boyut > 1024 * 1024:
                boyut_str = f"{boyut / (1024*1024):.1f} MB"
            elif boyut > 1024:
                boyut_str = f"{boyut / 1024:.1f} KB"
            else:
                boyut_str = f"{boyut} B"
            
            self.tree.insert("", "end", values=(
                yedek["dosya"],
                yedek["tarih"],
                yedek["tip"],
                boyut_str
            ), tags=(yedek["yol"],))
    
    def manuel_yedek_al(self):
        basarili, sonuc = self.db.yedek_al(manuel=True)
        
        if basarili:
            # İşlem kaydı
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                self.db.islem_kaydet(
                    kullanici_id=self.controller.aktif_kullanici.get('id'),
                    kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                    islem_turu="MANUEL YEDEK",
                    islem_detay="Manuel yedek alındı"
                )
            
            self.lift()
            self.focus_force()
            messagebox.showinfo("Başarılı", f"Yedek başarıyla alındı!\n\n{sonuc}", parent=self)
            self.listeyi_yenile()
        else:
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", f"Yedek alınamadı!\n\n{sonuc}", parent=self)
    
    def geri_yukle(self):
        secili = self.tree.selection()
        if not secili:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen geri yüklemek için bir yedek seçin.", parent=self)
            return
        
        item = self.tree.item(secili)
        dosya_adi = item['values'][0]
        yedek_yolu = item['tags'][0]
        
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno(
            "Dikkat!", 
            f"'{dosya_adi}' yedeğini geri yüklemek istediğinize emin misiniz?\n\n"
            "⚠️ Mevcut tüm veriler bu yedekle değiştirilecek!\n"
            "⚠️ Bu işlem geri alınamaz!",
            icon="warning",
            parent=self
        )
        
        if onay:
            basarili, mesaj = self.db.yedekten_geri_yukle(yedek_yolu)
            
            if basarili:
                self.lift()
                self.focus_force()
                messagebox.showinfo("Başarılı", "Yedek başarıyla geri yüklendi!\n\nUygulama yeniden başlatılacak.", parent=self)
                self.destroy()
                # Uygulamayı yeniden başlat
                import sys
                import os
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                self.lift()
                self.focus_force()
                messagebox.showerror("Hata", f"Geri yükleme başarısız!\n\n{mesaj}", parent=self)
    
    def yedek_sil(self):
        secili = self.tree.selection()
        if not secili:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir yedek seçin.", parent=self)
            return
        
        item = self.tree.item(secili)
        dosya_adi = item['values'][0]
        yedek_yolu = item['tags'][0]
        
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", f"'{dosya_adi}' yedeğini silmek istediğinize emin misiniz?", parent=self)
        
        if onay:
            try:
                import os
                os.remove(yedek_yolu)
                self.lift()
                self.focus_force()
                messagebox.showinfo("Başarılı", "Yedek silindi.", parent=self)
                self.listeyi_yenile()
            except Exception as e:
                self.lift()
                self.focus_force()
                messagebox.showerror("Hata", f"Yedek silinemedi!\n\n{e}", parent=self)


class IslemGecmisiPenceresi(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("📋 İşlem Geçmişi")
        self.geometry("1000x600")
        self.attributes("-topmost", True)
        
        # Üst Panel
        ust_panel = ctk.CTkFrame(self, height=60, corner_radius=0)
        ust_panel.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(ust_panel, text="📋 İşlem Geçmişi", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(ust_panel, text="🔄 Yenile", command=self.listeyi_yenile, width=100).pack(side="right", padx=20, pady=15)
        
        # Tablo
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=30, font=("Arial", 9))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        # Tablo Frame
        tablo_frame = ctk.CTkFrame(self, fg_color="transparent")
        tablo_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("id", "tarih", "kullanici", "islem_turu", "detay", "kayit_no", "degisiklik")
        self.tree = ttk.Treeview(tablo_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("tarih", text="Tarih")
        self.tree.heading("kullanici", text="Kullanıcı")
        self.tree.heading("islem_turu", text="İşlem Türü")
        self.tree.heading("detay", text="Detay")
        self.tree.heading("kayit_no", text="Şikayet No")
        self.tree.heading("degisiklik", text="Değişiklik")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("tarih", width=150, anchor="center")
        self.tree.column("kullanici", width=120)
        self.tree.column("islem_turu", width=140)
        self.tree.column("detay", width=200)
        self.tree.column("kayit_no", width=120, anchor="center")
        self.tree.column("degisiklik", width=180)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tablo_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Alt Panel
        alt_panel = ctk.CTkFrame(self, height=60, corner_radius=0)
        alt_panel.pack(fill="x", padx=0, pady=0)
        
        # İşlem türü renkleri
        ctk.CTkLabel(alt_panel, text="Renk Kodları:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20, pady=15)
        
        renkler = [
            ("🟢 Yeni Şikayet", "#27ae60"),
            ("🔵 Güncelleme", "#3498db"),
            ("🟠 Durum Değişikliği", "#f39c12"),
            ("🔴 Silme", "#e74c3c"),
        ]
        
        for text, renk in renkler:
            ctk.CTkLabel(alt_panel, text=text, font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
        
        ctk.CTkButton(alt_panel, text="Kapat", command=self.destroy, width=100).pack(side="right", padx=20, pady=15)
        
        self.listeyi_yenile()
    
    def listeyi_yenile(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        islemler = self.db.islem_gecmisini_getir(200)
        
        for islem in islemler:
            # id, tarih, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_no, eski_deger, yeni_deger
            degisiklik = ""
            if islem[6] and islem[7]:
                degisiklik = f"{islem[6]} → {islem[7]}"
            
            self.tree.insert("", "end", values=(
                islem[0],  # id
                islem[1],  # tarih
                islem[2] or "-",  # kullanici_adi
                islem[3],  # islem_turu
                islem[4] or "-",  # islem_detay
                islem[5] or "-",  # ilgili_kayit_no
                degisiklik
            ))


class KullaniciYonetimi(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.controller = parent  # parent aynı zamanda controller
        self.db = db
        self.title("Kullanıcı Yönetimi")
        self.geometry("800x500")
        self.attributes("-topmost", True)
        
        # Üst Panel
        ust_panel = ctk.CTkFrame(self, height=60, corner_radius=0)
        ust_panel.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(ust_panel, text="👥 Kullanıcı Yönetimi", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(ust_panel, text="+ Yeni Kullanıcı", command=self.yeni_kullanici, fg_color="#2CC985", hover_color="#229C68").pack(side="right", padx=20, pady=15)
        
        # Tablo
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=35, font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        columns = ("id", "kullanici_adi", "ad_soyad", "email", "rol", "aktif", "son_giris")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("kullanici_adi", text="Kullanıcı Adı")
        self.tree.heading("ad_soyad", text="Ad Soyad")
        self.tree.heading("email", text="E-posta")
        self.tree.heading("rol", text="Rol")
        self.tree.heading("aktif", text="Durum")
        self.tree.heading("son_giris", text="Son Giriş")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("kullanici_adi", width=120)
        self.tree.column("ad_soyad", width=150)
        self.tree.column("email", width=180)
        self.tree.column("rol", width=80, anchor="center")
        self.tree.column("aktif", width=80, anchor="center")
        self.tree.column("son_giris", width=140, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Alt Panel
        alt_panel = ctk.CTkFrame(self, height=60, corner_radius=0)
        alt_panel.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkButton(alt_panel, text="Sil", command=self.kullanici_sil, fg_color="#FF4D4D", hover_color="#CC0000").pack(side="right", padx=20, pady=15)
        ctk.CTkButton(alt_panel, text="Düzenle", command=self.kullanici_duzenle, fg_color="#1F6AA5", hover_color="#144870").pack(side="right", padx=5, pady=15)
        ctk.CTkButton(alt_panel, text="Şifre Sıfırla", command=self.sifre_sifirla, fg_color="#E59400", hover_color="#B37400").pack(side="right", padx=5, pady=15)
        
        self.listeyi_yenile()
    
    def listeyi_yenile(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        kullanicilar = self.db.kullanicilari_getir()
        for k in kullanicilar:
            durum = "Aktif" if k[5] == 1 else "Pasif"
            son_giris = k[7] if k[7] else "-"
            self.tree.insert("", "end", values=(k[0], k[1], k[2], k[3], k[4], durum, son_giris))
    
    def yeni_kullanici(self):
        dialog = KullaniciDialog(self, self.db)
        self.wait_window(dialog)
        self.listeyi_yenile()
    
    def kullanici_duzenle(self):
        secili = self.tree.selection()
        if not secili:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen bir kullanıcı seçin.", parent=self)
            return
        
        item = self.tree.item(secili)
        kullanici_id = item['values'][0]
        
        kullanicilar = self.db.kullanicilari_getir()
        secilen = None
        for k in kullanicilar:
            if k[0] == kullanici_id:
                secilen = k
                break
        
        if secilen:
            dialog = KullaniciDialog(self, self.db, secilen)
            self.wait_window(dialog)
            self.listeyi_yenile()
    
    def kullanici_sil(self):
        secili = self.tree.selection()
        if not secili:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen bir kullanıcı seçin.", parent=self)
            return
        
        item = self.tree.item(secili)
        kullanici_id = item['values'][0]
        kullanici_adi = item['values'][1]
        
        if kullanici_adi == "admin":
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", "Admin kullanıcısı silinemez!", parent=self)
            return
        
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", f"'{kullanici_adi}' kullanıcısını silmek istediğinize emin misiniz?", parent=self)
        if onay:
            # İşlem kaydı
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                self.db.islem_kaydet(
                    kullanici_id=self.controller.aktif_kullanici.get('id'),
                    kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                    islem_turu="KULLANICI SİLME",
                    islem_detay=f"{kullanici_adi} kullanıcısı silindi"
                )
            
            self.db.kullanici_sil(kullanici_id)
            self.listeyi_yenile()
    
    def sifre_sifirla(self):
        secili = self.tree.selection()
        if not secili:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Lütfen bir kullanıcı seçin.", parent=self)
            return
        
        item = self.tree.item(secili)
        kullanici_id = item['values'][0]
        kullanici_adi = item['values'][1]
        
        self.lift()
        self.focus_force()
        onay = messagebox.askyesno("Onay", f"'{kullanici_adi}' kullanıcısının şifresini '123456' olarak sıfırlamak istiyor musunuz?", parent=self)
        if onay:
            # İşlem kaydı
            if hasattr(self.controller, 'aktif_kullanici') and self.controller.aktif_kullanici:
                self.db.islem_kaydet(
                    kullanici_id=self.controller.aktif_kullanici.get('id'),
                    kullanici_adi=self.controller.aktif_kullanici.get('kullanici_adi'),
                    islem_turu="ŞİFRE SIFIRLAMA",
                    islem_detay=f"{kullanici_adi} kullanıcısının şifresi sıfırlandı"
                )
            
            self.db.sifre_degistir(kullanici_id, "123456")
            self.lift()
            self.focus_force()
            messagebox.showinfo("Başarılı", "Şifre '123456' olarak sıfırlandı.", parent=self)


class KullaniciDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, kullanici=None):
        super().__init__(parent)
        self.db = db
        self.kullanici = kullanici
        
        self.title("Kullanıcı Düzenle" if kullanici else "Yeni Kullanıcı")
        self.geometry("400x450")
        self.attributes("-topmost", True)
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Kullanıcı Adı
        ctk.CTkLabel(frame, text="Kullanıcı Adı *", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_kullanici = ctk.CTkEntry(frame, height=40)
        self.entry_kullanici.pack(fill="x", pady=(0, 15))
        
        # Şifre (Sadece yeni kullanıcı için)
        if not kullanici:
            ctk.CTkLabel(frame, text="Şifre *", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
            self.entry_sifre = ctk.CTkEntry(frame, height=40, show="*")
            self.entry_sifre.pack(fill="x", pady=(0, 15))
        
        # Ad Soyad
        ctk.CTkLabel(frame, text="Ad Soyad", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_adsoyad = ctk.CTkEntry(frame, height=40)
        self.entry_adsoyad.pack(fill="x", pady=(0, 15))
        
        # E-posta
        ctk.CTkLabel(frame, text="E-posta", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_email = ctk.CTkEntry(frame, height=40)
        self.entry_email.pack(fill="x", pady=(0, 15))
        
        # Rol
        ctk.CTkLabel(frame, text="Rol", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.combo_rol = ctk.CTkComboBox(frame, values=["kullanici", "admin"], height=40, state="readonly")
        self.combo_rol.set("kullanici")
        self.combo_rol.pack(fill="x", pady=(0, 15))
        
        # Aktif
        self.var_aktif = ctk.BooleanVar(value=True)
        self.check_aktif = ctk.CTkCheckBox(frame, text="Aktif", variable=self.var_aktif)
        self.check_aktif.pack(anchor="w", pady=(0, 20))
        
        # Düzenleme modunda verileri doldur
        if kullanici:
            self.entry_kullanici.insert(0, kullanici[1])
            self.entry_kullanici.configure(state="disabled")  # Kullanıcı adı değiştirilemez
            self.entry_adsoyad.insert(0, kullanici[2] or "")
            self.entry_email.insert(0, kullanici[3] or "")
            self.combo_rol.set(kullanici[4])
            self.var_aktif.set(kullanici[5] == 1)
        
        # Butonlar
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(btn_frame, text="Kaydet", command=self.kaydet, fg_color="#2CC985", hover_color="#229C68").pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="İptal", command=self.destroy, fg_color="gray", hover_color="darkgray").pack(side="right", expand=True, fill="x", padx=(5, 0))
    
    def kaydet(self):
        kullanici_adi = self.entry_kullanici.get().strip()
        ad_soyad = self.entry_adsoyad.get().strip()
        email = self.entry_email.get().strip()
        rol = self.combo_rol.get()
        aktif = 1 if self.var_aktif.get() else 0
        
        if not kullanici_adi:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Kullanıcı adı zorunludur.", parent=self)
            return
        
        if self.kullanici:
            # Güncelleme
            self.db.kullanici_guncelle(self.kullanici[0], ad_soyad, email, rol, aktif)
            self.lift()
            self.focus_force()
            messagebox.showinfo("Başarılı", "Kullanıcı güncellendi.", parent=self)
        else:
            # Yeni kullanıcı
            sifre = self.entry_sifre.get().strip()
            if not sifre:
                self.lift()
                self.focus_force()
                messagebox.showwarning("Uyarı", "Şifre zorunludur.", parent=self)
                return
            
            if self.db.kullanici_ekle(kullanici_adi, sifre, ad_soyad, email, rol):
                self.lift()
                self.focus_force()
                messagebox.showinfo("Başarılı", "Kullanıcı eklendi.", parent=self)
            else:
                self.lift()
                self.focus_force()
                messagebox.showerror("Hata", "Bu kullanıcı adı zaten kullanılıyor.", parent=self)
                return
        
        self.destroy()


class SifreDegistir(ctk.CTkToplevel):
    def __init__(self, parent, db, kullanici):
        super().__init__(parent)
        self.db = db
        self.kullanici = kullanici
        
        self.title("Şifre Değiştir")
        self.geometry("350x300")
        self.attributes("-topmost", True)
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(frame, text="🔐 Şifre Değiştir", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 20))
        
        ctk.CTkLabel(frame, text="Mevcut Şifre", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_mevcut = ctk.CTkEntry(frame, height=40, show="*")
        self.entry_mevcut.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(frame, text="Yeni Şifre", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_yeni = ctk.CTkEntry(frame, height=40, show="*")
        self.entry_yeni.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(frame, text="Yeni Şifre (Tekrar)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_yeni2 = ctk.CTkEntry(frame, height=40, show="*")
        self.entry_yeni2.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(frame, text="Şifreyi Değiştir", command=self.degistir, fg_color="#2CC985", hover_color="#229C68", height=45).pack(fill="x")
    
    def degistir(self):
        mevcut = self.entry_mevcut.get()
        yeni = self.entry_yeni.get()
        yeni2 = self.entry_yeni2.get()
        
        if not mevcut or not yeni or not yeni2:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Tüm alanları doldurun.", parent=self)
            return
        
        if yeni != yeni2:
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", "Yeni şifreler eşleşmiyor.", parent=self)
            return
        
        if len(yeni) < 4:
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", "Şifre en az 4 karakter olmalıdır.", parent=self)
            return
        
        # Mevcut şifreyi kontrol et
        mevcut_hash = self.db.sifre_hashle(mevcut)
        self.db.imlec.execute("SELECT sifre_hash FROM kullanicilar WHERE id = ?", (self.kullanici['id'],))
        result = self.db.imlec.fetchone()
        
        if result[0] != mevcut_hash:
            self.lift()
            self.focus_force()
            messagebox.showerror("Hata", "Mevcut şifre yanlış.", parent=self)
            return
        
        self.db.sifre_degistir(self.kullanici['id'], yeni)
        self.lift()
        self.focus_force()
        messagebox.showinfo("Başarılı", "Şifreniz değiştirildi.", parent=self)
        self.destroy()


class GirisEkrani(ctk.CTkToplevel):
    def __init__(self, parent, db, callback):
        super().__init__(parent)
        self.db = db
        self.callback = callback
        
        self.title("Giriş Yap")
        self.geometry("500x580")
        self.resizable(False, False)
        
        # Pencereyi ortala
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (580 // 2)
        self.geometry(f"500x580+{x}+{y}")
        
        # Kapatma düğmesini devre dışı bırak
        self.protocol("WM_DELETE_WINDOW", self.kapat)
        
        # Ana Frame
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo için placeholder label
        self.logo_label = ctk.CTkLabel(frame, text="")
        self.logo_label.pack(pady=(0, 20))
        
        # Logo'yu yükle
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                aspect_ratio = pil_image.width / pil_image.height
                new_height = 80
                new_width = int(new_height * aspect_ratio)
                self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))
                self.logo_label.configure(image=self.logo_image)
            except Exception as e:
                print(f"Logo yükleme hatası: {e}")
        
        ctk.CTkLabel(frame, text="Şikayet Takip Sistemi", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(frame, text="Lütfen giriş yapın", font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(0, 30))
        
        # Kullanıcı Adı
        ctk.CTkLabel(frame, text="Kullanıcı Adı", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_kullanici = ctk.CTkEntry(frame, height=45, placeholder_text="Kullanıcı adınızı girin")
        self.entry_kullanici.pack(fill="x", pady=(0, 15))
        
        # Şifre
        ctk.CTkLabel(frame, text="Şifre", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_sifre = ctk.CTkEntry(frame, height=45, placeholder_text="Şifrenizi girin", show="*")
        self.entry_sifre.pack(fill="x", pady=(0, 25))
        
        # Giriş Butonu
        ctk.CTkButton(frame, text="GİRİŞ YAP", command=self.giris_yap, height=50, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#2CC985", hover_color="#229C68").pack(fill="x", pady=(0, 15))
        
        # Enter tuşu ile giriş
        self.entry_sifre.bind("<Return>", lambda e: self.giris_yap())
        self.entry_kullanici.bind("<Return>", lambda e: self.entry_sifre.focus())
        
        self.entry_kullanici.focus()
    
    def giris_yap(self):
        kullanici_adi = self.entry_kullanici.get().strip()
        sifre = self.entry_sifre.get()
        
        if not kullanici_adi or not sifre:
            self.lift()
            self.focus_force()
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre gereklidir.", parent=self)
            return
        
        kullanici = self.db.giris_yap(kullanici_adi, sifre)
        
        if kullanici:
            self.callback(kullanici)
            self.destroy()
        else:
            self.lift()
            self.focus_force()
            messagebox.showerror("Giriş Hatası", "Kullanıcı adı veya şifre hatalı!", parent=self)
            self.entry_sifre.delete(0, "end")
            self.entry_sifre.focus()
    
    def kapat(self):
        self.master.destroy()


class SikayetUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=("white", "gray10"))
        self.title("Şikayet Takip ve Arşivleme Sistemi")
        
        # Pencere modunda tam ekran (Maximized) - Küçültme/Büyütme butonları aktif olur
        self.state("zoomed")
        
        # Icon
        if os.path.exists("logo.png"):
            try:
                icon_image = tk.PhotoImage(file="logo.png")
                self.iconphoto(False, icon_image)
            except:
                pass
                
        self.db = VeritabaniYonetici()
        self.aktif_kullanici = None
        
        # Günlük otomatik yedekleme
        self.otomatik_yedek_al()
        
        self.container = ctk.CTkFrame(self, fg_color=("white", "gray17"))
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (AnaEkran, SikayetArsivi, Ayarlar):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Önce gizle, giriş sonrası göster
        self.withdraw()
        
        # Giriş ekranını aç
        self.after(100, self.giris_ekrani_ac)
        
    def giris_ekrani_ac(self):
        GirisEkrani(self, self.db, self.giris_basarili)
    
    def giris_basarili(self, kullanici):
        self.aktif_kullanici = kullanici
        
        # Giriş işlemini logla
        self.db.islem_kaydet(
            kullanici_id=kullanici.get('id'),
            kullanici_adi=kullanici.get('kullanici_adi'),
            islem_turu="GİRİŞ",
            islem_detay=f"{kullanici.get('ad_soyad', '')} sisteme giriş yaptı"
        )
        
        self.deiconify()  # Ana pencereyi göster
        self.show_frame("AnaEkran")
        
        # Kullanıcı bilgisini güncelle
        if hasattr(self.frames.get("AnaEkran"), 'kullanici_bilgisi_guncelle'):
            self.frames["AnaEkran"].kullanici_bilgisi_guncelle(kullanici)
        
        # Ayarlar sayfasını güncelle
        if hasattr(self.frames.get("Ayarlar"), 'kullanici_gorunumu_guncelle'):
            self.frames["Ayarlar"].kullanici_gorunumu_guncelle()
        
    def show_frame(self, page_name):
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()
            if page_name == "SikayetArsivi":
                frame.listeyi_yenile()
            
    def yeni_sikayet_ac(self, duzenlenecek_kayit=None):
        """Yeni şikayet veya düzenleme ekranını aç"""
        # Mevcut YeniSikayet frame'i varsa sil
        if "YeniSikayet" in self.frames:
            self.frames["YeniSikayet"].destroy()
            del self.frames["YeniSikayet"]
        
        callback = self.frames["SikayetArsivi"].listeyi_yenile
        frame = YeniSikayetPenceresi(
            parent=self.container, 
            db_yonetici=self.db, 
            callback_yenile=callback, 
            duzenlenecek_kayit=duzenlenecek_kayit,
            controller=self
        )
        self.frames["YeniSikayet"] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
    
    def sikayet_detay_ac(self, kayit):
        """Şikayet detay ekranını aç"""
        # Mevcut detay frame'i varsa sil
        if "SikayetDetay" in self.frames:
            self.frames["SikayetDetay"].destroy()
            del self.frames["SikayetDetay"]
        
        frame = SikayetDetayPenceresi(
            parent=self.container, 
            db=self.db, 
            kayit=kayit,
            controller=self
        )
        self.frames["SikayetDetay"] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
    
    def cikis_yap(self):
        # Çıkış işlemini logla
        if self.aktif_kullanici:
            self.db.islem_kaydet(
                kullanici_id=self.aktif_kullanici.get('id'),
                kullanici_adi=self.aktif_kullanici.get('kullanici_adi'),
                islem_turu="ÇIKIŞ",
                islem_detay=f"{self.aktif_kullanici.get('ad_soyad', '')} sistemden çıkış yaptı"
            )
        
        self.aktif_kullanici = None
        
        # Kullanıcı bilgilerini temizle
        if hasattr(self.frames.get("AnaEkran"), 'kullanici_bilgisi_guncelle'):
            self.frames["AnaEkran"].user_name_label.configure(text="")
            self.frames["AnaEkran"].user_role_label.configure(text="")
        
        self.withdraw()
        self.giris_ekrani_ac()

    def otomatik_yedek_al(self):
        """Uygulama açılışında günlük otomatik yedek al"""
        try:
            if self.db.gunluk_yedek_gerekli_mi():
                basarili, sonuc = self.db.yedek_al(manuel=False)
                if basarili:
                    print(f"Otomatik yedek alındı: {sonuc}")
        except Exception as e:
            print(f"Otomatik yedek hatası: {e}")


if __name__ == "__main__":
    app = SikayetUygulamasi()
    app.mainloop()
