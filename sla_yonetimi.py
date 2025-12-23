"""
SLA (Service Level Agreement) Yönetimi Modülü
Şikayet çözüm sürelerini takip eder
"""

import datetime
from typing import Dict, Tuple


class SLAYonetimi:
    def __init__(self):
        """
        SLA kuralları:
        - Acil: 4 saat
        - Yüksek: 24 saat (1 gün)
        - Orta: 72 saat (3 gün)
        - Düşük: 168 saat (7 gün)
        """
        self.sla_sureler = {
            'Acil': 4,      # saat
            'Yüksek': 24,   # saat
            'Orta': 72,     # saat
            'Düşük': 168    # saat
        }
    
    def sla_hesapla(self, kayit_tarihi: str, oncelik: str, durum: str) -> Dict:
        """
        Şikayet için SLA durumunu hesaplar
        
        Args:
            kayit_tarihi (str): Şikayetin kayıt tarihi
            oncelik (str): Öncelik seviyesi
            durum (str): Mevcut durum
            
        Returns:
            dict: {
                'hedef_tarih': datetime,
                'kalan_sure': timedelta,
                'gecikme': bool,
                'gecikme_suresi': timedelta veya None,
                'durum_renk': str,
                'yuzde': int
            }
        """
        try:
            # Tarihi parse et
            if ' ' in kayit_tarihi:
                kayit = datetime.datetime.strptime(kayit_tarihi, '%Y-%m-%d %H:%M:%S')
            else:
                kayit = datetime.datetime.strptime(kayit_tarihi, '%Y-%m-%d')
        except:
            # Hatalı tarih formatı
            return self._varsayilan_sla()
        
        # Çözülmüş şikayetler için SLA hesaplama
        if durum in ['Çözüldü', 'Kapalı']:
            return {
                'hedef_tarih': None,
                'kalan_sure': None,
                'gecikme': False,
                'gecikme_suresi': None,
                'durum_renk': 'success',
                'yuzde': 100,
                'durum_text': 'Tamamlandı'
            }
        
        # SLA süresini al
        sla_saat = self.sla_sureler.get(oncelik, 72)  # Varsayılan: Orta
        hedef_tarih = kayit + datetime.timedelta(hours=sla_saat)
        
        # Şu anki zaman
        simdi = datetime.datetime.now()
        
        # Kalan süre
        kalan_sure = hedef_tarih - simdi
        
        # Gecikme kontrolü
        gecikme = kalan_sure.total_seconds() < 0
        gecikme_suresi = abs(kalan_sure) if gecikme else None
        
        # Yüzde hesaplama
        toplam_sure = datetime.timedelta(hours=sla_saat)
        gecen_sure = simdi - kayit
        yuzde = min(100, int((gecen_sure.total_seconds() / toplam_sure.total_seconds()) * 100))
        
        # Durum rengi
        if gecikme:
            durum_renk = 'danger'
            durum_text = f'GECİKME: {self._sure_formatla(gecikme_suresi)}'
        elif yuzde >= 80:
            durum_renk = 'warning'
            durum_text = f'KALAN: {self._sure_formatla(kalan_sure)}'
        else:
            durum_renk = 'success'
            durum_text = f'KALAN: {self._sure_formatla(kalan_sure)}'
        
        return {
            'hedef_tarih': hedef_tarih,
            'kalan_sure': kalan_sure,
            'gecikme': gecikme,
            'gecikme_suresi': gecikme_suresi,
            'durum_renk': durum_renk,
            'yuzde': yuzde,
            'durum_text': durum_text
        }
    
    def _sure_formatla(self, timedelta_obj) -> str:
        """Timedelta'yı okunabilir formata çevir"""
        if not timedelta_obj:
            return "0s"
        
        total_seconds = int(abs(timedelta_obj.total_seconds()))
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}g")
        if hours > 0:
            parts.append(f"{hours}s")
        if minutes > 0 and days == 0:  # Günler varsa dakikaları gösterme
            parts.append(f"{minutes}d")
        
        return " ".join(parts) if parts else "0d"
    
    def _varsayilan_sla(self) -> Dict:
        """Hatalı veri için varsayılan SLA"""
        return {
            'hedef_tarih': None,
            'kalan_sure': None,
            'gecikme': False,
            'gecikme_suresi': None,
            'durum_renk': 'secondary',
            'yuzde': 0,
            'durum_text': 'Bilinmiyor'
        }
    
    def geciken_sikayetler(self, sikayetler) -> list:
        """
        Geciken şikayetleri listele
        
        Args:
            sikayetler (list): Tüm şikayetler
            
        Returns:
            list: Geciken şikayetlerin listesi
        """
        gecikenler = []
        
        for sikayet in sikayetler:
            kayit_tarihi = sikayet[9]
            oncelik = sikayet[16] if len(sikayet) > 16 else 'Orta'
            durum = sikayet[10]
            
            sla = self.sla_hesapla(kayit_tarihi, oncelik, durum)
            
            if sla['gecikme']:
                gecikenler.append({
                    'sikayet': sikayet,
                    'sla': sla
                })
        
        # Gecikme süresine göre sırala (en çok geciken önce)
        gecikenler.sort(key=lambda x: x['sla']['gecikme_suresi'], reverse=True)
        
        return gecikenler
    
    def sla_performansi(self, sikayetler) -> Dict:
        """
        Genel SLA performans metrikleri
        
        Returns:
            dict: {
                'toplam': int,
                'zamaninda': int,
                'geciken': int,
                'basari_orani': float
            }
        """
        toplam = 0
        zamaninda = 0
        geciken = 0
        
        for sikayet in sikayetler:
            # Sadece aktif şikayetleri say
            durum = sikayet[10]
            if durum in ['Çözüldü', 'Kapalı']:
                continue
            
            kayit_tarihi = sikayet[9]
            oncelik = sikayet[16] if len(sikayet) > 16 else 'Orta'
            
            sla = self.sla_hesapla(kayit_tarihi, oncelik, durum)
            
            toplam += 1
            if sla['gecikme']:
                geciken += 1
            else:
                zamaninda += 1
        
        basari_orani = (zamaninda / toplam * 100) if toplam > 0 else 0
        
        return {
            'toplam': toplam,
            'zamaninda': zamaninda,
            'geciken': geciken,
            'basari_orani': round(basari_orani, 1)
        }
    
    def sla_renk_kodu(self, yuzde: int) -> str:
        """
        SLA yüzdesine göre renk kodu döner
        
        Args:
            yuzde (int): SLA tamamlanma yüzdesi
            
        Returns:
            str: Hex renk kodu
        """
        if yuzde >= 100:
            return '#F44336'  # Kırmızı - Gecikmiş
        elif yuzde >= 80:
            return '#FF9800'  # Turuncu - Kritik
        elif yuzde >= 50:
            return '#FFC107'  # Sarı - Dikkat
        else:
            return '#4CAF50'  # Yeşil - İyi


# Test
if __name__ == "__main__":
    sla = SLAYonetimi()
    
    # Test 1: Yeni şikayet (2 saat önce, Acil)
    test_tarih = (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    sonuc = sla.sla_hesapla(test_tarih, 'Acil', 'Yeni')
    print(f"Test 1 - Acil (2 saat önce):")
    print(f"  Durum: {sonuc['durum_text']}")
    print(f"  Yüzde: {sonuc['yuzde']}%")
    print(f"  Renk: {sonuc['durum_renk']}")
    print()
    
    # Test 2: Gecikmiş şikayet (5 saat önce, Acil)
    test_tarih2 = (datetime.datetime.now() - datetime.timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
    sonuc2 = sla.sla_hesapla(test_tarih2, 'Acil', 'Yeni')
    print(f"Test 2 - Acil (5 saat önce - GECİKMİŞ):")
    print(f"  Durum: {sonuc2['durum_text']}")
    print(f"  Yüzde: {sonuc2['yuzde']}%")
    print(f"  Renk: {sonuc2['durum_renk']}")
    print()
    
    # Test 3: Çözülmüş şikayet
    sonuc3 = sla.sla_hesapla(test_tarih, 'Yüksek', 'Çözüldü')
    print(f"Test 3 - Çözülmüş:")
    print(f"  Durum: {sonuc3['durum_text']}")
    print(f"  Yüzde: {sonuc3['yuzde']}%")
