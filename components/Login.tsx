import React, { useState } from 'react';
import { firestoreService } from '../services/firestoreService';
import { User } from '../types';

interface LoginProps {
  onLogin: (user: User) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const user = await firestoreService.login(username, password);
    if (user) {
      onLogin(user);
    } else {
      setError('Kullanıcı adı veya şifre hatalı.');
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
              className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/20 focus:border-brand-blue focus:outline-none transition-all"
              placeholder="Kullanıcı adınızı girin"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Şifre</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/20 focus:border-brand-blue focus:outline-none transition-all"
              placeholder="Şifrenizi girin"
            />
          </div>

          {error && <p className="text-red-400 text-sm text-center bg-red-900/10 p-2 rounded border border-red-900/20">{error}</p>}

          <button
            type="submit"
            className="w-full bg-brand-blue text-white font-bold py-3 rounded-lg hover:bg-blue-600 transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.5)]"
          >
            Giriş Yap
          </button>
        </form>


      </div>
    </div>
  );
};

export default Login;