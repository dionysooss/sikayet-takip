import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut as firebaseSignOut,
    updatePassword as firebaseUpdatePassword,
    sendPasswordResetEmail,
    onAuthStateChanged,
    User as FirebaseUser
} from 'firebase/auth';
import app from './firebaseConfig';
import { User, UserRole } from '../types';
import { firestoreService } from './firestoreService';

const auth = getAuth(app);

export const authService = {
    /**
     * Yeni kullanıcı kaydı oluştur
     * @param email - Email adresi
     * @param password - Şifre
     * @param userData - Kullanıcı bilgileri
     */
    signUp: async (email: string, password: string, userData: Omit<User, 'id'>): Promise<User> => {
        try {
            // Firebase Auth'da kullanıcı oluştur
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const firebaseUser = userCredential.user;

            // Firestore'da kullanıcı kaydı oluştur
            const newUser: User = {
                ...userData,
                id: firebaseUser.uid,
                email: email
            };

            await firestoreService.createUserDocument(newUser);
            return newUser;
        } catch (error: any) {
            console.error('Sign up error:', error);

            // Firebase hata mesajlarını Türkçeleştir
            if (error.code === 'auth/email-already-in-use') {
                throw new Error('Bu email adresi zaten kullanımda');
            } else if (error.code === 'auth/invalid-email') {
                throw new Error('Geçersiz email adresi');
            } else if (error.code === 'auth/weak-password') {
                throw new Error('Şifre çok zayıf');
            }

            throw new Error('Kayıt işlemi başarısız oldu');
        }
    },

    /**
     * Kullanıcı girişi
     * @param email - Email adresi
     * @param password - Şifre
     */
    signIn: async (email: string, password: string): Promise<User | null> => {
        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const firebaseUser = userCredential.user;

            // Firestore'dan kullanıcı bilgilerini al
            const user = await firestoreService.getUserById(firebaseUser.uid);
            return user;
        } catch (error: any) {
            console.error('Sign in error:', error);

            // Firebase hata mesajlarını Türkçeleştir
            if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
                throw new Error('Email veya şifre hatalı');
            } else if (error.code === 'auth/invalid-email') {
                throw new Error('Geçersiz email adresi');
            } else if (error.code === 'auth/user-disabled') {
                throw new Error('Bu hesap devre dışı bırakılmış');
            } else if (error.code === 'auth/too-many-requests') {
                throw new Error('Çok fazla başarısız deneme. Lütfen daha sonra tekrar deneyin');
            }

            throw new Error('Giriş başarısız oldu');
        }
    },

    /**
     * Kullanıcı çıkışı
     */
    signOut: async (): Promise<void> => {
        try {
            await firebaseSignOut(auth);
        } catch (error) {
            console.error('Sign out error:', error);
            throw new Error('Çıkış işlemi başarısız oldu');
        }
    },

    /**
     * Şifre güncelleme
     * @param newPassword - Yeni şifre
     */
    updatePassword: async (newPassword: string): Promise<void> => {
        try {
            const user = auth.currentUser;
            if (!user) {
                throw new Error('Kullanıcı oturumu bulunamadı');
            }

            await firebaseUpdatePassword(user, newPassword);
        } catch (error: any) {
            console.error('Update password error:', error);

            if (error.code === 'auth/requires-recent-login') {
                throw new Error('Şifre değiştirmek için yeniden giriş yapmanız gerekiyor');
            } else if (error.code === 'auth/weak-password') {
                throw new Error('Şifre çok zayıf');
            }

            throw new Error('Şifre güncellenemedi');
        }
    },

    /**
     * Şifre sıfırlama emaili gönder
     * @param email - Email adresi
     */
    resetPassword: async (email: string): Promise<void> => {
        try {
            await sendPasswordResetEmail(auth, email);
        } catch (error: any) {
            console.error('Reset password error:', error);

            if (error.code === 'auth/user-not-found') {
                throw new Error('Bu email adresi ile kayıtlı kullanıcı bulunamadı');
            } else if (error.code === 'auth/invalid-email') {
                throw new Error('Geçersiz email adresi');
            }

            throw new Error('Şifre sıfırlama emaili gönderilemedi');
        }
    },

    /**
     * Mevcut kullanıcıyı al
     */
    getCurrentUser: (): FirebaseUser | null => {
        return auth.currentUser;
    },

    /**
     * Auth state değişikliklerini dinle
     * @param callback - Callback fonksiyonu
     */
    onAuthStateChanged: (callback: (user: FirebaseUser | null) => void) => {
        return onAuthStateChanged(auth, callback);
    }
};
