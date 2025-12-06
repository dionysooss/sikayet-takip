from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
import hashlib
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Supabase bağlantı bilgileri
DB_CONFIG = {
    "host": os.environ.get("SUPABASE_HOST", "db.whjoxpdlzraxuyabitfb.supabase.co"),
    "database": os.environ.get("SUPABASE_DATABASE", "postgres"),
    "user": os.environ.get("SUPABASE_USER", "postgres"),
    "password": os.environ.get("SUPABASE_PASSWORD", "dEmLmkl2ezShVMx8"),
    "port": os.environ.get("SUPABASE_PORT", "5432"),
    "sslmode": "require"
}

def get_db():
    """Veritabanı bağlantısı al"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Tabloları oluştur"""
    conn = get_db()
    cur = conn.cursor()
    
    # Şikayetler tablosu
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sikayetler (
            id SERIAL PRIMARY KEY,
            sikayet_no TEXT,
            yolcu_adi TEXT,
            seyahat_tarihi TEXT,
            guzergah TEXT,
            pnr TEXT,
            iletisim TEXT,
            platform TEXT,
            sikayet_detay TEXT,
            kayit_tarihi TEXT,
            durum TEXT DEFAULT 'Yeni',
            telefon TEXT,
            eposta TEXT,
            plaka TEXT,
            sikayet_turu TEXT,
            lokasyon TEXT,
            oncelik TEXT,
            satin_alinan_yer TEXT
        )
    """)
    
    # Kullanıcılar tablosu
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id SERIAL PRIMARY KEY,
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
    
    # Şikayet işlemleri tablosu
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sikayet_islemleri (
            id SERIAL PRIMARY KEY,
            sikayet_id INTEGER NOT NULL,
            tarih TEXT NOT NULL,
            kullanici_id INTEGER,
            kullanici_adi TEXT,
            islem_turu TEXT NOT NULL,
            aciklama TEXT,
            eski_durum TEXT,
            yeni_durum TEXT
        )
    """)
    
    # Admin kullanıcısı yoksa oluştur
    cur.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi = 'admin'")
    if cur.fetchone()[0] == 0:
        sifre_hash = hashlib.sha256("admin123".encode()).hexdigest()
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, email, rol, olusturma_tarihi)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ("admin", sifre_hash, "Sistem Yöneticisi", "admin@sistem.com", "admin", tarih))
    
    conn.commit()
    cur.close()
    conn.close()

# Giriş kontrolü decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen giriş yapın', 'warning')
            return redirect(url_for('giris'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('ana_sayfa'))
    return redirect(url_for('giris'))

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')
        sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, kullanici_adi, ad_soyad, rol, aktif 
            FROM kullanicilar WHERE kullanici_adi = %s AND sifre_hash = %s
        """, (kullanici_adi, sifre_hash))
        user = cur.fetchone()
        
        if user and user[4] == 1:
            session['user_id'] = user[0]
            session['kullanici_adi'] = user[1]
            session['ad_soyad'] = user[2]
            session['rol'] = user[3]
            
            # Son giriş güncelle
            cur.execute("UPDATE kullanicilar SET son_giris = %s WHERE id = %s", 
                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user[0]))
            conn.commit()
            cur.close()
            conn.close()
            
            flash(f'Hoş geldiniz, {user[2]}!', 'success')
            return redirect(url_for('ana_sayfa'))
        else:
            flash('Kullanıcı adı veya şifre hatalı', 'danger')
        
        cur.close()
        conn.close()
    
    return render_template('giris.html')

@app.route('/cikis')
def cikis():
    session.clear()
    flash('Çıkış yapıldı', 'info')
    return redirect(url_for('giris'))

@app.route('/ana-sayfa')
@login_required
def ana_sayfa():
    conn = get_db()
    cur = conn.cursor()
    
    # İstatistikler
    cur.execute("SELECT COUNT(*) FROM sikayetler")
    toplam = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM sikayetler WHERE durum = 'Yeni'")
    yeni = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM sikayetler WHERE durum = 'İşlemde'")
    islemde = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM sikayetler WHERE durum = 'Çözüldü'")
    cozuldu = cur.fetchone()[0]
    
    # Son şikayetler
    cur.execute("""
        SELECT id, sikayet_no, yolcu_adi, kayit_tarihi, durum, sikayet_turu, oncelik
        FROM sikayetler ORDER BY id DESC LIMIT 10
    """)
    son_sikayetler = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('ana_sayfa.html', 
                         toplam=toplam, yeni=yeni, islemde=islemde, cozuldu=cozuldu,
                         son_sikayetler=son_sikayetler)

@app.route('/sikayetler')
@login_required
def sikayetler():
    durum_filtre = request.args.get('durum', '')
    arama = request.args.get('arama', '')
    
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT id, sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, 
               platform, kayit_tarihi, durum, sikayet_turu, oncelik, telefon
        FROM sikayetler WHERE 1=1
    """
    params = []
    
    if durum_filtre:
        query += " AND durum = %s"
        params.append(durum_filtre)
    
    if arama:
        query += " AND (yolcu_adi ILIKE %s OR sikayet_no ILIKE %s OR pnr ILIKE %s)"
        params.extend([f'%{arama}%', f'%{arama}%', f'%{arama}%'])
    
    query += " ORDER BY id DESC"
    
    cur.execute(query, params)
    sikayetler = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('sikayetler.html', sikayetler=sikayetler, 
                         durum_filtre=durum_filtre, arama=arama)

@app.route('/sikayet/<int:id>')
@login_required
def sikayet_detay(id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr, iletisim,
               platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta, plaka,
               sikayet_turu, lokasyon, oncelik, satin_alinan_yer
        FROM sikayetler WHERE id = %s
    """, (id,))
    sikayet = cur.fetchone()
    
    if not sikayet:
        flash('Şikayet bulunamadı', 'danger')
        return redirect(url_for('sikayetler'))
    
    # İşlem geçmişi
    cur.execute("""
        SELECT tarih, kullanici_adi, islem_turu, aciklama, eski_durum, yeni_durum
        FROM sikayet_islemleri WHERE sikayet_id = %s ORDER BY id DESC
    """, (id,))
    islemler = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('sikayet_detay.html', sikayet=sikayet, islemler=islemler)

@app.route('/sikayet/yeni', methods=['GET', 'POST'])
@login_required
def yeni_sikayet():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        
        # Şikayet no oluştur
        yil = datetime.now().year
        cur.execute("SELECT sikayet_no FROM sikayetler WHERE sikayet_no LIKE %s ORDER BY id DESC LIMIT 1", 
                   (f"IPT/{yil}-%",))
        son = cur.fetchone()
        if son:
            son_no = int(son[0].split('-')[1])
            sikayet_no = f"IPT/{yil}-{son_no + 1:05d}"
        else:
            sikayet_no = f"IPT/{yil}-00001"
        
        kayit_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cur.execute("""
            INSERT INTO sikayetler (sikayet_no, yolcu_adi, seyahat_tarihi, guzergah, pnr,
                iletisim, platform, sikayet_detay, kayit_tarihi, durum, telefon, eposta,
                plaka, sikayet_turu, lokasyon, oncelik, satin_alinan_yer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            sikayet_no,
            request.form.get('yolcu_adi'),
            request.form.get('seyahat_tarihi'),
            request.form.get('guzergah'),
            request.form.get('pnr'),
            request.form.get('iletisim'),
            request.form.get('platform'),
            request.form.get('sikayet_detay'),
            kayit_tarihi,
            'Yeni',
            request.form.get('telefon'),
            request.form.get('eposta'),
            request.form.get('plaka'),
            request.form.get('sikayet_turu'),
            request.form.get('lokasyon'),
            request.form.get('oncelik', 'Normal'),
            request.form.get('satin_alinan_yer')
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash(f'Şikayet kaydedildi: {sikayet_no}', 'success')
        return redirect(url_for('sikayetler'))
    
    return render_template('yeni_sikayet.html')

@app.route('/sikayet/<int:id>/durum', methods=['POST'])
@login_required
def durum_guncelle(id):
    yeni_durum = request.form.get('durum')
    aciklama = request.form.get('aciklama', '')
    
    conn = get_db()
    cur = conn.cursor()
    
    # Eski durumu al
    cur.execute("SELECT durum FROM sikayetler WHERE id = %s", (id,))
    eski_durum = cur.fetchone()[0]
    
    # Durumu güncelle
    cur.execute("UPDATE sikayetler SET durum = %s WHERE id = %s", (yeni_durum, id))
    
    # İşlem kaydı
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO sikayet_islemleri (sikayet_id, tarih, kullanici_id, kullanici_adi, 
            islem_turu, aciklama, eski_durum, yeni_durum)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (id, tarih, session['user_id'], session['kullanici_adi'], 
          'Durum Değişikliği', aciklama, eski_durum, yeni_durum))
    
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Durum güncellendi', 'success')
    return redirect(url_for('sikayet_detay', id=id))

@app.route('/sikayet/<int:id>/sil', methods=['POST'])
@login_required
def sikayet_sil(id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM sikayet_islemleri WHERE sikayet_id = %s", (id,))
    cur.execute("DELETE FROM sikayetler WHERE id = %s", (id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Şikayet silindi', 'success')
    return redirect(url_for('sikayetler'))

@app.route('/istatistikler')
@login_required
def istatistikler():
    conn = get_db()
    cur = conn.cursor()
    
    # Durum dağılımı
    cur.execute("""
        SELECT durum, COUNT(*) FROM sikayetler GROUP BY durum
    """)
    durum_dagilimi = dict(cur.fetchall())
    
    # Platform dağılımı
    cur.execute("""
        SELECT platform, COUNT(*) FROM sikayetler WHERE platform IS NOT NULL AND platform != ''
        GROUP BY platform ORDER BY COUNT(*) DESC LIMIT 10
    """)
    platform_dagilimi = cur.fetchall()
    
    # Şikayet türü dağılımı
    cur.execute("""
        SELECT sikayet_turu, COUNT(*) FROM sikayetler WHERE sikayet_turu IS NOT NULL AND sikayet_turu != ''
        GROUP BY sikayet_turu ORDER BY COUNT(*) DESC LIMIT 10
    """)
    tur_dagilimi = cur.fetchall()
    
    # Aylık trend
    cur.execute("""
        SELECT TO_CHAR(TO_DATE(kayit_tarihi, 'YYYY-MM-DD'), 'YYYY-MM') as ay, COUNT(*)
        FROM sikayetler 
        WHERE kayit_tarihi IS NOT NULL
        GROUP BY ay ORDER BY ay DESC LIMIT 12
    """)
    aylik_trend = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('istatistikler.html', 
                         durum_dagilimi=durum_dagilimi,
                         platform_dagilimi=platform_dagilimi,
                         tur_dagilimi=tur_dagilimi,
                         aylik_trend=aylik_trend)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
