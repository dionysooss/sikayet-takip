
import React, { useState, useRef, useEffect } from 'react';
import { geminiService } from '../services/geminiService';
import { INITIAL_GREETING } from '../constants';

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; text: string; mode?: string }[]>([
    { role: 'ai', text: INITIAL_GREETING }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiMode, setAiMode] = useState<'standard' | 'thinking' | 'search'>('standard');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setIsLoading(true);

    let response = "";
    if (aiMode === 'search') {
      response = await geminiService.searchWeb(userMsg);
    } else {
      response = await geminiService.sendMessage(userMsg, aiMode === 'thinking');
    }

    setMessages(prev => [...prev, { role: 'ai', text: response || 'Yanıt alınamadı.', mode: aiMode }]);
    setIsLoading(false);
  };

  return (
    <div className="bg-brand-card rounded-xl shadow-xl border border-brand-border h-[600px] flex flex-col overflow-hidden">
      <div className="p-4 border-b border-brand-border bg-black/20 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-white flex items-center gap-2">🤖 Akıllı Asistan</h3>
          <div className="flex gap-1">
             <span className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${aiMode === 'thinking' ? 'bg-purple-900 border-purple-500 text-purple-200' : 'bg-gray-800 border-gray-700 text-gray-400'}`}>Pro</span>
             <span className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${aiMode === 'search' ? 'bg-blue-900 border-blue-500 text-blue-200' : 'bg-gray-800 border-gray-700 text-gray-400'}`}>Search</span>
          </div>
        </div>

        {/* Mode Selector */}
        <div className="flex gap-2">
          <button 
            onClick={() => setAiMode('standard')}
            className={`flex-1 text-[10px] py-1.5 rounded-lg border transition-all font-bold ${aiMode === 'standard' ? 'bg-brand-blue border-brand-blue text-white shadow-lg shadow-blue-900/40' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'}`}
          >
            Hızlı Yanıt
          </button>
          <button 
            onClick={() => setAiMode('thinking')}
            className={`flex-1 text-[10px] py-1.5 rounded-lg border transition-all font-bold ${aiMode === 'thinking' ? 'bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-900/40' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'}`}
          >
            🧠 Derin Düşün
          </button>
          <button 
            onClick={() => setAiMode('search')}
            className={`flex-1 text-[10px] py-1.5 rounded-lg border transition-all font-bold ${aiMode === 'search' ? 'bg-emerald-600 border-emerald-500 text-white shadow-lg shadow-emerald-900/40' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'}`}
          >
            🌐 Web'de Ara
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-brand-dark/30">
        {messages.map((m, i) => (
          <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
            {m.mode && m.role === 'ai' && (
              <span className="text-[9px] mb-1 opacity-50 uppercase tracking-tighter ml-2">
                {m.mode === 'thinking' ? '🧠 Düşünülerek Yanıtlandı' : m.mode === 'search' ? '🌐 Web Araması Kullanıldı' : ''}
              </span>
            )}
            <div className={`max-w-[90%] rounded-2xl p-3 text-sm leading-relaxed ${
              m.role === 'user' 
                ? 'bg-brand-blue text-white rounded-tr-none shadow-lg shadow-blue-900/20' 
                : 'bg-black/60 text-gray-200 border border-brand-border rounded-tl-none'
            }`}>
              <p className="whitespace-pre-wrap">{m.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-2 items-center text-blue-400 text-xs font-bold animate-pulse">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
            {aiMode === 'thinking' ? 'Karmaşık veriler analiz ediliyor...' : aiMode === 'search' ? 'İnternet kaynakları taranıyor...' : 'Yazıyor...'}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-brand-border bg-black/20 flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={aiMode === 'thinking' ? "Analiz edilecek detayları yazın..." : "Bir şey sorun..."}
          className="flex-1 bg-white text-black border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-4 focus:ring-blue-500/30 font-medium"
        />
        <button 
          onClick={handleSend}
          disabled={isLoading}
          className={`px-5 py-2.5 rounded-xl text-white font-bold transition-all shadow-lg flex items-center gap-2 ${
            aiMode === 'thinking' ? 'bg-purple-600 hover:bg-purple-700 shadow-purple-900/30' : 
            aiMode === 'search' ? 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-900/30' : 
            'bg-brand-blue hover:bg-blue-600 shadow-blue-900/30'
          }`}
        >
          {isLoading ? '...' : '✈️'}
        </button>
      </div>
    </div>
  );
};

export default AIChat;
