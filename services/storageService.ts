import { Complaint, ComplaintStatus, LogEntry, User, ComplaintCategory, UserRole } from "../types";
import { MOCK_USERS } from "../constants";

const USERS_KEY = 'ipt_users';
const COMPLAINTS_KEY = 'ipt_complaints';
const LOGS_KEY = 'ipt_logs';

const initData = () => {
  if (!localStorage.getItem(USERS_KEY)) {
    localStorage.setItem(USERS_KEY, JSON.stringify(MOCK_USERS));
  }
  if (!localStorage.getItem(COMPLAINTS_KEY)) {
    const defaultComplaint: Complaint = {
      id: 'default-1',
      ticketNumber: '2025/0001',
      passengerName: 'Seyhan Aydoğdu (Örnek Kayıt)',
      passengerPhone: '+90 (533) 118 39 11',
      passengerPhoneRaw: '5331183911',
      passengerCountryCode: 'TR',
      tripDate: '2025-05-20',
      tripRoute: 'Antalya - Isparta - İstanbul',
      category: ComplaintCategory.TIMING,
      description: 'Bu bir örnek kayıttır. Silme işlemini test edebilirsiniz.',
      status: ComplaintStatus.OPEN,
      createdBy: '1',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      attachments: [],
      managerNotes: []
    };
    localStorage.setItem(COMPLAINTS_KEY, JSON.stringify([defaultComplaint]));
  }
  if (!localStorage.getItem(LOGS_KEY)) {
    localStorage.setItem(LOGS_KEY, JSON.stringify([]));
  }
};

initData();

export const storageService = {
  getUsers: (): User[] => JSON.parse(localStorage.getItem(USERS_KEY) || '[]'),
  
  addUser: (newUser: User, performedBy: User) => {
    const users = storageService.getUsers();
    users.push(newUser);
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
    storageService.logAction(performedBy, 'KULLANICI_EKLEME', newUser.username);
  },

  updateUser: (updatedUser: User, performedBy: User) => {
    const users = storageService.getUsers();
    const idx = users.findIndex(u => u.id === updatedUser.id);
    if (idx !== -1) {
      users[idx] = { ...updatedUser, password: updatedUser.password || users[idx].password };
      localStorage.setItem(USERS_KEY, JSON.stringify(users));
    }
  },

  deleteUser: (id: string, performedBy: User) => {
    const users = storageService.getUsers();
    const newList = users.filter(u => u.id !== id);
    localStorage.setItem(USERS_KEY, JSON.stringify(newList));
  },
  
  login: (username: string, password?: string): User | null => {
    return storageService.getUsers().find(u => u.username.toLowerCase() === username.toLowerCase() && u.password === password) || null;
  },

  getComplaints: (): Complaint[] => {
    const data = localStorage.getItem(COMPLAINTS_KEY);
    const list = data ? JSON.parse(data) : [];
    // Veri güvenliği: Eksik alanları tamamla (managerNotes, attachments vb.)
    return list.map((c: any) => ({
      ...c,
      managerNotes: Array.isArray(c.managerNotes) ? c.managerNotes : [],
      attachments: Array.isArray(c.attachments) ? c.attachments : []
    }));
  },
  
  getComplaintById: (id: string) => storageService.getComplaints().find(c => c.id === id),

  saveComplaint: (complaint: Complaint, user: User, isNew: boolean) => {
    const list = storageService.getComplaints();
    if (isNew) {
      const year = new Date().getFullYear();
      const lastInYear = list.filter(c => c.ticketNumber?.startsWith(year.toString()));
      complaint.ticketNumber = `${year}/${(lastInYear.length + 1).toString().padStart(4, '0')}`;
      list.unshift(complaint);
    } else {
      const idx = list.findIndex(c => c.id === complaint.id);
      if (idx !== -1) list[idx] = { ...complaint, updatedAt: new Date().toISOString() };
    }
    localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(list));
    storageService.logAction(user, isNew ? 'KAYIT_OLUSTURMA' : 'KAYIT_GUNCELLEME', complaint.ticketNumber);
  },

  deleteComplaint: (id: string, performedBy: User): boolean => {
    // YETKİ KONTROLÜ
    if (performedBy.role !== UserRole.ADMIN && performedBy.role !== UserRole.MANAGER) {
      console.error("Yetkisiz silme girişimi:", performedBy.username);
      return false;
    }

    const list = storageService.getComplaints();
    const targetIndex = list.findIndex(c => c.id === id);
    
    if (targetIndex === -1) {
      console.error("Silinecek kayıt bulunamadı! ID:", id);
      return false;
    }

    const target = list[targetIndex];
    const newList = list.filter(c => c.id !== id);
    
    localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(newList));
    storageService.logAction(performedBy, 'SILME', `Bilet No: ${target.ticketNumber}`);
    return true;
  },

  updateStatus: (id: string, status: ComplaintStatus, user: User, note?: string) => {
    const list = storageService.getComplaints();
    const idx = list.findIndex(c => c.id === id);
    if (idx !== -1) {
      list[idx].status = status;
      // Güvenlik: managerNotes dizisinin varlığını kontrol et
      if (!list[idx].managerNotes) list[idx].managerNotes = [];
      
      if (note) list[idx].managerNotes.push(`[${new Date().toLocaleDateString()}]: ${note}`);
      localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(list));
    }
  },

  addNote: (id: string, note: string, user: User) => {
    const list = storageService.getComplaints();
    const idx = list.findIndex(c => c.id === id);
    if (idx !== -1) {
      if (!list[idx].managerNotes) list[idx].managerNotes = [];
      list[idx].managerNotes.push(`[${new Date().toLocaleString()} - ${user.fullName}]: ${note}`);
      localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(list));
    }
  },

  logAction: (user: User, action: string, details: string) => {
    const logs = JSON.parse(localStorage.getItem(LOGS_KEY) || '[]');
    logs.unshift({ id: Date.now().toString(), timestamp: new Date().toISOString(), userId: user.id, userName: user.fullName, action, details });
    localStorage.setItem(LOGS_KEY, JSON.stringify(logs.slice(0, 100)));
  },

  getLogs: (): LogEntry[] => JSON.parse(localStorage.getItem(LOGS_KEY) || '[]'),
  
  readFileAsBase64: (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
};