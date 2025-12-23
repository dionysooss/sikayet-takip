import sqlite3
import datetime
import hashlib
import os
import shutil

class VeritabaniYonetici:
    """Yerel Veritabanı Yöneticisi (Çevrimdışı/Offline)"""
    
    def __init__(self, db_adi="sikayet_takip_local.db"):
        self.db_adi = db_adi
        self.baglanti = None
        self.imlec = None
        self.baglanti_kur()
        
    def baglanti_kur(self):
        """Yerel SQLite veritabanına bağlan"""
        try:
            self.baglanti = sqlite3.connect(self.db_adi, check_same_thread=False)
            self.imlec = self.baglanti.cursor()
            self._tablolari_olustur()
            print("📁 Yerel veritabanı hazır")
        except Exception as e:
            print(f"❌ Yerel veritabanı hatası: {e}")

    def _tablolari_olustur(self):
        """Yerel SQLite tablolarını oluştur"""
        # Şikayetler
        self.imlec.execute("""
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
                satin_alinan_yer TEXT,
                basvurulan_yer TEXT,
                bilet_ucreti TEXT
            )
        """)
        
        # Kullanıcılar
        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre_hash TEXT NOT NULL,
                ad_soyad TEXT,
                email TEXT,
                rol TEXT DEFAULT 'kullanici',
                aktif INTEGER DEFAULT 1,
                olusturma_tarihi TEXT,
                son_giris TEXT
            )
        """)
        
        # İşlem Geçmişi
        self.imlec.execute("""
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
                yeni_deger TEXT
            )
        """)
        
        # Şikayet İşlemleri (Detaylı loglar)
        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS sikayet_islemleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                sikayet_id INTEGER, 
                tarih TEXT, 
                kullanici_id INTEGER, 
                kullanici_adi TEXT, 
                islem_turu TEXT, 
                aciklama TEXT, 
                eski_durum TEXT, 
                yeni_durum TEXT
            )
        """)
        
        # Hatırlatıcılar
        self.imlec.execute("""
            CREATE TABLE IF NOT EXISTS hatirlaticilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sikayet_id INTEGER,
                not_metni TEXT,
                hedef_tarih TEXT,
                durum TEXT DEFAULT 'Aktif',
                olusturan_id INTEGER,
                olusturma_tarihi TEXT
            )
        """)

        # Diğer Tablolar
        self.imlec.execute("""CREATE TABLE IF NOT EXISTS sikayet_notlari (id INTEGER PRIMARY KEY, sikayet_id INTEGER, not_metni TEXT, olusturma_tarihi TEXT, kullanici_adi TEXT)""")
        self.imlec.execute("""CREATE TABLE IF NOT EXISTS sikayet_dosyalari (id INTEGER PRIMARY KEY, sikayet_id INTEGER, dosya_adi TEXT, dosya_yolu TEXT)""")
        
        # Sütun güncellemeleri
        cols = ["satin_alinan_yer", "basvurulan_yer", "bilet_ucreti", "tc_kimlik", "koltuk_no"]
        for col in cols:
            try: self.imlec.execute(f"ALTER TABLE sikayetler ADD COLUMN {col} TEXT")
            except: pass
        
        # YENİ: AI ve SLA kolonları
        ai_sla_cols = [
            "ai_kategori",           # AI tarafından önerilen kategori
            "ai_oncelik",            # AI tarafından önerilen öncelik
            "ai_duygu",              # Duygu analizi sonucu
            "ai_ozet",               # AI özeti
            "ai_anahtar_kelimeler",  # Anahtar kelimeler (JSON)
            "sla_hedef_tarih",       # SLA hedef tarihi
            "whatsapp_bildirim"      # WhatsApp bildirimi gönderildi mi (0/1)
        ]
        for col in ai_sla_cols:
            try: self.imlec.execute(f"ALTER TABLE sikayetler ADD COLUMN {col} TEXT")
            except: pass

        # PERFORMANS: Index'ler ekle
        try:
            self.imlec.execute("CREATE INDEX IF NOT EXISTS idx_sikayet_no ON sikayetler(sikayet_no)")
            self.imlec.execute("CREATE INDEX IF NOT EXISTS idx_durum ON sikayetler(durum)")
            self.imlec.execute("CREATE INDEX IF NOT EXISTS idx_kayit_tarihi ON sikayetler(kayit_tarihi DESC)")
            self.imlec.execute("CREATE INDEX IF NOT EXISTS idx_oncelik ON sikayetler(oncelik)")
            self.imlec.execute("CREATE INDEX IF NOT EXISTS idx_yolcu_adi ON sikayetler(yolcu_adi)")
            print("✅ Veritabanı index'leri oluşturuldu")
        except Exception as e:
            print(f"⚠️ Index oluşturma hatası (normal olabilir): {e}")
        
        self.baglanti.commit()
        
        # Admin Hesabı
        self.imlec.execute("SELECT COUNT(*) FROM kullanicilar")
        if self.imlec.fetchone()[0] == 0:
            self.kullanici_ekle("admin", "admin123", "Yönetici", "admin@sistem.com", "admin")

    # --- ŞİKAYET YÖNETİMİ ---
    def sikayetleri_getir(self, limit=None, offset=0, filtre=None, siralama="kayit_tarihi DESC"):
        """
        Şikayetleri sayfalama ve filtre desteğiyle getir
        
        Args:
            limit: Maksimum kayıt sayısı (None = tümü)
            offset: Başlangıç pozisyonu (sayfalama için)
            filtre: Dict - {'durum': 'Yeni', 'oncelik': 'Yüksek', 'arama': 'ahmet', 'tur': 'Personel Davranışı'}
            siralama: Sıralama kriteri (örn: "kayit_tarihi DESC")
        """
        try:
            query = """SELECT id, sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, 
                       platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka, 
                       sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, 
                       bilet_ucreti, tc_kimlik, koltuk_no 
                       FROM sikayetler WHERE 1=1"""
            params = []
            
            # Filtreler
            if filtre:
                if filtre.get('durum') and filtre['durum'] != 'Tümü':
                    query += " AND durum = ?"
                    params.append(filtre['durum'])
                
                if filtre.get('oncelik') and filtre['oncelik'] != 'Tümü':
                    query += " AND oncelik = ?"
                    params.append(filtre['oncelik'])
                
                if filtre.get('tur') and filtre['tur'] != 'Tümü':
                    query += " AND sikayet_turu = ?"
                    params.append(filtre['tur'])
                
                if filtre.get('arama'):
                    arama = f"%{filtre['arama']}%"
                    query += """ AND (yolcu_adi LIKE ? OR telefon LIKE ? OR pnr LIKE ? 
                                OR guzergah LIKE ? OR sikayet_no LIKE ?)"""
                    params.extend([arama, arama, arama, arama, arama])
            
            query += f" ORDER BY {siralama}"
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            self.imlec.execute(query, params)
            return self.imlec.fetchall()
        except Exception as e:
            print(f"❌ Şikayet getirme hatası: {e}")
            return []
    
    def sikayetleri_say(self, filtre=None):
        """Toplam kayıt sayısını döndür (sayfalama için)"""
        try:
            query = "SELECT COUNT(*) FROM sikayetler WHERE 1=1"
            params = []
            
            if filtre:
                if filtre.get('durum') and filtre['durum'] != 'Tümü':
                    query += " AND durum = ?"
                    params.append(filtre['durum'])
                
                if filtre.get('oncelik') and filtre['oncelik'] != 'Tümü':
                    query += " AND oncelik = ?"
                    params.append(filtre['oncelik'])
                
                if filtre.get('tur') and filtre['tur'] != 'Tümü':
                    query += " AND sikayet_turu = ?"
                    params.append(filtre['tur'])
                
                if filtre.get('arama'):
                    arama = f"%{filtre['arama']}%"
                    query += """ AND (yolcu_adi LIKE ? OR telefon LIKE ? OR pnr LIKE ? 
                                OR guzergah LIKE ? OR sikayet_no LIKE ?)"""
                    params.extend([arama, arama, arama, arama, arama])
            
            self.imlec.execute(query, params)
            return self.imlec.fetchone()[0]
        except:
            return 0

    def sikayet_ekle(self, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, telefon="", eposta="", plaka="", sikayet_turu="", lokasyon="", oncelik="", durum="Yeni", satin_alinan_yer="", basvurulan_yer="", bilet_ucreti="", tc_kimlik="", koltuk_no=""):
        try:
            no = self.sikayet_no_olustur()
            tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.imlec.execute("""INSERT INTO sikayetler (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bilet_ucreti, tc_kimlik, koltuk_no) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                               (no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, tarih, durum, telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bilet_ucreti, tc_kimlik, koltuk_no))
            self.baglanti.commit()
            return True
        except Exception as e:
            print(f"HATA: sikayet_ekle sırasında hata oluştu: {e}")
            raise e

    def sikayet_guncelle(self, id, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer="", basvurulan_yer="", bilet_ucreti="", tc_kimlik="", koltuk_no=""):
        try:
            self.imlec.execute("""UPDATE sikayetler SET yolcu_adi=?, seyahat_tarihi=?, guzergah=?, pnr=?, iletisim=?, platform=?, sikayet_detay=?, telefon=?, eposta=?, plaka=?, sikayet_turu=?, lokasyon=?, oncelik=?, satin_alinan_yer=?, basvurulan_yer=?, bilet_ucreti=?, tc_kimlik=?, koltuk_no=? WHERE id=?""", 
                               (yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim, platform, sikayet_detay, telefon, eposta, plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer, basvurulan_yer, bilet_ucreti, tc_kimlik, koltuk_no, id))
            self.baglanti.commit()
        except Exception as e:
            print(f"HATA: sikayet_guncelle sırasında hata: {e}")
            raise e

    def durumu_guncelle(self, id, durum):
        try:
            self.imlec.execute("UPDATE sikayetler SET durum=? WHERE id=?", (durum, id))
            self.baglanti.commit()
        except Exception as e:
            print(f"HATA: durumu_guncelle sırasında hata: {e}")

    def sikayet_sil(self, id):
        try:
            self.imlec.execute("DELETE FROM sikayetler WHERE id=?", (id,))
            self.baglanti.commit()
        except Exception as e:
            print(f"HATA: sikayet_sil sırasında hata: {e}")
            raise e

    def sikayet_no_olustur(self):
        simdi = datetime.datetime.now()
        prefix = f"IPT/{simdi.year}-"
        self.imlec.execute("SELECT sikayet_no FROM sikayetler WHERE sikayet_no LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
        res = self.imlec.fetchone()
        num = int(res[0].split('-')[1]) if res else 0
        return f"{prefix}{num+1:05d}"
    
    def istatistikleri_getir(self):
        stats = {}
        try:
            self.imlec.execute("SELECT COUNT(*) FROM sikayetler")
            stats['toplam'] = self.imlec.fetchone()[0]
            self.imlec.execute("SELECT durum, COUNT(*) FROM sikayetler GROUP BY durum")
            for r in self.imlec.fetchall(): stats[r[0]] = r[1]
        except: pass
        return stats

    # --- KULLANICI İŞLEMLERİ ---
    def sifre_hashle(self, s): return hashlib.sha256(s.encode()).hexdigest()

    def giris_yap(self, kadi, sifre):
        h = self.sifre_hashle(sifre)
        self.imlec.execute("SELECT id, kullanici_adi, ad_soyad, email, rol, aktif FROM kullanicilar WHERE kullanici_adi=? AND sifre_hash=?", (kadi, h))
        u = self.imlec.fetchone()
        if u and u[5] == 1:
            self.imlec.execute("UPDATE kullanicilar SET son_giris=? WHERE id=?", (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), u[0]))
            self.baglanti.commit()
            return {"id":u[0], "kullanici_adi":u[1], "ad_soyad":u[2], "email":u[3], "rol":u[4]}
        return None

    def kullanici_ekle(self, ka, sifre, ad="", em="", rol="kullanici"):
        try:
            self.imlec.execute("INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, email, rol, olusturma_tarihi) VALUES (?,?,?,?,?,?)", 
                               (ka, self.sifre_hashle(sifre), ad, em, rol, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.baglanti.commit()
            return True
        except: return False

    def kullanicilari_getir(self):
        self.imlec.execute("SELECT id, kullanici_adi, ad_soyad, email, rol, aktif, olusturma_tarihi, son_giris FROM kullanicilar")
        return self.imlec.fetchall()
        
    def kullanici_sil(self, uid):
        self.imlec.execute("DELETE FROM kullanicilar WHERE id=?", (uid,))
        self.baglanti.commit()
        return True
        
    def kullanici_guncelle(self, uid, ad, mail, rol, aktif):
        self.imlec.execute("UPDATE kullanicilar SET ad_soyad=?, email=?, rol=?, aktif=? WHERE id=?", (ad, mail, rol, aktif, uid))
        self.baglanti.commit()
        
    def sifre_degistir(self, uid, yeni):
        self.imlec.execute("UPDATE kullanicilar SET sifre_hash=? WHERE id=?", (self.sifre_hashle(yeni), uid))
        self.baglanti.commit()

    # --- MAIN.PY UYUMLULUĞU ---
    
    def islem_kaydet(self, kullanici_id, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_id=None, ilgili_kayit_no=None, eski_deger=None, yeni_deger=None):
        """İşlem geçmişine kayıt at"""
        self.imlec.execute("INSERT INTO islem_gecmisi (tarih, kullanici_id, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_id, ilgili_kayit_no, eski_deger, yeni_deger) VALUES (?,?,?,?,?,?,?,?,?)",
                           (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), kullanici_id, kullanici_adi, islem_turu, islem_detay, ilgili_kayit_id, ilgili_kayit_no, eski_deger, yeni_deger))
        self.baglanti.commit()
        
    def sikayet_islemi_ekle(self, sikayet_id, kullanici_id, kullanici_adi, islem_turu, aciklama, eski_durum=None, yeni_durum=None):
        """Şikayet özelinde işlem kaydı"""
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.imlec.execute("INSERT INTO sikayet_islemleri (sikayet_id, tarih, kullanici_id, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum) VALUES (?,?,?,?,?,?,?,?)",
                           (sikayet_id, tarih, kullanici_id, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum))
        self.baglanti.commit()

    def sikayet_islemlerini_getir(self, sikayet_id):
        self.imlec.execute("SELECT * FROM sikayet_islemleri WHERE sikayet_id=? ORDER BY tarih DESC", (sikayet_id,))
        return self.imlec.fetchall()

    def sikayet_islemini_sil(self, islem_id):
        self.imlec.execute("DELETE FROM sikayet_islemleri WHERE id=?", (islem_id,))
        self.baglanti.commit()


    def notlari_getir(self, sikayet_id):
        try:
            # Sütun kontrolü (Eski veritabanları için)
            try: self.imlec.execute("SELECT kullanici_adi FROM sikayet_notlari LIMIT 1")
            except: 
                try: self.imlec.execute("ALTER TABLE sikayet_notlari ADD COLUMN kullanici_adi TEXT")
                except: pass
            
            self.imlec.execute("SELECT id, kullanici_adi, not_metni, olusturma_tarihi FROM sikayet_notlari WHERE sikayet_id=? ORDER BY olusturma_tarihi DESC", (sikayet_id,))
            res = self.imlec.fetchall()
            # Eğer tuple dönerse (id, user, text, date) formatında olmalı.
            # Eğer kullanıcı adı None ise "Sistem" yap
            sonuc = []
            for r in res:
                r_list = list(r)
                if not r_list[1]: r_list[1] = "Sistem"
                sonuc.append(tuple(r_list))
            return sonuc
        except Exception as e:
            print(f"Not getirme hatası: {e}")
            return []
            
    def not_ekle(self, sikayet_id, kullanici_adi, not_metni):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.imlec.execute("INSERT INTO sikayet_notlari (sikayet_id, kullanici_adi, not_metni, olusturma_tarihi) VALUES (?,?,?,?)",
                            (sikayet_id, kullanici_adi, not_metni, tarih))
            self.baglanti.commit()
            return True
        except: return False

    def not_sil(self, not_id):
        self.imlec.execute("DELETE FROM sikayet_notlari WHERE id=?", (not_id,))
        self.baglanti.commit()


    def baglanti_durumu(self):
        """Offline mod olduğu için sabit"""
        return {"online": True, "bekleyen": 0}

    def yeniden_baglan(self):
        return True

    # --- HATIRLATICI İŞLEMLERİ ---
    def hatirlatici_ekle(self, sikayet_id, not_metni, hedef_tarih, olusturan_id):
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.imlec.execute("INSERT INTO hatirlaticilar (sikayet_id, not_metni, hedef_tarih, olusturan_id, olusturma_tarihi) VALUES (?,?,?,?,?)",
                           (sikayet_id, not_metni, hedef_tarih, olusturan_id, tarih))
        self.baglanti.commit()
        return True

    def hatirlaticilari_getir(self, kullanici_id=None):
        # Sadece aktif hatırlatıcıları getir
        self.imlec.execute("""
            SELECT h.id, h.not_metni, h.hedef_tarih, s.sikayet_no, s.yolcu_adi 
            FROM hatirlaticilar h 
            LEFT JOIN sikayetler s ON h.sikayet_id = s.id 
            WHERE h.durum='Aktif' ORDER BY h.hedef_tarih ASC
        """)
        return self.imlec.fetchall()

    def hatirlatici_tamamla(self, hatirlatici_id):
        self.imlec.execute("UPDATE hatirlaticilar SET durum='Tamamlandı' WHERE id=?", (hatirlatici_id,))
        self.baglanti.commit()

    def hatirlatici_sil(self, hatirlatici_id):
        self.imlec.execute("DELETE FROM hatirlaticilar WHERE id=?", (hatirlatici_id,))
        self.baglanti.commit()

    def islem_gecmisini_getir(self, limit=100):
        self.imlec.execute(f"SELECT * FROM islem_gecmisi ORDER BY id DESC LIMIT {limit}")
        return self.imlec.fetchall()

    def cop_kutusuna_tasi(self, sikayet_id, user_id, user_name):
        self.sikayet_sil(sikayet_id)
        return True, "Sikayet silindi"

    # --- YEDEKLEME ---
    def yedek_al(self, manuel=True):
        try:
            klasor = "yedekler"
            if not os.path.exists(klasor): os.makedirs(klasor)
            ad = f"yedek_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            hedef = os.path.join(klasor, ad)
            shutil.copy2(self.db_adi, hedef)
            return True, hedef
        except Exception as e: return False, str(e)

    def gunluk_yedek_gerekli_mi(self):
        klasor = "yedekler"
        if not os.path.exists(klasor): return True
        bugun = datetime.datetime.now().strftime("%Y%m%d")
        for f in os.listdir(klasor):
            if f.startswith(f"yedek_{bugun}"): return False
        return True
    
    def get_statistics(self):
        """Dashboard için istatistikler"""
        try:
            stats = {}
            # Toplam
            self.imlec.execute("SELECT COUNT(*) FROM sikayetler")
            stats['total'] = self.imlec.fetchone()[0]
            
            # Açık (Yeni + İşlemde)
            self.imlec.execute("SELECT COUNT(*) FROM sikayetler WHERE durum IN ('Yeni', 'İşlemde')")
            stats['open'] = self.imlec.fetchone()[0]
            
            # Kapalı
            self.imlec.execute("SELECT COUNT(*) FROM sikayetler WHERE durum='Kapalı'")
            stats['closed'] = self.imlec.fetchone()[0]
            
            # Acil
            self.imlec.execute("SELECT COUNT(*) FROM sikayetler WHERE oncelik='Acil'")
            stats['urgent'] = self.imlec.fetchone()[0]
            
            return stats
        except Exception as e:
            print(f"İstatistik hatası: {e}")
            return {'total': 0, 'open': 0, 'closed': 0, 'urgent': 0}
