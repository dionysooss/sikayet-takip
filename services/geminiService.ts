import { GoogleGenerativeAI } from "@google/generative-ai";

const getAIClient = () => {
  const apiKey = import.meta.env.VITE_GOOGLE_AI_API_KEY;
  if (!apiKey) {
    throw new Error("Google AI API key is missing. Please add VITE_GOOGLE_AI_API_KEY to your .env file");
  }
  return new GoogleGenerativeAI(apiKey);
};

export const geminiService = {
  // Standart Chat (Gemini 3 Pro - Thinking Aktif)
  sendMessage: async (message: string, useThinking: boolean = false) => {
    try {
      const ai = getAIClient();
      const modelName = useThinking ? "gemini-2.0-flash-thinking-exp" : "gemini-2.0-flash-exp";

      const model = ai.getGenerativeModel({
        model: modelName,
        systemInstruction: "Sen Isparta Petrol Turizm'in yardımsever bir yapay zeka asistanısın. Personelin şikayet analizlerine, kurumsal yazışmalarına ve operasyonel sorularına yanıt verirsin.",
      });

      const result = await model.generateContent(message);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error("Gemini Pro Error:", error);
      return "Üzgünüm, şu anda derin analiz yapamıyorum. Lütfen API key'inizin doğru olduğundan emin olun.";
    }
  },

  // Google Search ile Arama (Gemini Flash with Google Search)
  searchWeb: async (query: string) => {
    try {
      const ai = getAIClient();
      const model = ai.getGenerativeModel({
        model: "gemini-2.0-flash-exp",
        tools: [{ googleSearch: {} }],
      });

      const result = await model.generateContent(query);
      const response = await result.response;
      let text = response.text();

      const groundingMetadata = response.candidates?.[0]?.groundingMetadata;
      if (groundingMetadata?.groundingChunks && groundingMetadata.groundingChunks.length > 0) {
        text += "\n\n**Kaynaklar:**\n";
        groundingMetadata.groundingChunks.forEach((chunk: any, i: number) => {
          if (chunk.web) {
            text += `[${i + 1}] ${chunk.web.title}: ${chunk.web.uri}\n`;
          }
        });
      }
      return text;
    } catch (error) {
      console.error("Gemini Search Error:", error);
      return "Web araması sırasında bir hata oluştu. Lütfen API key'inizin doğru olduğundan emin olun.";
    }
  },

  editImage: async (base64Image: string, prompt: string): Promise<string | null> => {
    try {
      const ai = getAIClient();
      const base64Data = base64Image.replace(/^data:image\/\w+;base64,/, "");
      const mimeType = base64Image.match(/data:([a-zA-Z0-9]+\/[a-zA-Z0-9-.+]+).*,.*/)?.[1] || 'image/jpeg';

      const model = ai.getGenerativeModel({ model: "gemini-2.0-flash-exp" });

      const result = await model.generateContent([
        {
          inlineData: {
            data: base64Data,
            mimeType: mimeType
          }
        },
        { text: prompt }
      ]);

      const response = await result.response;
      const candidates = response.candidates;

      if (candidates && candidates[0].content.parts) {
        for (const part of candidates[0].content.parts) {
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