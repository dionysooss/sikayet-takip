// Local Storage Service - Firestore yerine localStorage kullanımı

export interface Complaint {
    id: string;
    complaintNumber: string;
    customerName: string;
    customerPhone: string;
    customerPhoneRaw: string;
    customerPhoneCountryCode: string;
    productType: string;
    complaintType: string;
    description: string;
    status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
    priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
    assignedTo?: string;
    branch: string;
    createdBy: string;
    createdAt: string;
    updatedAt: string;
    resolvedAt?: string;
    resolution?: string;
    internalNotes?: string;
}

const COMPLAINTS_KEY = 'sts_complaints';
const COUNTER_KEY = 'sts_complaint_counter';

export class LocalStorageService {
    // Şikayet numarası oluştur
    private static getNextComplaintNumber(): string {
        const counter = parseInt(localStorage.getItem(COUNTER_KEY) || '0') + 1;
        localStorage.setItem(COUNTER_KEY, counter.toString());
        return `SK${new Date().getFullYear()}${counter.toString().padStart(5, '0')}`;
    }

    // Tüm şikayetleri getir
    static getAllComplaints(): Complaint[] {
        try {
            const data = localStorage.getItem(COMPLAINTS_KEY);
            return data ? JSON.parse(data) : [];
        } catch (error) {
            console.error('Şikayetler yüklenirken hata:', error);
            return [];
        }
    }

    // ID'ye göre şikayet getir
    static getComplaintById(id: string): Complaint | null {
        const complaints = this.getAllComplaints();
        return complaints.find(c => c.id === id) || null;
    }

    // Yeni şikayet ekle
    static addComplaint(complaintData: Omit<Complaint, 'id' | 'complaintNumber' | 'createdAt' | 'updatedAt'>): Complaint {
        const complaints = this.getAllComplaints();

        const newComplaint: Complaint = {
            ...complaintData,
            id: `complaint_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            complaintNumber: this.getNextComplaintNumber(),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        complaints.push(newComplaint);
        localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(complaints));

        return newComplaint;
    }

    // Şikayet güncelle
    static updateComplaint(id: string, updates: Partial<Complaint>): Complaint | null {
        const complaints = this.getAllComplaints();
        const index = complaints.findIndex(c => c.id === id);

        if (index === -1) return null;

        complaints[index] = {
            ...complaints[index],
            ...updates,
            updatedAt: new Date().toISOString()
        };

        localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(complaints));
        return complaints[index];
    }

    // Şikayet sil
    static deleteComplaint(id: string): boolean {
        const complaints = this.getAllComplaints();
        const filtered = complaints.filter(c => c.id !== id);

        if (filtered.length === complaints.length) return false;

        localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(filtered));
        return true;
    }

    // Filtreleme
    static filterComplaints(filters: {
        status?: string;
        priority?: string;
        branch?: string;
        assignedTo?: string;
        searchTerm?: string;
    }): Complaint[] {
        let complaints = this.getAllComplaints();

        if (filters.status) {
            complaints = complaints.filter(c => c.status === filters.status);
        }

        if (filters.priority) {
            complaints = complaints.filter(c => c.priority === filters.priority);
        }

        if (filters.branch) {
            complaints = complaints.filter(c => c.branch === filters.branch);
        }

        if (filters.assignedTo) {
            complaints = complaints.filter(c => c.assignedTo === filters.assignedTo);
        }

        if (filters.searchTerm) {
            const term = filters.searchTerm.toLowerCase();
            complaints = complaints.filter(c =>
                c.complaintNumber.toLowerCase().includes(term) ||
                c.customerName.toLowerCase().includes(term) ||
                c.description.toLowerCase().includes(term)
            );
        }

        return complaints;
    }

    // Tüm verileri temizle (test için)
    static clearAllData(): void {
        localStorage.removeItem(COMPLAINTS_KEY);
        localStorage.removeItem(COUNTER_KEY);
    }

    // Demo veriler ekle
    static initializeDemoData(): void {
        const existing = this.getAllComplaints();
        if (existing.length > 0) return; // Zaten veri varsa ekleme

        const demoComplaints: Omit<Complaint, 'id' | 'complaintNumber' | 'createdAt' | 'updatedAt'>[] = [
            {
                customerName: 'Ahmet Yılmaz',
                customerPhone: '+90 (555) 123 45 67',
                customerPhoneRaw: '5551234567',
                customerPhoneCountryCode: 'TR',
                productType: 'Benzin',
                complaintType: 'Kalite',
                description: 'Aldığım benzinin kalitesinden şüpheleniyorum',
                status: 'OPEN',
                priority: 'HIGH',
                branch: 'Merkez',
                createdBy: 'devran'
            },
            {
                customerName: 'Ayşe Demir',
                customerPhone: '+90 (555) 987 65 43',
                customerPhoneRaw: '5559876543',
                customerPhoneCountryCode: 'TR',
                productType: 'Motorin',
                complaintType: 'Hizmet',
                description: 'Personel ilgisiz davrandı',
                status: 'IN_PROGRESS',
                priority: 'MEDIUM',
                assignedTo: 'devran',
                branch: 'Merkez',
                createdBy: 'devran'
            }
        ];

        demoComplaints.forEach(complaint => this.addComplaint(complaint));
    }
}
