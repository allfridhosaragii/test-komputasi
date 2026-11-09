import concurrent.futures
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_results_summary():
    print("=" * 75)
    print("🔥 MENJALANKAN EXTREME STRESS & HARD TESTING (BUG-HUNTING)")
    print("=" * 75)

    failures = []
    passes = []

    # -------------------------------------------------------------
    # EXTREME TEST 1: Concurrency / Race Condition Test
    # 20 simultaneous threads trying to book the exact same slot
    # Only 1 should succeed, 19 should be rejected!
    # -------------------------------------------------------------
    print("\n[UJI 1] Concurrency & Race Condition (20 Request Bersamaan pada Detik Sama)...")
    import time
    unique_days = 20 + int(time.time()) % 500
    target_date = (datetime.now() + timedelta(days=unique_days)).strftime("%Y-%m-%d")
    slot_start = f"{target_date}T10:00:00"
    slot_end = f"{target_date}T12:00:00"

    def book_slot(i):
        payload = {
            "room_id": 2,
            "customer_name": f"Concurrent User {i}",
            "participants": 5,
            "start_time": slot_start,
            "end_time": slot_end
        }
        try:
            res = requests.post(f"{BASE_URL}/api/bookings", json=payload, timeout=10)
            return res.status_code, res.json()
        except Exception as e:
            return 500, str(e)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(book_slot, i) for i in range(20)]
        results = [f.result() for f in futures]

    successes = [r for r in results if r[0] == 201]
    rejections = [r for r in results if r[0] == 400]

    print(f"      -> Sukses (201): {len(successes)}")
    print(f"      -> Ditolak (400): {len(rejections)}")

    if len(successes) == 1 and len(rejections) == 19:
        passes.append("UJI 1: Concurrency Race Condition Aman (Tidak Terjadi Double Booking)")
    else:
        failures.append(f"UJI 1 GAGAL: Terjadi Race Condition! {len(successes)} booking diterima untuk slot yang sama!")

    # -------------------------------------------------------------
    # EXTREME TEST 2: Cross-Day / Midnight Operating Hour Bypass Bug
    # Booking from 20:00 to 03:00 next day (duration 7 hours)
    # Must be REJECTED!
    # -------------------------------------------------------------
    print("\n[UJI 2] Midnight / Cross-Day Booking Bypass (20.00 malam ke 03.00 subuh)...")
    day1 = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    day2 = (datetime.now() + timedelta(days=16)).strftime("%Y-%m-%d")
    res_midnight = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Midnight Hacker",
        "participants": 4,
        "start_time": f"{day1}T20:00:00",
        "end_time": f"{day2}T03:00:00"
    })
    if res_midnight.status_code == 400:
        passes.append("UJI 2: Midnight / Cross-Day Booking Ditolak dengan Tepat")
    else:
        failures.append(f"UJI 2 GAGAL: Booking subuh/lintas hari lolos! (Status: {res_midnight.status_code})")

    # -------------------------------------------------------------
    # EXTREME TEST 3: Past Date Booking Bug
    # Booking for yesterday / year 2020
    # Must be REJECTED!
    # -------------------------------------------------------------
    print("\n[UJI 3] Past Date Booking (Mencoba booking di masa lampau)...")
    res_past = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Time Traveler",
        "participants": 4,
        "start_time": "2020-01-01T10:00:00",
        "end_time": "2020-01-01T12:00:00"
    })
    if res_past.status_code == 400:
        passes.append("UJI 3: Past Date Booking Ditolak dengan Tepat")
    else:
        failures.append(f"UJI 3 GAGAL: Booking masa lampau diterima! (Status: {res_past.status_code})")

    # -------------------------------------------------------------
    # EXTREME TEST 4: Fractional / Negative / Malformed Participants
    # -------------------------------------------------------------
    print("\n[UJI 4] Fuzzing Input Peserta (Float 3.5, Negatif -5, String 'abc')...")
    res_float = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Float User",
        "participants": 3.5,
        "start_time": f"{day1}T10:00:00",
        "end_time": f"{day1}T12:00:00"
    })
    res_neg = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "Negative User",
        "participants": -5,
        "start_time": f"{day1}T10:00:00",
        "end_time": f"{day1}T12:00:00"
    })
    res_str = requests.post(f"{BASE_URL}/api/bookings", json={
        "room_id": 1,
        "customer_name": "String User",
        "participants": "banyak",
        "start_time": f"{day1}T10:00:00",
        "end_time": f"{day1}T12:00:00"
    })
    if res_float.status_code == 400 and res_neg.status_code == 400 and res_str.status_code == 400:
        passes.append("UJI 4: Validasi Peserta Ekstrem (Float/Negatif/String) Ditolak")
    else:
        failures.append(f"UJI 4 GAGAL: Float/Negatif peserta lolos! (Float: {res_float.status_code}, Neg: {res_neg.status_code}, Str: {res_str.status_code})")

    # -------------------------------------------------------------
    # EXTREME TEST 5: SQL Injection & XSS Payload Injection
    # -------------------------------------------------------------
    print("\n[UJI 5] Security Injection Fuzzing (SQLi / XSS)...")
    sqli_payload = "'; DROP TABLE rooms; --"
    res_sqli = requests.post(f"{BASE_URL}/api/rooms", json={
        "name": sqli_payload,
        "capacity": 10,
        "facilities": "Safe",
        "price_per_hour": 100000
    })
    # Verify rooms table is still alive
    r_check = requests.get(f"{BASE_URL}/api/rooms")
    if r_check.status_code == 200 and len(r_check.json().get("data", [])) >= 3:
        passes.append("UJI 5: SQL Injection Terisolasi Aman & Parameterized")
    else:
        failures.append("UJI 5 GAGAL: Terjadi kerentanan SQL Injection!")

    # -------------------------------------------------------------
    # EXTREME TEST 6: Non-Integer URL Parameter Handling
    # GET /api/rooms/abc, POST /api/bookings/xyz/cancel
    # -------------------------------------------------------------
    print("\n[UJI 6] Non-Integer ID Parameter Sanitization (/api/rooms/abc)...")
    res_bad_id1 = requests.get(f"{BASE_URL}/api/rooms/abc")
    res_bad_id2 = requests.post(f"{BASE_URL}/api/bookings/xyz/cancel", json={})
    if res_bad_id1.status_code in [400, 404] and res_bad_id2.status_code in [400, 404]:
        passes.append("UJI 6: Non-Integer ID Ditangani dengan Bersih (Bukan 500 Server Crash)")
    else:
        failures.append(f"UJI 6 GAGAL: ID 'abc' menghasilkan server error! (Status: {res_bad_id1.status_code}, {res_bad_id2.status_code})")

    # -------------------------------------------------------------
    # EXTREME TEST 7: Availability Query Date Fuzzing
    # -------------------------------------------------------------
    print("\n[UJI 7] Date Query Fuzzing (/api/rooms/availability?date=NOT_A_DATE)...")
    res_bad_date = requests.get(f"{BASE_URL}/api/rooms/availability?date=INVALID_DATE_FORMAT")
    if res_bad_date.status_code == 400:
        passes.append("UJI 7: Date Query Parameter Tervalidasi Format YYYY-MM-DD")
    else:
        failures.append(f"UJI 7 GAGAL: Tanggal tidak valid mengembalikan status {res_bad_date.status_code} bukannya 400")

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print(f"HASIL EXTREME TESTING: {len(passes)} Lolos | {len(failures)} Masalah Ditemukan")
    print("=" * 75)
    for p in passes:
        print(f"  [PASS] {p}")
    for f in failures:
        print(f"  [FAIL] {f}")

    return len(failures)

if __name__ == "__main__":
    exit(test_results_summary())
