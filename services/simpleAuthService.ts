// Simple Authentication Service
// Kullanıcı: devran, Şifre: Dionysos.1881

export interface User {
    id: string;
    username: string;
    fullName: string;
    role: 'ADMIN' | 'MANAGER' | 'USER';
    branch: string;
}

// Hardcoded admin kullanıcısı
const ADMIN_USER = {
    username: 'devran',
    password: 'Dionysos.1881', // Production'da hash'lenmiş olmalı
    user: {
        id: 'admin-001',
        username: 'devran',
        fullName: 'Devran Yönetici',
        role: 'ADMIN' as const,
        branch: 'Merkez'
    }
};

const SESSION_KEY = 'sts_session';
const SESSION_TIMEOUT = 24 * 60 * 60 * 1000; // 24 saat

interface Session {
    user: User;
    timestamp: number;
}

export class SimpleAuthService {
    // Login fonksiyonu
    static login(username: string, password: string): { success: boolean; user?: User; error?: string } {
        // Kullanıcı adı ve şifre kontrolü
        if (username === ADMIN_USER.username && password === ADMIN_USER.password) {
            const session: Session = {
                user: ADMIN_USER.user,
                timestamp: Date.now()
            };

            // Session'ı localStorage'a kaydet
            localStorage.setItem(SESSION_KEY, JSON.stringify(session));

            return {
                success: true,
                user: ADMIN_USER.user
            };
        }

        return {
            success: false,
            error: 'Kullanıcı adı veya şifre hatalı'
        };
    }

    // Logout fonksiyonu
    static logout(): void {
        localStorage.removeItem(SESSION_KEY);
    }

    // Mevcut kullanıcıyı al
    static getCurrentUser(): User | null {
        try {
            const sessionData = localStorage.getItem(SESSION_KEY);
            if (!sessionData) return null;

            const session: Session = JSON.parse(sessionData);

            // Session timeout kontrolü
            if (Date.now() - session.timestamp > SESSION_TIMEOUT) {
                this.logout();
                return null;
            }

            return session.user;
        } catch (error) {
            console.error('Session okuma hatası:', error);
            return null;
        }
    }

    // Kullanıcı giriş yapmış mı?
    static isAuthenticated(): boolean {
        return this.getCurrentUser() !== null;
    }

    // Session'ı yenile (kullanıcı aktif olduğunda)
    static refreshSession(): void {
        const user = this.getCurrentUser();
        if (user) {
            const session: Session = {
                user,
                timestamp: Date.now()
            };
            localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        }
    }
}
