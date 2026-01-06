import React from 'react';

interface ConfirmationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    isProcessing?: boolean;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmLabel = "Evet, Sil",
    cancelLabel = "İptal",
    isProcessing = false,
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
            <div className="bg-brand-card border border-brand-border rounded-xl shadow-2xl max-w-md w-full overflow-hidden transform transition-all scale-100">

                {/* Header */}
                <div className="p-6 border-b border-brand-border bg-red-900/10">
                    <div className="flex items-center gap-3 text-red-400">
                        <div className="p-2 bg-red-900/20 rounded-full">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-bold">{title}</h3>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6">
                    <p className="text-gray-300 leading-relaxed whitespace-pre-line">
                        {message}
                    </p>
                </div>

                {/* Actions */}
                <div className="p-4 bg-black/20 border-t border-brand-border flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        disabled={isProcessing}
                        className="px-4 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors font-medium text-sm disabled:opacity-50"
                    >
                        {cancelLabel}
                    </button>

                    <button
                        onClick={onConfirm}
                        disabled={isProcessing}
                        className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold text-sm shadow-lg shadow-red-900/20 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isProcessing ? (
                            <>
                                <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                İşleniyor...
                            </>
                        ) : (
                            confirmLabel
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationModal;
