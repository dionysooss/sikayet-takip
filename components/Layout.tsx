import React from 'react';
import { User, UserRole } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  user: User;
  onLogout: () => void;
  currentPage: string;
  onNavigate: (page: string) => void;
}

// Menü öğesi için tip tanımı
interface MenuItem {
  id: string;
  label: string;
  roles: UserRole[];
}

const Layout: React.FC<LayoutProps> = ({ children, user, onLogout, currentPage, onNavigate }) => {
  // Menü konfigürasyonu
  const menuItems: MenuItem[] = [
    {
      id: 'home',
      label: '🏠 Ana Sayfa',
      roles: [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]
    },
    {
      id: 'dashboard',
      label: '📊 Panel',
      roles: [UserRole.MANAGER, UserRole.ADMIN]
    },
    {
      id: 'list',
      label: '📋 Geri Bildirim Merkezi',
      roles: [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]
    },
    {
      id: 'users',
      label: '👥 Kullanıcılar',
      roles: [UserRole.ADMIN]
    },
    {
      id: 'logs',
      label: '📜 İşlem Kayıtları',
      roles: [UserRole.ADMIN]
    },
  ];

  // user.role is a string, convert to lowercase for comparison
  const userRoleString = user.role.toLowerCase();
  const visibleMenuItems = menuItems.filter(item => {
    // Check if user role matches any of the allowed roles
    return item.roles.some(role => role.toLowerCase() === userRoleString);
  });

  return (
    <div className="flex h-screen bg-brand-dark overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-brand-card border-r border-brand-border text-white flex flex-col shadow-2xl z-10">
        <div className="p-6 border-b border-brand-border flex justify-center">
          <img src="/logo.png" alt="Logo" className="h-12 object-contain" />
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {visibleMenuItems.map(item => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 border ${currentPage === item.id
                ? 'bg-brand-blue border-brand-blue text-white font-medium shadow-[0_0_15px_rgba(59,130,246,0.5)]'
                : 'bg-transparent border-transparent text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-brand-border space-y-3">
          {/* Profile Shortcut */}
          <button
            onClick={() => onNavigate('profile')}
            className={`flex items-center gap-3 w-full p-2 rounded-lg transition-colors ${currentPage === 'profile' ? 'bg-white/10' : 'hover:bg-white/5'}`}
          >
            <div className="w-8 h-8 rounded-full bg-brand-dark border border-brand-border flex items-center justify-center text-sm font-bold text-brand-blue">
              {user.fullName.charAt(0)}
            </div>
            <div className="text-left flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-200 truncate">{user.fullName}</p>
              <p className="text-xs text-gray-500 truncate">{user.role}</p>
            </div>
            <div className="text-gray-500">⚙️</div>
          </button>

          <button
            onClick={onLogout}
            className="w-full py-2 border border-brand-border rounded text-sm text-gray-400 hover:bg-white/10 hover:text-white transition-colors"
          >
            Çıkış Yap
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-brand-dark relative">
        <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-blue-900/5 to-transparent pointer-events-none" />
        <div className="p-8 max-w-7xl mx-auto relative z-0">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;