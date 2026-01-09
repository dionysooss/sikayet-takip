import { authService } from '../services/authService';
import { firestoreService } from '../services/firestoreService';
import { User } from '../types';

/**
 * Migrate existing users to Firebase Authentication
 * This script should be run once to migrate all existing users
 */
export const migrateUsersToFirebaseAuth = async (): Promise<void> => {
    try {
        console.log('🔄 Starting user migration to Firebase Authentication...');

        // Get all users from Firestore
        const users = await firestoreService.getUsers();
        console.log(`📋 Found ${users.length} users to migrate`);

        const results = {
            success: [] as string[],
            failed: [] as { username: string; error: string }[],
            skipped: [] as string[]
        };

        for (const user of users) {
            try {
                // Skip if user doesn't have email
                if (!user.email) {
                    console.log(`⏭️  Skipping ${user.username} - no email address`);
                    results.skipped.push(user.username);
                    continue;
                }

                // Generate a temporary password (user should reset it)
                const tempPassword = `Temp${Math.random().toString(36).slice(-8)}!`;

                // Create Firebase Auth account
                await authService.signUp(user.email, tempPassword, {
                    username: user.username,
                    fullName: user.fullName,
                    role: user.role,
                    phone: user.phone,
                    phoneRaw: user.phoneRaw,
                    phoneCountryCode: user.phoneCountryCode,
                    email: user.email,
                    branch: user.branch
                });

                console.log(`✅ Migrated ${user.username} (${user.email})`);
                console.log(`   Temporary password: ${tempPassword}`);
                results.success.push(user.username);

            } catch (error: any) {
                if (error.message?.includes('email-already-in-use')) {
                    console.log(`⚠️  ${user.username} already exists in Firebase Auth`);
                    results.skipped.push(user.username);
                } else {
                    console.error(`❌ Failed to migrate ${user.username}:`, error.message);
                    results.failed.push({ username: user.username, error: error.message });
                }
            }
        }

        // Print summary
        console.log('\n📊 Migration Summary:');
        console.log(`✅ Successfully migrated: ${results.success.length}`);
        console.log(`⏭️  Skipped: ${results.skipped.length}`);
        console.log(`❌ Failed: ${results.failed.length}`);

        if (results.success.length > 0) {
            console.log('\n🔑 Temporary Passwords (save these securely):');
            console.log('Users should change their passwords after first login.');
        }

        if (results.failed.length > 0) {
            console.log('\n❌ Failed migrations:');
            results.failed.forEach(({ username, error }) => {
                console.log(`   ${username}: ${error}`);
            });
        }

        console.log('\n✅ Migration complete!');
    } catch (error) {
        console.error('❌ Migration failed:', error);
        throw error;
    }
};

/**
 * Create a single user in Firebase Authentication
 * Useful for adding new users through the admin panel
 */
export const createFirebaseAuthUser = async (
    email: string,
    password: string,
    userData: Omit<User, 'id'>
): Promise<User> => {
    try {
        const newUser = await authService.signUp(email, password, userData);
        console.log(`✅ Created user: ${userData.username} (${email})`);
        return newUser;
    } catch (error: any) {
        console.error(`❌ Failed to create user ${userData.username}:`, error.message);
        throw error;
    }
};
