"""
Dashboard Grafikleri Modülü
Matplotlib ile görsel raporlar
"""

import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışması için
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from collections import Counter
import os

# Türkçe karakter desteği
plt.rcParams['font.family'] = 'DejaVu Sans'


class DashboardGrafikleri:
    def __init__(self):
        self.renkler = {
            'Yeni': '#2196F3',
            'İşlemde': '#FFC107',
            'Çözüldü': '#4CAF50',
            'Kapalı': '#9E9E9E'
        }
        
        self.oncelik_renkleri = {
            'Acil': '#F44336',
            'Yüksek': '#FF9800',
            'Orta': '#FFC107',
            'Düşük': '#2196F3'
        }
    
    def durum_dagilimi_grafigi(self, sikayetler, canvas_parent=None):
        """
        Durum dağılımı pasta grafiği
        
        Args:
            sikayetler (list): Şikayet listesi
            canvas_parent: Tkinter parent widget (opsiyonel)
            
        Returns:
            Figure veya Canvas
        """
        # Durum sayımı
        durumlar = [s[10] for s in sikayetler]
        durum_sayim = Counter(durumlar)
        
        # Grafik oluştur
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        labels = list(durum_sayim.keys())
        sizes = list(durum_sayim.values())
        colors = [self.renkler.get(label, '#999999') for label in labels]
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 10})
        ax.set_title('Durum Dağılımı', fontsize=12, fontweight='bold', pad=20)
        
        fig.tight_layout()
        
        if canvas_parent:
            canvas = FigureCanvasTkAgg(fig, master=canvas_parent)
            canvas.draw()
            return canvas.get_tk_widget()
        else:
            return fig
    
    def oncelik_dagilimi_grafigi(self, sikayetler, canvas_parent=None):
        """Öncelik dağılımı çubuk grafiği"""
        # Öncelik sayımı
        oncelikler = [s[16] if len(s) > 16 and s[16] else 'Belirtilmemiş' for s in sikayetler]
        oncelik_sayim = Counter(oncelikler)
        
        # Sıralama
        sira = ['Acil', 'Yüksek', 'Orta', 'Düşük', 'Belirtilmemiş']
        labels = [o for o in sira if o in oncelik_sayim]
        sizes = [oncelik_sayim[o] for o in labels]
        colors = [self.oncelik_renkleri.get(label, '#999999') for label in labels]
        
        # Grafik
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        bars = ax.bar(labels, sizes, color=colors, alpha=0.8)
        ax.set_title('Öncelik Dağılımı', fontsize=12, fontweight='bold', pad=20)
        ax.set_ylabel('Adet', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        # Değerleri çubukların üstüne yaz
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        
        if canvas_parent:
            canvas = FigureCanvasTkAgg(fig, master=canvas_parent)
            canvas.draw()
            return canvas.get_tk_widget()
        else:
            return fig
    
    def aylik_trend_grafigi(self, sikayetler, canvas_parent=None):
        """Aylık şikayet trendi çizgi grafiği"""
        # Tarih bazlı sayım
        aylik_sayim = {}
        
        for sikayet in sikayetler:
            kayit_tarihi = sikayet[9]  # kayit_tarihi
            if kayit_tarihi:
                try:
                    # Tarih formatını parse et
                    if ' ' in kayit_tarihi:
                        tarih = datetime.datetime.strptime(kayit_tarihi.split()[0], '%Y-%m-%d')
                    else:
                        tarih = datetime.datetime.strptime(kayit_tarihi, '%Y-%m-%d')
                    
                    ay_key = tarih.strftime('%Y-%m')
                    aylik_sayim[ay_key] = aylik_sayim.get(ay_key, 0) + 1
                except:
                    pass
        
        if not aylik_sayim:
            # Veri yoksa boş grafik
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Veri Yok', ha='center', va='center', fontsize=14)
            ax.set_title('Aylık Trend', fontsize=12, fontweight='bold')
            fig.tight_layout()
            
            if canvas_parent:
                canvas = FigureCanvasTkAgg(fig, master=canvas_parent)
                canvas.draw()
                return canvas.get_tk_widget()
            return fig
        
        # Sırala
        sorted_aylar = sorted(aylik_sayim.items())
        aylar = [ay for ay, _ in sorted_aylar]
        sayilar = [sayi for _, sayi in sorted_aylar]
        
        # Grafik
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(aylar, sayilar, marker='o', linewidth=2, markersize=8, color='#2196F3')
        ax.fill_between(range(len(aylar)), sayilar, alpha=0.3, color='#2196F3')
        
        ax.set_title('Aylık Şikayet Trendi', fontsize=12, fontweight='bold', pad=20)
        ax.set_ylabel('Şikayet Sayısı', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # X ekseni etiketlerini döndür
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        
        if canvas_parent:
            canvas = FigureCanvasTkAgg(fig, master=canvas_parent)
            canvas.draw()
            return canvas.get_tk_widget()
        else:
            return fig
    
    def en_cok_sikayet_edilen_konular(self, sikayetler, canvas_parent=None, top_n=5):
        """En çok şikayet edilen konular yatay çubuk grafiği"""
        # Tür sayımı
        turler = [s[14] if len(s) > 14 and s[14] else 'Belirtilmemiş' for s in sikayetler]
        tur_sayim = Counter(turler)
        
        # En çok şikayet edilen top_n tür
        en_coklar = tur_sayim.most_common(top_n)
        
        if not en_coklar:
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Veri Yok', ha='center', va='center', fontsize=14)
            ax.set_title('En Çok Şikayet Edilen Konular', fontsize=12, fontweight='bold')
            fig.tight_layout()
            
            if canvas_parent:
                canvas = FigureCanvasTkAgg(fig, master=canvas_parent)
                canvas.draw()
                return canvas.get_tk_widget()
            return fig
        
        labels = [tur for tur, _ in en_coklar]
        sizes = [sayi for _, sayi in en_coklar]
        
        # Grafik
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        y_pos = range(len(labels))
        bars = ax.barh(y_pos, sizes, color='#FF5722', alpha=0.8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.invert_yaxis()  # En yüksek üstte
        ax.set_xlabel('Şikayet Sayısı', fontsize=10)
        ax.set_title(f'En Çok Şikayet Edilen {top_n} Konu', fontsize=12, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        # Değerleri çubukların sonuna yaz
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {int(width)}',
                   ha='left', va='center', fontsize=9)
        
        fig.tight_layout()
        
        if canvas_parent:
            canvas = FigureCanvasTkAgg(fig, master=canvas_parent)
            canvas.draw()
            return canvas.get_tk_widget()
        else:
            return fig
    
    def grafikleri_kaydet(self, sikayetler, klasor="raporlar"):
        """Tüm grafikleri PNG olarak kaydet"""
        if not os.path.exists(klasor):
            os.makedirs(klasor)
        
        tarih = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Durum dağılımı
        fig1 = self.durum_dagilimi_grafigi(sikayetler)
        fig1.savefig(f"{klasor}/durum_dagilimi_{tarih}.png", dpi=150, bbox_inches='tight')
        plt.close(fig1)
        
        # Öncelik dağılımı
        fig2 = self.oncelik_dagilimi_grafigi(sikayetler)
        fig2.savefig(f"{klasor}/oncelik_dagilimi_{tarih}.png", dpi=150, bbox_inches='tight')
        plt.close(fig2)
        
        # Aylık trend
        fig3 = self.aylik_trend_grafigi(sikayetler)
        fig3.savefig(f"{klasor}/aylik_trend_{tarih}.png", dpi=150, bbox_inches='tight')
        plt.close(fig3)
        
        # En çok şikayet edilen konular
        fig4 = self.en_cok_sikayet_edilen_konular(sikayetler)
        fig4.savefig(f"{klasor}/en_cok_sikayet_{tarih}.png", dpi=150, bbox_inches='tight')
        plt.close(fig4)
        
        return f"{klasor}/"


# Test
if __name__ == "__main__":
    # Örnek veri
    test_sikayetler = [
        (1, "IPT/2024-00001", "Ahmet", "2024-01-15", "İst-Ank", "ABC", "", "Web", "Test", "2024-01-15 10:00", "Yeni", "", "", "", "Hijyen", "", "Yüksek"),
        (2, "IPT/2024-00002", "Ayşe", "2024-01-16", "Ank-İzm", "DEF", "", "Web", "Test", "2024-01-16 11:00", "İşlemde", "", "", "", "Rötar", "", "Orta"),
        (3, "IPT/2024-00003", "Mehmet", "2024-02-10", "İzm-Ank", "GHI", "", "Web", "Test", "2024-02-10 12:00", "Çözüldü", "", "", "", "Personel", "", "Acil"),
    ]
    
    dashboard = DashboardGrafikleri()
    klasor = dashboard.grafikleri_kaydet(test_sikayetler)
    print(f"Grafikler kaydedildi: {klasor}")
