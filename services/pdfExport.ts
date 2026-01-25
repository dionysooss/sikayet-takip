import { Complaint } from '../types';

export const exportComplaintToPDF = (complaint: Complaint) => {
  const printWindow = window.open('', '_blank');

  if (!printWindow) {
    alert('Pop-up engelleyici nedeniyle PDF oluşturulamadı. Lütfen pop-up izni verin.');
    return;
  }

  const html = `
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Şikayet ${complaint.ticketNumber}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    @page {
      size: A4;
      margin: 20mm;
    }
    
    @media print {
      @page {
        margin-top: 0;
        margin-bottom: 0;
      }
      
      body {
        margin-top: 20mm;
        margin-bottom: 20mm;
      }
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 10pt;
      line-height: 1.6;
      color: #1f2937;
    }
    
    .header {
      text-align: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 3px solid #3B82F6;
    }
    
    .company-name {
      font-size: 18pt;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 4px;
    }
    
    .company-tagline {
      font-size: 9pt;
      color: #6b7280;
      font-style: italic;
    }
    
    .document-title {
      background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 20px;
      text-align: center;
    }
    
    .document-title h1 {
      font-size: 14pt;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    
    .ticket-info {
      background: #f9fafb;
      border-left: 4px solid #3B82F6;
      padding: 12px 16px;
      margin-bottom: 20px;
      border-radius: 4px;
    }
    
    .ticket-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 6px;
      font-size: 10pt;
    }
    
    .ticket-row:last-child {
      margin-bottom: 0;
    }
    
    .ticket-row .label {
      font-weight: 600;
      color: #4b5563;
      min-width: 120px;
    }
    
    .ticket-row .value {
      color: #1f2937;
      flex: 1;
      text-align: right;
    }
    
    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 9pt;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .status-open {
      background: #fef3c7;
      color: #92400e;
    }
    
    .status-investigating {
      background: #dbeafe;
      color: #1e40af;
    }
    
    .status-resolved {
      background: #d1fae5;
      color: #065f46;
    }
    
    .status-rejected {
      background: #fee2e2;
      color: #991b1b;
    }
    
    .section {
      margin-top: 20px;
      page-break-inside: avoid;
    }
    
    .section-header {
      background: #f3f4f6;
      padding: 8px 12px;
      border-radius: 6px;
      margin-bottom: 12px;
      border-left: 3px solid #3B82F6;
    }
    
    .section-title {
      font-size: 11pt;
      font-weight: 600;
      color: #1f2937;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 16px;
      margin-bottom: 8px;
    }
    
    .info-item {
      display: flex;
      padding: 6px 0;
      border-bottom: 1px solid #e5e7eb;
    }
    
    .info-item .label {
      font-weight: 500;
      color: #6b7280;
      min-width: 100px;
      font-size: 9pt;
    }
    
    .info-item .value {
      color: #1f2937;
      font-weight: 400;
      flex: 1;
    }
    
    .description-box {
      background: #f9fafb;
      padding: 14px;
      border-radius: 6px;
      border: 1px solid #e5e7eb;
      margin-top: 8px;
      white-space: pre-wrap;
      line-height: 1.7;
      font-size: 10pt;
    }
    
    .notes-list {
      list-style: none;
      padding-left: 0;
      margin-top: 8px;
    }
    
    .notes-list li {
      background: #fffbeb;
      border-left: 3px solid #f59e0b;
      padding: 10px 12px;
      margin-bottom: 8px;
      border-radius: 4px;
      font-size: 9pt;
      line-height: 1.5;
    }
    
    .no-notes {
      color: #9ca3af;
      font-style: italic;
      font-size: 9pt;
      padding: 8px 0;
    }
    
    .footer {
      margin-top: 30px;
      padding-top: 16px;
      border-top: 2px solid #e5e7eb;
      text-align: center;
      font-size: 8pt;
      color: #9ca3af;
    }
    
    .footer-row {
      margin-bottom: 4px;
    }
    
    @media print {
      body {
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
      }
      
      .section {
        page-break-inside: avoid;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="company-name">Isparta Petrol Turizm</div>
    <div class="company-tagline">Kilometrelerce hikâye taşıyoruz</div>
  </div>

  <div class="document-title">
    <h1>ŞİKAYET DETAY RAPORU</h1>
  </div>

  <div class="ticket-info">
    <div class="ticket-row">
      <span class="label">Şikayet No</span>
      <span class="value" style="font-weight: 700; color: #3B82F6; font-size: 11pt;">${complaint.ticketNumber}</span>
    </div>
    <div class="ticket-row">
      <span class="label">Oluşturulma</span>
      <span class="value">${new Date(complaint.createdAt).toLocaleDateString('tr-TR')} • ${new Date(complaint.createdAt).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}</span>
    </div>
    <div class="ticket-row">
      <span class="label">Durum</span>
      <span class="value">
        <span class="status-badge ${complaint.status === 'Açık' ? 'status-open' :
      complaint.status === 'İnceleniyor' ? 'status-investigating' :
        complaint.status === 'Çözüldü' ? 'status-resolved' :
          'status-rejected'
    }">${complaint.status}</span>
      </span>
    </div>
    <div class="ticket-row">
      <span class="label">Kategori</span>
      <span class="value" style="font-weight: 600;">${complaint.category}</span>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <div class="section-title">👤 Yolcu Bilgileri</div>
    </div>
    <div class="info-grid">
      <div class="info-item">
        <span class="label">Ad Soyad</span>
        <span class="value">${complaint.passengerName}</span>
      </div>
      <div class="info-item">
        <span class="label">Telefon</span>
        <span class="value">${complaint.passengerPhone}</span>
      </div>
      <div class="info-item" style="grid-column: 1 / -1;">
        <span class="label">E-posta</span>
        <span class="value">${complaint.passengerEmail || '-'}</span>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <div class="section-title">🚌 Sefer Bilgileri</div>
    </div>
    <div class="info-grid">
      <div class="info-item" style="grid-column: 1 / -1;">
        <span class="label">Güzergah</span>
        <span class="value" style="font-weight: 600;">${complaint.tripRoute}</span>
      </div>
      <div class="info-item">
        <span class="label">Tarih</span>
        <span class="value">${complaint.tripDate}</span>
      </div>
      <div class="info-item">
        <span class="label">Kalkış Saati</span>
        <span class="value">${complaint.departureTime || '-'}</span>
      </div>
      <div class="info-item">
        <span class="label">PNR</span>
        <span class="value">${complaint.pnr || '-'}</span>
      </div>
      <div class="info-item">
        <span class="label">Plaka</span>
        <span class="value">${complaint.licensePlate || '-'}</span>
      </div>
      <div class="info-item">
        <span class="label">Bilet Ücreti</span>
        <span class="value">${complaint.ticketPrice || '-'}</span>
      </div>
      <div class="info-item">
        <span class="label">Satın Alınan Yer</span>
        <span class="value">${complaint.purchaseChannel || '-'}</span>
      </div>
      <div class="info-item">
        <span class="label">Başvuru</span>
        <span class="value">${complaint.applicationChannel || '-'}</span>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <div class="section-title">⚠️ Şikayet Açıklaması</div>
    </div>
    <div class="description-box">${complaint.description}</div>
  </div>

  <div class="section">
    <div class="section-header">
      <div class="section-title">📝 Yönetici Notları</div>
    </div>
    ${complaint.managerNotes.length > 0
      ? `<ul class="notes-list">${complaint.managerNotes.map(note => `<li>${note}</li>`).join('')}</ul>`
      : '<p class="no-notes">Henüz bir not eklenmemiş</p>'
    }
  </div>

  <div class="footer">
    <div class="footer-row">Bu rapor Isparta Petrol Turizm Şikayet Takip Sistemi tarafından otomatik olarak oluşturulmuştur.</div>
    <div class="footer-row">© ${new Date().getFullYear()} Isparta Petrol Turizm • Tüm hakları saklıdır</div>
  </div>

  <script>
    window.onload = function() {
      setTimeout(() => {
        window.print();
        setTimeout(() => window.close(), 100);
      }, 500);
    };
  </script>
</body>
</html>
  `;

  printWindow.document.write(html);
  printWindow.document.close();
};
