import React, { useState } from 'react';
import { User, UserRole } from '../types';
import ConfirmationModal from './ConfirmationModal';

interface DeleteButtonProps {
  user: User;
  onDelete: () => void;
  confirmMessage: string;
  complaintOwnerId?: string; // Şikayeti oluşturan kullanıcının ID'si
  label?: string;
  iconOnly?: boolean;
  className?: string;
}

const DeleteButton: React.FC<DeleteButtonProps> = ({
  user,
  onDelete,
  confirmMessage,
  complaintOwnerId,
  label,
  iconOnly = false,
  className = ""
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Admin/Manager tüm şikayetleri silebilir
  // Normal kullanıcılar sadece kendi şikayetlerini silebilir
  const isAdminOrManager = user.role === UserRole.ADMIN || user.role === UserRole.MANAGER;
  const isOwner = complaintOwnerId ? user.id === complaintOwnerId : false;
  const canDelete = isAdminOrManager || isOwner;

  if (!canDelete) return null;

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsModalOpen(true);
  };

  const handleConfirm = async () => {
    setIsDeleting(true);
    // Simulate a small delay for better UX or if onDelete is async
    try {
      await onDelete();
    } catch (error) {
      console.error("Delete failed", error);
    } finally {
      setIsDeleting(false);
      setIsModalOpen(false);
    }
  };

  return (
    <>
      {iconOnly ? (
        <button
          type="button"
          onClick={handleDeleteClick}
          className={`p-2 rounded-lg bg-red-900/10 text-red-500 hover:bg-red-500 hover:text-white transition-all border border-red-900/30 group/del shadow-sm relative z-20 cursor-pointer ${className}`}
          title={label || "Kaydı Sil"}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      ) : (
        <button
          type="button"
          onClick={handleDeleteClick}
          className={`flex items-center gap-2 bg-red-900/10 text-red-400 border border-red-900/30 px-4 py-2 rounded-lg hover:bg-red-900/30 transition-all text-sm font-medium hover:text-red-300 shadow-sm relative z-20 cursor-pointer ${className}`}
        >
          <span className="text-lg">🗑️</span> {label || "Kaydı Sil"}
        </button>
      )}

      <ConfirmationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleConfirm}
        title="Silme İşlemi"
        message={confirmMessage}
        isProcessing={isDeleting}
      />
    </>
  );
};

export default DeleteButton;