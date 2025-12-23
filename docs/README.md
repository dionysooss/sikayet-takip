# Şikayet Takip ve Arşivleme Sistemi

Bu uygulama, şikayetleri yerel bir veritabanında saklayan, internet bağlantısı gerektirmeyen ve taşınabilir bir Python uygulamasıdır.

## Özellikler
- **İnternetsiz Çalışma:** Tüm veriler bilgisayarınızda saklanır.
- **Taşınabilirlik:** Bu klasörü başka bir bilgisayara kopyaladığınızda, verileriniz (şikayetleriniz) de taşınır.
- **Arşivleme:** Şikayetleri tarih, müşteri adı ve duruma göre saklar.

## Kurulum ve Çalıştırma

1. Bilgisayarınızda Python'un yüklü olduğundan emin olun. (https://www.python.org/downloads/)
2. Bu klasörün içindeyken terminal veya komut satırını açın.
3. Aşağıdaki komutu yazarak uygulamayı başlatın:

```bash
python main.py
```

## Dosya Yapısı
- `main.py`: Uygulamanın ana arayüz dosyasıdır.
- `veritabani.py`: Veritabanı işlemlerini yöneten dosyadır.
- `sikayet_arsivi.db`: Uygulamayı ilk çalıştırdığınızda otomatik oluşan veritabanı dosyasıdır. Tüm kayıtlarınız buradadır. **Bu dosyayı silmeyin.**

## Taşıma İşlemi
Uygulamayı başka bir bilgisayara taşımak için, `ŞİKAYET TAKİP SİSTEMİ` klasörünü olduğu gibi (içindeki `.db` dosyasıyla birlikte) USB bellek veya başka bir yöntemle kopyalamanız yeterlidir.
