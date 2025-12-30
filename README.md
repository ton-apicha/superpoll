# QuickPoll 📊

ระบบสำรวจความคิดเห็นสาธารณะ (Public Opinion Poll) พัฒนาด้วย Python Streamlit

## ✨ Features

### สำหรับผู้ตอบแบบสอบถาม (Voter)
- 📱 Mobile-first design - ใช้งานง่ายบนมือถือ
- 🖱️ ไม่ต้องพิมพ์ - แค่จิ้มเลือก
- 🚫 ไม่ต้องสมัครสมาชิก
- 📊 ดูผลโหวตได้ทันทีหลังตอบ (ถ้าเปิดใช้งาน)

### สำหรับผู้ดูแลระบบ (Admin)
- ➕ สร้างแคมเปญโพลได้ไม่จำกัด
- 📝 Question Builder - รองรับ Single/Multi select
- 📊 Real-time Dashboard - ดูผลแบบเรียลไทม์
- 🔍 Cross-tabulation - วิเคราะห์เชิงลึกตามกลุ่มประชากร
- 📥 Export CSV - ส่งออกข้อมูลดิบ
- 🔗 แชร์ QR Code - แจกลิงก์โพลได้ง่าย

## 🚀 Quick Start

### วิธีที่ 1: ใช้ Docker (แนะนำ)

```bash
# Clone หรือ cd ไปที่โฟลเดอร์โปรเจกต์
cd SuperPoll

# รัน Docker Compose
docker-compose up --build -d

# เข้าใช้งานที่
# http://localhost:8501
```

### วิธีที่ 2: รันแบบ Local

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน Streamlit
streamlit run app.py
```

## 📖 วิธีใช้งาน

### การเข้าถึงหน้าต่างๆ

| หน้า | URL |
|------|-----|
| หน้าหลัก | `http://localhost:8501` |
| Admin Panel | `http://localhost:8501?admin` |
| ทำโพล | `http://localhost:8501?poll=<campaign_id>` |

### รหัสผ่าน Admin

- Default: `admin123`
- เปลี่ยนได้ใน `docker-compose.yml` (ตัวแปร `ADMIN_PASSWORD`)

## 📁 Project Structure

```
SuperPoll/
├── app.py                    # Main application
├── pages/
│   ├── voter.py              # Voter interface
│   └── admin.py              # Admin panel
├── utils/
│   ├── database.py           # SQLite operations
│   ├── auth.py               # Authentication
│   └── charts.py             # Plotly charts
├── data/
│   └── quickpoll.db          # SQLite database (auto-created)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🔒 Security Features

- **Anti-spam**: ป้องกันการโหวตซ้ำด้วย browser token
- **IP Logging**: บันทึก IP สำหรับตรวจสอบความผิดปกติ
- **Password Protection**: Admin panel ต้องใช้รหัสผ่าน

## 📊 Demographic Options

ระบบรองรับการเก็บข้อมูลประชากร:
- ช่วงอายุ
- ระดับการศึกษา
- ภูมิภาค
- อาชีพ
- รายได้เฉลี่ย

## 🛠️ Tech Stack

- **Frontend & Backend**: Streamlit
- **Database**: SQLite
- **Charts**: Plotly
- **QR Code**: qrcode library
- **Deployment**: Docker

---

Made with ❤️ for public opinion polling
