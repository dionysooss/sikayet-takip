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
  <style>
    @page {
      size: A5;
      margin: 15mm;
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: Arial, sans-serif;
      font-size: 10pt;
      line-height: 1.4;
      color: #000;
    }
    
    .header {
      text-align: center;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 2px solid #333;
    }
    
    .logo {
      max-height: 40px;
      margin-bottom: 10px;
    }
    
    h1 {
      font-size: 14pt;
      font-weight: bold;
      margin-bottom: 15px;
    }
    
    .info-row {
      margin-bottom: 3px;
      display: flex;
      justify-content: space-between;
    }
    
    .info-row strong {
      font-weight: bold;
    }
    
    .section {
      margin-top: 15px;
      padding-top: 10px;
      border-top: 1px solid #ccc;
    }
    
    .section-title {
      font-size: 11pt;
      font-weight: bold;
      margin-bottom: 8px;
      text-transform: uppercase;
    }
    
    .description-box {
      background: #f5f5f5;
      padding: 10px;
      border-radius: 4px;
      margin-top: 5px;
      white-space: pre-wrap;
    }
    
    .notes-list {
      list-style: none;
      padding-left: 0;
    }
    
    .notes-list li {
      margin-bottom: 5px;
      padding-left: 15px;
      position: relative;
    }
    
    .notes-list li:before {
      content: "•";
      position: absolute;
      left: 0;
    }
    
    @media print {
      body {
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <img src="/logo.png" alt="Logo" class="logo" onerror="this.style.display='none'">
    <h1>ŞİKAYET DETAY RAPORU</h1>
  </div>

  <div class="info-row">
    <strong>Şikayet No:</strong> <span>${complaint.ticketNumber}</span>
  </div>
  <div class="info-row">
    <strong>Oluşturulma:</strong> <span>${new Date(complaint.createdAt).toLocaleDateString('tr-TR')} – Saat: ${new Date(complaint.createdAt).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}</span>
  </div>
  <div class="info-row">
    <strong>Durum:</strong> <span>${complaint.status}</span>
  </div>
  <div class="info-row">
    <strong>Kategori:</strong> <span>${complaint.category}</span>
  </div>

  <div class="section">
    <div class="section-title">Yolcu Bilgileri</div>
    <div class="info-row">
      <strong>Ad Soyad:</strong> <span>${complaint.passengerName}</span>
    </div>
    <div class="info-row">
      <strong>Telefon:</strong> <span>${complaint.passengerPhone}</span>
    </div>
    <div class="info-row">
      <strong>E-posta:</strong> <span>${complaint.passengerEmail || '-'}</span>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Sefer Bilgileri</div>
    <div class="info-row">
      <strong>Güzergah:</strong> <span>${complaint.tripRoute}</span>
    </div>
    <div class="info-row">
      <strong>Tarih / Saat:</strong> <span>${complaint.tripDate} / ${complaint.departureTime || '-'}</span>
    </div>
    <div class="info-row">
      <strong>PNR:</strong> <span>${complaint.pnr || '-'}</span>
    </div>
    <div class="info-row">
      <strong>Plaka:</strong> <span>${complaint.licensePlate || '-'}</span>
    </div>
    <div class="info-row">
      <strong>Bilet Ücreti:</strong> <span>${complaint.ticketPrice || '-'}</span>
    </div>
    <div class="info-row">
      <strong>Satın Alınan:</strong> <span>${complaint.purchaseChannel || '-'}</span>
    </div>
    <div class="info-row">
      <strong>Başvuru Platformu:</strong> <span>${complaint.applicationChannel || '-'}</span>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Şikayet Açıklaması</div>
    <div class="description-box">${complaint.description}</div>
  </div>

  <div class="section">
    <div class="section-title">Yönetici Notu</div>
    ${complaint.managerNotes.length > 0
            ? `<ul class="notes-list">${complaint.managerNotes.map(note => `<li>${note}</li>`).join('')}</ul>`
            : '<p>Henüz bir not eklenmemiş</p>'
        }
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
