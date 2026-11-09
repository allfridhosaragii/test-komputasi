import concurrent.futures
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def run_deep_extreme_audit():
    print("=" * 80)
    print("🛡️  RUANGKITA — ULTRA-HARDCORE DEEP STRESS & BOUNDARY AUDIT SUITE v2.0")
    print("=" * 80)

    passes = []
    failures = []

    # Helper for unique target date to guarantee pristine isolated state
    unique_day_offset = 50 + int(time.time() * 1000) % 5000

    # -------------------------------------------------------------------------
    # SUITE 1: OPERATING HOURS & DURATION BOUNDARY TESTING (To the Exact Minute)
    # -------------------------------------------------------------------------
    print("\n[SUITE 1] Pengujian Batas Presisi Menit Jam Operasional (08.00 - 21.00) & Durasi (1-8 Jam)...")
    target_date = (datetime.now() + timedelta(days=unique_day_offset)).strftime("%Y-%m-%d")

    # 1.A Exact 08:00:00 - 09:00:00 (1 hour exact, valid)
    r = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Boundary Test 1A",
        "participants": 4,
        "start_time": f"{target_date}T08:00:00",
        "end_time": f"{target_date}T09:00:00"
    })
    if r.status_code == 201:
        passes.append("1.A Batas Tepat Jam Buka (08.00-09.00, durasi 1 jam) DITERIMA")
    else:
        failures.append(f"1.A GAGAL: 08.00-09.00 ditolak ({r.status_code}): {r.text}")

    # 1.B Exact 20:00:00 - 21:00:00 (1 hour exact, valid closing edge)
    r = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Boundary Test 1B",
        "participants": 4,
        "start_time": f"{target_date}T20:00:00",
        "end_time": f"{target_date}T21:00:00"
    })
    if r.status_code == 201:
        passes.append("1.B Batas Tepat Jam Tutup (20.00-21.00, durasi 1 jam) DITERIMA")
    else:
        failures.append(f"1.B GAGAL: 20.00-21.00 ditolak ({r.status_code}): {r.text}")

    # 1.C 07:59:00 (1 menit sebelum jam buka) -> MUST REJECT
    r = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Boundary Test 1C Early",
        "participants": 4,
        "start_time": f"{target_date}T07:59:00",
        "end_time": f"{target_date}T09:00:00"
    })
    if r.status_code == 400:
        passes.append("1.C Booking 1 menit sebelum jam buka (07.59) DITOLAK")
    else:
        failures.append(f"1.C GAGAL: 07.59 lolos ({r.status_code})")

    # 1.D 21:01:00 (1 menit lewat jam tutup) -> MUST REJECT
    r = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Boundary Test 1D Late",
        "participants": 4,
        "start_time": f"{target_date}T20:01:00",
        "end_time": f"{target_date}T21:01:00"
    })
    if r.status_code == 400:
        passes.append("1.D Booking lewat batas tutup (21.01) DITOLAK")
    else:
        failures.append(f"1.D GAGAL: 21.01 lolos ({r.status_code})")

    # 1.E Durasi 59 menit (< 1 jam) -> MUST REJECT
    r = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Boundary Test 1E Short",
        "participants": 4,
        "start_time": f"{target_date}T10:00:00",
        "end_time": f"{target_date}T10:59:00"
    })
    if r.status_code == 400:
        passes.append("1.E Durasi 59 Menit (< 1 jam minimal) DITOLAK")
    else:
        failures.append(f"1.E GAGAL: Durasi < 1 jam lolos ({r.status_code})")

    # 1.F Durasi 8 jam 1 menit (> 8 jam) -> MUST REJECT
    r = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Boundary Test 1F Long",
        "participants": 4,
        "start_time": f"{target_date}T10:00:00",
        "end_time": f"{target_date}T18:01:00"
    })
    if r.status_code == 400:
        passes.append("1.F Durasi 8 Jam 1 Menit (> 8 jam maksimal) DITOLAK")
    else:
        failures.append(f"1.F GAGAL: Durasi > 8 jam lolos ({r.status_code})")

    # -------------------------------------------------------------------------
    # SUITE 2: CONTIGUOUS BACK-TO-BACK BOOKING (Touching Boundary Zero Overlap)
    # -------------------------------------------------------------------------
    print("\n[SUITE 2] Pengujian Slot Berdampingan Tepat (Back-to-Back Contiguous Slots)...")
    date_suite2 = (datetime.now() + timedelta(days=unique_day_offset + 1)).strftime("%Y-%m-%d")

    # Booking Slot A: 11:00 - 13:00
    r_a = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Slot A Company",
        "participants": 3,
        "start_time": f"{date_suite2}T11:00:00",
        "end_time": f"{date_suite2}T13:00:00"
    })
    # Booking Slot B: 13:00 - 15:00 (Starts exactly when Slot A ends)
    r_b = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 3,
        "customer_name": "Slot B Company",
        "participants": 3,
        "start_time": f"{date_suite2}T13:00:00",
        "end_time": f"{date_suite2}T15:00:00"
    })
    if r_a.status_code == 201 and r_b.status_code == 201:
        passes.append("2. Slot Berurutan Tepat (11.00-13.00 & 13.00-15.00) Diterima Tanpa False Overlap")
    else:
        failures.append(f"2. GAGAL: Slot contiguous ditolak keliru! (Slot A: {r_a.status_code}, Slot B: {r_b.status_code})")

    # -------------------------------------------------------------------------
    # SUITE 3: ROOM CAPACITY BOUNDARY VERIFICATION
    # -------------------------------------------------------------------------
    print("\n[SUITE 3] Pengujian Batas Kapasitas Ruangan (Exact Max vs Max + 1 vs 0)...")
    date_suite3 = (datetime.now() + timedelta(days=unique_day_offset + 2)).strftime("%Y-%m-%d")

    # Room 1 capacity = 8
    # 3.A Exact 8 participants -> SUCCEED
    r_cap_exact = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Exact 8 People",
        "participants": 8,
        "start_time": f"{date_suite3}T10:00:00",
        "end_time": f"{date_suite3}T12:00:00"
    })
    # 3.B 9 participants (8 + 1) -> REJECT
    r_cap_over = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Over 9 People",
        "participants": 9,
        "start_time": f"{date_suite3}T13:00:00",
        "end_time": f"{date_suite3}T15:00:00"
    })
    # 3.C 0 participants -> REJECT
    r_cap_zero = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Zero People",
        "participants": 0,
        "start_time": f"{date_suite3}T16:00:00",
        "end_time": f"{date_suite3}T17:00:00"
    })

    if r_cap_exact.status_code == 201 and r_cap_over.status_code == 400 and r_cap_zero.status_code == 400:
        passes.append("3. Batas Kapasitas Presisi (Kapasitas Pas: 201 | Lebih 1: 400 | Nol: 400) Sempurna")
    else:
        failures.append(f"3. GAGAL: Batas kapasitas salah! (Pas: {r_cap_exact.status_code}, Lebih: {r_cap_over.status_code}, Nol: {r_cap_zero.status_code})")

    # -------------------------------------------------------------------------
    # SUITE 4: CANCELLATION & REPLAY ATTACK (DOUBLE CANCELLATION)
    # -------------------------------------------------------------------------
    print("\n[SUITE 4] Pengujian Pembatalan Berulang (Double Cancellation Replay Attack)...")
    date_suite4 = (datetime.now() + timedelta(days=unique_day_offset + 3)).strftime("%Y-%m-%d")

    # Create a booking
    r_new_b = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Replay Target",
        "participants": 2,
        "start_time": f"{date_suite4}T10:00:00",
        "end_time": f"{date_suite4}T12:00:00"
    })
    booking_id = r_new_b.json()["data"]["id"]

    # First cancel -> 200
    r_cancel_1 = requests.post(f"{BASE_URL}/api/bookings/{booking_id}/cancel", json={})
    # Second cancel (Replay) -> MUST REJECT (400)
    r_cancel_2 = requests.post(f"{BASE_URL}/api/bookings/{booking_id}/cancel", json={})

    if r_cancel_1.status_code == 200 and r_cancel_2.status_code == 400:
        passes.append("4. Proteksi Double-Cancellation (Replay Attack Ditolak 400) Aman")
    else:
        failures.append(f"4. GAGAL: Replay pembatalan bermasalah! (Cancel 1: {r_cancel_1.status_code}, Cancel 2: {r_cancel_2.status_code})")

    # -------------------------------------------------------------------------
    # SUITE 5: CANCELLATION FEE STRICT TIME BOUNDARY (2 Hours Cutoff)
    # -------------------------------------------------------------------------
    print("\n[SUITE 5] Pengujian Presisi Denda Pembatalan (Toleransi 2 Jam Sebelum Mulai)...")
    date_suite5 = "2027-01-10"

    # Booking: 10:00:00 - 12:00:00
    r_b_fee = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Fee Boundary Target",
        "participants": 2,
        "start_time": f"{date_suite5}T10:00:00",
        "end_time": f"{date_suite5}T12:00:00"
    })
    b_fee_id = r_b_fee.json()["data"]["id"]

    # Cancel at 08:00:00 (Exactly 2.0 hours before start) -> >= 2 hours => NO FEE (0)
    # Note: diffHours = 2.0, condition is diffHours < 2 for fee. So 2.0 has NO fee.
    r_c_free = requests.post(f"{BASE_URL}/api/bookings/{b_fee_id}/cancel", json={
        "cancellation_time": f"{date_suite5}T08:00:00"
    })
    res_free_data = r_c_free.json()

    # Create another booking for < 2 hr test
    r_b_fee2 = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Fee Boundary Target 2",
        "participants": 2,
        "start_time": f"{date_suite5}T14:00:00",
        "end_time": f"{date_suite5}T16:00:00"
    })
    b_fee2_id = r_b_fee2.json()["data"]["id"]

    # Cancel at 12:01:00 (1 hour 59 mins before start -> < 2 hours) => FEE 50%
    r_c_paid = requests.post(f"{BASE_URL}/api/bookings/{b_fee2_id}/cancel", json={
        "cancellation_time": f"{date_suite5}T12:01:00"
    })
    res_paid_data = r_c_paid.json()

    free_ok = (res_free_data.get("cancellation_details", {}).get("fee_applied") == False)
    paid_ok = (res_paid_data.get("cancellation_details", {}).get("fee_applied") == True)

    if free_ok and paid_ok:
        passes.append("5. Presisi Denda Pembatalan (Tepat 2 Jam: Bebas Denda | 1 Jam 59 Menit: Kena Denda 50%) Sempurna")
    else:
        failures.append(f"5. GAGAL: Presisi denda salah! (Bebas: {free_ok}, Kena: {paid_ok})")

    # -------------------------------------------------------------------------
    # SUITE 6: ROOM CATALOG CRUD ROBUSTNESS & MALFORMED PAYLOADS
    # -------------------------------------------------------------------------
    print("\n[SUITE 6] Pengujian CRUD Katalog Ruangan & Sanitasi Payload...")

    # 6.A Missing fields
    r_crud_bad1 = requests.post(f"{BASE_URL}/api/rooms", json={"name": "Incomplete Room"})
    # 6.B Negative price
    r_crud_bad2 = requests.post(f"{BASE_URL}/api/rooms", json={"name": "Bad Price", "capacity": 10, "facilities": "All", "price_per_hour": -50000})
    # 6.C Float capacity
    r_crud_bad3 = requests.post(f"{BASE_URL}/api/rooms", json={"name": "Float Cap", "capacity": 10.5, "facilities": "All", "price_per_hour": 50000})
    # 6.D Delete non-existent
    r_crud_bad4 = requests.delete(f"{BASE_URL}/api/rooms/99999999")

    if r_crud_bad1.status_code == 400 and r_crud_bad2.status_code == 400 and r_crud_bad3.status_code == 400 and r_crud_bad4.status_code == 404:
        passes.append("6. CRUD Sanitasi Ekstrem (Field Kurang: 400 | Harga Negatif: 400 | Kapasitas Pecahan: 400 | Delete 404) Aman")
    else:
        failures.append(f"6. GAGAL: Validasi CRUD room tidak lengkap! ({r_crud_bad1.status_code}, {r_crud_bad2.status_code}, {r_crud_bad3.status_code}, {r_crud_bad4.status_code})")

    # -------------------------------------------------------------------------
    # SUITE 7: BURST CONCURRENCY LOAD (50 PARALLEL CLIENTS)
    # -------------------------------------------------------------------------
    print("\n[SUITE 7] Pengujian Beban Puncak 50 Klien Konkuren Simultan (Burst Load)...")
    date_burst = (datetime.now() + timedelta(days=unique_day_offset + 5)).strftime("%Y-%m-%d")

    def burst_worker(idx):
        # Even indices do queries, odd indices try booking room 1 on different non-overlapping slots
        if idx % 2 == 0:
            res = requests.get(f"{BASE_URL}/api/rooms/availability?date={date_burst}", timeout=5)
            return res.status_code
        else:
            # Different hours to avoid internal conflict
            hour = 8 + (idx % 12)
            res = requests.post(f"{BASE_URL}/api/bookings", json={
                "room_id": 2,
                "customer_name": f"Burst Client {idx}",
                "participants": 4,
                "start_time": f"{date_burst}T{hour:02d}:00:00",
                "end_time": f"{date_burst}T{hour+1:02d}:00:00"
            }, timeout=5)
            return res.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        burst_futures = [executor.submit(burst_worker, i) for i in range(50)]
        burst_results = [f.result() for f in burst_futures]

    error_500s = [code for code in burst_results if code >= 500]
    if len(error_500s) == 0:
        passes.append("7. Beban Puncak 50 Klien Konkuren Sukses 100% Tanpa Crash / 500 Server Error")
    else:
        failures.append(f"7. GAGAL: Terjadi {len(error_500s)} internal server error 500 pada beban puncak!")

    # -------------------------------------------------------------------------
    # SUMMARY REPORT
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"📊 HASIL ULTRA-HARDCORE AUDIT: {len(passes)} LOLOS | {len(failures)} GAGAL")
    print("=" * 80)
    for p in passes:
        print(f"  ✅ {p}")
    for f in failures:
        print(f"  ❌ {f}")

    if len(failures) == 0:
        print("\n🎉 SISTEM 100% AMAN, KOKOH, & MEMENUHI SELURUH STANDAR DEVOPS LEVEL TINGGI!")
        return 0
    else:
        print(f"\n⚠️  DITEMUKAN {len(failures)} MASALAH YANG PERLU DIPERBAIKI!")
        return len(failures)

if __name__ == "__main__":
    exit(run_deep_extreme_audit())