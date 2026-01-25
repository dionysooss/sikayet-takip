import React, { useState, useEffect } from 'react';
import { getFirestore, collection, query, where, getDocs, doc, updateDoc } from 'firebase/firestore';
import { User } from '../types';
import { checkRateLimit, resetRateLimit } from '../utils/security';
import { verifyPassword, saveSession } from '../utils/auth';
import { firestoreService } from '../services/firestoreService';

interface LoginProps {
  onLogin: (user: User) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [blockedUntil, setBlockedUntil] = useState<Date | null>(null);

  // Bloke süresini kontrol et
  useEffect(() => {
    if (blockedUntil) {
      const timer = setInterval(() => {
        if (new Date() > blockedUntil) {
          setBlockedUntil(null);
          setError('');
        }
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [blockedUntil]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Boş alan kontrolü
    if (!username.trim() || !password.trim()) {
      setError('Kullanıcı adı ve şifre gereklidir');
      return;
    }

    // Rate limiting kontrolü
    const rateLimitCheck = checkRateLimit(username.toLowerCase(), 5, 15 * 60 * 1000, 5 * 60 * 1000);

    if (!rateLimitCheck.allowed) {
      const remainingTime = Math.ceil((rateLimitCheck.blockedUntil!.getTime() - Date.now()) / 1000 / 60);
      setError(`Çok fazla başarısız deneme. ${remainingTime} dakika sonra tekrar deneyin.`);
      setBlockedUntil(rateLimitCheck.blockedUntil!);
      return;
    }

    setIsLoading(true);

    try {
      const db = getFirestore();

      // 1. Kullanıcıyı kullanıcı adı ile bul
      const usersRef = collection(db, 'users');
      const q = query(usersRef, where('username', '==', username.toLowerCase()));
      const querySnapshot = await getDocs(q);

      if (querySnapshot.empty) {
        // Kullanıcı bulunamadı
        const remainingAttempts = rateLimitCheck.remainingAttempts || 0;
        if (remainingAttempts > 0) {
          setError(`Kullanıcı adı veya şifre hatalı. Kalan deneme hakkı: ${remainingAttempts}`);
        } else {
          setError('Kullanıcı adı veya şifre hatalı.');
        }
        setIsLoading(false);
        return;
      }

      const userDoc = querySnapshot.docs[0];
      const userData = userDoc.data();

      // 2. Firebase Auth ile giriş yap (gizli email kullanarak)
      const { getAuth, signInWithEmailAndPassword } = await import('firebase/auth');
      const auth = getAuth();

      // Email otomatik oluştur (kullanıcı görmez)
      const email = userData.email || `${userData.username}@ispartapetrol.internal`;

      try {
        await signInWithEmailAndPassword(auth, email, password);
      } catch (authError: any) {
        // Firebase Auth hatası
        const remainingAttempts = rateLimitCheck.remainingAttempts || 0;
        if (remainingAttempts > 0) {
          setError(`Kullanıcı adı veya şifre hatalı. Kalan deneme hakkı: ${remainingAttempts}`);
        } else {
          setError('Kullanıcı adı veya şifre hatalı.');
        }
        setIsLoading(false);
        return;
      }

      // 3. Başarılı giriş - User objesi oluştur
      const user: User = {
        id: userDoc.id,
        username: userData.username,
        fullName: userData.fullName,
        role: userData.role,
        branch: userData.branch || '',
        phone: userData.phone || '',
        photoURL: userData.photoURL || '',
      };

      // 4. Session'ı kaydet (localStorage)
      saveSession(user, auth.currentUser!.uid);

      // 5. Son giriş zamanını güncelle
      await updateDoc(doc(db, 'users', userDoc.id), {
        lastLogin: new Date()
      });

      // 6. Rate limit'i sıfırla
      resetRateLimit(username.toLowerCase());

      // 7. Login logunu kaydet
      await firestoreService.logAction(user, 'LOGIN', `Sisteme giriş yapıldı (IP: ${window.location.hostname})`);

      // 8. Kullanıcıyı giriş yaptır
      onLogin(user);

    } catch (err: any) {
      console.error('Login error:', err);
      setError('Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-dark relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-brand-dark to-brand-dark pointer-events-none"></div>

      <div className="bg-brand-card p-8 rounded-2xl shadow-2xl w-full max-w-md border border-brand-border relative z-10">
        <div className="text-center mb-8">
          <div className="flex justify-center">
            <img src="/logo.png" alt="Isparta Petrol Logo" className="h-40 object-contain" />
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Kullanıcı Adı</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading || !!blockedUntil}
              className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/20 focus:border-brand-blue focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="Kullanıcı adınızı girin"
              autoComplete="username"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Şifre</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading || !!blockedUntil}
              className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/20 focus:border-brand-blue focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="Şifrenizi girin"
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center bg-red-900/10 p-3 rounded border border-red-900/20">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !!blockedUntil}
            className="w-full bg-brand-blue text-white font-bold py-3 rounded-lg hover:bg-blue-600 transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.5)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Giriş yapılıyor...' : blockedUntil ? 'Geçici olarak engellendi' : 'Giriş Yap'}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-gray-500">
          <p>🔒 Güvenli bağlantı</p>
        </div>
      </div>
    </div>
  );
};

export default Login;