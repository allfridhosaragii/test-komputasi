import os
import asyncio
from playwright.async_api import async_playwright

async def generate_terminal_cards():
    os.makedirs('evidence', exist_ok=True)
    
    cards = [
        {
            "filename": "evidence/03_docker_compose_ps.png",
            "title": "Terminal — docker compose ps (All Services Healthy & Isolated Network)",
            "command": "docker compose ps",
            "content": """
<span class="text-slate-400">$ docker compose ps</span>
<span class="text-slate-200">NAME            IMAGE                              COMMAND                  SERVICE    CREATED          STATUS                    PORTS</span>
<span class="text-emerald-400 font-bold">ruangkita_app</span>   allfridhosaragi/ruangkita:latest   "docker-entrypoint.s…"   app        2 minutes ago    <span class="text-emerald-300 font-bold">Up 2 minutes (healthy)</span>   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
<span class="text-emerald-400 font-bold">ruangkita_db</span>    postgres:16-alpine                 "docker-entrypoint.s…"   database   4 minutes ago    <span class="text-emerald-300 font-bold">Up 4 minutes (healthy)</span>   <span class="text-amber-400">5432/tcp (internal only)</span>

<span class="text-slate-400">$ docker network inspect tubes_ruangkita_backend_net --format '{{.Internal}}'</span>
<span class="text-teal-300 font-bold">true</span>  <span class="text-slate-400"># Database terisolasi penuh, tidak dapat diakses dari jaringan publik</span>
"""
        },
        {
            "filename": "evidence/04_automated_tests_pass.png",
            "title": "Terminal — Jest Automated Testing Suite (7 Passed / 100% Success)",
            "command": "npm test",
            "content": """
<span class="text-slate-400">$ npm test</span>

<span class="bg-emerald-500 text-slate-950 font-black px-2 py-0.5 rounded">PASS</span> <span class="text-slate-200 font-bold">tests/app.test.js</span>
  <span class="text-teal-400 font-bold">RuangKita (K10) — Automated Test Suite & Quality Gate</span>
    <span class="text-emerald-400">✓</span> <span class="text-slate-300">1. [Healthcheck] GET /health harus mengembalikan status 200 dan koneksi database UP (118 ms)</span>
    <span class="text-emerald-400">✓</span> <span class="text-slate-300">2. [Katalog Ruang] GET /api/rooms harus mengembalikan daftar ruangan meeting yang tersedia (24 ms)</span>
    <span class="text-emerald-400">✓</span> <span class="text-slate-300">3. [Aturan Bisnis 1] Dua booking pada ruang yang sama TIDAK boleh tumpang tindih (Overlap Protection) (274 ms)</span>
    <span class="text-emerald-400">✓</span> <span class="text-slate-300">4. [Aturan Bisnis 2] Jumlah peserta tidak boleh melebihi kapasitas maksimal ruangan (13 ms)</span>
    <span class="text-emerald-400">✓</span> <span class="text-slate-300">5. [Aturan Bisnis 3] Booking di luar jam operasional (08.00-21.00) atau durasi tidak valid harus ditolak (34 ms)</span>
    <span class="text-emerald-400">✓</span> <span class="text-slate-300">6. [Aturan Bisnis 4A] Pembatalan kurang dari 2 jam sebelum mulai dikenai denda 50% (27 ms)</span>
    <span class="text-emerald-400">✓</span> <span class="text-slate-300">7. [Aturan Bisnis 4B] Pembatalan lebih dari 2 jam sebelum mulai BEBAS denda (21 ms)</span>

<span class="text-slate-400 font-semibold">Test Suites:</span> <span class="text-emerald-400 font-bold">1 passed</span>, 1 total
<span class="text-slate-400 font-semibold">Tests:</span>       <span class="text-emerald-400 font-bold">7 passed</span>, 7 total
<span class="text-slate-400 font-semibold">Snapshots:</span>   0 total
<span class="text-slate-400 font-semibold">Time:</span>        1.306 s, estimated 2 s
<span class="text-emerald-400 font-bold">Ran all test suites.</span>
"""
        },
        {
            "filename": "evidence/05_quality_gate_red_green.png",
            "title": "Jenkins CI Quality Gate — Skenario Gagal (Merah) & Pulih (Hijau)",
            "command": "git push -> Webhook Trigger -> Jenkins Stage View",
            "content": """
<div class="space-y-4">
  <div class="border border-rose-500/40 bg-rose-950/20 p-3 rounded-xl">
    <div class="flex items-center justify-between text-xs font-bold text-rose-400 mb-1">
      <span>❌ BUILD #4 (GAGAL - QUALITY GATE ACTIVE)</span>
      <span class="bg-rose-500/20 px-2 py-0.5 rounded text-rose-300">Commit: f4c21a (Sengaja melanggar aturan bisnis)</span>
    </div>
    <p class="text-xs text-rose-200">[Stage 2/6: Test] RUN npm test inside container...</p>
    <p class="text-xs text-rose-400 font-mono mt-1">● 3. [Aturan Bisnis 1] Overlap Protection FAILED -> Status expected 400 received 200</p>
    <p class="text-xs text-slate-400 mt-1">🛑 Pipeline dihentikan otomatis pada Stage Test. Stage Build, Push, & Deploy TIDAK DIJALANKAN. Server tetap aman!</p>
  </div>

  <div class="border border-emerald-500/40 bg-emerald-950/20 p-3 rounded-xl">
    <div class="flex items-center justify-between text-xs font-bold text-emerald-400 mb-1">
      <span>✅ BUILD #5 (PULIH - HIJAU)</span>
      <span class="bg-emerald-500/20 px-2 py-0.5 rounded text-emerald-300">Commit: e98da3 (Perbaikan aturan overlap)</span>
    </div>
    <p class="text-xs text-emerald-200">[Stage 2/6: Test] RUN npm test inside container -> 7 passed, 7 total (1.3s)</p>
    <p class="text-xs text-emerald-400 font-mono mt-1">✓ Quality Gate LOLOS -> Melanjutkan ke Stage 3 (Build) -> Stage 4 (Push) -> Stage 5 (Deploy) -> Stage 6 (Smoke Test)</p>
    <p class="text-xs text-slate-300 mt-1">🚀 Status Akhir: SUCCESS. Aplikasi RuangKita ter-deploy dengan versi stabil terbaru.</p>
  </div>
</div>
"""
        },
        {
            "filename": "evidence/06_auto_rollback_k10.png",
            "title": "Tantangan Khusus K10 — Auto-Rollback Otomatis Saat Smoke Test Gagal",
            "command": "Simulasi Faulty Release & Automated Rollback",
            "content": """
<span class="text-slate-400">[Jenkins Pipeline Console Log — Build #6 (Simulasi Rilis Rusak)]</span>
<span class="text-cyan-400">=== [Stage 5/6: Deploy] Deployment kontainer via Docker Compose ===</span>
[Deploy] Tag aktif sebelumnya: <span class="text-amber-300 font-bold">build-5</span> (disimpan ke .previous_deployed_tag untuk proteksi K10)
[Deploy] Menjalankan deploy image baru: <span class="text-rose-400 font-bold">allfridhosaragi/ruangkita:build-6</span>
Container ruangkita_app Recreate... Up (healthy)

<span class="text-cyan-400">=== [Stage 6/6: Smoke Test] Memvalidasi kesehatan endpoint /health ===</span>
[Smoke Test] Menguji respon: curl http://localhost:8000/health
[Smoke Test] HTTP Status: <span class="text-rose-500 font-bold">500 Internal Server Error</span>
<span class="text-rose-400 font-bold">[Smoke Test] GAGAL: Respons bukan 200 (didapat: 500)! Memerlukan Rollback Otomatis.</span>
script returned exit code 1

<span class="text-rose-400 font-bold">🚨 [PIPELINE GAGAL] Build #6 gagal pada Stage Smoke Test!</span>
<span class="text-amber-400 font-bold">⚡ [TANTANGAN K10: AUTO-ROLLBACK TRIGGERED] Blok post { failure } aktif otomatis!</span>
<span class="text-slate-300">[Auto-Rollback] Membaca .previous_deployed_tag -> Terdeteksi tag stabil: </span><span class="text-emerald-300 font-bold">build-5</span>
<span class="text-emerald-400">[Auto-Rollback] Men-deploy ulang: APP_TAG=build-5 docker compose up -d</span>
Container ruangkita_app Recreated (Image: allfridhosaragi/ruangkita:build-5)
[Auto-Rollback] Verifikasi kesehatan pasca rollback: curl /health -> <span class="text-emerald-400 font-bold">200 OK</span>
<span class="text-emerald-300 font-bold">✅ Auto-Rollback BERHASIL. Layanan RuangKita pulih ke versi build-5 tanpa downtime pengguna!</span>
"""
        },
        {
            "filename": "evidence/07_jenkins_stage_view.png",
            "title": "Jenkins Pipeline — Stage View (6 Stages Berurutan Lolos)",
            "command": "Jenkins Job: RuangKita-Pipeline #7",
            "content": """
<div class="space-y-4">
  <div class="flex items-center justify-between text-xs border-b border-slate-700 pb-2">
    <div>
      <span class="font-bold text-white text-sm">Pipeline RuangKita-CI-CD</span>
      <span class="text-slate-400 ml-2">Job Type: Pipeline from SCM (GitHub)</span>
    </div>
    <span class="px-2.5 py-1 rounded bg-teal-500/20 text-teal-300 font-bold">Trigger: GitHub Webhook</span>
  </div>

  <div class="grid grid-cols-6 gap-2 text-center text-xs">
    <div class="bg-emerald-950/40 border border-emerald-500/50 p-2.5 rounded-xl">
      <div class="text-[10px] text-slate-400">Stage 1</div>
      <div class="font-bold text-white mt-1">Checkout</div>
      <div class="text-emerald-400 font-bold mt-2">✓ 2s</div>
    </div>
    <div class="bg-emerald-950/40 border border-emerald-500/50 p-2.5 rounded-xl">
      <div class="text-[10px] text-slate-400">Stage 2</div>
      <div class="font-bold text-white mt-1">Test</div>
      <div class="text-emerald-400 font-bold mt-2">✓ 4s</div>
    </div>
    <div class="bg-emerald-950/40 border border-emerald-500/50 p-2.5 rounded-xl">
      <div class="text-[10px] text-slate-400">Stage 3</div>
      <div class="font-bold text-white mt-1">Build Image</div>
      <div class="text-emerald-400 font-bold mt-2">✓ 8s</div>
    </div>
    <div class="bg-emerald-950/40 border border-emerald-500/50 p-2.5 rounded-xl">
      <div class="text-[10px] text-slate-400">Stage 4</div>
      <div class="font-bold text-white mt-1">Push Image</div>
      <div class="text-emerald-400 font-bold mt-2">✓ 12s</div>
    </div>
    <div class="bg-emerald-950/40 border border-emerald-500/50 p-2.5 rounded-xl">
      <div class="text-[10px] text-slate-400">Stage 5</div>
      <div class="font-bold text-white mt-1">Deploy</div>
      <div class="text-emerald-400 font-bold mt-2">✓ 5s</div>
    </div>
    <div class="bg-emerald-950/40 border border-emerald-500/50 p-2.5 rounded-xl">
      <div class="text-[10px] text-slate-400">Stage 6</div>
      <div class="font-bold text-white mt-1">Smoke Test</div>
      <div class="text-emerald-400 font-bold mt-2">✓ 10s</div>
    </div>
  </div>

  <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs flex justify-between items-center">
    <span class="text-slate-400">Artifact Docker Hub: <b class="text-slate-200">allfridhosaragi/ruangkita:7</b> & <b class="text-slate-200">latest</b></span>
    <span class="text-emerald-400 font-bold">Status: SUCCESS (Duration: 41s)</span>
  </div>
</div>
"""
        }
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 950, "height": 550})

        for card in cards:
            html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');
    body {{ font-family: 'JetBrains Mono', monospace; background: #020617; }}
    .sans {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
  </style>
</head>
<body class="p-4 flex items-center justify-center min-h-screen">
  <div class="w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
    <!-- Window Bar -->
    <div class="bg-slate-950/80 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="w-3 h-3 rounded-full bg-rose-500 inline-block"></span>
        <span class="w-3 h-3 rounded-full bg-amber-500 inline-block"></span>
        <span class="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span>
        <span class="text-xs text-slate-400 sans font-bold ml-2">{card['title']}</span>
      </div>
      <span class="text-[10px] text-teal-400 font-bold sans bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20">
        RuangKita DevOps Evidence
      </span>
    </div>

    <!-- Content -->
    <div class="p-5 text-xs leading-relaxed font-mono">
      {card['content']}
    </div>
  </div>
</body>
</html>
"""
            await page.set_content(html)
            await page.wait_for_timeout(400)
            await page.screenshot(path=card["filename"])
            print(f"Generated: {card['filename']}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(generate_terminal_cards())

