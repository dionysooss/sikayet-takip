import React, { useState } from 'react';
import { geminiService } from '../services/geminiService';

interface ImageEditorProps {
  originalImage: string; // Base64
  onClose: () => void;
}

const ImageEditor: React.FC<ImageEditorProps> = ({ originalImage, onClose }) => {
  const [prompt, setPrompt] = useState('');
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEdit = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    try {
      // Use original image if it's the first edit, or subsequent result if iterating?
      // For simplicity, always edit original or current result
      const source = resultImage || originalImage;
      const result = await geminiService.editImage(source, prompt);
      if (result) {
        setResultImage(result);
      } else {
        setError("Görüntü oluşturulamadı. Lütfen tekrar deneyin.");
      }
    } catch (err) {
        console.error(err);
      setError("AI servisine bağlanırken hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-brand-card rounded-xl w-full max-w-4xl h-[90vh] flex flex-col overflow-hidden border border-brand-border shadow-2xl">
        <div className="p-4 border-b border-brand-border flex justify-between items-center bg-black/20">
          <h3 className="font-bold text-lg text-white">AI Resim Düzenleyici (Gemini 2.5)</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-red-500 text-2xl transition-colors">&times;</button>
        </div>
        
        <div className="flex-1 flex flex-col md:flex-row p-4 gap-4 overflow-hidden">
          <div className="flex-1 flex items-center justify-center bg-black/40 border border-brand-border rounded-lg relative overflow-auto">
            <img 
              src={resultImage || originalImage} 
              alt="Edit target" 
              className="max-h-full max-w-full object-contain"
            />
            {loading && (
              <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-brand-blue border-t-transparent"></div>
              </div>
            )}
          </div>
          
          <div className="w-full md:w-80 flex flex-col gap-4">
            <div className="bg-blue-900/20 border border-blue-900/50 p-4 rounded-lg text-sm text-blue-200">
              <p>💡 Örnek Komutlar:</p>
              <ul className="list-disc pl-4 mt-2 space-y-1 text-blue-300">
                <li>"Hasarlı bölgeyi kırmızı çember içine al"</li>
                <li>"Arka planı bulanıklaştır"</li>
                <li>"Görüntü kalitesini iyileştir"</li>
              </ul>
            </div>

            <textarea 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Yapay zekaya ne yapmasını istediğinizi yazın..."
              className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 h-32 resize-none focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none"
            />
            
            {error && <p className="text-red-400 text-sm">{error}</p>}
            
            <button 
              onClick={handleEdit}
              disabled={loading || !prompt.trim()}
              className="w-full bg-brand-blue text-white py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-blue-900/20"
            >
              ✨ {loading ? 'İşleniyor...' : 'Düzenle'}
            </button>
            
            {resultImage && (
               <button 
               onClick={() => setResultImage(null)}
               className="w-full border border-gray-600 text-gray-300 py-2 rounded-lg hover:bg-white/10"
             >
               Orijinale Dön
             </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageEditor;