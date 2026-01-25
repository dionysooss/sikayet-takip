import React from 'react';
import { User, UserRole } from '../types';

interface HomeProps {
  user: User;
  onNavigate: (page: string) => void;
}

const Home: React.FC<HomeProps> = ({ user, onNavigate }) => {
  const canViewDashboard = user.role === 'admin' || user.role === 'manager';

  return (
    <div className="min-h-[80vh] flex flex-col justify-start pt-12 max-w-5xl mx-auto space-y-12 relative">

      {/* Welcome Section - Header removed, motto kept */}
      <div className="text-center space-y-4 animate-fade-in py-4">
        <p className="text-2xl text-gray-300 font-medium max-w-2xl mx-auto italic">
          "Her yolcu bir emanet, her emanet bir sorumluluktur."
        </p>
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">

        {/* Create Complaint Card */}
        <button
          onClick={() => onNavigate('new')}
          className="group bg-brand-card hover:bg-white/5 border border-brand-border p-8 rounded-2xl text-left transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:border-brand-blue/30"
        >
          <div className="h-12 w-12 bg-blue-900/20 rounded-xl flex items-center justify-center text-2xl mb-6 group-hover:bg-brand-blue group-hover:text-white transition-colors border border-blue-900/30">
            📝
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Şikayet Oluştur</h3>
          <p className="text-sm text-gray-500 group-hover:text-gray-300 transition-colors">
            Yeni bir yolcu talebi veya şikayeti kaydetmek için buraya tıklayın.
          </p>
        </button>

        {/* Complaint List Card */}
        <button
          onClick={() => onNavigate('list')}
          className="group bg-brand-card hover:bg-white/5 border border-brand-border p-8 rounded-2xl text-left transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:border-brand-blue/30"
        >
          <div className="h-12 w-12 bg-purple-900/20 rounded-xl flex items-center justify-center text-2xl mb-6 group-hover:bg-purple-600 group-hover:text-white transition-colors border border-purple-900/30">
            📋
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Şikayet Listesi</h3>
          <p className="text-sm text-gray-500 group-hover:text-gray-300 transition-colors">
            Mevcut kayıtları inceleyin, durumlarını kontrol edin ve güncelleyin.
          </p>
        </button>

        {/* Dashboard Card (Conditional) */}
        {canViewDashboard ? (
          <button
            onClick={() => onNavigate('dashboard')}
            className="group bg-brand-card hover:bg-white/5 border border-brand-border p-8 rounded-2xl text-left transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:border-brand-blue/30"
          >
            <div className="h-12 w-12 bg-green-900/20 rounded-xl flex items-center justify-center text-2xl mb-6 group-hover:bg-green-600 group-hover:text-white transition-colors border border-green-900/30">
              📊
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Yönetim Paneli</h3>
            <p className="text-sm text-gray-500 group-hover:text-gray-300 transition-colors">
              Genel istatistikleri, raporları ve analizleri görüntüleyin.
            </p>
          </button>
        ) : (
          /* Placeholder for spacing if not manager */
          <div className="bg-brand-card/30 border border-brand-border/30 p-8 rounded-2xl flex flex-col justify-center items-center text-center opacity-50 cursor-not-allowed">
            <div className="text-4xl mb-4 grayscale">🔒</div>
            <p className="text-gray-500 text-sm">Yönetici Paneli<br />(Yetkiniz Yok)</p>
          </div>
        )}

      </div>

      {/* Fixed Slogan Signature */}
      <div className="fixed bottom-8 right-10 pointer-events-none opacity-80 z-50 hidden md:block">
        <span className="text-[#ccc] text-xl font-normal italic tracking-wide drop-shadow-md font-sans">
          Kilometrelerce hikâye taşıyoruz.
        </span>
      </div>

    </div>
  );
};

export default Home;