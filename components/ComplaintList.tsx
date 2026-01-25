import React, { useState, useMemo } from 'react';
import { Complaint, ComplaintStatus, User } from '../types';
import DeleteButton from './DeleteButton';
import ComplaintForm from './ComplaintForm';

interface ComplaintListProps {
  complaints: Complaint[];
  user: User;
  onSelect: (c: Complaint) => void;
  onDelete: (id: string) => void;
  onUpdate: () => void;
}

// Alt bileşeni dışarı alarak render performansını artırıyoruz
const StatusBadge = ({ status }: { status: ComplaintStatus | string }) => {
  const safeStatus = status || 'Bilinmiyor';

  const styles: Record<string, string> = {
    [ComplaintStatus.OPEN]: "bg-amber-500/20 text-amber-200 border-amber-500/30 ring-amber-500/20",
    [ComplaintStatus.INVESTIGATING]: "bg-blue-500/20 text-blue-200 border-blue-500/30 ring-blue-500/20",
    [ComplaintStatus.RESOLVED]: "bg-emerald-500/20 text-emerald-200 border-emerald-500/30 ring-emerald-500/20",
    [ComplaintStatus.REJECTED]: "bg-rose-500/20 text-rose-200 border-rose-500/30 ring-rose-500/20",
  };

  const icons: Record<string, string> = {
    [ComplaintStatus.OPEN]: "⏳",
    [ComplaintStatus.INVESTIGATING]: "🔍",
    [ComplaintStatus.RESOLVED]: "✅",
    [ComplaintStatus.REJECTED]: "❌",
  };

  const styleClass = styles[safeStatus] || "bg-gray-800 text-gray-300 border-gray-700";
  const iconChar = icons[safeStatus] || "•";

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ring-1 ${styleClass}`}>
      <span>{iconChar}</span>
      {safeStatus}
    </span>
  );
};

const ComplaintList: React.FC<ComplaintListProps> = ({ complaints, user, onSelect, onDelete, onUpdate }) => {
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);

  const filteredComplaints = useMemo(() => {
    return complaints.filter(c => {
      const matchesStatus = filterStatus === 'ALL' || c.status === filterStatus;
      const searchLower = searchQuery.toLowerCase();

      const ticket = c.ticketNumber || '';
      const pName = c.passengerName || '';
      const pPhone = c.passengerPhone || '';

      return matchesStatus && (
        ticket.toLowerCase().includes(searchLower) ||
        pName.toLowerCase().includes(searchLower) ||
        pPhone.includes(searchQuery)
      );
    });
  }, [complaints, filterStatus, searchQuery]);

  // If form is active, show only the form
  if (showForm) {
    return (
      <ComplaintForm
        user={user}
        onSuccess={() => {
          setShowForm(false);
          onUpdate();
        }}
        onCancel={() => setShowForm(false)}
      />
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header & Filters */}
      <div className="flex flex-col md:flex-row justify-between items-end md:items-center gap-4 bg-gradient-to-r from-brand-card to-transparent p-1 rounded-xl">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight">Geri Bildirim Merkezi</h2>
          <p className="text-gray-400 text-sm mt-1">Toplam {filteredComplaints.length} kayıt görüntüleniyor</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center justify-center gap-2 bg-brand-blue text-white px-5 py-2.5 rounded-xl hover:bg-blue-600 transition-all shadow-lg shadow-blue-900/20 font-semibold text-sm"
          >
            <span className="text-lg">+</span> Yeni Kayıt Oluştur
          </button>

          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-500 group-focus-within:text-brand-blue transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Hızlı Arama..."
              className="bg-black/40 border border-brand-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-white w-full sm:w-64 focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="relative">
            <select
              className="bg-black/40 border border-brand-border rounded-xl pl-4 pr-10 py-2.5 text-sm text-white focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue transition-all appearance-none cursor-pointer w-full sm:w-auto"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="ALL">Tüm Durumlar</option>
              {Object.values(ComplaintStatus).map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
            </div>
          </div>
        </div>
      </div>

      {/* Modern Table Layout */}
      <div className="bg-brand-card rounded-2xl border border-brand-border overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-black/40 border-b border-brand-border text-xs text-gray-400 uppercase tracking-wider">
                <th className="p-5 font-semibold">Bilet Bilgisi</th>
                <th className="p-5 font-semibold">Yolcu Detayı</th>
                <th className="p-5 font-semibold">Konu</th>
                <th className="p-5 font-semibold">Durum</th>
                <th className="p-5 font-semibold text-right">Eylemler</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border/30">
              {filteredComplaints.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-gray-500">
                    Kayıt bulunamadı.
                  </td>
                </tr>
              ) : filteredComplaints.map((c) => (
                <tr
                  key={c.id}
                  className="hover:bg-brand-blue/5 transition-colors group cursor-pointer"
                  onClick={() => onSelect(c)}
                >
                  <td className="p-5">
                    <div className="flex flex-col gap-1">
                      <span className="font-mono text-brand-blue font-bold bg-brand-blue/10 px-2 py-0.5 rounded w-fit text-xs border border-brand-blue/20">
                        #{c.ticketNumber}
                      </span>
                      <span className="text-xs text-gray-500 flex items-center gap-1">
                        📅 {new Date(c.createdAt).toLocaleDateString('tr-TR')}
                      </span>
                    </div>
                  </td>

                  <td className="p-5">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 border border-gray-600 flex items-center justify-center text-sm font-bold text-gray-300 shadow-inner">
                        {c.passengerName ? c.passengerName.charAt(0).toUpperCase() : '?'}
                      </div>
                      <div>
                        <div className="text-gray-200 font-medium">{c.passengerName}</div>
                        <div className="text-gray-500 text-xs">{c.passengerPhone}</div>
                      </div>
                    </div>
                  </td>

                  <td className="p-5">
                    <div className="max-w-xs">
                      <div className="text-gray-300 font-medium mb-0.5">{c.category}</div>
                      <div className="text-gray-500 text-xs truncate">{c.description}</div>
                    </div>
                  </td>

                  <td className="p-5">
                    <StatusBadge status={c.status} />
                  </td>

                  <td className="p-5 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        className="p-2 text-blue-400 hover:text-white hover:bg-blue-500/20 rounded-lg transition-colors"
                        title="Detayları Görüntüle"
                      >
                        👁️
                      </button>
                      <DeleteButton
                        user={user}
                        complaintOwnerId={c.createdBy}
                        onDelete={() => onDelete(c.id)}
                        confirmMessage={`${c.ticketNumber} numaralı kaydı silmek istediğinize emin misiniz?`}
                        iconOnly={true}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div >
  );
};

export default ComplaintList;