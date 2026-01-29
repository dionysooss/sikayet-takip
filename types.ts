
export enum UserRole {
  STAFF = 'STAFF',
  MANAGER = 'MANAGER',
  ADMIN = 'ADMIN'
}

export enum ComplaintStatus {
  OPEN = 'AÇIK',
  INVESTIGATING = 'İNCELEMEDE',
  RESOLVED = 'ÇÖZÜLDÜ',
  REJECTED = 'HAKSIZ VE YERSİZ',
  PENDING = 'BEKLEMEDE',
  WAITING_FOR_INFO = 'MÜŞTERIDEN BİLGİ BEKLENİYOR',
  ESCALATED = 'YÖNETİME İLETİLDİ',
  PARTIALLY_RESOLVED = 'KISMEN ÇÖZÜLDÜ',
  LEGAL_PROCESS = 'YASAL SÜREÇTE',
  REOPENED = 'TEKRAR AÇILDI',
  CANCELLED = 'İPTAL EDİLDİ'
}

export enum ComplaintCategory {
  SERVICE = 'Hizmet Kalitesi',
  TIMING = 'Sefer Saati/Gecikme',
  VEHICLE = 'Araç Durumu',
  LUGGAGE = 'Bagaj Hasarı',
  LUGGAGE_MIX = 'Bagaj Karışıklığı',
  LOST_ITEM = 'Eşya Unutma',
  DEPOSIT = 'Emanet',
  PAYMENT_ERROR = 'Hatalı Çekim ve İade',
  PERSONNEL = 'Personel Davranışı',
  OTHER = 'Diğer'
}

export enum ActionType {
  STAFF_PHONE_CALL = 'Personel ile Telefon Görüşmesi',
  STAFF_FACE_TO_FACE = 'Personel ile Yüzyüze Görüşme',
  PASSENGER_PHONE_CALL = 'Yolcu ile Telefon Görüşmesi',
  PASSENGER_FACE_TO_FACE = 'Yolcu ile Yüzyüze Görüşme',
  TICKET_REFUND = 'Bilet İadesi',
  COMPENSATION = 'Tazminat İşlemi',
  INFO_OR_APOLOGY = 'Bilgilendirme veya Özür Mesajı'
}

export interface User {
  id: string;
  username: string;
  password?: string;
  fullName: string;
  role: UserRole;
  phone: string; // Formatted (+90 (5XX)...)
  phoneRaw?: string; // Raw digits (5XXXXXXXXX)
  phoneCountryCode?: string; // TR, US, etc.
  email?: string;
  branch?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: string;
  details: string;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  data: string; // Base64
}

export interface ManagerAction {
  id: string;
  note: string;
  actionType: ActionType;
  timestamp: string;
  userId: string;
  userName: string;
}

export interface Complaint {
  id: string;
  ticketNumber: string;

  // Passenger Info
  passengerName: string;
  passengerPhone: string; // Formatted
  passengerPhoneRaw?: string; // New: Raw digits
  passengerCountryCode?: string; // New: Country Code (TR)
  passengerEmail?: string;

  // Trip Info
  pnr?: string;
  tripDate: string;
  departureTime?: string;
  tripRoute: string;
  licensePlate?: string;
  ticketPrice?: string;
  purchaseChannel?: string;
  applicationChannel?: string;

  // Complaint Details
  category: ComplaintCategory;
  subcategory?: string;
  description: string;

  // System Info
  status: ComplaintStatus;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  attachments: Attachment[];
  managerNotes: string[];
  managerActions?: ManagerAction[]; // New: Detailed action history with types
}

export interface DashboardStats {
  total: number;
  open: number;
  resolved: number;
  byCategory: Record<string, number>;
}