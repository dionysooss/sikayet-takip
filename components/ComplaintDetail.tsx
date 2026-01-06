
import React, { useState } from 'react';
import { Complaint, ComplaintStatus, User } from '../types';
import { firestoreService } from '../services/firestoreService';
import ImageEditor from './ImageEditor';
import AIChat from './AIChat';
import ComplaintForm from './ComplaintForm';
import DeleteButton from './DeleteButton';
import { exportComplaintToPDF } from '../services/pdfExport';

interface ComplaintDetailProps {
  complaint: Complaint;
  user: User;
  onBack: () => void;
  onUpdate: () => void; // Trigger refresh
  onDelete: () => void; // Handler passed from App.tsx
}

const ComplaintDetail: React.FC<ComplaintDetailProps> = ({ complaint, user, onBack, onUpdate, onDelete }) => {
  const [newNote, setNewNote] = useState('');
  const [editImage, setEditImage] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Managers/Admins can edit status/notes and delete.
  const canManage = true; // DeleteButton will handle specific role check
  const canEditDetails = true;

  const handleStatusChange = async (status: string) => {
    await firestoreService.updateStatus(complaint.id, status as ComplaintStatus, user);
    onUpdate();
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    await firestoreService.addNote(complaint.id, newNote, user);
    setNewNote('');
    onUpdate();
  };

  if (isEditing) {
    return (
      <ComplaintForm
        user={user}
        initialData={complaint}
        onSuccess={() => {
          setIsEditing(false);
          onUpdate();
        }}
        onCancel={() => setIsEditing(false)}
      />
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between bg-brand-card/30 p-4 rounded-xl border border-brand-border/50">
        <button onClick={onBack} className="text-gray-400 hover:text-white flex items-center gap-1 transition-colors font-medium">
          ← Listeye Dön
        </button>

        <div className="flex items-center gap-3">
          {/* MODÜLER SİLME BUTONU */}
          <DeleteButton
            user={user}
            onDelete={onDelete}
            confirmMessage={`${complaint.ticketNumber} numaralı şikayeti silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz!`}
            label="Şikayeti Sil"
          />

          {canEditDetails && (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 bg-white/10 text-white border border-white/20 px-4 py-2 rounded-lg hover:bg-white/20 transition-all text-sm font-medium shadow-sm"
            >
              ✏️ Düzenle
            </button>
          )}

          <button
            onClick={() => exportComplaintToPDF(complaint)}
            className="flex items-center gap-2 bg-green-900/10 text-green-400 border border-green-900/30 px-4 py-2 rounded-lg hover:bg-green-900/30 transition-all text-sm font-medium shadow-sm"
          >
            📄 PDF İndir
          </button>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: Info */}
        <div className="flex-1 space-y-6">
          <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border">
            <div className="flex justify-between items-start mb-6 border-b border-brand-border pb-4">
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight">{complaint.ticketNumber}</h2>
                <div className="flex gap-2 mt-2">
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold
                    ${complaint.status === ComplaintStatus.OPEN ? 'bg-yellow-900/50 text-yellow-200 border border-yellow-800' : ''}
                    ${complaint.status === ComplaintStatus.RESOLVED ? 'bg-green-900/50 text-green-200 border border-green-800' : ''}
                    ${complaint.status === ComplaintStatus.REJECTED ? 'bg-red-900/50 text-red-200 border border-red-800' : ''}
                    ${complaint.status === ComplaintStatus.INVESTIGATING ? 'bg-blue-900/50 text-blue-200 border border-blue-800' : ''}
                  `}>
                    {complaint.status}
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-800 text-gray-300 border border-gray-700">
                    {complaint.category}
                  </span>
                </div>
              </div>
              <div className="text-right text-sm text-gray-400 font-mono">
                <p>Oluşturulma: {new Date(complaint.createdAt).toLocaleDateString()}</p>
                <p>Saat: {new Date(complaint.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6 mb-6">
              {/* Passenger Column */}
              <div>
                <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-4 opacity-80">Yolcu Bilgileri</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Ad Soyad:</span>
                    <span className="font-medium text-white">{complaint.passengerName}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Telefon:</span>
                    <span className="font-medium text-white">{complaint.passengerPhone}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">E-posta:</span>
                    <span className="font-medium text-white">{complaint.passengerEmail || '-'}</span>
                  </div>
                </div>
              </div>

              {/* Trip Column */}
              <div>
                <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-4 opacity-80">Sefer Bilgileri</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Güzergah:</span>
                    <span className="font-medium text-white">{complaint.tripRoute}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Tarih / Saat:</span>
                    <span className="font-medium text-white">{complaint.tripDate} {complaint.departureTime ? `/ ${complaint.departureTime}` : ''}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">PNR:</span>
                    <span className="font-medium text-white font-mono">{complaint.pnr || '-'}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Plaka:</span>
                    <span className="font-medium text-white font-mono">{complaint.licensePlate || '-'}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Bilet Ücreti:</span>
                    <span className="font-medium text-white">{complaint.ticketPrice || '-'}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Satın Alınan:</span>
                    <span className="font-medium text-white">{complaint.purchaseChannel || '-'}</span>
                  </div>
                  <div className="flex justify-between border-b border-gray-800 pb-1">
                    <span className="text-gray-500">Başvuru Platformu:</span>
                    <span className="font-medium text-white">{complaint.applicationChannel || '-'}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8">
              <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-3 opacity-80">Şikayet Açıklaması</h3>
              <div className="bg-black/40 border border-brand-border p-5 rounded-xl">
                <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">{complaint.description}</p>
              </div>
            </div>
          </div>

          {/* Attachments */}
          {complaint.attachments.length > 0 && (
            <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border">
              <h3 className="font-bold mb-4 text-white">Ekli Dosyalar</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {complaint.attachments.map(att => (
                  <div key={att.id} className="group relative rounded-lg overflow-hidden border border-gray-700 aspect-video cursor-pointer">
                    <img src={att.data} alt={att.name} className="w-full h-full object-cover transition-transform group-hover:scale-105" />
                    <button
                      onClick={() => setEditImage(att.data)}
                      className="absolute inset-0 bg-black/0 group-hover:bg-black/60 flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 text-white font-semibold text-sm"
                    >
                      ✨ AI ile Düzenle
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Actions */}
        <div className="w-full lg:w-96 space-y-6">
          <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border">
            <h3 className="font-bold mb-4 text-white">Yönetici İşlemleri</h3>
            <div className="mb-4">
              <label className="block text-xs text-gray-400 mb-1 font-semibold uppercase tracking-wider">Durum Güncelle</label>
              <select
                value={complaint.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 text-sm focus:outline-none focus:ring-4 focus:ring-blue-500/30 font-medium"
              >
                {Object.values(ComplaintStatus).map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div className="mt-6">
              <label className="block text-xs text-gray-400 mb-1 font-semibold uppercase tracking-wider">Not / Talimat Ekle</label>
              <textarea
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 text-sm h-32 mb-3 focus:outline-none focus:ring-4 focus:ring-blue-500/30 resize-none"
                placeholder="İlgili personele veya sürece dair not bırakın..."
              />
              <button
                onClick={handleAddNote}
                className="w-full bg-brand-blue text-white py-3 rounded-lg text-sm hover:bg-blue-600 transition-all shadow-lg shadow-blue-900/20 font-bold"
              >
                Notu Kaydet
              </button>
            </div>
          </div>

          <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border">
            <h3 className="font-bold mb-4 text-xs text-white uppercase tracking-widest opacity-80">İşlem Geçmişi & Notlar</h3>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
              {complaint.managerNotes.map((note, i) => (
                <div key={i} className="text-xs bg-yellow-900/10 p-3 rounded-lg border border-yellow-800/30 text-yellow-100/80 leading-relaxed italic">
                  {note}
                </div>
              ))}
              {complaint.managerNotes.length === 0 && <p className="text-gray-500 text-sm italic">Henüz bir not eklenmemiş.</p>}
            </div>
          </div>

          <AIChat />
        </div>
      </div>

      {editImage && (
        <ImageEditor
          originalImage={editImage}
          onClose={() => setEditImage(null)}
        />
      )}
    </div>
  );
};

export default ComplaintDetail;
