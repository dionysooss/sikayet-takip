# 🌐 Şikayet Takip Web Uygulaması - Ücretsiz Deploy

## ✅ Uygulama Hazır!

Web versiyonu çalışıyor. Şimdi ücretsiz olarak internete yayınlayalım.

---

## 🚀 Render.com'da Ücretsiz Yayınlama (En Kolay)

### Adım 1: GitHub'a Yükle

1. https://github.com adresine git, hesap aç (yoksa)
2. "New Repository" tıkla
3. İsim: `sikayet-takip`
4. "Create repository" tıkla
5. Aşağıdaki dosyaları yükle:
   - `web/` klasörü (tüm içeriğiyle)
   - `requirements.txt`
   - `Procfile`

### Adım 2: Render.com'a Deploy

1. https://render.com adresine git, GitHub ile giriş yap
2. "New +" → "Web Service"
3. GitHub reposunu seç
4. Ayarlar:
   - **Name:** sikayet-takip
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn web.app:app`
5. Environment Variables ekle:
   - `SUPABASE_HOST` = db.whjoxpdlzraxuyabitfb.supabase.co
   - `SUPABASE_DATABASE` = postgres
   - `SUPABASE_USER` = postgres
   - `SUPABASE_PASSWORD` = dEmLmkl2ezShVMx8
   - `SUPABASE_PORT` = 5432
6. "Create Web Service" tıkla

### Adım 3: Bitti! 🎉

URL'in: `https://sikayet-takip.onrender.com`

---

## 🔑 Giriş Bilgileri

- **Kullanıcı:** admin
- **Şifre:** admin123

---

## 📱 Özellikler

- ✅ Windows, Mac, iPhone, Android - hepsi çalışır
- ✅ Kurulum YOK - tarayıcıdan aç
- ✅ Aynı veritabanı - masaüstü uygulamayla senkron
- ✅ 7/24 çalışır

---

## ⚠️ Notlar

- Render ücretsiz planda 15 dk kullanılmazsa uyur (ilk açılış 30 sn sürer)
- Ücretli plan ($7/ay) alırsan hep açık kalır
