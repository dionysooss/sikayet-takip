export interface User {
    id: string;
    username: string;
    fullName: string;
    role: string;
    branch: string;
    phone: string;
    photoURL: string;
}

export interface SessionData {
    user: User;
    sessionId: string;
    timestamp: number;
}

/**
 * Web Crypto API kullanarak şifreyi hashler (SHA-256)
 */
export async function hashPassword(password: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}

/**
 * Şifreyi doğrular (hash karşılaştırması)
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
    const passwordHash = await hashPassword(password);
    return passwordHash === hash;
}

/**
 * Session'ı localStorage'a kaydeder
 */
export function saveSession(user: User, sessionId: string): void {
    const sessionData: SessionData = {
        user,
        sessionId,
        timestamp: Date.now()
    };
    localStorage.setItem('session', JSON.stringify(sessionData));
}

/**
 * Mevcut session'ı getirir
 */
export function getSession(): SessionData | null {
    try {
        const sessionStr = localStorage.getItem('session');
        if (!sessionStr) return null;

        const session: SessionData = JSON.parse(sessionStr);

        // Session 7 gün geçerliliği kontrolü
        const sevenDays = 7 * 24 * 60 * 60 * 1000;
        if (Date.now() - session.timestamp > sevenDays) {
            clearSession();
            return null;
        }

        return session;
    } catch (error) {
        clearSession();
        return null;
    }
}

/**
 * Session'ı temizler (logout)
 */
export async function clearSession(): Promise<void> {
    // Get session ID before clearing
    const session = getSession();
    if (session?.sessionId) {
        // Delete from Firestore
        const { deleteSession } = await import('./sessionManager');
        await deleteSession(session.sessionId);
    }
    localStorage.removeItem('session');
}

/**
 * Kullanıcının giriş yapıp yapmadığını kontrol eder
 */
export function isAuthenticated(): boolean {
    return getSession() !== null;
}
