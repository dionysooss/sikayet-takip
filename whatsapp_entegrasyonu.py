"""
WhatsApp Entegrasyonu Modülü
Twilio API ile WhatsApp mesajlaşma
"""

from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()


class WhatsAppEntegrasyonu:
    def __init__(self):
        """Twilio API yapılandırması"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.whatsapp_from = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')  # Twilio Sandbox
        
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.aktif = True
                print("✅ WhatsApp entegrasyonu aktif")
            except Exception as e:
                self.aktif = False
                print(f"⚠️ WhatsApp entegrasyonu başlatılamadı: {e}")
        else:
            self.aktif = False
            print("⚠️ Twilio bilgileri bulunamadı. WhatsApp özellikleri devre dışı.")
    
    def mesaj_gonder(self, telefon_no: str, mesaj: str) -> bool:
        """
        WhatsApp mesajı gönder
        
        Args:
            telefon_no (str): Alıcı telefon numarası (örn: +905551234567)
            mesaj (str): Gönderilecek mesaj
            
        Returns:
            bool: Başarılı ise True
        """
        if not self.aktif:
            print("WhatsApp entegrasyonu aktif değil")
            return False
        
        try:
            # Telefon numarasını formatla
            if not telefon_no.startswith('+'):
                # Türkiye için varsayılan
                telefon_no = '+90' + telefon_no.replace(' ', '').replace('-', '')
            
            whatsapp_to = f'whatsapp:{telefon_no}'
            
            # Mesaj gönder
            message = self.client.messages.create(
                from_=self.whatsapp_from,
                body=mesaj,
                to=whatsapp_to
            )
            
            print(f"✅ WhatsApp mesajı gönderildi: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ WhatsApp mesajı gönderilemedi: {e}")
            return False
    
    def yeni_sikayet_bildirimi(self, sikayet_no: str, yolcu_adi: str, telefon_no: str) -> bool:
        """
        Yeni şikayet bildirimi gönder
        
        Args:
            sikayet_no (str): Şikayet numarası
            yolcu_adi (str): Yolcu adı
            telefon_no (str): Telefon numarası
            
        Returns:
            bool: Başarılı ise True
        """
        mesaj = f"""
🎫 *Şikayet Takip Sistemi*

Sayın {yolcu_adi},

Şikayetiniz başarıyla kaydedilmiştir.

📋 *Şikayet No:* {sikayet_no}
⏰ *Durum:* Yeni
✅ *İşlem:* En kısa sürede değerlendirilecektir

Şikayetinizin durumunu takip edebilirsiniz.

Teşekkür ederiz.
"""
        return self.mesaj_gonder(telefon_no, mesaj.strip())
    
    def durum_degisiklik_bildirimi(self, sikayet_no: str, yolcu_adi: str, telefon_no: str, 
                                   eski_durum: str, yeni_durum: str, aciklama: str = "") -> bool:
        """
        Durum değişikliği bildirimi gönder
        
        Args:
            sikayet_no (str): Şikayet numarası
            yolcu_adi (str): Yolcu adı
            telefon_no (str): Telefon numarası
            eski_durum (str): Eski durum
            yeni_durum (str): Yeni durum
            aciklama (str): Ek açıklama (opsiyonel)
            
        Returns:
            bool: Başarılı ise True
        """
        # Durum emoji'leri
        durum_emoji = {
            'Yeni': '🆕',
            'İşlemde': '⏳',
            'Çözüldü': '✅',
            'Kapalı': '🔒'
        }
        
        emoji = durum_emoji.get(yeni_durum, '📌')
        
        mesaj = f"""
🎫 *Şikayet Takip Sistemi*

Sayın {yolcu_adi},

Şikayetinizin durumu güncellendi.

📋 *Şikayet No:* {sikayet_no}
{emoji} *Yeni Durum:* {yeni_durum}
"""
        
        if aciklama:
            mesaj += f"\n💬 *Açıklama:* {aciklama}\n"
        
        mesaj += "\nTeşekkür ederiz."
        
        return self.mesaj_gonder(telefon_no, mesaj.strip())
    
    def cozum_bildirimi(self, sikayet_no: str, yolcu_adi: str, telefon_no: str, 
                       cozum_aciklamasi: str) -> bool:
        """
        Şikayet çözüm bildirimi gönder
        
        Args:
            sikayet_no (str): Şikayet numarası
            yolcu_adi (str): Yolcu adı
            telefon_no (str): Telefon numarası
            cozum_aciklamasi (str): Çözüm açıklaması
            
        Returns:
            bool: Başarılı ise True
        """
        mesaj = f"""
🎫 *Şikayet Takip Sistemi*

Sayın {yolcu_adi},

Şikayetiniz çözüme kavuşturulmuştur.

📋 *Şikayet No:* {sikayet_no}
✅ *Durum:* Çözüldü

💬 *Çözüm:*
{cozum_aciklamasi}

Memnuniyetiniz bizim için önemlidir.

Teşekkür ederiz.
"""
        return self.mesaj_gonder(telefon_no, mesaj.strip())
    
    def hatirlatici_mesaji(self, sikayet_no: str, yolcu_adi: str, telefon_no: str, 
                          hatirlatma_mesaji: str) -> bool:
        """
        Hatırlatıcı mesajı gönder
        
        Args:
            sikayet_no (str): Şikayet numarası
            yolcu_adi (str): Yolcu adı
            telefon_no (str): Telefon numarası
            hatirlatma_mesaji (str): Hatırlatma mesajı
            
        Returns:
            bool: Başarılı ise True
        """
        mesaj = f"""
🎫 *Şikayet Takip Sistemi*

Sayın {yolcu_adi},

📋 *Şikayet No:* {sikayet_no}

🔔 *Hatırlatma:*
{hatirlatma_mesaji}

Teşekkür ederiz.
"""
        return self.mesaj_gonder(telefon_no, mesaj.strip())
    
    def toplu_bildirim(self, alicilar: list, mesaj: str) -> dict:
        """
        Birden fazla kişiye aynı mesajı gönder
        
        Args:
            alicilar (list): [(telefon_no, yolcu_adi), ...] formatında liste
            mesaj (str): Gönderilecek mesaj
            
        Returns:
            dict: {'basarili': int, 'basarisiz': int, 'detay': [...]}
        """
        sonuclar = {
            'basarili': 0,
            'basarisiz': 0,
            'detay': []
        }
        
        for telefon_no, yolcu_adi in alicilar:
            # Mesajı kişiselleştir
            kisisel_mesaj = mesaj.replace('{yolcu_adi}', yolcu_adi)
            
            basarili = self.mesaj_gonder(telefon_no, kisisel_mesaj)
            
            if basarili:
                sonuclar['basarili'] += 1
                sonuclar['detay'].append({
                    'telefon': telefon_no,
                    'durum': 'Başarılı'
                })
            else:
                sonuclar['basarisiz'] += 1
                sonuclar['detay'].append({
                    'telefon': telefon_no,
                    'durum': 'Başarısız'
                })
        
        return sonuclar


# Test
if __name__ == "__main__":
    whatsapp = WhatsAppEntegrasyonu()
    
    if whatsapp.aktif:
        # Test mesajı (kendi numaranızı kullanın)
        test_telefon = "+905551234567"  # BURAYA KENDİ NUMARANIZI YAZIN
        
        print("Test mesajı gönderiliyor...")
        basarili = whatsapp.yeni_sikayet_bildirimi(
            sikayet_no="IPT/2024-00001",
            yolcu_adi="Test Kullanıcı",
            telefon_no=test_telefon
        )
        
        if basarili:
            print("✅ Test mesajı başarıyla gönderildi!")
        else:
            print("❌ Test mesajı gönderilemedi!")
    else:
        print("WhatsApp entegrasyonu aktif değil.")
        print("\nAktifleştirmek için .env dosyasına şunları ekleyin:")
        print("TWILIO_ACCOUNT_SID=your_account_sid")
        print("TWILIO_AUTH_TOKEN=your_auth_token")
        print("TWILIO_WHATSAPP_FROM=whatsapp:+14155238886")
