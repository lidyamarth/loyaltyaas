# Layanan Loyalty-as-a-Service (LaaS) dengan Mekanisme Poin Dinamis sebagai Solusi Peningkatan Engagement untuk UMKM
> Final Project - II3160 Integrated Systems Technology

## Loyalty Core API
**Loyalty Core API** adalah *backend service* yang dirancang sebagai mesin utama (*core engine*) untuk sistem loyalitas UMKM. Layanan ini menangani logika bisnis seperti perhitungan poin dinamis, manajemen tingkatan pelanggan (*tiering*), serta validasi penukaran hadiah secara *real-time* dan aman.


[![CI/CD Pipeline](https://github.com/lidyamarth/loyaltyaas/actions/workflows/ci.yml/badge.svg)](https://github.com/lidyamarth/loyaltyaas/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.2-green)](https://fastapi.tiangolo.com/)
[![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen)](https://pytest.org/)
[![Deployed on Railway](https://img.shields.io/badge/Deploy-Railway-purple)](https://railway.app/)

---

## Fitur Utama
- **Manajemen Membership**: Pendaftaran anggota baru dengan *unique ID*.
- **Poin Dinamis**: Perhitungan poin otomatis berdasarkan aturan (misal: per nominal belanja atau per kunjungan).
- **Tiering System**: Kenaikan level member otomatis (Bronze → Silver → Gold) berdasarkan akumulasi poin.
- **Redemption**: Penukaran poin dengan hadiah yang divalidasi oleh sistem (mencegah saldo negatif).
- **Keamanan**: Autentikasi menggunakan **JWT (JSON Web Token)** dan standar OAuth2.
- **Reliabilitas**: Dilengkapi dengan **Unit Testing (Coverage >95%)** dan pipeline **CI/CD**.

---

## Deployment
Layanan ini telah di-*deploy* dan dapat diakses secara publik melalui platform **Railway**:

- **Base URL**: `https://loyalty-api-limart.up.railway.app`
- **Dokumentasi API (Swagger UI)**: **[https://loyalty-api-limart.up.railway.app/docs](https://loyalty-api-limart.up.railway.app/docs)**

---

## Instalasi & Menjalankan Lokal
Pastikan telah menginstal **[uv](https://github.com/astral-sh/uv)** (Package manager Python) atau Python 3.13+.
### 1. Clone Repository
```bash
git clone https://github.com/lidyamarth/loyaltyaas
```

### 2. Install Dependencies
Jika menggunakan uv (Direkomendasikan):
```bash
uv sync
```

Atau menggunakan pip standar:
```bash
pip install -r requirements.txt
```

### 3. Jalankan Server
```bash
uv run uvicorn src.main:app --reload --port 8000
```

Server akan berjalan di http://127.0.0.1:8000.

---

## API Overview & Keamanan
Semua endpoint dilindungi oleh JWT Authentication. Sehingga harus menyertakan Header Authorization: Bearer <token> pada setiap request.

**Akun Demo (Default)**
Gunakan kredensial ini untuk mendapatkan token di endpoint /token:
- Username: admin
- Password: rahasia123

**Daftar Endpoint Utama**
| Method        | Endpoint                 | Deskripsi                                             | Akses   |
|---------------|--------------------------|-------------------------------------------------------|---------|
| POST          | /token                   | Login. Menukar username/password dengan Access Token. | Public  |
| POST          | /memberships/            | Mendaftarkan member baru.                             | Secured |
| GET           | /memberships/{id}        | Cek saldo poin, status tier, dan riwayat transaksi.   | Secured |
| POST          | /memberships/{id}/earn   | Menambah poin dari transaksi belanja.                 | Secured |
| POST          | /memberships/{id}/redeem | Menukar poin dengan hadiah.                           | Secured |

---

## Testing & Code Coverage
Layanan ini menerapkan metodologi Test Driven Deployment (TDD). Pengujian mencakup logic domain, integrasi API, security flows, hingga edge cases.

**Menjalankan Unit Test**
```bash
uv run pytest
```

**Cek Laporan Coverage**
```bash
uv run pytest --cov=src --cov-report=term-missing
```

---

## CI/CD Pipeline
Repositori ini terintegrasi dengan GitHub Actions untuk menjaga kualitas kode secara otomatis.
- Trigger: Setiap kali ada push atau pull request ke branch main.
- Proses:
1. Setup environment Python & uv.
2. Install dependencies.
3. Menjalankan seluruh Unit Test.
4. Memverifikasi Coverage.
- Status: Tanda ✅ pada commit menandakan kode aman, lolos uji, dan siap deploy.

---

## Struktur Proyek
```
loyaltyaas/
├── .github/workflows/    
│   └── ci.yml
├── src/
│   ├── main.py                 
│   └── domain.py         
├── tests/    
│   └── test_app.py          
├── Procfile              
├── pyproject.toml        
├── uv.lock    
├── requirements.txt            
└── README.md             
```

---

## Contoh Payload (JSON)
Berikut adalah contoh format data (*payload*) untuk setiap endpoint yang membutuhkan input.

### Login (Autentikasi)
Endpoint ini menggunakan format **Form Data (`x-www-form-urlencoded`)**, bukan JSON.
**Body:**
| Key      | Value      |
|----------|------------|
| `username` | `admin`      |
| `password` | `rahasia123` |

### Create Membership
Mendaftarkan pelanggan baru untuk mendapatkan `membershipId`.
```json
{
    "pelangganId": "CUST-001",
    "merchantId": "MERCH-A"
  }
```

### Menambah Poin (Earn)
Mencatat transaksi belanja dan menghitung poin berdasarkan aturan yang dikirim.
```json
{
  "transaksi": {
    "transaksiId": "TRX-101",
    "totalBelanja": 50000
  },
  "aturan": {
    "tipeAturan": "PER_RUPIAH",
    "nilaiKelipatan": 10000,
    "poinDiberikan": 10
  }
}
```

### Redeem point
Menukarkan poin yang dimiliki dengan hadiah.
```json
{
  "hadiahId": "VOUCHER-50K",
  "hargaPoin": 50
}
```

---
Dibuat oleh: **Lidya Marthadilla (18223134)** Program Studi Sistem dan Teknologi Informasi - ITB
