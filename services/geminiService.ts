import { GoogleGenAI } from "@google/genai";

const getAIClient = () => {
  return new GoogleGenAI({ apiKey: process.env.API_KEY });
};

export const geminiService = {
  // Standart Chat (Gemini 3 Pro - Thinking Aktif)
  sendMessage: async (message: string, useThinking: boolean = false) => {
    try {
      const ai = getAIClient();
      const config: any = {
        systemInstruction: "Sen Isparta Petrol Turizm'in yardımsever bir yapay zeka asistanısın. Personelin şikayet analizlerine, kurumsal yazışmalarına ve operasyonel sorularına yanıt verirsin.",
      };

      if (useThinking) {
        config.thinkingConfig = { thinkingBudget: 32768 };
      }

      const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: [{ role: 'user', parts: [{ text: message }] }],
        config
      });

      return response.text;
    } catch (error) {
      console.error("Gemini Pro Error:", error);
      return "Üzgünüm, şu anda derin analiz yapamıyorum.";
    }
  },

  // Google Search ile Arama (Gemini 3 Flash)
  searchWeb: async (query: string) => {
    try {
      const ai = getAIClient();
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: [{ role: 'user', parts: [{ text: query }] }],
        config: {
          tools: [{ googleSearch: {} }]
        }
      });

      let text = response.text || "";
      const sources = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
      
      if (sources && sources.length > 0) {
        text += "\n\n**Kaynaklar:**\n";
        sources.forEach((chunk: any, i: number) => {
          if (chunk.web) {
            text += `[${i+1}] ${chunk.web.title}: ${chunk.web.uri}\n`;
          }
        });
      }
      return text;
    } catch (error) {
      console.error("Gemini Search Error:", error);
      return "Web araması sırasında bir hata oluştu.";
    }
  },

  editImage: async (base64Image: string, prompt: string): Promise<string | null> => {
    try {
      const ai = getAIClient();
      const base64Data = base64Image.replace(/^data:image\/\w+;base64,/, "");
      const mimeType = base64Image.match(/data:([a-zA-Z0-9]+\/[a-zA-Z0-9-.+]+).*,.*/)?.[1] || 'image/jpeg';

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash-image',
        contents: {
          parts: [
            { inlineData: { data: base64Data, mimeType: mimeType } },
            { text: prompt },
          ],
        },
      });

      if (response.candidates && response.candidates[0].content.parts) {
        for (const part of response.candidates[0].content.parts) {
          if (part.inlineData) {
            return `data:image/png;base64,${part.inlineData.data}`;
          }
        }
      }
      return null;
    } catch (error) {
      console.error("Gemini Image Edit Error:", error);
      throw error;
    }
  }
};