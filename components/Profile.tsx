import React, { useState } from 'react';
import { User } from '../types';
import { firestoreService } from '../services/firestoreService';
import PhoneInput from './PhoneInput';

interface ProfileProps {
  user: User;
  onUpdate: (updatedUser: User) => void;
}

const Profile: React.FC<ProfileProps> = ({ user, onUpdate }) => {
  const [formData, setFormData] = useState({
    fullName: user.fullName,
    password: '',
    phone: user.phone || '',
    phoneRaw: user.phoneRaw || '',
    phoneCountryCode: user.phoneCountryCode || 'TR',
    email: user.email || '',
    branch: user.branch || ''
  });
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    if (formData.password && formData.password.length < 6) {
      setMessage({ type: 'error', text: 'Yeni şifre en az 6 karakter olmalıdır.' });
      return;
    }

    if (!formData.phoneRaw || formData.phoneRaw.length < 5) {
      setMessage({ type: 'error', text: 'Lütfen geçerli bir telefon numarası giriniz.' });
      return;
    }

    try {
      const updatedUser: User = {
        ...user,
        fullName: formData.fullName,
        phone: formData.phone,
        phoneRaw: formData.phoneRaw,
        phoneCountryCode: formData.phoneCountryCode,
        email: formData.email,
        branch: formData.branch,
        // Only update password if user typed a new one
        password: formData.password || undefined
      };

      await firestoreService.updateUser(updatedUser, user);
      onUpdate(updatedUser); // Update App state

      setMessage({ type: 'success', text: 'Profiliniz başarıyla güncellendi.' });
      setFormData(prev => ({ ...prev, password: '' })); // Clear password field
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Güncelleme sırasında hata oluştu.' });
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

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-brand-card p-8 rounded-2xl shadow-xl border border-brand-border">
        <div className="flex items-center gap-4 mb-8 border-b border-brand-border pb-6">
          <div className="h-16 w-16 rounded-full bg-brand-blue flex items-center justify-center text-3xl font-bold text-white shadow-lg shadow-blue-900/40">
            {user.fullName.charAt(0)}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Profilim</h2>
            <p className="text-gray-400 text-sm">Hesap bilgilerinizi buradan güncelleyebilirsiniz.</p>
          </div>
        </div>

        {message && (
          <div className={`p-4 rounded-lg mb-6 ${message.type === 'success' ? 'bg-green-900/20 text-green-300 border border-green-800' : 'bg-red-900/20 text-red-300 border border-red-800'}`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Ad Soyad</label>
              <input required type="text" value={formData.fullName} onChange={e => setFormData({ ...formData, fullName: e.target.value })}
                className="w-full bg-black/20 border border-gray-700 rounded-lg p-3 text-white focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue transition-colors" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Kullanıcı Adı</label>
              <input type="text" value={user.username} disabled
                className="w-full bg-black/40 border border-brand-border rounded-lg p-3 text-gray-500 cursor-not-allowed" />
              <p className="text-xs text-gray-600 mt-1">Kullanıcı adı değiştirilemez.</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Rol</label>
              <div className="w-full bg-black/40 border border-brand-border rounded-lg p-3 text-gray-500 cursor-not-allowed">
                {user.role}
              </div>
              <p className="text-xs text-gray-600 mt-1">Rol değişikliği için yönetici ile görüşün.</p>
            </div>

            <div>
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
              <label className="block text-sm font-medium text-gray-300 mb-1">E-posta</label>
              <input type="email" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })}
                className="w-full bg-black/20 border border-gray-700 rounded-lg p-3 text-white focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue transition-colors" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Şube</label>
              <input type="text" value={formData.branch} onChange={e => setFormData({ ...formData, branch: e.target.value })}
                className="w-full bg-black/20 border border-gray-700 rounded-lg p-3 text-white focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue transition-colors" />
            </div>

            <div className="pt-4 border-t border-brand-border">
              <label className="block text-sm font-medium text-yellow-500 mb-1">Şifre Değiştir</label>
              <input type="password" value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })}
                className="w-full bg-black/20 border border-gray-700 rounded-lg p-3 text-white focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue transition-colors"
                placeholder="Sadece değiştirmek istiyorsanız doldurun (min. 6 karakter)" />
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button type="submit" className="bg-brand-blue text-white px-8 py-3 rounded-xl hover:bg-blue-600 transition-all shadow-lg shadow-blue-900/20 font-semibold">
              Değişiklikleri Kaydet
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Profile;