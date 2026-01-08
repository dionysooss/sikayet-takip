import React, { useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { firestoreService } from '../services/firestoreService';
import PhoneInput from './PhoneInput';
import { validatePassword, validateEmail } from '../utils/security';

interface UserManagementProps {
  currentUser: User;
}

const UserManagement: React.FC<UserManagementProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // Form State
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    fullName: '',
    role: UserRole.STAFF,
    phone: '',
    phoneRaw: '',
    phoneCountryCode: 'TR',
    email: '',
    branch: ''
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    const usersData = await firestoreService.getUsers();
    setUsers(usersData);
  };

  const handleOpenModal = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        username: user.username,
        password: '', // Don't show existing password
        fullName: user.fullName,
        role: user.role,
        phone: user.phone || '',
        phoneRaw: user.phoneRaw || '',
        phoneCountryCode: user.phoneCountryCode || 'TR',
        email: user.email || '',
        branch: user.branch || ''
      });
    } else {
      setEditingUser(null);
      setFormData({
        username: '',
        password: '',
        fullName: '',
        role: UserRole.STAFF,
        phone: '',
        phoneRaw: '',
        phoneCountryCode: 'TR',
        email: '',
        branch: ''
      });
    }
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    console.log('Delete button clicked for user ID:', id);
    if (confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) {
      console.log('User confirmed deletion');
      try {
        console.log('Calling firestoreService.deleteUser...');
        await firestoreService.deleteUser(id, currentUser);
        console.log('Delete successful, reloading users...');
        loadUsers();
      } catch (e: any) {
        console.error('Delete error:', e);
        alert(e.message);
      }
    } else {
      console.log('User cancelled deletion');
    }
  };

  const handlePhoneChange = (data: { formatted: string; raw: string; countryCode: string; isValid: boolean }) => {
    setFormData(prev => ({
      ...prev,
      phone: data.formatted,
      phoneRaw: data.raw,
      phoneCountryCode: data.countryCode
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Email validation
    if (formData.email && !validateEmail(formData.email)) {
      alert('Geçersiz email adresi.');
      return;
    }

    // Password validation for new users
    if (!editingUser) {
      if (!formData.password) {
        alert('Yeni kullanıcılar için şifre zorunludur.');
        return;
      }

      const passwordCheck = validatePassword(formData.password);
      if (!passwordCheck.isValid) {
        alert('Şifre güvenlik kuralları:\n' + passwordCheck.errors.join('\n'));
        return;
      }
    }

    // Password validation for existing users (if changing)
    if (editingUser && formData.password) {
      const passwordCheck = validatePassword(formData.password);
      if (!passwordCheck.isValid) {
        alert('Şifre güvenlik kuralları:\n' + passwordCheck.errors.join('\n'));
        return;
      }
    }

    // Phone validation
    if (!formData.phoneRaw || formData.phoneRaw.length < 5) {
      alert('Lütfen geçerli bir telefon numarası giriniz.');
      return;
    }

    try {
      if (editingUser) {
        // Update
        const updatedUser: User = {
          ...editingUser,
          ...formData,
          // If password is empty string, service handles keeping old one
          password: formData.password || undefined
        };
        await firestoreService.updateUser(updatedUser, currentUser);
      } else {
        // Create
        const newUser: User = {
          id: Date.now().toString(),
          ...formData,
          password: formData.password // Required for new
        };
        await firestoreService.addUser(newUser, currentUser);
      }
      setIsModalOpen(false);
      loadUsers();
    } catch (error: any) {
      alert(error.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Kullanıcı Yönetimi</h2>
        <button
          onClick={() => handleOpenModal()}
          className="bg-brand-blue text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors shadow-lg shadow-blue-900/20"
        >
          + Yeni Kullanıcı
        </button>
      </div>

      <div className="bg-brand-card rounded-xl shadow-xl border border-brand-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-black/40 text-gray-400 font-medium">
              <tr>
                <th className="p-4">Ad Soyad</th>
                <th className="p-4">Kullanıcı Adı</th>
                <th className="p-4">Rol</th>
                <th className="p-4">İletişim</th>
                <th className="p-4">Şube</th>
                <th className="p-4 text-right">İşlemler</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-white/5 transition-colors">
                  <td className="p-4 font-medium text-white">{u.fullName}</td>
                  <td className="p-4 text-gray-400">{u.username}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs border ${u.role === UserRole.ADMIN ? 'bg-red-900/30 text-red-200 border-red-800' :
                      u.role === UserRole.MANAGER ? 'bg-blue-900/30 text-blue-200 border-blue-800' :
                        'bg-gray-800 text-gray-300 border-gray-700'
                      }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="p-4 text-gray-300">
                    <div className="font-mono">{u.phone}</div>
                    <div className="text-xs text-gray-500">{u.email}</div>
                  </td>
                  <td className="p-4 text-gray-400">{u.branch || '-'}</td>
                  <td className="p-4 text-right space-x-2">
                    <button
                      onClick={() => handleOpenModal(u)}
                      className="text-blue-400 hover:text-white"
                    >
                      Düzenle
                    </button>
                    {u.id !== currentUser.id && (
                      <button
                        onClick={() => handleDelete(u.id)}
                        className="text-red-400 hover:text-white"
                      >
                        Sil
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-brand-card rounded-xl w-full max-w-2xl border border-brand-border shadow-2xl overflow-hidden">
            <div className="p-6 border-b border-brand-border flex justify-between items-center">
              <h3 className="font-bold text-lg text-white">
                {editingUser ? 'Kullanıcı Düzenle' : 'Yeni Kullanıcı Ekle'}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-white">&times;</button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Ad Soyad</label>
                  <input required type="text" value={formData.fullName} onChange={e => setFormData({ ...formData, fullName: e.target.value })} className="w-full bg-black/20 border border-gray-700 rounded p-2 text-white focus:border-brand-blue focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Kullanıcı Adı</label>
                  <input required type="text" value={formData.username} onChange={e => setFormData({ ...formData, username: e.target.value })} className="w-full bg-black/20 border border-gray-700 rounded p-2 text-white focus:border-brand-blue focus:outline-none" disabled={!!editingUser} />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Şifre {editingUser && '(Değişmeyecekse boş bırakın)'}</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={e => setFormData({ ...formData, password: e.target.value })}
                    className="w-full bg-black/20 border border-gray-700 rounded p-2 text-white focus:border-brand-blue focus:outline-none"
                    placeholder={editingUser ? '******' : 'Min 8 karakter, büyük/küçük harf, rakam'}
                  />
                  {!editingUser && (
                    <p className="text-xs text-gray-500 mt-1">En az 8 karakter, büyük harf, küçük harf ve rakam içermelidir</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Rol</label>
                  <select value={formData.role} onChange={e => setFormData({ ...formData, role: e.target.value as UserRole })} className="w-full bg-black/20 border border-gray-700 rounded p-2 text-white focus:border-brand-blue focus:outline-none">
                    {Object.values(UserRole).map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <PhoneInput
                    label="Telefon (Zorunlu)"
                    required
                    value={formData.phone}
                    initialCountryCode={formData.phoneCountryCode}
                    initialRawValue={formData.phoneRaw}
                    onChange={handlePhoneChange}
                    variant="dark"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">E-posta {!editingUser && <span className="text-red-400">*</span>}</label>
                  <input
                    type="email"
                    required={!editingUser}
                    value={formData.email}
                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                    className="w-full bg-black/20 border border-gray-700 rounded p-2 text-white focus:border-brand-blue focus:outline-none"
                    placeholder="ornek@ispartapetrol.com"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Şube</label>
                  <input type="text" value={formData.branch} onChange={e => setFormData({ ...formData, branch: e.target.value })} className="w-full bg-black/20 border border-gray-700 rounded p-2 text-white focus:border-brand-blue focus:outline-none" />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-400 hover:text-white">İptal</button>
                <button type="submit" className="bg-brand-blue text-white px-6 py-2 rounded hover:bg-blue-600 transition-colors">Kaydet</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;