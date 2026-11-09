# 🏢 RuangKita — Smart Coworking & Meeting Room Booking System
> **Tugas Besar 1: DevOps Automated CI/CD Pipeline Jenkins (K10 — Startup Edition)**  
> **Mata Kuliah**: Komputasi Awan (Semester Ganjil 2026/2027)  
> **Kelompok**: 1 (Kelas CC-01)  

---

## 👥 Identitas Tim & Pembagian Peran (Founding Engineers)

| No | Nama Lengkap | NIM | Peran Utama | Tanggung Jawab & Bukti Kontribusi |
|:--:|:---|:---:|:---|:---|
| 1 | **Muh Naufal Rabbani Marun** | `102062400038` | **Tech Lead / Backend** | Arsitektur API, skema database PostgreSQL, migrasi & seeder, implementasi CRUD Ruang & aturan bisnis reservasi. |
| 2 | **Allfridho Prima Anjaynata Saragi** | `102062400045` | **DevOps Engineer** | Setup Jenkins Pipeline, integrasi GitHub Webhook via Ngrok, manajemen Jenkins Credentials, dan logika **Auto-Rollback K10**. |
| 3 | **Andika Candra Kurniawan** | `102062400129` | **Container & QA Engineer** | Multi-stage `Dockerfile` (dengan target `test`), `compose.yaml` (network internal, healthcheck), test suites Jest (7 automated tests), penyusunan laporan PDF. |

---

## 🎯 Gambaran Studi Kasus (K10 — RuangKita)

RuangKita adalah platform pemesanan ruang meeting dan coworking space dengan arsitektur modern berstandar enterprise. Seluruh perubahan kode diverifikasi secara otomatis melalui Automated CI/CD Pipeline tanpa intervensi manual.

### 📌 Fitur Wajib Aplikasi
1. **CRUD Data Ruangan**: Pengelolaan kapasitas, fasilitas lengkap, dan tarif harga sewa per jam.
2. **Cek Ketersediaan per Tanggal**: Pengecekan slot waktu ruangan yang masih tersedia.
3. **Pemesanan (Booking) & Pembatalan**: Reservasi ruang terintegrasi validasi server mutlak.
4. **Kalender Pemakaian Ruang**: Visualisasi jadwal reservasi aktif.
5. **Endpoint Wajib `GET /health`**: Monitoring kesehatan aplikasi dan status koneksi database (HTTP 200 OK).

---

## ⚖️ 4 Aturan Bisnis Inti (Wajib Teruji Automated Tests)

Seluruh aturan bisnis divalidasi langsung di sisi server (*server-side enforcement*) dan dibuktikan melalui 7 automated tests:
1. **Anti-Tumpang Tindih (*Schedule Overlap Protection*)**: Dua booking pada ruangan yang sama tidak boleh bertabrakan waktu, termasuk irisan sebagian waktu.
2. **Kapasitas Maksimal**: Jumlah peserta reservasi dilarang melebihi kapasitas daya tampung ruangan.
3. **Jam Operasional & Durasi**: Reservasi hanya diizinkan berdurasi **1 hingga 8 jam** di dalam jam operasional **08.00 – 21.00 WIB**.
4. **Kebijakan Denda Pembatalan**: Pembatalan kurang dari **2 jam** sebelum jadwal mulai dikenai denda sebesar **50%** dari total tarif sewa.

---

## ⚡ Tantangan Khusus DevOps Kelompok 1 (K10: Auto-Rollback)

> **Rollback Otomatis ke Image Sebelumnya**  
Pipeline Jenkins secara cerdas mencatat tag image Docker yang sedang aktif/berjalan sebelum deployment dimulai (`.previous_deployed_tag`). Jika stage **Smoke Test** mendeteksi kegagalan (endpoint `/health` tidak merespons 200), blok `post { failure { ... } }` **secara otomatis men-deploy ulang tag image sebelumnya yang stabil**, sehingga layanan tetap prima tanpa downtime berkepanjangan.

---

## 🔄 Diagram Arsitektur CI/CD Pipeline & Container

```
 [ Developer ] ──> Push / Merge PR ke main (GitHub)
                         │
                         ▼ (GitHub Webhook via Ngrok Tunnel)
               [ Jenkins Server (CI/CD) ]
                         │
  ┌──────────────────────┴────────────────────────────────────────┐
  │  Stage 1: Checkout     (Git SCM clone repository)             │
  │  Stage 2: Test         (docker build --target test -> Jest)   │
  │  Stage 3: Build Image  (docker build -t app:TAG & latest)     │
  │  Stage 4: Push Image   (docker push ke Docker Hub via Secret) │
  │  Stage 5: Deploy       (docker compose pull && compose up -d) │
  │  Stage 6: Smoke Test   (curl /health == 200 OK)               │
  └──────────────────────┬────────────────────────────────────────┘
                         │
     ┌───────────────────┴───────────────────┐
     ▼ [ JIKA SUKSES ]                       ▼ [ JIKA GAGAL: K10 CHALLENGE ]
  [ Notifikasi Console:                   [ AUTO-ROLLBACK TRIGGERED ]
    Aplikasi Ter-deploy Sehat ]             Kembalikan kontainer ke tag
                                            image versi stabil sebelumnya!
```

### 🐳 Topologi Jaringan Kontainer (`compose.yaml`)

```
   [ Pengguna / Browser / Curl ]
                 │ Port 8000
                 ▼
  ┌──────────────────────────────────────────────────────────┐
  │  ruangkita_public_net (Bridge)                           │
  │   └── Service: app (allfridhosaragi/ruangkita:latest)     │
  └──────────────────────────────┬───────────────────────────┘
                                 │
  ┌──────────────────────────────┴───────────────────────────┐
  │  ruangkita_backend_net (internal: true)                  │
  │   ├── Service: app                                       │
  │   └── Service: database (postgres:16-alpine)             │
  │        └── Volume: ruangkita_postgres_data (persisten)   │
  └──────────────────────────────────────────────────────────┘
```

---

## 🚀 Panduan Menjalankan Secara Lokal

### 1. Prasyarat
- Docker Engine & Docker Compose
- Node.js v20+ (opsional untuk dev lokal)

### 2. Konfigurasi Environment
Salin file template `.env.example` menjadi `.env`:
```bash
cp .env.example .env
```

### 3. Menjalankan Kontainer
```bash
docker compose up -d
```

Verifikasi status kedua kontainer telah **healthy**:
```bash
docker compose ps
```

### 4. Akses Aplikasi
- **Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **Healthcheck**: [http://localhost:8000/health](http://localhost:8000/health)
- **API Ruangan**: [http://localhost:8000/api/rooms](http://localhost:8000/api/rooms)
- **API Booking**: [http://localhost:8000/api/bookings](http://localhost:8000/api/bookings)

### 5. Menjalankan Automated Test
```bash
# Pengujian lokal
npm test

# Pengujian via Docker Stage Test
docker build --target test -t ruangkita:test .
```

---

## 📂 Struktur Repositori

```
├── .dockerignore                 # Optimasi build context Docker
├── .env.example                  # Template konfigurasi rahasia
├── .gitignore                    # Pencegahan kebocoran secret & node_modules
├── Dockerfile                    # Multi-stage Dockerfile (base, test, runner)
├── Jenkinsfile                   # Declarative Pipeline 6 stage + Auto-Rollback K10
├── compose.yaml                  # Spesifikasi Docker Compose (app + db internal)
├── package.json                  # Dependensi Node.js, Express, Jest, Supertest
├── public/
│   └── index.html                # Modern Web Dashboard RuangKita
├── src/
│   ├── app.js                    # Express app configuration & routes
│   ├── server.js                 # Server entrypoint & DB auto-bootstrap
│   ├── config/
│   │   └── db.js                 # PostgreSQL connection pool & mock handler
│   ├── controllers/
│   │   ├── bookingController.js  # Implementasi 4 aturan bisnis booking & denda
│   │   ├── healthController.js   # Endpoint GET /health
│   │   └── roomController.js     # CRUD ruangan & cek ketersediaan
│   └── db/
│       ├── migrate.js            # Migrasi tabel rooms & bookings
│       └── seed.js               # Data seeder awal ruangan
├── tests/
│   └── app.test.js               # 7 automated tests (Jest + Supertest)
└── evidence/                     # Folder bukti screenshot & log pengujian
```

---
*© 2026 Kelompok 1 — Komputasi Awan. All rights reserved.*
