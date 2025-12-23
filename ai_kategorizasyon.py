"""
AI Kategorizasyon Modülü
Google Gemini API kullanarak şikayet analizi
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class AIKategorizasyon:
    def __init__(self):
        """Gemini API'yi yapılandır"""
        api_key = os.getenv('GEMINI_API_KEY', '')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.aktif = True
        else:
            self.aktif = False
            print("⚠️ GEMINI_API_KEY bulunamadı. AI özellikleri devre dışı.")
    
    def sikayet_analiz_et(self, sikayet_metni):
        """
        Şikayet metnini analiz eder ve kategori, öncelik ve duygu analizi döner
        
        Args:
            sikayet_metni (str): Analiz edilecek şikayet metni
            
        Returns:
            dict: {
                'kategori': str,
                'oncelik': str,
                'duygu': str,
                'ozet': str,
                'anahtar_kelimeler': list
            }
        """
        if not self.aktif or not sikayet_metni:
            return self._varsayilan_analiz()
        
        try:
            prompt = f"""
Aşağıdaki otobüs şirketine yapılan şikayeti analiz et ve JSON formatında yanıt ver:

ŞİKAYET METNİ:
{sikayet_metni}

GÖREV:
1. Şikayetin kategorisini belirle (şu kategorilerden biri olmalı):
   - Personel Davranışı
   - Rötar / Sefer İptali
   - Bagaj Hasarı
   - Bagaj Karışıklığı
   - Hijyen ve Temizlik
   - İkram Hizmetleri
   - Abonelik ve Puan İşlemleri
   - Hatalı Çekim ve İade
   - Elektronik Bilet İşlemleri
   - Diğer

2. Öncelik seviyesini belirle:
   - Acil: Ciddi güvenlik sorunu, yaralanma, büyük maddi zarar
   - Yüksek: Önemli hizmet aksaklığı, müşteri memnuniyetsizliği
   - Orta: Standart şikayetler
   - Düşük: Küçük sorunlar, öneriler

3. Duygu analizi yap:
   - Çok Olumsuz: Çok kızgın, hayal kırıklığı
   - Olumsuz: Memnuniyetsiz
   - Nötr: Tarafsız bildirim
   - Olumlu: Yapıcı eleştiri

4. Kısa özet (max 100 karakter)

5. Anahtar kelimeler (max 5 kelime)

YANIT FORMATI (sadece JSON döndür, başka açıklama ekleme):
{{
    "kategori": "...",
    "oncelik": "...",
    "duygu": "...",
    "ozet": "...",
    "anahtar_kelimeler": ["...", "..."]
}}
"""
            
            response = self.model.generate_content(prompt)
            
            # JSON parse et
            import json
            # Yanıttan JSON'ı çıkar (markdown kod bloğu varsa temizle)
            response_text = response.text.strip()
            if response_text.startswith('```'):
                # Markdown kod bloğunu temizle
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            analiz = json.loads(response_text.strip())
            
            # Güvenlik kontrolü - geçerli değerler mi?
            gecerli_kategoriler = [
                "Personel Davranışı", "Rötar / Sefer İptali", "Bagaj Hasarı",
                "Bagaj Karışıklığı", "Hijyen ve Temizlik", "İkram Hizmetleri",
                "Abonelik ve Puan İşlemleri", "Hatalı Çekim ve İade",
                "Elektronik Bilet İşlemleri", "Diğer"
            ]
            
            if analiz.get('kategori') not in gecerli_kategoriler:
                analiz['kategori'] = "Diğer"
            
            if analiz.get('oncelik') not in ["Acil", "Yüksek", "Orta", "Düşük"]:
                analiz['oncelik'] = "Orta"
            
            return analiz
            
        except Exception as e:
            print(f"AI Analiz Hatası: {e}")
            return self._varsayilan_analiz()
    
    def _varsayilan_analiz(self):
        """AI kullanılamadığında varsayılan değerler"""
        return {
            'kategori': 'Diğer',
            'oncelik': 'Orta',
            'duygu': 'Nötr',
            'ozet': 'Manuel inceleme gerekli',
            'anahtar_kelimeler': []
        }
    
    def toplu_analiz(self, sikayet_listesi):
        """
        Birden fazla şikayeti analiz eder
        
        Args:
            sikayet_listesi (list): [(id, metin), ...] formatında liste
            
        Returns:
            dict: {id: analiz_sonucu, ...}
        """
        sonuclar = {}
        for sikayet_id, metin in sikayet_listesi:
            sonuclar[sikayet_id] = self.sikayet_analiz_et(metin)
        return sonuclar


# Test fonksiyonu
if __name__ == "__main__":
    ai = AIKategorizasyon()
    
    test_sikayet = """
    Dün akşam İstanbul-Ankara seferinde otobüste klima çalışmıyordu. 
    Çok sıcaktı ve muavin ilgilenmedi. Ayrıca koltuklar çok kirliydi.
    Bilet ücretim 450 TL idi ve bu hizmeti hak etmedim.
    """
    
    sonuc = ai.sikayet_analiz_et(test_sikayet)
    print("AI Analiz Sonucu:")
    print(f"Kategori: {sonuc['kategori']}")
    print(f"Öncelik: {sonuc['oncelik']}")
    print(f"Duygu: {sonuc['duygu']}")
    print(f"Özet: {sonuc['ozet']}")
    print(f"Anahtar Kelimeler: {', '.join(sonuc['anahtar_kelimeler'])}")
