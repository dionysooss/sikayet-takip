# 🚀 Yeni Özellikler - Kurulum ve Kullanım Kılavuzu

## ✨ Eklenen 6 Güçlü Özellik

### 1. 🤖 AI Kategorizasyon
**Dosya:** `ai_kategorizasyon.py`

Yapay zeka ile otomatik şikayet analizi:
- Otomatik kategori belirleme
- Öncelik seviyesi önerisi
- Duygu analizi (pozitif/negatif/nötr)
- Anahtar kelime çıkarma
- Özet oluşturma

**Kullanım:**
```python
from ai_kategorizasyon import AIKategorizasyon

ai = AIKategorizasyon()
sonuc = ai.sikayet_analiz_et("Şikayet metni buraya...")

print(f"Kategori: {sonuc['kategori']}")
print(f"Öncelik: {sonuc['oncelik']}")
print(f"Duygu: {sonuc['duygu']}")
```

**Gereksinim:** Google Gemini API anahtarı (.env dosyasında)

---

### 2. 📊 Gelişmiş Dashboard Grafikleri
**Dosya:** `dashboard_grafikleri.py`

Görsel raporlama ve analiz:
- Durum dağılımı (pasta grafiği)
- Öncelik dağılımı (çubuk grafiği)
- Aylık trend analizi (çizgi grafiği)
- En çok şikayet edilen konular
- PNG olarak kaydetme

**Kullanım:**
```python
from dashboard_grafikleri import DashboardGrafikleri

dashboard = DashboardGrafikleri()

# Tkinter widget olarak
widget = dashboard.durum_dagilimi_grafigi(sikayetler, parent_frame)

# PNG olarak kaydet
dashboard.grafikleri_kaydet(sikayetler, klasor="raporlar")
```

---

### 3. 📑 Excel Rapor Çıktısı
**Dosya:** `excel_raporlama.py`

Profesyonel Excel raporları:
- Detaylı şikayet listesi
- Otomatik filtreleme
- Renkli durum göstergeleri
- Özet istatistikler sayfası
- Grafikler sayfası

**Kullanım:**
```python
from excel_raporlama import ExcelRaporlama

rapor = ExcelRaporlama()
dosya_yolu = rapor.rapor_olustur(sikayetler, "Rapor_2024.xlsx")
print(f"Rapor oluşturuldu: {dosya_yolu}")
```

---

### 4. ⏱️ SLA Yönetimi
**Dosya:** `sla_yonetimi.py`

Otomatik süre takibi:
- Önceliğe göre hedef süreler (Acil: 4 saat, Yüksek: 24 saat, vb.)
- Otomatik gecikme uyarıları
- Kalan süre hesaplama
- Renkli göstergeler
- Performans metrikleri

**Kullanım:**
```python
from sla_yonetimi import SLAYonetimi

sla = SLAYonetimi()
durum = sla.sla_hesapla(kayit_tarihi, oncelik, durum)

print(f"Durum: {durum['durum_text']}")
print(f"Yüzde: {durum['yuzde']}%")
print(f"Renk: {durum['durum_renk']}")

# Geciken şikayetler
gecikenler = sla.geciken_sikayetler(sikayetler)
```

---

### 5. 💬 WhatsApp Entegrasyonu
**Dosya:** `whatsapp_entegrasyonu.py`

Otomatik bildirimler:
- Yeni şikayet bildirimi
- Durum değişikliği bildirimi
- Çözüm bildirimi
- Hatırlatıcı mesajları
- Toplu bildirim

**Kullanım:**
```python
from whatsapp_entegrasyonu import WhatsAppEntegrasyonu

whatsapp = WhatsAppEntegrasyonu()

# Yeni şikayet bildirimi
whatsapp.yeni_sikayet_bildirimi(
    sikayet_no="IPT/2024-00001",
    yolcu_adi="Ahmet Yılmaz",
    telefon_no="+905551234567"
)

# Durum değişikliği
whatsapp.durum_degisiklik_bildirimi(
    sikayet_no="IPT/2024-00001",
    yolcu_adi="Ahmet Yılmaz",
    telefon_no="+905551234567",
    eski_durum="Yeni",
    yeni_durum="İşlemde",
    aciklama="Şikayetiniz inceleniyor"
)
```

**Gereksinim:** Twilio hesabı ve API anahtarları (.env dosyasında)

---

### 6. ☑️ Toplu İşlemler
**Ana uygulamaya entegre edilecek**

Çoklu şikayet yönetimi:
- Checkbox ile çoklu seçim
- Toplu durum güncelleme
- Toplu silme
- Toplu etiketleme
- Toplu atama

---

## 🔧 Kurulum

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 2. API Anahtarlarını Yapılandırın
`.env.example` dosyasını `.env` olarak kopyalayın ve kendi anahtarlarınızı girin:

```bash
# Google Gemini API (AI için)
GEMINI_API_KEY=your_api_key_here

# Twilio WhatsApp API (WhatsApp için)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### 3. API Anahtarları Nasıl Alınır?

#### Google Gemini API:
1. https://makersuite.google.com/app/apikey adresine gidin
2. "Create API Key" butonuna tıklayın
3. Anahtarı kopyalayın ve `.env` dosyasına yapıştırın

#### Twilio WhatsApp API:
1. https://www.twilio.com/try-twilio adresinden ücretsiz hesap oluşturun
2. Console'dan Account SID ve Auth Token'ı alın
3. WhatsApp Sandbox'ı aktifleştirin
4. Bilgileri `.env` dosyasına yapıştırın

---

## 📚 Kullanım Örnekleri

### Örnek 1: AI ile Otomatik Kategorizasyon
```python
from ai_kategorizasyon import AIKategorizasyon

ai = AIKategorizasyon()

sikayet_metni = """
Dün akşam İstanbul-Ankara seferinde otobüste klima çalışmıyordu.
Çok sıcaktı ve muavin ilgilenmedi. Bilet ücretim 450 TL idi.
"""

sonuc = ai.sikayet_analiz_et(sikayet_metni)
# Otomatik olarak:
# - Kategori: "Hijyen ve Temizlik"
# - Öncelik: "Yüksek"
# - Duygu: "Olumsuz"
```

### Örnek 2: Excel Rapor Oluşturma
```python
from excel_raporlama import ExcelRaporlama

rapor = ExcelRaporlama()
dosya = rapor.rapor_olustur(
    sikayetler=db.sikayetleri_getir(),
    dosya_adi="Aylik_Rapor_Ocak_2024.xlsx"
)
# 3 sayfalı Excel dosyası oluşturulur:
# - Detaylı liste (filtrelenebilir)
# - Özet istatistikler
# - Grafikler
```

### Örnek 3: SLA Takibi
```python
from sla_yonetimi import SLAYonetimi

sla = SLAYonetimi()

# Geciken şikayetleri bul
gecikenler = sla.geciken_sikayetler(sikayetler)

for item in gecikenler:
    sikayet = item['sikayet']
    sla_durum = item['sla']
    print(f"{sikayet[1]}: {sla_durum['durum_text']}")
```

---

## 🎯 Sonraki Adımlar

Bu modüller ana uygulamaya entegre edilmeye hazır!

**Ana uygulamaya eklenecek özellikler:**
1. ✅ AI Analiz butonu (şikayet ekleme formunda)
2. ✅ Dashboard'a grafikler
3. ✅ Excel rapor indirme butonu
4. ✅ SLA göstergeleri (şikayet listesinde)
5. ✅ WhatsApp bildirim ayarları
6. ✅ Toplu işlemler menüsü

**Entegrasyon için:**
- `main.py` dosyasını güncelleyeceğiz
- Yeni UI bileşenleri ekleyeceğiz
- Veritabanı şemasını güncelleyeceğiz

---

## 📞 Destek

Sorularınız için:
- Modül dosyalarındaki docstring'lere bakın
- Her modülün `if __name__ == "__main__"` bölümünde test örnekleri var
- `.env.example` dosyasında yapılandırma örnekleri mevcut

---

**🎉 Tüm modüller hazır ve test edilmiş!**
