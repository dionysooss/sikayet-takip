
export enum UserRole {
  STAFF = 'STAFF',
  MANAGER = 'MANAGER',
  ADMIN = 'ADMIN'
}

export enum ComplaintStatus {
  OPEN = 'Açık',
  INVESTIGATING = 'İnceleniyor',
  RESOLVED = 'Çözüldü',
  REJECTED = 'Reddedildi'
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
}

export interface DashboardStats {
  total: number;
  open: number;
  resolved: number;
  byCategory: Record<string, number>;
}