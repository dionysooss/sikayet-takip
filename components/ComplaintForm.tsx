import React, { useState, useEffect } from 'react';
import { ComplaintCategory, ComplaintStatus, User, Attachment, Complaint } from '../types';
import { firestoreService } from '../services/firestoreService';
import PhoneInput from './PhoneInput';

interface ComplaintFormProps {
  user: User;
  onSuccess: () => void;
  initialData?: Complaint;
  onCancel?: () => void;
}

const PURCHASE_OPTIONS = ["Online - Obilet", "Online - Enuygun", "Online - Websitesi"];
const APP_PLATFORMS = ["WhatsApp", "Yüz Yüze Başvuru", "Telefon", "E-posta", "Web Formu"];

const ComplaintForm: React.FC<ComplaintFormProps> = ({ user, onSuccess, initialData, onCancel }) => {
  const [formData, setFormData] = useState({
    passengerName: '',
    passengerPhone: '', // Formatted string
    passengerPhoneRaw: '', // Raw digits
    passengerCountryCode: 'TR', // Country Code
    passengerEmail: '',
    pnr: '',
    tripDate: '',
    departureTime: '',
    tripRoute: '',
    licensePlate: '',
    ticketPrice: '',
    purchaseChannel: '',
    applicationChannel: '',
    category: ComplaintCategory.SERVICE,
    subcategory: '',
    description: '',
  });
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // State to handle the "Şube" logic for Purchase Channel
  const [purchaseMode, setPurchaseMode] = useState('');

  useEffect(() => {
    if (initialData) {
      setFormData({
        passengerName: initialData.passengerName,
        passengerPhone: initialData.passengerPhone,
        passengerPhoneRaw: initialData.passengerPhoneRaw || '',
        passengerCountryCode: initialData.passengerCountryCode || 'TR',
        passengerEmail: initialData.passengerEmail || '',
        pnr: initialData.pnr || '',
        tripDate: initialData.tripDate,
        departureTime: initialData.departureTime || '',
        tripRoute: initialData.tripRoute,
        licensePlate: initialData.licensePlate || '',
        ticketPrice: initialData.ticketPrice || '',
        purchaseChannel: initialData.purchaseChannel || '',
        applicationChannel: initialData.applicationChannel || '',
        category: initialData.category,
        subcategory: initialData.subcategory || '',
        description: initialData.description,
      });
      setAttachments(initialData.attachments);

      const pChannel = initialData.purchaseChannel || '';
      if (PURCHASE_OPTIONS.includes(pChannel)) {
        setPurchaseMode(pChannel);
      } else if (pChannel.length > 0) {
        setPurchaseMode('Şube');
      } else {
        setPurchaseMode('');
      }
    }
  }, [initialData]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      try {
        const base64 = await firestoreService.readFileAsBase64(file);
        const newAtt: Attachment = {
          id: Date.now().toString(),
          name: file.name,
          type: file.type,
          data: base64
        };
        setAttachments([...attachments, newAtt]);
      } catch (err) {
        console.error("File upload error", err);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const isEdit = !!initialData;

    const complaintData: Complaint = {
      id: initialData ? initialData.id : Date.now().toString(),
      // Ticket number is handled by firestoreService if it is new (empty string placeholder)
      ticketNumber: initialData ? initialData.ticketNumber : '',
      createdBy: initialData ? initialData.createdBy : user.id,
      createdAt: initialData ? initialData.createdAt : new Date().toISOString(),
      status: initialData ? initialData.status : ComplaintStatus.OPEN,
      managerNotes: initialData ? initialData.managerNotes : [],

      ...formData,
      attachments: attachments,
      updatedAt: new Date().toISOString(),
    };

    await firestoreService.saveComplaint(complaintData, user, !isEdit);

    setTimeout(() => {
      setIsSubmitting(false);
      onSuccess();
    }, 500);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePhoneChange = (data: { formatted: string; raw: string; countryCode: string; isValid: boolean }) => {
    setFormData({
      ...formData,
      passengerPhone: data.formatted,
      passengerPhoneRaw: data.raw,
      passengerCountryCode: data.countryCode
    });
  };

  const handlePurchaseModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const mode = e.target.value;
    setPurchaseMode(mode);
    if (mode === 'Şube') {
      setFormData({ ...formData, purchaseChannel: '' });
    } else {
      setFormData({ ...formData, purchaseChannel: mode });
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      onSuccess();
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="bg-brand-card p-8 rounded-2xl shadow-xl border border-brand-border">

        <div className="flex items-center gap-4 mb-8 border-b border-brand-border pb-6">
          <div className="h-14 w-14 rounded-2xl bg-blue-900/30 flex items-center justify-center text-2xl shadow-sm border border-blue-500/20 text-brand-blue">
            {initialData ? '✏️' : '📝'}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">
              {initialData ? 'Şikayet Düzenle' : 'Yeni Şikayet Kaydı'}
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {initialData
                ? 'Mevcut şikayet bilgilerini güncellemek için formu düzenleyiniz.'
                : 'Yolcu şikayetlerini sisteme kaydetmek için formu eksiksiz doldurunuz.'}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-10">

          {/* Section 1: Yolcu Bilgileri */}
          <section>
            <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-5 flex items-center gap-2 border-l-4 border-brand-blue pl-3">
              👤 Yolcu Bilgileri
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-black/20 p-6 rounded-xl border border-brand-border">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Yolcu Adı Soyadı</label>
                <input required type="text" name="passengerName" value={formData.passengerName} onChange={handleChange}
                  className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 shadow-sm"
                  placeholder="Ad Soyad giriniz"
                />
              </div>

              <div>
                <PhoneInput
                  label="Telefon Numarası"
                  required
                  value={formData.passengerPhone}
                  initialCountryCode={formData.passengerCountryCode}
                  initialRawValue={formData.passengerPhoneRaw}
                  onChange={handlePhoneChange}
                  variant="light"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">E-posta</label>
                <input type="email" name="passengerEmail" value={formData.passengerEmail} onChange={handleChange}
                  className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 shadow-sm"
                  placeholder="ornek@email.com"
                />
              </div>
            </div>
          </section>

          {/* Section 2: Sefer Bilgileri */}
          <section>
            <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-5 flex items-center gap-2 border-l-4 border-brand-blue pl-3">
              🚌 Sefer Detayları
            </h3>
            <div className="bg-black/20 p-6 rounded-xl border border-brand-border space-y-6">

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">PNR Kodu</label>
                  <input type="text" name="pnr" value={formData.pnr} onChange={handleChange}
                    className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 shadow-sm"
                    placeholder="1A60..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Sefer Tarihi</label>
                  <input required type="date" name="tripDate" value={formData.tripDate} onChange={handleChange}
                    className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all text-gray-800 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Kalkış Saati</label>
                  <input type="time" name="departureTime" value={formData.departureTime} onChange={handleChange}
                    className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all text-gray-800 shadow-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Güzergah</label>
                  <input required placeholder="Örn: Antalya - İstanbul" type="text" name="tripRoute" value={formData.tripRoute} onChange={handleChange}
                    className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Plaka</label>
                  <input type="text" name="licensePlate" value={formData.licensePlate} onChange={handleChange}
                    className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 shadow-sm"
                    placeholder="34 XX 123"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Bilet Ücreti</label>
                  <input type="text" name="ticketPrice" value={formData.ticketPrice} onChange={handleChange}
                    className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 shadow-sm"
                    placeholder="0.00 TL"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Satın Alınan Yer</label>
                  <div className="space-y-2">
                    <div className="relative">
                      <select
                        value={purchaseMode}
                        onChange={handlePurchaseModeChange}
                        className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 appearance-none focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all shadow-sm cursor-pointer"
                      >
                        <option value="">Seçiniz</option>
                        {PURCHASE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                        <option value="Şube">Şube</option>
                      </select>
                      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-black">
                        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
                      </div>
                    </div>

                    {purchaseMode === 'Şube' && (
                      <input
                        type="text"
                        name="purchaseChannel"
                        value={formData.purchaseChannel}
                        onChange={handleChange}
                        placeholder="Lütfen şube adını giriniz..."
                        className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all shadow-sm animate-fade-in"
                      />
                    )}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Başvuru Platformu</label>
                  <div className="relative">
                    <select
                      name="applicationChannel"
                      value={formData.applicationChannel}
                      onChange={handleChange}
                      className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 appearance-none focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all shadow-sm cursor-pointer"
                    >
                      <option value="">Seçiniz</option>
                      {APP_PLATFORMS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-black">
                      <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </section>

          {/* Section 3: Şikayet İçeriği */}
          <section>
            <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-5 flex items-center gap-2 border-l-4 border-brand-blue pl-3">
              ⚠️ Şikayet Detayları
            </h3>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Kategori</label>
                  <div className="relative">
                    <select name="category" value={formData.category} onChange={handleChange}
                      className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 appearance-none focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all shadow-sm cursor-pointer"
                    >
                      {Object.values(ComplaintCategory).map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-black">
                      <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
                    </div>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-300 mb-2">Alt Kategori (Opsiyonel)</label>
                  <input type="text" name="subcategory" value={formData.subcategory} onChange={handleChange}
                    className="w-full bg-white text-black border border-gray-300 rounded-lg p-3 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 shadow-sm"
                    placeholder="Örn: Koltuk arızası, Muavin davranışı vb."
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Açıklama</label>
                <textarea required rows={5} name="description" value={formData.description} onChange={handleChange}
                  className="w-full bg-white text-black border border-gray-300 rounded-lg p-4 focus:ring-4 focus:ring-blue-500/30 focus:border-brand-blue focus:outline-none transition-all placeholder-gray-500 resize-none shadow-sm"
                  placeholder="Lütfen olayı yer, zaman ve kişi belirterek detaylıca anlatınız..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">Dosya Ekle (Resim)</label>
                <div className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:bg-white/5 hover:border-brand-blue transition-all cursor-pointer group bg-black/20">
                  <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" id="file-upload" />
                  <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center justify-center w-full h-full">
                    <div className="h-12 w-12 mb-3 rounded-full bg-gray-800 group-hover:bg-blue-900/50 flex items-center justify-center text-2xl transition-colors border border-gray-700">
                      📷
                    </div>
                    <span className="text-gray-300 font-medium group-hover:text-brand-blue transition-colors">Bilgisayardan dosya seç</span>
                    <span className="text-gray-500 text-sm mt-1">veya sürükleyip bırakın (JPG, PNG)</span>
                  </label>
                </div>
                {attachments.length > 0 && (
                  <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
                    {attachments.map(att => (
                      <div key={att.id} className="relative group rounded-lg overflow-hidden border border-gray-700 shadow-sm">
                        <img src={att.data} alt={att.name} className="w-full h-32 object-cover" />
                        <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                          <button type="button" onClick={() => setAttachments(attachments.filter(a => a.id !== att.id))} className="bg-red-600 text-white rounded-full p-2 hover:bg-red-700 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Footer Actions */}
          <div className="flex items-center justify-end pt-6 border-t border-brand-border gap-3">
            <button type="button" onClick={handleCancel} className="px-6 py-3 rounded-xl text-gray-400 hover:bg-white/5 hover:text-white font-medium transition-colors">
              İptal Et
            </button>
            <button type="submit" disabled={isSubmitting} className="bg-brand-blue text-white px-8 py-3 rounded-xl hover:bg-blue-600 transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)] hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] disabled:opacity-70 font-semibold flex items-center gap-2">
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Kaydediliyor...
                </>
              ) : (
                <>
                  {initialData ? '💾 Değişiklikleri Kaydet' : '💾 Kaydı Oluştur'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ComplaintForm;