import React, { useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { User } from '../types';
import { checkRateLimit, resetRateLimit } from '../utils/security';

interface LoginProps {
  onLogin: (user: User) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
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
    if (!email.trim() || !password.trim()) {
      setError('Email ve şifre gereklidir');
      return;
    }

    // Rate limiting kontrolü
    const rateLimitCheck = checkRateLimit(email.toLowerCase(), 5, 15 * 60 * 1000, 5 * 60 * 1000);

    if (!rateLimitCheck.allowed) {
      const remainingTime = Math.ceil((rateLimitCheck.blockedUntil!.getTime() - Date.now()) / 1000 / 60);
      setError(`Çok fazla başarısız deneme. ${remainingTime} dakika sonra tekrar deneyin.`);
      setBlockedUntil(rateLimitCheck.blockedUntil!);
      return;
    }

    setIsLoading(true);

    try {
      const user = await authService.signIn(email, password);

      if (user) {
        // Başarılı giriş - rate limit'i sıfırla
        resetRateLimit(email.toLowerCase());
        onLogin(user);
      } else {
        // Başarısız giriş
        const remainingAttempts = rateLimitCheck.remainingAttempts || 0;

        if (remainingAttempts > 0) {
          setError(`Email veya şifre hatalı. Kalan deneme hakkı: ${remainingAttempts}`);
        } else {
          setError('Email veya şifre hatalı.');
        }
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.');
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
            <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading || !!blockedUntil}
              className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/20 focus:border-brand-blue focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="Email adresinizi girin"
              autoComplete="email"
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
          <p>🔒 Firebase Authentication ile güvenli bağlantı</p>
        </div>
      </div>
    </div>
  );
};

export default Login;