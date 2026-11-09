import sys
import json
import time
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def log_test(test_name, success, detail=""):
    mark = "✅ PASS" if success else "❌ FAIL"
    print(f"[{mark}] {test_name}")
    if detail:
        print(f"       Detail: {detail}")

def run_all_tests():
    print("=" * 70)
    print("🚀 MEMULAI AUDIT & PENGUJIAN MENYELURUH SISTEM RUANGKITA (K10)")
    print(f"📍 Target Server: {BASE_URL}")
    print(f"🕒 Waktu Mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    total_tests = 0
    passed_tests = 0

    # -------------------------------------------------------------
    # 1. Healthcheck Endpoint
    # -------------------------------------------------------------
    total_tests += 1
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        data = r.json()
        ok = r.status_code == 200 and data.get("status") == "UP" and data.get("database", {}).get("status") == "CONNECTED"
        log_test("1. Endpoint GET /health (Status 200 OK & Database Connected)", ok, f"HTTP {r.status_code}, Status: {data.get('status')}, DB: {data.get('database', {}).get('status')}")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("1. Endpoint GET /health", False, str(e))

    # -------------------------------------------------------------
    # 2. CRUD Ruangan: GET /api/rooms
    # -------------------------------------------------------------
    total_tests += 1
    try:
        r = requests.get(f"{BASE_URL}/api/rooms", timeout=5)
        data = r.json()
        rooms = data.get("data", [])
        ok = r.status_code == 200 and len(rooms) >= 3
        log_test("2. CRUD Ruang: GET /api/rooms (Memuat Ruangan Default)", ok, f"Ditemukan {len(rooms)} ruangan terdaftar")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("2. CRUD Ruang: GET /api/rooms", False, str(e))

    # -------------------------------------------------------------
    # 3. CRUD Ruangan: POST, PUT, DELETE Ruang
    # -------------------------------------------------------------
    total_tests += 1
    created_room_id = None
    try:
        # POST
        payload = {
            "name": "Ruang Inovasi Delta (Uji Otomatis)",
            "capacity": 10,
            "facilities": "Smartboard, 4K Display, High Speed WiFi",
            "price_per_hour": 85000
        }
        r_post = requests.post(f"{BASE_URL}/api/rooms", json=payload, timeout=5)
        d_post = r_post.json()
        created_room_id = d_post.get("data", {}).get("id")

        # PUT
        r_put = requests.put(f"{BASE_URL}/api/rooms/{created_room_id}", json={"price_per_hour": 95000}, timeout=5)

        # DELETE
        r_del = requests.delete(f"{BASE_URL}/api/rooms/{created_room_id}", timeout=5)

        ok = r_post.status_code == 201 and r_put.status_code == 200 and r_del.status_code == 200
        log_test("3. CRUD Ruang: Tambah (POST), Ubah (PUT), Hapus (DELETE)", ok, f"Ruang ID {created_room_id} berhasil dibuat, diupdate, dan dihapus")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("3. CRUD Ruang (POST/PUT/DELETE)", False, str(e))

    # -------------------------------------------------------------
    # 4. Cek Ketersediaan per Tanggal: GET /api/rooms/availability
    # -------------------------------------------------------------
    total_tests += 1
    tomorrow_str = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    try:
        r = requests.get(f"{BASE_URL}/api/rooms/availability?date={tomorrow_str}", timeout=5)
        data = r.json()
        ok = r.status_code == 200 and data.get("success") == True and len(data.get("data", [])) >= 3
        log_test(f"4. Cek Ketersediaan Ruangan per Tanggal ({tomorrow_str})", ok, f"Berhasil memuat slot ketersediaan untuk {len(data.get('data', []))} ruangan")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("4. Cek Ketersediaan Ruang", False, str(e))

    # -------------------------------------------------------------
    # 5. Aturan Bisnis 1: Anti-Tumpang Tindih (Overlap Protection)
    # -------------------------------------------------------------
    total_tests += 1
    booking1_id = None
    try:
        # Booking valid: Ruang 1 jam 09.00 - 11.00
        start1 = f"{tomorrow_str}T09:00:00"
        end1 = f"{tomorrow_str}T11:00:00"
        r1 = requests.post(f"{BASE_URL}/api/bookings", json={
            "room_id": 1,
            "customer_name": "PT Sinergi Mandiri",
            "participants": 6,
            "start_time": start1,
            "end_time": end1
        }, timeout=5)
        booking1_id = r1.json().get("data", {}).get("id")

        # Booking bentrok: Ruang 1 jam 10.00 - 12.00 (irisan jam 10.00-11.00)
        start2 = f"{tomorrow_str}T10:00:00"
        end2 = f"{tomorrow_str}T12:00:00"
        r2 = requests.post(f"{BASE_URL}/api/bookings", json={
            "room_id": 1,
            "customer_name": "PT Penantang Bentrok",
            "participants": 4,
            "start_time": start2,
            "end_time": end2
        }, timeout=5)
        d2 = r2.json()

        ok = r1.status_code == 201 and r2.status_code == 400 and d2.get("error_code") == "SCHEDULE_OVERLAP"
        log_test("5. Aturan Bisnis 1: Anti-Tumpang Tindih (Overlap Protection)", ok, f"Booking 1 diterima (ID: {booking1_id}), Booking 2 bentrok ditolak dengan kode: {d2.get('error_code')}")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("5. Aturan Bisnis 1: Overlap Protection", False, str(e))

    # -------------------------------------------------------------
    # 6. Aturan Bisnis 2: Batas Kapasitas Ruangan
    # -------------------------------------------------------------
    total_tests += 1
    try:
        # Ruang 1 kapasitas 8 orang. Coba pesan dengan 16 orang
        r_cap = requests.post(f"{BASE_URL}/api/bookings", json={
            "room_id": 1,
            "customer_name": "Rombongan Besar",
            "participants": 16,
            "start_time": f"{tomorrow_str}T13:00:00",
            "end_time": f"{tomorrow_str}T15:00:00"
        }, timeout=5)
        d_cap = r_cap.json()
        ok = r_cap.status_code == 400 and d_cap.get("error_code") == "CAPACITY_EXCEEDED"
        log_test("6. Aturan Bisnis 2: Batas Kapasitas Ruangan", ok, f"Peserta 16 > Kapasitas 8 ditolak dengan pesan: '{d_cap.get('message')}'")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("6. Aturan Bisnis 2: Batas Kapasitas", False, str(e))

    # -------------------------------------------------------------
    # 7. Aturan Bisnis 3: Jam Operasional & Durasi 1-8 Jam
    # -------------------------------------------------------------
    total_tests += 1
    try:
        # A: Jam 06.00 subuh (Di luar jam 08.00-21.00)
        r_time = requests.post(f"{BASE_URL}/api/bookings", json={
            "room_id": 1,
            "customer_name": "Subuh Meeting",
            "participants": 4,
            "start_time": f"{tomorrow_str}T06:00:00",
            "end_time": f"{tomorrow_str}T08:00:00"
        }, timeout=5)

        # B: Durasi 9 jam (Di luar batas 1-8 jam)
        r_dur = requests.post(f"{BASE_URL}/api/bookings", json={
            "room_id": 1,
            "customer_name": "Overtime Session",
            "participants": 4,
            "start_time": f"{tomorrow_str}T09:00:00",
            "end_time": f"{tomorrow_str}T18:30:00"
        }, timeout=5)

        ok = r_time.status_code == 400 and r_time.json().get("error_code") == "OUTSIDE_OPERATING_HOURS" and \
             r_dur.status_code == 400 and r_dur.json().get("error_code") == "INVALID_DURATION"
        log_test("7. Aturan Bisnis 3: Jam Operasional 08.00-21.00 & Durasi 1-8 Jam", ok, "Jam subuh (06:00) & durasi 9.5 jam keduanya ditolak server")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("7. Aturan Bisnis 3: Operasional & Durasi", False, str(e))

    # -------------------------------------------------------------
    # 8. Aturan Bisnis 4: Denda Pembatalan 50% (< 2 Jam)
    # -------------------------------------------------------------
    total_tests += 1
    try:
        # Buat booking Ruang 1 jam 15.00 - 17.00 (Tarif 2 jam x 75.000 = 150.000)
        r_book = requests.post(f"{BASE_URL}/api/bookings", json={
            "room_id": 1,
            "customer_name": "Klien Uji Batal Denda",
            "participants": 4,
            "start_time": f"{tomorrow_str}T15:00:00",
            "end_time": f"{tomorrow_str}T17:00:00"
        }, timeout=5)
        b_id = r_book.json().get("data", {}).get("id")

        # Batalkan pada jam 14.00 (Hanya 1 jam sebelum mulai -> < 2 jam)
        r_cancel = requests.post(f"{BASE_URL}/api/bookings/{b_id}/cancel", json={
            "cancellation_time": f"{tomorrow_str}T14:00:00"
        }, timeout=5)
        d_cancel = r_cancel.json()
        fee = d_cancel.get("cancellation_details", {}).get("fee_amount")
        fee_applied = d_cancel.get("cancellation_details", {}).get("fee_applied")

        ok = r_cancel.status_code == 200 and fee_applied == True and fee == 75000
        log_test("8. Aturan Bisnis 4A: Denda Pembatalan 50% jika < 2 Jam Sebelum Mulai", ok, f"Total Rp 150.000 -> Denda dikenakan: Rp {fee:,.0f} (Status: CANCELLED)")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("8. Aturan Bisnis 4A: Denda 50%", False, str(e))

    # -------------------------------------------------------------
    # 9. Aturan Bisnis 4B: Bebas Denda (>= 2 Jam)
    # -------------------------------------------------------------
    total_tests += 1
    try:
        r_book2 = requests.post(f"{BASE_URL}/api/bookings", json={
            "room_id": 2,
            "customer_name": "Klien Disiplin",
            "participants": 8,
            "start_time": f"{tomorrow_str}T18:00:00",
            "end_time": f"{tomorrow_str}T20:00:00"
        }, timeout=5)
        b_id2 = r_book2.json().get("data", {}).get("id")

        # Batalkan pada jam 10.00 (8 jam sebelum mulai -> > 2 jam)
        r_cancel2 = requests.post(f"{BASE_URL}/api/bookings/{b_id2}/cancel", json={
            "cancellation_time": f"{tomorrow_str}T10:00:00"
        }, timeout=5)
        d_cancel2 = r_cancel2.json()
        fee2 = d_cancel2.get("cancellation_details", {}).get("fee_amount")
        fee_applied2 = d_cancel2.get("cancellation_details", {}).get("fee_applied")

        ok = r_cancel2.status_code == 200 and fee_applied2 == False and fee2 == 0
        log_test("9. Aturan Bisnis 4B: Pembatalan Bebas Denda jika >= 2 Jam", ok, f"Dibatalkan 8 jam sebelum mulai -> Denda: Rp {fee2:,.0f}")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("9. Aturan Bisnis 4B: Bebas Denda", False, str(e))

    # -------------------------------------------------------------
    # 10. Kalender Pemakaian Ruang: GET /api/bookings/calendar
    # -------------------------------------------------------------
    total_tests += 1
    try:
        r_cal = requests.get(f"{BASE_URL}/api/bookings/calendar", timeout=5)
        d_cal = r_cal.json()
        ok = r_cal.status_code == 200 and d_cal.get("success") == True and isinstance(d_cal.get("data"), list)
        log_test("10. Kalender Pemakaian Ruangan: GET /api/bookings/calendar", ok, f"Memuat {len(d_cal.get('data', []))} reservasi aktif")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("10. Kalender Pemakaian Ruang", False, str(e))

    # -------------------------------------------------------------
    # 11. Web UI Dashboard: GET /
    # -------------------------------------------------------------
    total_tests += 1
    try:
        r_ui = requests.get(f"{BASE_URL}/", timeout=5)
        ok = r_ui.status_code == 200 and "RuangKita" in r_ui.text and "K10" in r_ui.text
        log_test("11. Web Dashboard Frontend: GET /", ok, f"HTTP {r_ui.status_code}, memuat dokumen HTML RuangKita Dashboard")
        if ok: passed_tests += 1
    except Exception as e:
        log_test("11. Web Dashboard Frontend", False, str(e))

    print("=" * 70)
    print(f"📊 HASIL AKHIR: {passed_tests} DARI {total_tests} PENGUJIAN LOLOS ({passed_tests/total_tests*100:.1f}%)")
    print("=" * 70)

    if passed_tests == total_tests:
        print("🎉 SELURUH FITUR & ATURAN BISNIS RUANGKITA BERFUNGSI 100% SEMPURNA!")
        return 0
    else:
        print("⚠️ Terdapat beberapa pengujian yang gagal.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
