import bcrypt from 'bcryptjs';
import { MOCK_USERS } from '../constants';
import { firestoreService } from '../services/firestoreService';

/**
 * Mevcut kullanıcıların şifrelerini hash'le
 * Bu script sadece bir kez çalıştırılmalı
 */
export const migrateUserPasswords = async (): Promise<void> => {
    console.log('🔐 Şifre migration başlıyor...');

    try {
        // Tüm kullanıcıları al
        const users = await firestoreService.getUsers();

        for (const user of users) {
            // Eğer şifre zaten hash'lenmişse (60 karakter bcrypt hash) atla
            if (user.password && user.password.length === 60 && user.password.startsWith('$2')) {
                console.log(`✓ ${user.username} - Şifre zaten hash'lenmiş, atlanıyor`);
                continue;
            }

            // Şifreyi hash'le
            if (user.password) {
                const salt = await bcrypt.genSalt(10);
                const hashedPassword = await bcrypt.hash(user.password, salt);

                // Kullanıcıyı güncelle
                const updatedUser = {
                    ...user,
                    password: hashedPassword
                };

                await firestoreService.updateUser(updatedUser, user);
                console.log(`✓ ${user.username} - Şifre hash'lendi`);
            }
        }

        console.log('✅ Şifre migration tamamlandı!');
    } catch (error) {
        console.error('❌ Migration hatası:', error);
        throw error;
    }
};

/**
 * Default kullanıcıları hash'lenmiş şifrelerle oluştur
 */
export const initializeDefaultUsers = async (): Promise<void> => {
    console.log('👤 Default kullanıcılar oluşturuluyor...');

    try {
        const users = await firestoreService.getUsers();

        // Eğer kullanıcı yoksa, default kullanıcıları ekle
        if (users.length === 0) {
            for (const mockUser of MOCK_USERS) {
                if (mockUser.password) {
                    const salt = await bcrypt.genSalt(10);
                    const hashedPassword = await bcrypt.hash(mockUser.password, salt);

                    const userWithHashedPassword = {
                        ...mockUser,
                        password: hashedPassword
                    };

                    await firestoreService.addUser(userWithHashedPassword, mockUser);
                    console.log(`✓ ${mockUser.username} oluşturuldu`);
                }
            }
            console.log('✅ Default kullanıcılar oluşturuldu!');
        } else {
            console.log('ℹ️ Kullanıcılar zaten mevcut, atlanıyor');
        }
    } catch (error) {
        console.error('❌ Default kullanıcı oluşturma hatası:', error);
        throw error;
    }
};
