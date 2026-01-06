import { UserRole } from "./types";

export const APP_NAME = "Isparta Petrol CRM";

export const MOCK_USERS = [
  { 
    id: '1', 
    username: 'Devran', 
    password: '123456', 
    fullName: 'Devran Yönetici', 
    role: UserRole.ADMIN,
    phone: '+90 (555) 000 00 00',
    phoneRaw: '5550000000',
    phoneCountryCode: 'TR',
    email: 'devran@ispartapetrol.com',
    branch: 'Merkez'
  }
];

export const INITIAL_GREETING = "Merhaba! Size nasıl yardımcı olabilirim?";

export interface CountryPhone {
  code: string;
  name: string;
  dialCode: string;
  flag: string;
  mask: string; // Use # for digits
}

export const COUNTRY_PHONE_CODES: CountryPhone[] = [
  { code: 'TR', name: 'Türkiye', dialCode: '+90', flag: '🇹🇷', mask: '(###) ### ## ##' },
  { code: 'DE', name: 'Almanya', dialCode: '+49', flag: '🇩🇪', mask: '### #######' },
  { code: 'FR', name: 'Fransa', dialCode: '+33', flag: '🇫🇷', mask: '# ## ## ## ##' },
  { code: 'UK', name: 'İngiltere', dialCode: '+44', flag: '🇬🇧', mask: '#### ###### ' }, // UK variable, simplified
  { code: 'US', name: 'Amerika', dialCode: '+1', flag: '🇺🇸', mask: '(###) ###-####' },
  { code: 'NL', name: 'Hollanda', dialCode: '+31', flag: '🇳🇱', mask: '## ########' },
  { code: 'IT', name: 'İtalya', dialCode: '+39', flag: '🇮🇹', mask: '### #######' },
  { code: 'ES', name: 'İspanya', dialCode: '+34', flag: '🇪🇸', mask: '### ### ###' },
  { code: 'RU', name: 'Rusya', dialCode: '+7', flag: '🇷🇺', mask: '(###) ###-##-##' },
  { code: 'AZ', name: 'Azerbaycan', dialCode: '+994', flag: '🇦🇿', mask: '(##) ### ## ##' },
];