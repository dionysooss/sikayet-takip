import validator from 'validator';

/**
 * Güvenlik yardımcı fonksiyonları
 */

// Şifre güvenlik kuralları
export interface PasswordValidation {
    isValid: boolean;
    errors: string[];
}

/**
 * Şifre güvenlik kurallarını kontrol eder
 * @param password - Kontrol edilecek şifre
 * @returns Validation sonucu
 */
export const validatePassword = (password: string): PasswordValidation => {
    const errors: string[] = [];

    if (!password || password.length < 8) {
        errors.push('Şifre en az 8 karakter olmalıdır');
    }

    if (!/[A-Z]/.test(password)) {
        errors.push('Şifre en az bir büyük harf içermelidir');
    }

    if (!/[a-z]/.test(password)) {
        errors.push('Şifre en az bir küçük harf içermelidir');
    }

    if (!/[0-9]/.test(password)) {
        errors.push('Şifre en az bir rakam içermelidir');
    }

    return {
        isValid: errors.length === 0,
        errors
    };
};

/**
 * Email formatını kontrol eder
 * @param email - Kontrol edilecek email
 * @returns Geçerli mi?
 */
export const validateEmail = (email: string): boolean => {
    return validator.isEmail(email);
};

/**
 * XSS saldırılarına karşı input temizleme
 * @param input - Temizlenecek string
 * @returns Temizlenmiş string
 */
export const sanitizeInput = (input: string): string => {
    if (!input) return '';

    // HTML karakterlerini escape et
    return input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/\//g, '&#x2F;');
};

/**
 * Rate limiting için basit bir implementasyon
 */
interface RateLimitEntry {
    count: number;
    firstAttempt: number;
    blockedUntil?: number;
}

const rateLimitStore = new Map<string, RateLimitEntry>();

/**
 * Rate limiting kontrolü
 * @param key - Unique key (örn: username, IP)
 * @param maxAttempts - Maksimum deneme sayısı
 * @param windowMs - Zaman penceresi (ms)
 * @param blockDurationMs - Bloke süresi (ms)
 * @returns Blocked mi?
 */
export const checkRateLimit = (
    key: string,
    maxAttempts: number = 5,
    windowMs: number = 15 * 60 * 1000, // 15 dakika
    blockDurationMs: number = 5 * 60 * 1000 // 5 dakika
): { allowed: boolean; remainingAttempts?: number; blockedUntil?: Date } => {
    const now = Date.now();
    const entry = rateLimitStore.get(key);

    // Eğer bloke edilmişse
    if (entry?.blockedUntil && entry.blockedUntil > now) {
        return {
            allowed: false,
            blockedUntil: new Date(entry.blockedUntil)
        };
    }

    // Eğer entry yoksa veya zaman penceresi geçmişse, yeni entry oluştur
    if (!entry || (now - entry.firstAttempt) > windowMs) {
        rateLimitStore.set(key, {
            count: 1,
            firstAttempt: now
        });
        return {
            allowed: true,
            remainingAttempts: maxAttempts - 1
        };
    }

    // Deneme sayısını artır
    entry.count++;

    // Maksimum deneme aşıldıysa bloke et
    if (entry.count > maxAttempts) {
        entry.blockedUntil = now + blockDurationMs;
        rateLimitStore.set(key, entry);
        return {
            allowed: false,
            blockedUntil: new Date(entry.blockedUntil)
        };
    }

    rateLimitStore.set(key, entry);
    return {
        allowed: true,
        remainingAttempts: maxAttempts - entry.count
    };
};

/**
 * Rate limit'i sıfırla (başarılı login sonrası)
 * @param key - Unique key
 */
export const resetRateLimit = (key: string): void => {
    rateLimitStore.delete(key);
};

/**
 * Telefon numarasını validate et
 * @param phone - Telefon numarası
 * @returns Geçerli mi?
 */
export const validatePhone = (phone: string): boolean => {
    // Sadece rakamları al
    const digits = phone.replace(/\D/g, '');

    // En az 10 rakam olmalı
    return digits.length >= 10 && digits.length <= 15;
};

/**
 * Username güvenlik kontrolü
 * @param username - Kullanıcı adı
 * @returns Geçerli mi?
 */
export const validateUsername = (username: string): { isValid: boolean; error?: string } => {
    if (!username || username.length < 3) {
        return { isValid: false, error: 'Kullanıcı adı en az 3 karakter olmalıdır' };
    }

    if (username.length > 20) {
        return { isValid: false, error: 'Kullanıcı adı en fazla 20 karakter olabilir' };
    }

    // Sadece harf, rakam ve alt çizgi
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        return { isValid: false, error: 'Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir' };
    }

    return { isValid: true };
};
