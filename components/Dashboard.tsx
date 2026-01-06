import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Complaint, ComplaintStatus } from '../types';

interface DashboardProps {
  complaints: Complaint[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#1d4ed8'];

const Dashboard: React.FC<DashboardProps> = ({ complaints }) => {
  const stats = useMemo(() => {
    const total = complaints.length;
    const open = complaints.filter(c => c.status === ComplaintStatus.OPEN).length;
    const resolved = complaints.filter(c => c.status === ComplaintStatus.RESOLVED).length;
    
    // Category Data
    const catMap: Record<string, number> = {};
    complaints.forEach(c => {
      catMap[c.category] = (catMap[c.category] || 0) + 1;
    });
    const categoryData = Object.keys(catMap).map(key => ({ name: key, value: catMap[key] }));

    // Status Data
    const statusMap: Record<string, number> = {};
    complaints.forEach(c => {
      statusMap[c.status] = (statusMap[c.status] || 0) + 1;
    });
    const statusData = Object.keys(statusMap).map(key => ({ name: key, value: statusMap[key] }));

    return { total, open, resolved, categoryData, statusData };
  }, [complaints]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Yönetim Özeti</h2>
      
      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <span className="text-6xl">📊</span>
          </div>
          <p className="text-sm text-gray-400 mb-1">Toplam Şikayet</p>
          <p className="text-3xl font-bold text-white">{stats.total}</p>
        </div>
        <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <span className="text-6xl">⏳</span>
          </div>
          <p className="text-sm text-gray-400 mb-1">Açık / İncelenen</p>
          <p className="text-3xl font-bold text-yellow-500">{stats.open}</p>
        </div>
        <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <span className="text-6xl">✅</span>
          </div>
          <p className="text-sm text-gray-400 mb-1">Çözüme Ulaşan</p>
          <p className="text-3xl font-bold text-green-500">{stats.resolved}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border h-96">
          <h3 className="text-lg font-semibold mb-4 text-white">Kategori Dağılımı</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.categoryData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" stroke="#666" />
              <YAxis dataKey="name" type="category" width={120} style={{ fontSize: '12px' }} stroke="#aaa" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-brand-card p-6 rounded-xl shadow-xl border border-brand-border h-96">
          <h3 className="text-lg font-semibold mb-4 text-white">Durum Özeti</h3>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={stats.statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {stats.statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="#18181b" />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;