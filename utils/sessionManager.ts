import { getFirestore, collection, doc, setDoc, getDoc, deleteDoc, query, where, getDocs } from 'firebase/firestore';

// Generate unique session ID
export function generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
}

// Create session in Firestore
export async function createSession(userId: string, username: string, role: string): Promise<string> {
    const db = getFirestore();
    const sessionId = generateSessionId();

    const sessionData = {
        sessionId,
        userId,
        username,
        role,
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
        lastActivity: new Date()
    };

    await setDoc(doc(db, 'sessions', sessionId), sessionData);

    return sessionId;
}

// Validate session from Firestore
export async function validateSession(sessionId: string): Promise<boolean> {
    if (!sessionId) return false;

    try {
        const db = getFirestore();
        const sessionDoc = await getDoc(doc(db, 'sessions', sessionId));

        if (!sessionDoc.exists()) return false;

        const sessionData = sessionDoc.data();
        const now = new Date();

        // Check if session expired
        if (sessionData.expiresAt.toDate() < now) {
            // Delete expired session
            await deleteDoc(doc(db, 'sessions', sessionId));
            return false;
        }

        // Update last activity
        await setDoc(doc(db, 'sessions', sessionId), {
            ...sessionData,
            lastActivity: now
        });

        return true;
    } catch (error) {
        console.error('Session validation error:', error);
        return false;
    }
}

// Get session data
export async function getSessionData(sessionId: string) {
    if (!sessionId) return null;

    try {
        const db = getFirestore();
        const sessionDoc = await getDoc(doc(db, 'sessions', sessionId));

        if (!sessionDoc.exists()) return null;

        return sessionDoc.data();
    } catch (error) {
        console.error('Get session data error:', error);
        return null;
    }
}

// Delete session (logout)
export async function deleteSession(sessionId: string): Promise<void> {
    if (!sessionId) return;

    try {
        const db = getFirestore();
        await deleteDoc(doc(db, 'sessions', sessionId));
    } catch (error) {
        console.error('Delete session error:', error);
    }
}

// Clean up expired sessions (can be called periodically)
export async function cleanupExpiredSessions(): Promise<void> {
    try {
        const db = getFirestore();
        const now = new Date();
        const sessionsRef = collection(db, 'sessions');
        const snapshot = await getDocs(sessionsRef);

        const deletePromises: Promise<void>[] = [];

        snapshot.forEach((doc) => {
            const sessionData = doc.data();
            if (sessionData.expiresAt.toDate() < now) {
                deletePromises.push(deleteDoc(doc.ref));
            }
        });

        await Promise.all(deletePromises);
    } catch (error) {
        console.error('Cleanup expired sessions error:', error);
    }
}
