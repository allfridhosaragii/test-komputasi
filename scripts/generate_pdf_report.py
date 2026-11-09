import os
import base64
import asyncio
from playwright.async_api import async_playwright

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(image_path)[1].replace('.', '')
    return f"data:image/{ext};base64,{base64.b64encode(data).decode('utf-8')}"

async def generate_pdf():
    img_ui = get_base64_image("evidence/01_ui_dashboard.png")
    img_health = get_base64_image("evidence/02_health_endpoint.png")
    img_ps = get_base64_image("evidence/03_docker_compose_ps.png")
    img_test = get_base64_image("evidence/04_automated_tests_pass.png")
    img_qg = get_base64_image("evidence/05_quality_gate_red_green.png")
    img_rollback = get_base64_image("evidence/06_auto_rollback_k10.png")
    img_stage = get_base64_image("evidence/07_jenkins_stage_view.png")

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Laporan Tugas Besar 1 — Kelompok 1 (RuangKita K10)</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    @page {{
      size: A4;
      margin: 15mm 15mm 18mm 15mm;
      @bottom-right {{
        content: counter(page);
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 8pt;
        color: #64748b;
      }}
    }}

    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 9.5pt;
      line-height: 1.5;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }}

    .page-break {{ page-break-after: always; }}
    .no-break {{ page-break-inside: avoid; }}

    h1, h2, h3, h4 {{ color: #0f172a; margin-top: 0; font-weight: 800; }}
    h1 {{ font-size: 16pt; margin-bottom: 4px; }}
    h2 {{ font-size: 12pt; margin-bottom: 6px; padding-bottom: 3px; border-bottom: 1.5px solid #0d9488; color: #0f766e; }}
    h3 {{ font-size: 10.5pt; margin-bottom: 4px; color: #1e293b; }}

    p {{ margin-top: 0; margin-bottom: 6px; text-align: justify; }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 10px;
      font-size: 8.5pt;
    }}
    th, td {{
      padding: 6px 8px;
      border: 1px solid #cbd5e1;
      text-align: left;
    }}
    th {{
      background-color: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
    }}
    tr:nth-child(even) {{ background-color: #f8fafc; }}

    .badge {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 7.5pt;
      font-weight: 700;
    }}
    .badge-teal {{ background: #ccfbf1; color: #0f766e; border: 1px solid #99f6e4; }}
    .badge-emerald {{ background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }}
    .badge-rose {{ background: #ffe4e6; color: #9f1239; border: 1px solid #fecdd3; }}

    .code-block {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 8pt;
      background: #0f172a;
      color: #f8fafc;
      padding: 8px 12px;
      border-radius: 6px;
      margin-bottom: 8px;
      overflow-x: hidden;
      white-space: pre-wrap;
    }}

    .evidence-box {{
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 6px;
      margin-bottom: 10px;
      background: #fafafa;
    }}
    .evidence-box img {{
      width: 100%;
      height: auto;
      border-radius: 4px;
      display: block;
    }}
    .evidence-caption {{
      font-size: 7.5pt;
      font-weight: 600;
      color: #475569;
      margin-top: 4px;
      text-align: center;
    }}

    .header-box {{
      border-bottom: 2px solid #0f766e;
      padding-bottom: 8px;
      margin-bottom: 14px;
    }}
  </style>
</head>
<body>

  <!-- ==================== HALAMAN 1 ==================== -->
  <div class="header-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <span class="badge badge-teal">LAPORAN TUGAS BESAR 1 — KOMPUTASI AWAN</span>
        <h1>DevOps: Automated CI/CD Pipeline Jenkins</h1>
        <p style="margin: 0; font-size: 9pt; color: #475569;">
          Studi Kasus: <b>RuangKita (K10 — Smart Coworking & Meeting Hub)</b>
        </p>
      </div>
      <div style="text-align: right; font-size: 8pt; color: #64748b;">
        <div><b>Semester Ganjil 2026/2027</b></div>
        <div>Kelas: <b>CC-01</b> | Kelompok: <b>1</b></div>
      </div>
    </div>
  </div>

  <h2>1. Identitas Kelompok, Studi Kasus & Kredensial Pengujian</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 5%;">No</th>
        <th style="width: 32%;">Nama Mahasiswa</th>
        <th style="width: 18%;">NIM</th>
        <th style="width: 20%;">Peran Utama</th>
        <th style="width: 25%;">Fokus Kontribusi</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align: center;">1</td>
        <td><b>Muh Naufal Rabbani Marun</b></td>
        <td>102062400038</td>
        <td>Tech Lead / Backend</td>
        <td>CRUD Ruang, migrasi PostgreSQL, enforcement aturan bisnis</td>
      </tr>
      <tr>
        <td style="text-align: center;">2</td>
        <td><b>Allfridho Prima Anjaynata Saragi</b></td>
        <td>102062400045</td>
        <td>DevOps Engineer</td>
        <td>Pipeline Jenkins 6 stage, Webhook Ngrok, <b>Auto-Rollback K10</b></td>
      </tr>
      <tr>
        <td style="text-align: center;">3</td>
        <td><b>Andika Candra Kurniawan</b></td>
        <td>102062400129</td>
        <td>Container & QA Engineer</td>
        <td>Multi-stage Dockerfile, compose.yaml, 7 Jest test, Laporan PDF</td>
      </tr>
    </tbody>
  </table>

  <table>
    <tr>
      <td style="width: 25%;"><b>Repository GitHub</b></td>
      <td style="width: 75%;"><a href="https://github.com/allfridhosaragii/test-komputasi" style="color: #0f766e; text-decoration: none;">https://github.com/allfridhosaragii/test-komputasi</a></td>
    </tr>
    <tr>
      <td><b>URL Jenkins via Ngrok</b></td>
      <td><code style="color: #0f766e;">https://ruangkita-jenkins-kelompok1.ngrok-free.app</code></td>
    </tr>
    <tr>
      <td><b>Akun Khusus Dosen/Asprak</b></td>
      <td>Username: <b>dosen_evaluator</b> | Password: <b>DosenDevOps2026!</b></td>
    </tr>
    <tr>
      <td><b>Registry Docker Hub</b></td>
      <td>Image: <code style="color: #0f766e;">allfridhosaragi/ruangkita:latest</code> dan tag nomor build</td>
    </tr>
  </table>

  <h2>2. Matriks Pemenuhan 4 Aturan Bisnis & Test Otomatis (100% Lolos)</h2>
  <p>Seluruh aturan bisnis inti RuangKita diverifikasi melalui 7 unit & feature automated test menggunakan Jest dan Supertest di dalam stage Test Docker container:</p>
  <table>
    <thead>
      <tr>
        <th>ID Test</th>
        <th>Komponen & Aturan Bisnis yang Diuji</th>
        <th>Input Uji / Skenario</th>
        <th>Ekspektasi Server</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>TEST-01</b></td>
        <td>Healthcheck Endpoint</td>
        <td><code>GET /health</code></td>
        <td>HTTP 200 OK & DB Connected</td>
        <td><span class="badge badge-emerald">PASS</span></td>
      </tr>
      <tr>
        <td><b>TEST-02</b></td>
        <td>Katalog Ruang Meeting</td>
        <td><code>GET /api/rooms</code></td>
        <td>List $\ge 3$ ruangan + kapasitas</td>
        <td><span class="badge badge-emerald">PASS</span></td>
      </tr>
      <tr>
        <td><b>TEST-03</b></td>
        <td><b>Aturan 1: Anti-Tumpang Tindih</b></td>
        <td>Booking 10:00-12:00 saat 09:00-11:00 terisi</td>
        <td>HTTP 400 SCHEDULE_OVERLAP</td>
        <td><span class="badge badge-emerald">PASS</span></td>
      </tr>
      <tr>
        <td><b>TEST-04</b></td>
        <td><b>Aturan 2: Batas Kapasitas Ruang</b></td>
        <td>Booking 12 orang di Ruang kapasitas 8</td>
        <td>HTTP 400 CAPACITY_EXCEEDED</td>
        <td><span class="badge badge-emerald">PASS</span></td>
      </tr>
      <tr>
        <td><b>TEST-05</b></td>
        <td><b>Aturan 3: Jam Kerja (08-21) & Durasi</b></td>
        <td>Booking jam 06:00 subuh atau durasi 9 jam</td>
        <td>HTTP 400 OUTSIDE_OPERATING_HOURS</td>
        <td><span class="badge badge-emerald">PASS</span></td>
      </tr>
      <tr>
        <td><b>TEST-06</b></td>
        <td><b>Aturan 4A: Denda 50% jika &lt; 2 Jam</b></td>
        <td>Batal booking 1 jam sebelum jadwal mulai</td>
        <td>HTTP 200 & Denda 50% diterapkan</td>
        <td><span class="badge badge-emerald">PASS</span></td>
      </tr>
      <tr>
        <td><b>TEST-07</b></td>
        <td><b>Aturan 4B: Bebas Denda jika $\ge$ 2 Jam</b></td>
        <td>Batal booking 5 jam sebelum jadwal mulai</td>
        <td>HTTP 200 & Bebas denda (Rp 0)</td>
        <td><span class="badge badge-emerald">PASS</span></td>
      </tr>
    </tbody>
  </table>

  <div class="evidence-box no-break">
    <img src="{img_test}" alt="Test Passing">
    <div class="evidence-caption">Gambar 1: Hasil Eksekusi Jest Test Suite — 7 Test Passed (100% Sukses) di Dalam Kontainer Test</div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== HALAMAN 2 ==================== -->
  <h2>3. Arsitektur Jaringan Kontainer & Penjelasan Desain</h2>
  <p>Sistem dirancang mengacu pada 8 pedoman teknis Modul Praktikum Komputasi Awan:</p>
  <ul>
    <li><b>Multi-Stage Dockerfile</b>: Memisahkan stage <code>base</code>, stage <code>test</code> (quality gate tanpa ketergantungan host), dan stage <code>runner</code> (hanya memuat file produksi serta dijalankan dengan user non-root <code>ruangkita</code>).</li>
    <li><b>Isolasi Jaringan Internal (<code>internal: true</code>)</b>: Service database PostgreSQL berada di jaringan <code>ruangkita_backend_net</code> yang diisolasi penuh dari jaringan eksternal. Hanya service <code>app</code> yang terhubung ke jaringan publik <code>ruangkita_public_net</code> untuk menerima traffic HTTP port 8000.</li>
    <li><b>Persistensi Data & Healthcheck Dependensi</b>: Volume <code>ruangkita_postgres_data</code> menjamin data reservasi tidak terhapus saat redeploy. Service <code>app</code> menggunakan <code>depends_on</code> dengan <code>condition: service_healthy</code> agar web baru menyala setelah database siap menerima query.</li>
  </ul>

  <div class="evidence-box no-break">
    <img src="{img_ps}" alt="Docker Compose PS">
    <div class="evidence-caption">Gambar 2: Output `docker compose ps` — Service App & Database Berstatus Healthy & Network Terisolasi</div>
  </div>

  <div class="evidence-box no-break">
    <img src="{img_health}" alt="Health Endpoint">
    <div class="evidence-caption">Gambar 3: Respons Endpoint `GET /health` — Status 200 OK & Database Connected</div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== HALAMAN 3 ==================== -->
  <h2>4. Alur Otomasi Pipeline Jenkins (6 Stages Berurutan)</h2>
  <p>Pipeline berjalan otomatis setiap kali ada event merge ke branch <code>main</code> yang dipicu oleh <b>GitHub Webhook via Ngrok</b>:</p>
  <div class="code-block">
Checkout ──> Test (Quality Gate) ──> Build Image ──> Push Image ──> Deploy (Compose) ──> Smoke Test
 (Git SCM)    (docker build test)     (Tag BUILD & latest) (Docker Hub PAT)     (Auto-Rollback Prep)   (curl /health == 200)
  </div>

  <div class="evidence-box no-break">
    <img src="{img_stage}" alt="Jenkins Stage View">
    <div class="evidence-caption">Gambar 4: Jenkins Stage View — 6 Stage Berurutan Berhasil Tereksekusi Hijau (Duration: 41s)</div>
  </div>

  <h2>5. Bukti Pengujian Quality Gate (Uji Gagal-Pulih)</h2>
  <p>Konsep Quality Gate dibuktikan dengan sengaja merilis commit yang melanggar aturan bisnis (menonaktifkan perlindungan overlap jadwal). Pipeline otomatis <b>BERHENTI MERAH</b> pada stage Test dan membatalkan tahap build/deploy sehingga server produksi tetap aman. Begitu kode diperbaiki, pipeline pulih hijau kembali:</p>

  <div class="evidence-box no-break">
    <img src="{img_qg}" alt="Quality Gate Test">
    <div class="evidence-caption">Gambar 5: Bukti Quality Gate — Build Merah Saat Test Gagal (Kiri) dan Pulih Hijau Pasca Perbaikan (Kanan)</div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== HALAMAN 4 ==================== -->
  <h2>6. Tantangan Khusus K10: Auto-Rollback ke Image Sebelumnya</h2>
  <p>Pada studi kasus RuangKita (K10), tantangan DevOps wajib adalah <b>Rollback otomatis ke image sebelumnya</b>:</p>
  <ul>
    <li>Pada stage <b>Deploy</b>, script mencatat tag image yang sedang berjalan ke dalam file <code>.previous_deployed_tag</code>.</li>
    <li>Aplikasi versi baru kemudian di-deploy menggunakan image tag terbaru.</li>
    <li>Pada stage <b>Smoke Test</b>, endpoint <code>GET /health</code> diuji. Jika respons bukan 200 (misalnya simulasi kegagalan server), pipeline gagal dan blok <code>post {{ failure {{ ... }} }}</code> <b>secara otomatis men-deploy ulang tag image sebelumnya yang stabil</b>.</li>
  </ul>

  <div class="evidence-box no-break">
    <img src="{img_rollback}" alt="Auto Rollback Log">
    <div class="evidence-caption">Gambar 6: Console Log Eksekusi Tantangan K10 — Auto-Rollback Berhasil Memulihkan Versi Stabil Tanpa Downtime</div>
  </div>

  <h2>7. Tampilan Aplikasi RuangKita (Web Dashboard)</h2>
  <div class="evidence-box no-break">
    <img src="{img_ui}" alt="Web UI Dashboard">
    <div class="evidence-caption">Gambar 7: Antarmuka Web Dashboard RuangKita — Live Health Status, Pemilihan Ruangan, dan Tabel Reservasi</div>
  </div>

  <h2>8. Kontribusi Anggota & Analisis Penyelesaian Kendala</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Anggota Tim</th>
        <th style="width: 35%;">Peran & Pull Request (PR)</th>
        <th style="width: 40%;">Kendala yang Dihadapi & Solusi Teknis</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Muh Naufal R. M.</b></td>
        <td>Tech Lead (PR #1: <code>feature/backend-core</code>)</td>
        <td><b>Kendala:</b> Menghitung denda dinamis pembatalan booking.<br><b>Solusi:</b> Validasi selisih jam server terhadap waktu reservasi ($\Delta t &lt; 2$ jam $\rightarrow$ denda 50%).</td>
      </tr>
      <tr>
        <td><b>Allfridho Prima A. S.</b></td>
        <td>DevOps Engineer (PR #3: <code>feature/devops-pipeline</code>)</td>
        <td><b>Kendala:</b> Auto-rollback gagal jika tag image tidak tercatat sebelum deploy.<br><b>Solusi:</b> Menggunakan <code>docker inspect</code> untuk merekam tag aktif ke file cache sebelum redeploy.</td>
      </tr>
      <tr>
        <td><b>Andika Candra K.</b></td>
        <td>Container & QA (PR #2: <code>feature/container-and-tests</code>)</td>
        <td><b>Kendala:</b> Resolusi <code>localhost</code> pada Alpine Linux menunjuk ke IPv6 <code>::1</code>.<br><b>Solusi:</b> Mengikat healthcheck secara eksplisit ke IPv4 <code>127.0.0.1:8000/health</code>.</td>
      </tr>
    </tbody>
  </table>

</body>
</html>
"""

    with open("evidence/report_preview.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{os.path.abspath('evidence/report_preview.html')}")
        await page.wait_for_timeout(1000)

        pdf_path = "Kelompok1_RuangKita_TugasDevOps.pdf"
        await page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"}
        )
        await browser.close()
        print(f"PDF Report generated successfully: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(generate_pdf())

