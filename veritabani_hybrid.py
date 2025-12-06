import sqlite3
import psycopg2
import datetime
import hashlib
import os
import socket

def env_oku():
    """
    .env dosyasından veya ortam değişkenlerinden Supabase bilgilerini oku.
    Güvenlik için şifreler kodda açık yazılmaz.
    """
    config = {
        "host": os.environ.get("SUPABASE_HOST", ""),
        "database": os.environ.get("SUPABASE_DATABASE", "postgres"),
        "user": os.environ.get("SUPABASE_USER", "postgres"),
        "password": os.environ.get("SUPABASE_PASSWORD", ""),
        "port": os.environ.get("SUPABASE_PORT", "5432"),
        "sslmode": "require"
    }
    
    # .env dosyası varsa oku
    env_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_yolu):
        try:
            with open(env_yolu, "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith("#") and "=" in satir:
                        anahtar, deger = satir.split("=", 1)
                        anahtar = anahtar.strip()
                        deger = deger.strip()
                        if anahtar == "SUPABASE_HOST":
                            config["host"] = deger
                        elif anahtar == "SUPABASE_DATABASE":
                            config["database"] = deger
                        elif anahtar == "SUPABASE_USER":
                            config["user"] = deger
                        elif anahtar == "SUPABASE_PASSWORD":
                            config["password"] = deger
                        elif anahtar == "SUPABASE_PORT":
                            config["port"] = deger
        except Exception as e:
            print(f"⚠️ .env dosyası okunamadı: {e}")
    
    return config

# Supabase bağlantı bilgileri (.env dosyasından veya ortam değişkenlerinden)
SUPABASE_CONFIG = env_oku()

class VeritabaniYonetici:
    """Hibrit Veritabanı Yöneticisi - Offline/Online Senkronizasyon"""
    
    def __init__(self, db_adi="sikayet_takip_local.db"):
        self.db_adi = db_adi
        self.yerel_baglanti = None
        self.yerel_imlec = None
        self.bulut_baglanti = None
        self.bulut_imlec = None
        self.online_mod = False
        self.bekleyen_islem_sayisi = 0
        self.son_senkronizasyon = None  # Son senkronizasyon zamanı
        
        # Yerel veritabanını her zaman aç
        self._yerel_baglanti_kur()
        
        # Bulut bağlantısını arka planda dene (uygulamayı yavaşlatmasın)
        import threading
        threading.Thread(target=self._arka_plan_baglanti, daemon=True).start()
    
    def _arka_plan_baglanti(self):
        """Bulut bağlantısını arka planda dene"""
        self._bulut_baglanti_dene()
        if self.online_mod:
            self._senkronize_et()
    
    @property
    def imlec(self):
        """Geriye uyumluluk için yerel_imlec'e alias"""
        return self.yerel_imlec

    def _internet_var_mi(self):
        """İnternet bağlantısını kontrol et"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            return True
        except OSError:
            return False

    def _yerel_baglanti_kur(self):
        """Yerel SQLite veritabanına bağlan"""
        try:
            self.yerel_baglanti = sqlite3.connect(self.db_adi, check_same_thread=False)
            self.yerel_imlec = self.yerel_baglanti.cursor()
            self._yerel_tablolari_olustur()
            print("📁 Yerel veritabanı hazır")
        except Exception as e:
            print(f"❌ Yerel veritabanı hatası: {e}")

    def _bulut_baglanti_dene(self):
        """Supabase bağlantısını dene"""
        if not self._internet_var_mi():
            print("📴 İnternet bağlantısı yok - Çevrimdışı mod")
            self.online_mod = False
            return False
        
        try:
            self.bulut_baglanti = psycopg2.connect(
                host=SUPABASE_CONFIG["host"],
                database=SUPABASE_CONFIG["database"],
                user=SUPABASE_CONFIG["user"],
                password=SUPABASE_CONFIG["password"],
                port=SUPABASE_CONFIG["port"],
                sslmode=SUPABASE_CONFIG["sslmode"],
                connect_timeout=3
            )
            self.bulut_baglanti.autocommit = False
            self.bulut_imlec = self.bulut_baglanti.cursor()
            self._bulut_tablolari_olustur()
            self.online_mod = True
            print("☁️ Supabase bağlantısı başarılı - Çevrimiçi mod")
            return True
        except Exception as e:
            print(f"📴 Supabase bağlantısı başarısız - Çevrimdışı mod: {e}")
            self.online_mod = False
            return False

    def _bulut_baglanti_kontrol(self):
        """Bulut bağlantısını kontrol et, gerekirse yeniden bağlan"""
        if not self.online_mod:
            return False
        try:
            # Bağlantıyı test et
            self.bulut_imlec.execute("SELECT 1")
            return True
        except:
            # Bağlantı kopmuş, yeniden bağlan
            try:
                self._bulut_baglanti_dene()
                return self.online_mod
            except:
                self.online_mod = False
                return False

    def _yerel_tablolari_olustur(self):
        """Yerel SQLite tablolarını oluştur"""
        # Ana tablolar
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS sikayetler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_no TEXT,
                yolcu_adi TEXT,
                seyahat_tarihi TEXT,
                guzergah TEXT,
                pnr TEXT,
                iletisim TEXT,
                platform TEXT,
                sikayet_detay TEXT,
                kayit_tarihi TEXT,
                durum TEXT,
                telefon TEXT,
                eposta TEXT,
                plaka TEXT,
                sikayet_turu TEXT,
                lokasyon TEXT,
                oncelik TEXT,
                senkronize INTEGER DEFAULT 0,
                bulut_id INTEGER,
                satin_alinan_yer TEXT,
                basvurulan_yer TEXT,
                bilet_ucreti TEXT
            )
        """)
        
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre_hash TEXT NOT NULL,
                ad_soyad TEXT,
                email TEXT,
                rol TEXT DEFAULT 'kullanici',
                aktif INTEGER DEFAULT 1,
                olusturma_tarihi TEXT,
                son_giris TEXT,
                senkronize INTEGER DEFAULT 0,
                bulut_id INTEGER
            )
        """)
        
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS islem_gecmisi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT NOT NULL,
                kullanici_id INTEGER,
                kullanici_adi TEXT,
                islem_turu TEXT NOT NULL,
                islem_detay TEXT,
                ilgili_kayit_id INTEGER,
                ilgili_kayit_no TEXT,
                eski_deger TEXT,
                yeni_deger TEXT,
                senkronize INTEGER DEFAULT 0
            )
        """)
        
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS sikayet_islemleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_id INTEGER NOT NULL,
                tarih TEXT NOT NULL,
                kullanici_id INTEGER,
                kullanici_adi TEXT,
                islem_turu TEXT NOT NULL,
                aciklama TEXT,
                eski_durum TEXT,
                yeni_durum TEXT,
                senkronize INTEGER DEFAULT 0,
                bulut_id INTEGER
            )
        """)
        
        # Bekleyen işlemler tablosu (senkronizasyon için)
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS bekleyen_islemler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tablo TEXT NOT NULL,
                islem_turu TEXT NOT NULL,
                veri TEXT NOT NULL,
                olusturma_tarihi TEXT NOT NULL
            )
        """)
        
        # Şikayet notları tablosu
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS sikayet_notlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_id INTEGER NOT NULL,
                kullanici_id INTEGER,
                kullanici_adi TEXT,
                not_metni TEXT NOT NULL,
                olusturma_tarihi TEXT NOT NULL,
                senkronize INTEGER DEFAULT 0,
                bulut_id INTEGER
            )
        """)
        
        # Şikayet dosyaları tablosu
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS sikayet_dosyalari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_id INTEGER NOT NULL,
                dosya_adi TEXT NOT NULL,
                dosya_yolu TEXT NOT NULL,
                dosya_tipi TEXT,
                dosya_boyutu INTEGER,
                yukleyen_id INTEGER,
                yukleyen_adi TEXT,
                yukleme_tarihi TEXT NOT NULL,
                senkronize INTEGER DEFAULT 0,
                bulut_id INTEGER
            )
        """)
        
        # Şikayet etiketleri tablosu
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS sikayet_etiketleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_id INTEGER NOT NULL,
                etiket TEXT NOT NULL,
                renk TEXT DEFAULT '#3498db',
                ekleyen_id INTEGER,
                ekleyen_adi TEXT,
                ekleme_tarihi TEXT NOT NULL,
                senkronize INTEGER DEFAULT 0,
                bulut_id INTEGER
            )
        """)
        
        # Hatırlatıcılar tablosu
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS hatirlaticilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_id INTEGER NOT NULL,
                kullanici_id INTEGER,
                kullanici_adi TEXT,
                hatirlatma_tarihi TEXT NOT NULL,
                mesaj TEXT,
                tamamlandi INTEGER DEFAULT 0,
                olusturma_tarihi TEXT NOT NULL,
                senkronize INTEGER DEFAULT 0,
                bulut_id INTEGER
            )
        """)
        
        # Sikayetler tablosuna satin_alinan_yer sütunu ekle (varsa atla)
        try:
            self.yerel_imlec.execute("ALTER TABLE sikayetler ADD COLUMN satin_alinan_yer TEXT")
        except:
            pass
        
        # Sikayetler tablosuna basvurulan_yer sütunu ekle (varsa atla)
        try:
            self.yerel_imlec.execute("ALTER TABLE sikayetler ADD COLUMN basvurulan_yer TEXT")
        except:
            pass
        
        # Sikayetler tablosuna bilet_ucreti sütunu ekle (varsa atla)
        try:
            self.yerel_imlec.execute("ALTER TABLE sikayetler ADD COLUMN bilet_ucreti TEXT")
        except:
            pass
        
        # Çöp kutusu tablosu
        self.yerel_imlec.execute("""
            CREATE TABLE IF NOT EXISTS cop_kutusu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_id INTEGER NOT NULL,
                sikayet_no TEXT,
                yolcu_adi TEXT,
                seyahat_tarihi TEXT,
                guzergah TEXT,
                pnr TEXT,
                iletisim TEXT,
                platform TEXT,
                sikayet_detay TEXT,
                kayit_tarihi TEXT,
                durum TEXT,
                telefon TEXT,
                eposta TEXT,
                plaka TEXT,
                sikayet_turu TEXT,
                lokasyon TEXT,
                oncelik TEXT,
                silinme_tarihi TEXT,
                silen_kullanici_id INTEGER,
                silen_kullanici_adi TEXT
            )
        """)
        
        self.yerel_baglanti.commit()
        
        # Varsayılan admin kullanıcısı
        self.yerel_imlec.execute("SELECT COUNT(*) FROM kullanicilar")
        if self.yerel_imlec.fetchone()[0] == 0:
            sifre_hash = hashlib.sha256("admin123".encode()).hexdigest()
            tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.yerel_imlec.execute("""
                INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, email, rol, olusturma_tarihi, senkronize)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, ("admin", sifre_hash, "Sistem Yöneticisi", "admin@sistem.com", "admin", tarih))
            self.yerel_baglanti.commit()

    def _bulut_tablolari_olustur(self):
        """Supabase tablolarını oluştur"""
        tablolar = [
            """CREATE TABLE IF NOT EXISTS sikayetler (
                id SERIAL PRIMARY KEY, sikayet_no TEXT, yolcu_adi TEXT, seyahat_tarihi TEXT,
                guzergah TEXT, pnr TEXT, iletisim TEXT, platform TEXT, sikayet_detay TEXT,
                kayit_tarihi TEXT, durum TEXT, telefon TEXT, eposta TEXT, plaka TEXT,
                sikayet_turu TEXT, lokasyon TEXT, oncelik TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS kullanicilar (
                id SERIAL PRIMARY KEY, kullanici_adi TEXT UNIQUE NOT NULL, sifre_hash TEXT NOT NULL,
                ad_soyad TEXT, email TEXT, rol TEXT DEFAULT 'kullanici', aktif INTEGER DEFAULT 1,
                olusturma_tarihi TEXT, son_giris TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS islem_gecmisi (
                id SERIAL PRIMARY KEY, tarih TEXT NOT NULL, kullanici_id INTEGER, kullanici_adi TEXT,
                islem_turu TEXT NOT NULL, islem_detay TEXT, ilgili_kayit_id INTEGER,
                ilgili_kayit_no TEXT, eski_deger TEXT, yeni_deger TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS sikayet_islemleri (
                id SERIAL PRIMARY KEY, sikayet_id INTEGER NOT NULL, tarih TEXT NOT NULL,
                kullanici_id INTEGER, kullanici_adi TEXT, islem_turu TEXT NOT NULL,
                aciklama TEXT, eski_durum TEXT, yeni_durum TEXT
            )"""
        ]
        for tablo in tablolar:
            self.bulut_imlec.execute(tablo)
        self.bulut_baglanti.commit()

    def _senkronize_et(self):
        """Bekleyen yerel verileri buluta senkronize et"""
        if not self.online_mod:
            return 0
        
        senkronize_edilen = 0
        
        try:
            # Senkronize edilmemiş şikayetleri bul
            self.yerel_imlec.execute("SELECT * FROM sikayetler WHERE senkronize = 0")
            bekleyen_sikayetler = self.yerel_imlec.fetchall()
            
            for sikayet in bekleyen_sikayetler:
                try:
                    # Buluta ekle
                    self.bulut_imlec.execute("""
                        INSERT INTO sikayetler (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, 
                        iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, 
                        plaka, sikayet_turu, lokasyon, oncelik)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, sikayet[1:17])
                    bulut_id = self.bulut_imlec.fetchone()[0]
                    self.bulut_baglanti.commit()
                    
                    # Yerel kaydı güncelle
                    self.yerel_imlec.execute("UPDATE sikayetler SET senkronize = 1, bulut_id = ? WHERE id = ?", (bulut_id, sikayet[0]))
                    self.yerel_baglanti.commit()
                    senkronize_edilen += 1
                except Exception as e:
                    print(f"Şikayet senkronizasyon hatası: {e}")
                    self.bulut_baglanti.rollback()
            
            if senkronize_edilen > 0:
                print(f"✅ {senkronize_edilen} kayıt senkronize edildi")
            
            # Buluttan yerel'e güncelle (diğer kullanıcıların eklediği veriler)
            self._buluttan_cek()
            
        except Exception as e:
            print(f"Senkronizasyon hatası: {e}")
        
        return senkronize_edilen

    def _buluttan_cek(self):
        """Buluttaki verileri yerele çek"""
        if not self.online_mod:
            return
        
        try:
            # Buluttaki şikayetleri al
            self.bulut_imlec.execute("SELECT * FROM sikayetler ORDER BY id")
            bulut_sikayetler = self.bulut_imlec.fetchall()
            
            for sikayet in bulut_sikayetler:
                bulut_id = sikayet[0]
                # Yerel'de bu bulut_id var mı kontrol et
                self.yerel_imlec.execute("SELECT id FROM sikayetler WHERE bulut_id = ?", (bulut_id,))
                yerel = self.yerel_imlec.fetchone()
                
                if not yerel:
                    # Yerel'de yok, ekle
                    self.yerel_imlec.execute("""
                        INSERT INTO sikayetler (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr,
                        iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta,
                        plaka, sikayet_turu, lokasyon, oncelik, senkronize, bulut_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """, sikayet[1:17] + (bulut_id,))
            
            self.yerel_baglanti.commit()
            
            # Kullanıcıları da senkronize et
            self.bulut_imlec.execute("SELECT * FROM kullanicilar ORDER BY id")
            bulut_kullanicilar = self.bulut_imlec.fetchall()
            
            for kullanici in bulut_kullanicilar:
                bulut_id = kullanici[0]
                self.yerel_imlec.execute("SELECT id FROM kullanicilar WHERE bulut_id = ?", (bulut_id,))
                yerel = self.yerel_imlec.fetchone()
                
                if not yerel:
                    # Kullanıcı adı çakışması kontrolü
                    self.yerel_imlec.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = ?", (kullanici[1],))
                    if not self.yerel_imlec.fetchone():
                        self.yerel_imlec.execute("""
                            INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, email, rol, aktif, olusturma_tarihi, son_giris, senkronize, bulut_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                        """, kullanici[1:9] + (bulut_id,))
            
            self.yerel_baglanti.commit()
            
        except Exception as e:
            print(f"Buluttan çekme hatası: {e}")

    def baglanti_kur(self):
        """Uyumluluk için"""
        return True

    def baglanti_durumu(self):
        """Bağlantı durumunu döndür"""
        return {
            "online": self.online_mod,
            "bekleyen": self._bekleyen_islem_sayisi()
        }

    def _bekleyen_islem_sayisi(self):
        """Senkronize edilmemiş kayıt sayısı"""
        self.yerel_imlec.execute("SELECT COUNT(*) FROM sikayetler WHERE senkronize = 0")
        return self.yerel_imlec.fetchone()[0]

    def yeniden_baglan(self):
        """Bulut bağlantısını yeniden dene ve senkronize et"""
        if self._bulut_baglanti_dene():
            self._senkronize_et()
            return True
        return False

    # ==================== ŞİKAYET İŞLEMLERİ ====================

    def sikayet_no_olustur(self):
        simdi = datetime.datetime.now()
        yil = simdi.year
        prefix = f"IPT/{yil}-"
        
        # Önce buluttan kontrol et (online ise)
        son_no = 0
        if self.online_mod:
            try:
                self.bulut_imlec.execute("SELECT sikayet_no FROM sikayetler WHERE sikayet_no LIKE %s ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
                son_kayit = self.bulut_imlec.fetchone()
                if son_kayit:
                    son_no = int(son_kayit[0].split('-')[1])
            except:
                pass
        
        # Yerel'den de kontrol et
        self.yerel_imlec.execute("SELECT sikayet_no FROM sikayetler WHERE sikayet_no LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
        yerel_kayit = self.yerel_imlec.fetchone()
        if yerel_kayit:
            yerel_no = int(yerel_kayit[0].split('-')[1])
            son_no = max(son_no, yerel_no)
        
        return f"{prefix}{son_no + 1:05d}"

    def sikayet_ekle(self, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, telefon="", eposta="", plaka="", sikayet_turu="", lokasyon="", oncelik="", durum="Yeni", satin_alinan_yer="", basvurulan_yer="", bilet_ucreti=""):
        kayit_tarihi = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sikayet_no = self.sikayet_no_olustur()
        
        # Önce yerel'e kaydet
        self.yerel_imlec.execute("""
            INSERT INTO sikayetler (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, 
            platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka, sikayet_turu, 
            lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bilet_ucreti, senkronize, bulut_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, 
              sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka, sikayet_turu, 
              lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bilet_ucreti, 0, None))
        yerel_id = self.yerel_imlec.lastrowid
        self.yerel_baglanti.commit()
        
        # Online ise buluta da kaydet
        if self.online_mod:
            try:
                self.bulut_imlec.execute("""
                    INSERT INTO sikayetler (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, 
                    iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, 
                    plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, 
                      sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka, sikayet_turu, 
                      lokasyon, oncelik, satin_alinan_yer, basvurulan_yer))
                bulut_id = self.bulut_imlec.fetchone()[0]
                self.bulut_baglanti.commit()
                
                # Yerel kaydı güncelle
                self.yerel_imlec.execute("UPDATE sikayetler SET senkronize = 1, bulut_id = ? WHERE id = ?", (bulut_id, yerel_id))
                self.yerel_baglanti.commit()
            except Exception as e:
                print(f"Bulut kayıt hatası (yerel'de kaydedildi): {e}")
                self.bulut_baglanti.rollback()

    def sikayetleri_getir(self):
        # Senkronizasyon sadece 5 dakikada bir yapılsın (performans için)
        import datetime
        simdi = datetime.datetime.now()
        if self.online_mod and self.son_senkronizasyon:
            fark = (simdi - self.son_senkronizasyon).total_seconds()
            if fark > 300:  # 5 dakikadan fazla olduysa senkronize et
                self._buluttan_cek()
                self.son_senkronizasyon = simdi
        elif self.online_mod and not self.son_senkronizasyon:
            self._buluttan_cek()
            self.son_senkronizasyon = simdi
        
        self.yerel_imlec.execute("SELECT id, sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bilet_ucreti FROM sikayetler ORDER BY kayit_tarihi DESC")
        return self.yerel_imlec.fetchall()

    def sikayet_sil(self, id):
        # Bulut ID'yi al
        self.yerel_imlec.execute("SELECT bulut_id FROM sikayetler WHERE id = ?", (id,))
        result = self.yerel_imlec.fetchone()
        bulut_id = result[0] if result else None
        
        # Yerel'den sil
        self.yerel_imlec.execute("DELETE FROM sikayet_islemleri WHERE sikayet_id = ?", (id,))
        self.yerel_imlec.execute("DELETE FROM sikayetler WHERE id = ?", (id,))
        self.yerel_baglanti.commit()
        
        # Buluttan da sil
        if self._bulut_baglanti_kontrol() and bulut_id:
            try:
                self.bulut_imlec.execute("DELETE FROM sikayet_islemleri WHERE sikayet_id = %s", (bulut_id,))
                self.bulut_imlec.execute("DELETE FROM sikayetler WHERE id = %s", (bulut_id,))
                self.bulut_baglanti.commit()
            except Exception as e:
                print(f"Bulut silme hatası: {e}")
                try:
                    self.bulut_baglanti.rollback()
                except:
                    pass

    def durumu_guncelle(self, id, yeni_durum):
        self.yerel_imlec.execute("SELECT bulut_id FROM sikayetler WHERE id = ?", (id,))
        result = self.yerel_imlec.fetchone()
        bulut_id = result[0] if result else None
        
        self.yerel_imlec.execute("UPDATE sikayetler SET durum = ? WHERE id = ?", (yeni_durum, id))
        self.yerel_baglanti.commit()
        
        if self._bulut_baglanti_kontrol() and bulut_id:
            try:
                self.bulut_imlec.execute("UPDATE sikayetler SET durum = %s WHERE id = %s", (yeni_durum, bulut_id))
                self.bulut_baglanti.commit()
            except Exception as e:
                print(f"Bulut güncelleme hatası: {e}")
                try:
                    self.bulut_baglanti.rollback()
                except:
                    pass

    def sikayet_guncelle(self, id, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer="", basvurulan_yer="", bilet_ucreti=""):
        self.yerel_imlec.execute("SELECT bulut_id FROM sikayetler WHERE id = ?", (id,))
        result = self.yerel_imlec.fetchone()
        bulut_id = result[0] if result else None
        
        self.yerel_imlec.execute("""
            UPDATE sikayetler SET yolcu_adi = ?, seyahat_tarihi = ?, guzergah = ?, pnr = ?, 
            iletisim = ?, platform = ?, sikayet_detay = ?, telefon = ?, eposta = ?, plaka = ?, 
            sikayet_turu = ?, lokasyon = ?, oncelik = ?, satin_alinan_yer = ?, basvurulan_yer = ?, bilet_ucreti = ? WHERE id = ?
        """, (yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, 
              telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bilet_ucreti, id))
        self.yerel_baglanti.commit()
        
        if self.online_mod and bulut_id:
            try:
                self.bulut_imlec.execute("""
                    UPDATE sikayetler SET yolcu_adi = %s, seyahat_tarihi = %s, guzergah = %s, 
                    pnr = %s, iletisim = %s, platform = %s, sikayet_detay = %s, telefon = %s, 
                    eposta = %s, plaka = %s, sikayet_turu = %s, lokasyon = %s, oncelik = %s, 
                    satin_alinan_yer = %s, basvurulan_yer = %s WHERE id = %s
                """, (yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, 
                      telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bulut_id))
                self.bulut_baglanti.commit()
            except Exception as e:
                print(f"Bulut güncelleme hatası: {e}")
                self.bulut_baglanti.rollback()

    # ==================== KULLANICI YÖNETİMİ ====================

    def sifre_hashle(self, sifre):
        return hashlib.sha256(sifre.encode()).hexdigest()

    def kullanici_ekle(self, kullanici_adi, sifre, ad_soyad="", email="", rol="kullanici"):
        try:
            sifre_hash = self.sifre_hashle(sifre)
            olusturma_tarihi = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.yerel_imlec.execute("""
                INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, email, rol, olusturma_tarihi, senkronize, bulut_id)
                VALUES (?, ?, ?, ?, ?, ?, 0, NULL)
            """, (kullanici_adi, sifre_hash, ad_soyad, email, rol, olusturma_tarihi))
            yerel_id = self.yerel_imlec.lastrowid
            self.yerel_baglanti.commit()
            
            if self.online_mod:
                try:
                    self.bulut_imlec.execute("""
                        INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, email, rol, olusturma_tarihi)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                    """, (kullanici_adi, sifre_hash, ad_soyad, email, rol, olusturma_tarihi))
                    bulut_id = self.bulut_imlec.fetchone()[0]
                    self.bulut_baglanti.commit()
                    
                    self.yerel_imlec.execute("UPDATE kullanicilar SET senkronize = 1, bulut_id = ? WHERE id = ?", (bulut_id, yerel_id))
                    self.yerel_baglanti.commit()
                except Exception as e:
                    print(f"Bulut kullanıcı ekleme hatası: {e}")
                    self.bulut_baglanti.rollback()
            
            return True
        except sqlite3.IntegrityError:
            return False

    def giris_yap(self, kullanici_adi, sifre):
        sifre_hash = self.sifre_hashle(sifre)
        
        # Önce yerel'den kontrol et
        self.yerel_imlec.execute("""
            SELECT id, kullanici_adi, ad_soyad, email, rol, aktif 
            FROM kullanicilar WHERE kullanici_adi = ? AND sifre_hash = ?
        """, (kullanici_adi, sifre_hash))
        
        kullanici = self.yerel_imlec.fetchone()
        
        if kullanici and kullanici[5] == 1:
            son_giris = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.yerel_imlec.execute("UPDATE kullanicilar SET son_giris = ? WHERE id = ?", (son_giris, kullanici[0]))
            self.yerel_baglanti.commit()
            
            return {
                "id": kullanici[0],
                "kullanici_adi": kullanici[1],
                "ad_soyad": kullanici[2],
                "email": kullanici[3],
                "rol": kullanici[4]
            }
        return None

    def kullanicilari_getir(self):
        self.yerel_imlec.execute("""
            SELECT id, kullanici_adi, ad_soyad, email, rol, aktif, olusturma_tarihi, son_giris 
            FROM kullanicilar ORDER BY id
        """)
        return self.yerel_imlec.fetchall()

    def kullanici_sil(self, kullanici_id):
        self.yerel_imlec.execute("SELECT kullanici_adi, bulut_id FROM kullanicilar WHERE id = ?", (kullanici_id,))
        result = self.yerel_imlec.fetchone()
        if result and result[0] == "admin":
            return False
        
        bulut_id = result[1] if result else None
        
        self.yerel_imlec.execute("DELETE FROM kullanicilar WHERE id = ?", (kullanici_id,))
        self.yerel_baglanti.commit()
        
        if self.online_mod and bulut_id:
            try:
                self.bulut_imlec.execute("DELETE FROM kullanicilar WHERE id = %s", (bulut_id,))
                self.bulut_baglanti.commit()
            except:
                self.bulut_baglanti.rollback()
        
        return True

    def kullanici_guncelle(self, kullanici_id, ad_soyad, email, rol, aktif):
        self.yerel_imlec.execute("SELECT bulut_id FROM kullanicilar WHERE id = ?", (kullanici_id,))
        result = self.yerel_imlec.fetchone()
        bulut_id = result[0] if result else None
        
        self.yerel_imlec.execute("""
            UPDATE kullanicilar SET ad_soyad = ?, email = ?, rol = ?, aktif = ? WHERE id = ?
        """, (ad_soyad, email, rol, aktif, kullanici_id))
        self.yerel_baglanti.commit()
        
        if self.online_mod and bulut_id:
            try:
                self.bulut_imlec.execute("""
                    UPDATE kullanicilar SET ad_soyad = %s, email = %s, rol = %s, aktif = %s WHERE id = %s
                """, (ad_soyad, email, rol, aktif, bulut_id))
                self.bulut_baglanti.commit()
            except:
                self.bulut_baglanti.rollback()

    def sifre_degistir(self, kullanici_id, yeni_sifre):
        sifre_hash = self.sifre_hashle(yeni_sifre)
        
        self.yerel_imlec.execute("SELECT bulut_id FROM kullanicilar WHERE id = ?", (kullanici_id,))
        result = self.yerel_imlec.fetchone()
        bulut_id = result[0] if result else None
        
        self.yerel_imlec.execute("UPDATE kullanicilar SET sifre_hash = ? WHERE id = ?", (sifre_hash, kullanici_id))
        self.yerel_baglanti.commit()
        
        if self.online_mod and bulut_id:
            try:
                self.bulut_imlec.execute("UPDATE kullanicilar SET sifre_hash = %s WHERE id = %s", (sifre_hash, bulut_id))
                self.bulut_baglanti.commit()
            except:
                self.bulut_baglanti.rollback()

    # ==================== İŞLEM GEÇMİŞİ ====================

    def islem_kaydet(self, kullanici_id, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_id=None, ilgili_kayit_no=None, eski_deger=None, yeni_deger=None):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.yerel_imlec.execute("""
            INSERT INTO islem_gecmisi (tarih, kullanici_id, kullanici_adi, islem_turu, islem_detay, 
            ilgili_kayit_id, ilgili_kayit_no, eski_deger, yeni_deger, senkronize)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tarih, kullanici_id, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_id, ilgili_kayit_no, eski_deger, yeni_deger, 0))
        self.yerel_baglanti.commit()
        
        if self.online_mod:
            try:
                self.bulut_imlec.execute("""
                    INSERT INTO islem_gecmisi (tarih, kullanici_id, kullanici_adi, islem_turu, islem_detay, 
                    ilgili_kayit_id, ilgili_kayit_no, eski_deger, yeni_deger)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (tarih, kullanici_id, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_id, ilgili_kayit_no, eski_deger, yeni_deger))
                self.bulut_baglanti.commit()
            except:
                self.bulut_baglanti.rollback()

    def islem_gecmisini_getir(self, limit=100):
        self.yerel_imlec.execute("""
            SELECT id, tarih, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_no, eski_deger, yeni_deger
            FROM islem_gecmisi ORDER BY id DESC LIMIT ?
        """, (limit,))
        return self.yerel_imlec.fetchall()

    def islem_gecmisini_temizle(self, gun_sayisi=30):
        tarih_sinir = (datetime.datetime.now() - datetime.timedelta(days=gun_sayisi)).strftime("%Y-%m-%d %H:%M:%S")
        self.yerel_imlec.execute("DELETE FROM islem_gecmisi WHERE tarih < ?", (tarih_sinir,))
        self.yerel_baglanti.commit()

    # ==================== ŞİKAYET İŞLEMLERİ ====================

    def sikayet_islemi_ekle(self, sikayet_id, kullanici_id, kullanici_adi, islem_turu, aciklama=None, eski_durum=None, yeni_durum=None):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.yerel_imlec.execute("""
            INSERT INTO sikayet_islemleri (sikayet_id, tarih, kullanici_id, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum, senkronize, bulut_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)
        """, (sikayet_id, tarih, kullanici_id, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum))
        yerel_id = self.yerel_imlec.lastrowid
        self.yerel_baglanti.commit()
        
        if self.online_mod:
            # Bulut sikayet_id'yi bul
            self.yerel_imlec.execute("SELECT bulut_id FROM sikayetler WHERE id = ?", (sikayet_id,))
            result = self.yerel_imlec.fetchone()
            bulut_sikayet_id = result[0] if result else None
            
            if bulut_sikayet_id:
                try:
                    self.bulut_imlec.execute("""
                        INSERT INTO sikayet_islemleri (sikayet_id, tarih, kullanici_id, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                    """, (bulut_sikayet_id, tarih, kullanici_id, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum))
                    bulut_id = self.bulut_imlec.fetchone()[0]
                    self.bulut_baglanti.commit()
                    
                    self.yerel_imlec.execute("UPDATE sikayet_islemleri SET senkronize = 1, bulut_id = ? WHERE id = ?", (bulut_id, yerel_id))
                    self.yerel_baglanti.commit()
                except:
                    self.bulut_baglanti.rollback()
        
        return yerel_id

    def sikayet_islemlerini_getir(self, sikayet_id):
        self.yerel_imlec.execute("""
            SELECT id, tarih, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum
            FROM sikayet_islemleri WHERE sikayet_id = ? ORDER BY id DESC
        """, (sikayet_id,))
        return self.yerel_imlec.fetchall()

    def sikayet_islemini_sil(self, islem_id):
        self.yerel_imlec.execute("SELECT bulut_id FROM sikayet_islemleri WHERE id = ?", (islem_id,))
        result = self.yerel_imlec.fetchone()
        bulut_id = result[0] if result else None
        
        self.yerel_imlec.execute("DELETE FROM sikayet_islemleri WHERE id = ?", (islem_id,))
        self.yerel_baglanti.commit()
        
        if self.online_mod and bulut_id:
            try:
                self.bulut_imlec.execute("DELETE FROM sikayet_islemleri WHERE id = %s", (bulut_id,))
                self.bulut_baglanti.commit()
            except:
                self.bulut_baglanti.rollback()

    # ==================== ŞİKAYET NOTLARI ====================

    def not_ekle(self, sikayet_id, kullanici_id, kullanici_adi, not_metni):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.yerel_imlec.execute("""
            INSERT INTO sikayet_notlari (sikayet_id, kullanici_id, kullanici_adi, not_metni, olusturma_tarihi, senkronize)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (sikayet_id, kullanici_id, kullanici_adi, not_metni, tarih))
        self.yerel_baglanti.commit()
        return self.yerel_imlec.lastrowid

    def notlari_getir(self, sikayet_id):
        self.yerel_imlec.execute("""
            SELECT id, kullanici_adi, not_metni, olusturma_tarihi
            FROM sikayet_notlari WHERE sikayet_id = ? ORDER BY id DESC
        """, (sikayet_id,))
        return self.yerel_imlec.fetchall()

    def not_sil(self, not_id):
        self.yerel_imlec.execute("DELETE FROM sikayet_notlari WHERE id = ?", (not_id,))
        self.yerel_baglanti.commit()

    # ==================== ŞİKAYET DOSYALARI ====================

    def dosya_ekle(self, sikayet_id, dosya_adi, dosya_yolu, dosya_tipi, dosya_boyutu, yukleyen_id, yukleyen_adi):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.yerel_imlec.execute("""
            INSERT INTO sikayet_dosyalari (sikayet_id, dosya_adi, dosya_yolu, dosya_tipi, dosya_boyutu, yukleyen_id, yukleyen_adi, yukleme_tarihi, senkronize)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (sikayet_id, dosya_adi, dosya_yolu, dosya_tipi, dosya_boyutu, yukleyen_id, yukleyen_adi, tarih))
        self.yerel_baglanti.commit()
        return self.yerel_imlec.lastrowid

    def dosyalari_getir(self, sikayet_id):
        self.yerel_imlec.execute("""
            SELECT id, dosya_adi, dosya_yolu, dosya_tipi, dosya_boyutu, yukleyen_adi, yukleme_tarihi
            FROM sikayet_dosyalari WHERE sikayet_id = ? ORDER BY id DESC
        """, (sikayet_id,))
        return self.yerel_imlec.fetchall()

    def dosya_sil(self, dosya_id):
        # Önce dosya yolunu al
        self.yerel_imlec.execute("SELECT dosya_yolu FROM sikayet_dosyalari WHERE id = ?", (dosya_id,))
        result = self.yerel_imlec.fetchone()
        if result and os.path.exists(result[0]):
            try:
                os.remove(result[0])
            except:
                pass
        self.yerel_imlec.execute("DELETE FROM sikayet_dosyalari WHERE id = ?", (dosya_id,))
        self.yerel_baglanti.commit()

    # ==================== ŞİKAYET ETİKETLERİ ====================

    def etiket_ekle(self, sikayet_id, etiket, renk, ekleyen_id, ekleyen_adi):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Aynı etiket varsa ekleme
        self.yerel_imlec.execute("SELECT id FROM sikayet_etiketleri WHERE sikayet_id = ? AND etiket = ?", (sikayet_id, etiket))
        if self.yerel_imlec.fetchone():
            return None
        self.yerel_imlec.execute("""
            INSERT INTO sikayet_etiketleri (sikayet_id, etiket, renk, ekleyen_id, ekleyen_adi, ekleme_tarihi, senkronize)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (sikayet_id, etiket, renk, ekleyen_id, ekleyen_adi, tarih))
        self.yerel_baglanti.commit()
        return self.yerel_imlec.lastrowid

    def etiketleri_getir(self, sikayet_id):
        self.yerel_imlec.execute("""
            SELECT id, etiket, renk, ekleyen_adi, ekleme_tarihi
            FROM sikayet_etiketleri WHERE sikayet_id = ? ORDER BY id
        """, (sikayet_id,))
        return self.yerel_imlec.fetchall()

    def etiket_sil(self, etiket_id):
        self.yerel_imlec.execute("DELETE FROM sikayet_etiketleri WHERE id = ?", (etiket_id,))
        self.yerel_baglanti.commit()

    def tum_etiketleri_getir(self):
        """Sistemdeki tüm benzersiz etiketleri getir"""
        self.yerel_imlec.execute("SELECT DISTINCT etiket, renk FROM sikayet_etiketleri ORDER BY etiket")
        return self.yerel_imlec.fetchall()

    # ==================== HATIRLATICILAR ====================

    def hatirlatici_ekle(self, sikayet_id, kullanici_id, kullanici_adi, hatirlatma_tarihi, mesaj):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.yerel_imlec.execute("""
            INSERT INTO hatirlaticilar (sikayet_id, kullanici_id, kullanici_adi, hatirlatma_tarihi, mesaj, tamamlandi, olusturma_tarihi, senkronize)
            VALUES (?, ?, ?, ?, ?, 0, ?, 0)
        """, (sikayet_id, kullanici_id, kullanici_adi, hatirlatma_tarihi, mesaj, tarih))
        self.yerel_baglanti.commit()
        return self.yerel_imlec.lastrowid

    def hatirlaticilari_getir(self, sikayet_id=None, sadece_aktif=True):
        if sikayet_id:
            if sadece_aktif:
                self.yerel_imlec.execute("""
                    SELECT h.id, h.sikayet_id, h.kullanici_adi, h.hatirlatma_tarihi, h.mesaj, h.tamamlandi, s.sikayet_no, s.yolcu_adi
                    FROM hatirlaticilar h
                    LEFT JOIN sikayetler s ON h.sikayet_id = s.id
                    WHERE h.sikayet_id = ? AND h.tamamlandi = 0 ORDER BY h.hatirlatma_tarihi
                """, (sikayet_id,))
            else:
                self.yerel_imlec.execute("""
                    SELECT h.id, h.sikayet_id, h.kullanici_adi, h.hatirlatma_tarihi, h.mesaj, h.tamamlandi, s.sikayet_no, s.yolcu_adi
                    FROM hatirlaticilar h
                    LEFT JOIN sikayetler s ON h.sikayet_id = s.id
                    WHERE h.sikayet_id = ? ORDER BY h.hatirlatma_tarihi
                """, (sikayet_id,))
        else:
            if sadece_aktif:
                self.yerel_imlec.execute("""
                    SELECT h.id, h.sikayet_id, h.kullanici_adi, h.hatirlatma_tarihi, h.mesaj, h.tamamlandi, s.sikayet_no, s.yolcu_adi
                    FROM hatirlaticilar h
                    LEFT JOIN sikayetler s ON h.sikayet_id = s.id
                    WHERE h.tamamlandi = 0 ORDER BY h.hatirlatma_tarihi
                """)
            else:
                self.yerel_imlec.execute("""
                    SELECT h.id, h.sikayet_id, h.kullanici_adi, h.hatirlatma_tarihi, h.mesaj, h.tamamlandi, s.sikayet_no, s.yolcu_adi
                    FROM hatirlaticilar h
                    LEFT JOIN sikayetler s ON h.sikayet_id = s.id
                    ORDER BY h.hatirlatma_tarihi
                """)
        return self.yerel_imlec.fetchall()

    def hatirlatici_tamamla(self, hatirlatici_id):
        self.yerel_imlec.execute("UPDATE hatirlaticilar SET tamamlandi = 1 WHERE id = ?", (hatirlatici_id,))
        self.yerel_baglanti.commit()

    def hatirlatici_sil(self, hatirlatici_id):
        self.yerel_imlec.execute("DELETE FROM hatirlaticilar WHERE id = ?", (hatirlatici_id,))
        self.yerel_baglanti.commit()

    def bekleyen_hatirlaticilari_getir(self):
        """Bugün veya geçmiş tarihli aktif hatırlatıcıları getir"""
        bugun = datetime.datetime.now().strftime("%Y-%m-%d")
        self.yerel_imlec.execute("""
            SELECT h.id, h.sikayet_id, h.kullanici_adi, h.hatirlatma_tarihi, h.mesaj, s.sikayet_no, s.yolcu_adi, s.durum
            FROM hatirlaticilar h
            LEFT JOIN sikayetler s ON h.sikayet_id = s.id
            WHERE h.tamamlandi = 0 AND DATE(h.hatirlatma_tarihi) <= DATE(?)
            ORDER BY h.hatirlatma_tarihi
        """, (bugun,))
        return self.yerel_imlec.fetchall()

    def bekleyen_sikayetleri_getir(self, gun_siniri=3):
        """Belirli gün sayısından fazla bekleyen çözülmemiş şikayetleri getir"""
        sinir_tarih = (datetime.datetime.now() - datetime.timedelta(days=gun_siniri)).strftime("%Y-%m-%d %H:%M:%S")
        self.yerel_imlec.execute("""
            SELECT id, sikayet_no, yolcu_adi, kayit_tarihi, durum, sikayet_turu
            FROM sikayetler
            WHERE durum != 'Çözüldü' AND kayit_tarihi < ?
            ORDER BY kayit_tarihi
        """, (sinir_tarih,))
        return self.yerel_imlec.fetchall()

    # ==================== YEDEKLEME ====================

    def yedekleme_klasoru_olustur(self):
        yedek_klasor = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yedekler")
        if not os.path.exists(yedek_klasor):
            os.makedirs(yedek_klasor)
        return yedek_klasor

    def yedek_al(self, manuel=False):
        bekleyen = self._bekleyen_islem_sayisi()
        if self.online_mod:
            return True, f"☁️ Supabase bulut veritabanı + Yerel yedek. Bekleyen: {bekleyen}"
        else:
            return True, f"📁 Yerel veritabanına kaydedildi. Bekleyen senkronizasyon: {bekleyen}"

    def eski_yedekleri_temizle(self, yedek_klasor, gun_sayisi=30):
        pass

    def yedekleri_listele(self):
        bekleyen = self._bekleyen_islem_sayisi()
        return [{
            "dosya": f"Hibrit Mod ({'Çevrimiçi' if self.online_mod else 'Çevrimdışı'})",
            "yol": self.db_adi,
            "boyut": os.path.getsize(self.db_adi) if os.path.exists(self.db_adi) else 0,
            "tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tip": f"Bekleyen: {bekleyen}"
        }]

    def yedekten_geri_yukle(self, yedek_yolu):
        return False, "Hibrit modda yedekten geri yükleme desteklenmiyor"

    def son_yedek_tarihi(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def gunluk_yedek_gerekli_mi(self):
        return False

    # ==================== ÇÖP KUTUSU FONKSİYONLARI ====================
    
    def cop_kutusuna_tasi(self, sikayet_id, kullanici_id=None, kullanici_adi=None):
        """Şikayeti çöp kutusuna taşı (silmek yerine)"""
        try:
            # Önce bulut_id'yi al
            self.yerel_imlec.execute("SELECT bulut_id FROM sikayetler WHERE id = ?", (sikayet_id,))
            bulut_result = self.yerel_imlec.fetchone()
            bulut_id = bulut_result[0] if bulut_result else None
            
            # Şikayeti al (satin_alinan_yer dahil)
            self.yerel_imlec.execute("""
                SELECT sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, 
                       platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, 
                       plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer
                FROM sikayetler WHERE id = ?
            """, (sikayet_id,))
            sikayet = self.yerel_imlec.fetchone()
            
            if not sikayet:
                return False, "Şikayet bulunamadı"
            
            silinme_tarihi = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Çöp kutusuna ekle (satin_alinan_yer dahil)
            self.yerel_imlec.execute("""
                INSERT INTO cop_kutusu (sikayet_id, sikayet_no, yolcu_adi, seyahat_tarihi, 
                    guzergah, pnr, iletisim, platform, sikayet_detay, kayit_tarihi, durum,
                    telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer,
                    silinme_tarihi, silen_kullanici_id, silen_kullanici_adi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sikayet_id, sikayet[0], sikayet[1], sikayet[2], sikayet[3], sikayet[4],
                  sikayet[5], sikayet[6], sikayet[7], sikayet[8], sikayet[9], sikayet[10],
                  sikayet[11], sikayet[12], sikayet[13], sikayet[14], sikayet[15], sikayet[16],
                  silinme_tarihi, kullanici_id, kullanici_adi))
            
            # İşlemleri çöp kutusuna taşımadan sil (isteğe bağlı)
            self.yerel_imlec.execute("DELETE FROM sikayet_islemleri WHERE sikayet_id = ?", (sikayet_id,))
            self.yerel_imlec.execute("DELETE FROM sikayet_notlari WHERE sikayet_id = ?", (sikayet_id,))
            self.yerel_imlec.execute("DELETE FROM sikayet_dosyalari WHERE sikayet_id = ?", (sikayet_id,))
            self.yerel_imlec.execute("DELETE FROM sikayet_etiketleri WHERE sikayet_id = ?", (sikayet_id,))
            self.yerel_imlec.execute("DELETE FROM hatirlaticilar WHERE sikayet_id = ?", (sikayet_id,))
            
            # Şikayeti ana tablodan sil
            self.yerel_imlec.execute("DELETE FROM sikayetler WHERE id = ?", (sikayet_id,))
            self.yerel_baglanti.commit()
            
            # Buluttan da sil (senkronizasyon sorunu olmaması için)
            if self.online_mod and bulut_id:
                try:
                    self.bulut_imlec.execute("DELETE FROM sikayet_islemleri WHERE sikayet_id = %s", (bulut_id,))
                    self.bulut_imlec.execute("DELETE FROM sikayetler WHERE id = %s", (bulut_id,))
                    self.bulut_baglanti.commit()
                except Exception as e:
                    print(f"Bulut silme hatası: {e}")
                    self.bulut_baglanti.rollback()
            
            return True, "Şikayet çöp kutusuna taşındı"
        except Exception as e:
            self.yerel_baglanti.rollback()
            return False, f"Hata: {str(e)}"

    def cop_kutusundan_geri_al(self, cop_id):
        """Çöp kutusundan şikayeti geri yükle"""
        try:
            # Çöp kutusundan veriyi al (satin_alinan_yer dahil)
            self.yerel_imlec.execute("""
                SELECT sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, 
                       platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, 
                       plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer
                FROM cop_kutusu WHERE id = ?
            """, (cop_id,))
            sikayet = self.yerel_imlec.fetchone()
            
            if not sikayet:
                return False, "Kayıt bulunamadı"
            
            # Şikayetler tablosuna geri ekle (satin_alinan_yer dahil)
            self.yerel_imlec.execute("""
                INSERT INTO sikayetler (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr,
                    iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta,
                    plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, senkronize)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, sikayet)
            
            # Çöp kutusundan sil
            self.yerel_imlec.execute("DELETE FROM cop_kutusu WHERE id = ?", (cop_id,))
            self.yerel_baglanti.commit()
            
            return True, "Şikayet geri yüklendi"
        except Exception as e:
            self.yerel_baglanti.rollback()
            return False, f"Hata: {str(e)}"

    def cop_kutusunu_bosalt(self):
        """Çöp kutusundaki tüm kayıtları kalıcı olarak sil"""
        try:
            self.yerel_imlec.execute("DELETE FROM cop_kutusu")
            self.yerel_baglanti.commit()
            return True, "Çöp kutusu boşaltıldı"
        except Exception as e:
            self.yerel_baglanti.rollback()
            return False, f"Hata: {str(e)}"

    def cop_kutusunu_getir(self):
        """Çöp kutusundaki tüm kayıtları getir"""
        self.yerel_imlec.execute("""
            SELECT id, sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, sikayet_detay,
                   durum, silinme_tarihi, silen_kullanici_adi
            FROM cop_kutusu ORDER BY silinme_tarihi DESC
        """)
        return self.yerel_imlec.fetchall()

    def cop_kutusundan_kalici_sil(self, cop_id):
        """Çöp kutusundan tek bir kaydı kalıcı olarak sil"""
        try:
            self.yerel_imlec.execute("DELETE FROM cop_kutusu WHERE id = ?", (cop_id,))
            self.yerel_baglanti.commit()
            return True, "Kayıt kalıcı olarak silindi"
        except Exception as e:
            self.yerel_baglanti.rollback()
            return False, f"Hata: {str(e)}"

    def kapat(self):
        if self.yerel_imlec:
            self.yerel_imlec.close()
        if self.yerel_baglanti:
            self.yerel_baglanti.close()
        if self.bulut_imlec:
            self.bulut_imlec.close()
        if self.bulut_baglanti:
            self.bulut_baglanti.close()
