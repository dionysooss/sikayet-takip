import {
    collection,
    doc,
    getDocs,
    getDoc,
    addDoc,
    updateDoc,
    deleteDoc,
    query,
    orderBy,
    limit,
    where,
    Timestamp,
    setDoc
} from 'firebase/firestore';
import { db } from './firebaseConfig';
import { Complaint, ComplaintStatus, LogEntry, User, ComplaintCategory, UserRole } from '../types';
import { MOCK_USERS } from '../constants';
import bcrypt from 'bcryptjs';

// Collection references
const usersCollection = collection(db, 'users');
const complaintsCollection = collection(db, 'complaints');
const logsCollection = collection(db, 'logs');

// Initialize default data in Firestore (run once)
const initFirestoreData = async () => {
    try {
        // Check if users exist
        const usersSnapshot = await getDocs(usersCollection);
        if (usersSnapshot.empty) {
            // Add default users
            for (const user of MOCK_USERS) {
                await setDoc(doc(db, 'users', user.id), user);
            }
            console.log('Default users added to Firestore');
        }

        // Check if complaints exist
        const complaintsSnapshot = await getDocs(complaintsCollection);
        if (complaintsSnapshot.empty) {
            // Add default complaint
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
            await setDoc(doc(db, 'complaints', defaultComplaint.id), defaultComplaint);
            console.log('Default complaint added to Firestore');
        }
    } catch (error) {
        console.error('Error initializing Firestore data:', error);
    }
};

// Call init on module load
initFirestoreData();

export const firestoreService = {
    // User operations
    getUsers: async (): Promise<User[]> => {
        try {
            const snapshot = await getDocs(usersCollection);
            return snapshot.docs.map(doc => doc.data() as User);
        } catch (error) {
            console.error('Error getting users:', error);
            return [];
        }
    },

    addUser: async (newUser: User, performedBy: User) => {
        try {
            // Şifreyi hash'le
            if (newUser.password) {
                const salt = await bcrypt.genSalt(10);
                newUser.password = await bcrypt.hash(newUser.password, salt);
            }

            await setDoc(doc(db, 'users', newUser.id), newUser);
            await firestoreService.logAction(performedBy, 'KULLANICI_EKLEME', newUser.username);
        } catch (error) {
            console.error('Error adding user:', error);
            throw error;
        }
    },

    updateUser: async (updatedUser: User, performedBy: User) => {
        try {
            const userRef = doc(db, 'users', updatedUser.id);
            const userDoc = await getDoc(userRef);

            if (userDoc.exists()) {
                const existingUser = userDoc.data() as User;

                // Eğer şifre değiştiriliyorsa hash'le
                let passwordToSave = existingUser.password;
                if (updatedUser.password && updatedUser.password !== existingUser.password) {
                    const salt = await bcrypt.genSalt(10);
                    passwordToSave = await bcrypt.hash(updatedUser.password, salt);
                }

                const dataToUpdate = {
                    ...updatedUser,
                    password: passwordToSave
                };
                await updateDoc(userRef, dataToUpdate as any);
            }
        } catch (error) {
            console.error('Error updating user:', error);
            throw error;
        }
    },

    deleteUser: async (id: string, performedBy: User) => {
        try {
            // Permission check - only admin and manager can delete users
            if (performedBy.role !== UserRole.ADMIN && performedBy.role !== UserRole.MANAGER) {
                throw new Error('Bu işlem için yetkiniz yok. Sadece yöneticiler kullanıcı silebilir.');
            }

            // Prevent self-deletion
            if (id === performedBy.id) {
                throw new Error('Kendi hesabınızı silemezsiniz.');
            }

            const userRef = doc(db, 'users', id);
            const userDoc = await getDoc(userRef);

            if (!userDoc.exists()) {
                throw new Error('Kullanıcı bulunamadı.');
            }

            const targetUser = userDoc.data() as User;
            await deleteDoc(userRef);
            await firestoreService.logAction(performedBy, 'KULLANICI_SILME', `${targetUser.fullName} (${targetUser.username})`);
        } catch (error: any) {
            console.error('Error deleting user:', error);
            throw new Error(error.message || 'Kullanıcı silinirken bir hata oluştu.');
        }
    },

    login: async (username: string, password?: string): Promise<User | null> => {
        try {
            const users = await firestoreService.getUsers();
            const user = users.find(u => u.username.toLowerCase() === username.toLowerCase());

            if (!user || !password) {
                return null;
            }

            // Şifre hash'ini kontrol et
            const isPasswordValid = await bcrypt.compare(password, user.password || '');

            if (isPasswordValid) {
                return user;
            }

            return null;
        } catch (error) {
            console.error('Error during login:', error);
            return null;
        }
    },

    // Yeni yardımcı fonksiyonlar
    getUserById: async (id: string): Promise<User | null> => {
        try {
            const userRef = doc(db, 'users', id);
            const userDoc = await getDoc(userRef);

            if (userDoc.exists()) {
                return userDoc.data() as User;
            }
            return null;
        } catch (error) {
            console.error('Error getting user by ID:', error);
            return null;
        }
    },

    createUserDocument: async (user: User): Promise<void> => {
        try {
            await setDoc(doc(db, 'users', user.id), user);
        } catch (error) {
            console.error('Error creating user document:', error);
            throw error;
        }
    },

    // Complaint operations
    getComplaints: async (): Promise<Complaint[]> => {
        try {
            const q = query(complaintsCollection, orderBy('createdAt', 'desc'));
            const snapshot = await getDocs(q);
            return snapshot.docs.map(doc => {
                const data = doc.data();
                return {
                    ...data,
                    managerNotes: Array.isArray(data.managerNotes) ? data.managerNotes : [],
                    attachments: Array.isArray(data.attachments) ? data.attachments : []
                } as Complaint;
            });
        } catch (error) {
            console.error('Error getting complaints:', error);
            return [];
        }
    },

    getComplaintById: async (id: string): Promise<Complaint | undefined> => {
        try {
            const docRef = doc(db, 'complaints', id);
            const docSnap = await getDoc(docRef);
            if (docSnap.exists()) {
                return docSnap.data() as Complaint;
            }
            return undefined;
        } catch (error) {
            console.error('Error getting complaint by ID:', error);
            return undefined;
        }
    },

    saveComplaint: async (complaint: Complaint, user: User, isNew: boolean) => {
        try {
            if (isNew) {
                // Generate ticket number
                const year = new Date().getFullYear();
                const allComplaints = await firestoreService.getComplaints();
                const lastInYear = allComplaints.filter(c => c.ticketNumber?.startsWith(year.toString()));
                complaint.ticketNumber = `${year}/${(lastInYear.length + 1).toString().padStart(4, '0')}`;

                // Add new complaint
                await setDoc(doc(db, 'complaints', complaint.id), complaint);
                await firestoreService.logAction(user, 'KAYIT_OLUSTURMA', complaint.ticketNumber);
            } else {
                // Update existing complaint
                const complaintRef = doc(db, 'complaints', complaint.id);
                await updateDoc(complaintRef, {
                    ...complaint,
                    updatedAt: new Date().toISOString()
                } as any);
                await firestoreService.logAction(user, 'KAYIT_GUNCELLEME', complaint.ticketNumber);
            }
        } catch (error) {
            console.error('Error saving complaint:', error);
            throw error;
        }
    },

    deleteComplaint: async (id: string, performedBy: User): Promise<boolean> => {
        try {
            // Permission check
            if (performedBy.role !== UserRole.ADMIN && performedBy.role !== UserRole.MANAGER) {
                console.error('Unauthorized delete attempt:', performedBy.username);
                return false;
            }

            const complaintRef = doc(db, 'complaints', id);
            const complaintDoc = await getDoc(complaintRef);

            if (!complaintDoc.exists()) {
                console.error('Complaint not found for deletion! ID:', id);
                return false;
            }

            const target = complaintDoc.data() as Complaint;
            await deleteDoc(complaintRef);
            await firestoreService.logAction(performedBy, 'SILME', `Bilet No: ${target.ticketNumber}`);
            return true;
        } catch (error) {
            console.error('Error deleting complaint:', error);
            return false;
        }
    },

    updateStatus: async (id: string, status: ComplaintStatus, user: User, note?: string) => {
        try {
            const complaintRef = doc(db, 'complaints', id);
            const complaintDoc = await getDoc(complaintRef);

            if (complaintDoc.exists()) {
                const complaint = complaintDoc.data() as Complaint;
                const managerNotes = complaint.managerNotes || [];

                if (note) {
                    managerNotes.push(`[${new Date().toLocaleDateString()}]: ${note}`);
                }

                await updateDoc(complaintRef, {
                    status,
                    managerNotes
                });
            }
        } catch (error) {
            console.error('Error updating status:', error);
            throw error;
        }
    },

    addNote: async (id: string, note: string, user: User) => {
        try {
            const complaintRef = doc(db, 'complaints', id);
            const complaintDoc = await getDoc(complaintRef);

            if (complaintDoc.exists()) {
                const complaint = complaintDoc.data() as Complaint;
                const managerNotes = complaint.managerNotes || [];
                managerNotes.push(`[${new Date().toLocaleString()} - ${user.fullName}]: ${note}`);

                await updateDoc(complaintRef, {
                    managerNotes
                });
            }
        } catch (error) {
            console.error('Error adding note:', error);
            throw error;
        }
    },

    // Log operations
    logAction: async (user: User, action: string, details: string) => {
        try {
            const logEntry: LogEntry = {
                id: Date.now().toString(),
                timestamp: new Date().toISOString(),
                userId: user.id,
                userName: user.fullName,
                action,
                details
            };
            await addDoc(logsCollection, logEntry);
        } catch (error) {
            console.error('Error logging action:', error);
        }
    },

    getLogs: async (): Promise<LogEntry[]> => {
        try {
            const q = query(logsCollection, orderBy('timestamp', 'desc'), limit(100));
            const snapshot = await getDocs(q);
            return snapshot.docs.map(doc => doc.data() as LogEntry);
        } catch (error) {
            console.error('Error getting logs:', error);
            return [];
        }
    },

    // File handling (same as before, works with base64)
    readFileAsBase64: (file: File): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
};
