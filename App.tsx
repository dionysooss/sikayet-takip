import React, { useState, useEffect, useCallback } from 'react';
import Login from './components/Login';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import ComplaintForm from './components/ComplaintForm';
import ComplaintList from './components/ComplaintList';
import ComplaintDetail from './components/ComplaintDetail';
import Home from './components/Home';
import UserManagement from './components/UserManagement';
import Profile from './components/Profile';
import { User, Complaint, LogEntry, UserRole } from './types';
import { firestoreService } from './services/firestoreService';
import { authService } from './services/authService';
import { migrateUserPasswords } from './utils/migration';

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [page, setPage] = useState('home');
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  // Complaints state, refreshed explicitly
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  // Firebase Auth state listener - auto-login
  useEffect(() => {
    const unsubscribe = authService.onAuthStateChanged(async (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in, get user data from Firestore
        const userData = await authService.getUserData(firebaseUser.uid);
        if (userData) {
          setUser(userData);
        }
      } else {
        // User is signed out
        setUser(null);
      }
      setIsAuthLoading(false);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  // Veri yükleme fonksiyonu - Firestore'dan async olarak
  const loadAllData = useCallback(async () => {
    if (!user) return;
    try {
      const data = await firestoreService.getComplaints();
      setComplaints([...data]);
      const logsData = await firestoreService.getLogs();
      setLogs([...logsData]);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  }, [user]);

  // Sayfa veya kullanıcı değiştiğinde veriyi yenile
  useEffect(() => {
    loadAllData();
  }, [loadAllData, page]);

  // Şifre migration - sadece bir kez çalışır
  useEffect(() => {
    const runMigration = async () => {
      try {
        await migrateUserPasswords();
      } catch (error) {
        console.error('Migration error:', error);
      }
    };
    runMigration();
  }, []);

  // Seçili şikayet güncellemelerini takip et
  useEffect(() => {
    if (selectedComplaint) {
      firestoreService.getComplaintById(selectedComplaint.id).then(updated => {
        if (updated) {
          // Sadece veri değişmişse güncelle (infinite loop önlemi)
          if (JSON.stringify(updated) !== JSON.stringify(selectedComplaint)) {
            setSelectedComplaint(updated);
          }
        } else {
          // Kayıt artık yoksa (silinmişse) detayı kapat
          setSelectedComplaint(null);
        }
      });
    }
  }, [complaints, selectedComplaint]);

  const handleLogin = (u: User) => {
    setUser(u);
    setPage('home');
  };

  const handleLogout = async () => {
    try {
      await authService.signOut();
      setUser(null);
      setPage('login');
      setSelectedComplaint(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleDeleteComplaint = async (id: string) => {
    if (!user) return;

    // 1. Firestore'dan sil
    const success = await firestoreService.deleteComplaint(id, user);

    if (success) {
      // 2. UI State'ini manuel güncelle (Anında Tepki)
      setComplaints(prev => prev.filter(c => c.id !== id));

      // 3. Eğer silinen kayıt detayda açıksa kapat
      if (selectedComplaint && selectedComplaint.id === id) {
        setSelectedComplaint(null);
      }

      // 4. Eğer liste sayfasında değilsek listeye dön (Opsiyonel, duruma göre)
      if (page !== 'list' && page !== 'home') {
        // Kullanıcı detaydan sildiyse listeye dönsün
        // Listeden sildiyse sayfada kalsın
        if (selectedComplaint) setPage('list');
      }

      // 5. Arka planda tam senkronizasyon için logları vs güncelle
      setTimeout(loadAllData, 100);
    } else {
      alert("Silme işlemi başarısız oldu veya yetkiniz yok.");
    }
  };

  // Show loading state while checking auth
  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-brand-dark">
        <div className="text-white text-xl">Yükleniyor...</div>
      </div>
    );
  }

  if (!user) return <Login onLogin={handleLogin} />;

  const renderContent = () => {
    if (selectedComplaint) {
      return (
        <ComplaintDetail
          complaint={selectedComplaint}
          user={user}
          onBack={() => { setSelectedComplaint(null); loadAllData(); }}
          onUpdate={loadAllData}
          onDelete={() => handleDeleteComplaint(selectedComplaint.id)}
        />
      );
    }

    switch (page) {
      case 'home': return <Home user={user} onNavigate={setPage} />;
      case 'dashboard': return <Dashboard complaints={complaints} />;
      case 'list': return <ComplaintList complaints={complaints} user={user} onSelect={setSelectedComplaint} onDelete={handleDeleteComplaint} onUpdate={loadAllData} />;
      case 'users': return <UserManagement currentUser={user} />;
      case 'profile': return <Profile user={user} onUpdate={(u) => { setUser(u); loadAllData(); }} />;
      case 'logs': return (
        <div className="bg-brand-card rounded-xl border border-brand-border p-6 overflow-hidden">
          <h2 className="text-xl font-bold mb-4">Sistem İşlem Kayıtları</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-black/40 text-gray-400 font-semibold">
                <tr>
                  <th className="p-3">Zaman</th>
                  <th className="p-3">Personel</th>
                  <th className="p-3">İşlem</th>
                  <th className="p-3">Detay</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {logs.map(log => (
                  <tr key={log.id} className="hover:bg-white/5">
                    <td className="p-3 text-gray-500">{new Date(log.timestamp).toLocaleString('tr-TR')}</td>
                    <td className="p-3 font-bold text-brand-blue">{log.userName}</td>
                    <td className="p-3 uppercase font-mono">{log.action}</td>
                    <td className="p-3 text-gray-300">{log.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
      default: return <div>Sayfa Bulunamadı</div>;
    }
  };

  return (
    <Layout user={user} onLogout={handleLogout} currentPage={page} onNavigate={(p) => { setPage(p); setSelectedComplaint(null); }}>
      {renderContent()}
    </Layout>
  );
};

export default App;