process.env.NODE_ENV = 'test';
const request = require('supertest');
const app = require('../src/app');
const { inMemoryStore } = require('../src/config/db');

describe('RuangKita (K10) — Automated Test Suite & Quality Gate', () => {

  beforeEach(() => {
    // Reset bookings before each test
    inMemoryStore.bookings = [];
    inMemoryStore.bookingIdCounter = 1;
  });

  // TEST 1: Endpoint GET /health
  test('1. [Healthcheck] GET /health harus mengembalikan status 200 dan koneksi database UP', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('UP');
    expect(res.body.app).toBe('RuangKita');
    expect(res.body.database).toBeDefined();
    expect(res.body.database.status).toBe('CONNECTED');
  });

  // TEST 2: Endpoint CRUD Ruang
  test('2. [Katalog Ruang] GET /api/rooms harus mengembalikan daftar ruangan meeting yang tersedia', async () => {
    const res = await request(app).get('/api/rooms');
    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(Array.isArray(res.body.data)).toBe(true);
    expect(res.body.data.length).toBeGreaterThanOrEqual(3);
    expect(res.body.data[0]).toHaveProperty('capacity');
    expect(res.body.data[0]).toHaveProperty('price_per_hour');
  });

  // TEST 3: ATURAN BISNIS 1 — Anti-Tumpang Tindih (Overlap Protection)
  test('3. [Aturan Bisnis 1] Dua booking pada ruang yang sama TIDAK boleh tumpang tindih (Overlap Protection)', async () => {
    // Booking 1: Ruang 1 pada jam 09:00 - 11:00 (Besok)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];

    const booking1Payload = {
      room_id: 1,
      customer_name: 'PT Tim Pertama',
      participants: 4,
      start_time: `${dateStr}T09:00:00`,
      end_time: `${dateStr}T11:00:00`,
    };

    const res1 = await request(app).post('/api/bookings').send(booking1Payload);
    expect(res1.status).toBe(201);
    expect(res1.body.success).toBe(true);

    // Booking 2: Ruang 1 pada jam 10:00 - 12:00 (Irisan sebagian jam 10.00-11.00)
    const booking2Payload = {
      room_id: 1,
      customer_name: 'PT Tim Kedua (Bentrok)',
      participants: 5,
      start_time: `${dateStr}T10:00:00`,
      end_time: `${dateStr}T12:00:00`,
    };

    const res2 = await request(app).post('/api/bookings').send(booking2Payload);
    expect(res2.status).toBe(400);
    expect(res2.body.success).toBe(false);
    expect(res2.body.error_code).toBe('SCHEDULE_OVERLAP');
    expect(res2.body.message).toContain('tumpang tindih');
  });

  // TEST 4: ATURAN BISNIS 2 — Batas Kapasitas Ruangan
  test('4. [Aturan Bisnis 2] Jumlah peserta tidak boleh melebihi kapasitas maksimal ruangan', async () => {
    // Ruang 1 memiliki kapasitas 8 orang. Coba booking dengan 12 peserta.
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];

    const payload = {
      room_id: 1,
      customer_name: 'Delegasi Raksasa',
      participants: 12, // Melebihi kapasitas (8)
      start_time: `${dateStr}T13:00:00`,
      end_time: `${dateStr}T15:00:00`,
    };

    const res = await request(app).post('/api/bookings').send(payload);
    expect(res.status).toBe(400);
    expect(res.body.success).toBe(false);
    expect(res.body.error_code).toBe('CAPACITY_EXCEEDED');
    expect(res.body.message).toContain('melebihi kapasitas');
  });

  // TEST 5: ATURAN BISNIS 3 — Jam Operasional 08.00-21.00 & Durasi 1-8 Jam
  test('5. [Aturan Bisnis 3] Booking di luar jam operasional (08.00-21.00) atau durasi tidak valid harus ditolak', async () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];

    // Kasus A: Mulai jam 06.00 pagi (Di luar operasional)
    const payloadEarly = {
      room_id: 1,
      customer_name: 'Subuh Meeting',
      participants: 4,
      start_time: `${dateStr}T06:00:00`,
      end_time: `${dateStr}T08:00:00`,
    };
    const resEarly = await request(app).post('/api/bookings').send(payloadEarly);
    expect(resEarly.status).toBe(400);
    expect(resEarly.body.error_code).toBe('OUTSIDE_OPERATING_HOURS');

    // Kasus B: Durasi lebih dari 8 jam (misal 9 jam: 09.00 - 18.00)
    const payloadLong = {
      room_id: 1,
      customer_name: 'Marathon Workshop',
      participants: 4,
      start_time: `${dateStr}T09:00:00`,
      end_time: `${dateStr}T18:30:00`,
    };
    const resLong = await request(app).post('/api/bookings').send(payloadLong);
    expect(resLong.status).toBe(400);
    expect(resLong.body.error_code).toBe('INVALID_DURATION');
  });

  // TEST 6: ATURAN BISNIS 4A — Denda Pembatalan 50% jika < 2 Jam Sebelum Mulai
  test('6. [Aturan Bisnis 4A] Pembatalan kurang dari 2 jam sebelum mulai dikenai denda 50%', async () => {
    // Buat booking jam 10.00 - 12.00 (Tarif 2 jam x 75.000 = 150.000)
    const bookingDate = new Date('2026-12-01T10:00:00');
    const bookingEnd = new Date('2026-12-01T12:00:00');

    const createRes = await request(app).post('/api/bookings').send({
      room_id: 1,
      customer_name: 'Startup Cepat',
      participants: 4,
      start_time: bookingDate.toISOString(),
      end_time: bookingEnd.toISOString(),
    });

    const bookingId = createRes.body.data.id;
    const totalPrice = parseFloat(createRes.body.data.total_price);
    expect(totalPrice).toBe(150000);

    // Batalkan pada jam 09.00 (Hanya 1 jam sebelum mulai -> < 2 jam)
    const cancelRes = await request(app)
      .post(`/api/bookings/${bookingId}/cancel`)
      .send({ cancellation_time: '2026-12-01T09:00:00' });

    expect(cancelRes.status).toBe(200);
    expect(cancelRes.body.success).toBe(true);
    expect(cancelRes.body.cancellation_details.fee_applied).toBe(true);
    expect(cancelRes.body.cancellation_details.fee_amount).toBe(totalPrice * 0.5);
    expect(cancelRes.body.data.status).toBe('CANCELLED');
  });

  // TEST 7: ATURAN BISNIS 4B — Pembatalan Bebas Denda jika >= 2 Jam Sebelum Mulai
  test('7. [Aturan Bisnis 4B] Pembatalan lebih dari 2 jam sebelum mulai BEBAS denda', async () => {
    // Buat booking jam 15.00 - 17.00
    const bookingDate = new Date('2026-12-01T15:00:00');
    const bookingEnd = new Date('2026-12-01T17:00:00');

    const createRes = await request(app).post('/api/bookings').send({
      room_id: 1,
      customer_name: 'Klien Disiplin',
      participants: 4,
      start_time: bookingDate.toISOString(),
      end_time: bookingEnd.toISOString(),
    });

    const bookingId = createRes.body.data.id;

    // Batalkan pada jam 10.00 (5 jam sebelum mulai -> > 2 jam)
    const cancelRes = await request(app)
      .post(`/api/bookings/${bookingId}/cancel`)
      .send({ cancellation_time: '2026-12-01T10:00:00' });

    expect(cancelRes.status).toBe(200);
    expect(cancelRes.body.success).toBe(true);
    expect(cancelRes.body.cancellation_details.fee_applied).toBe(false);
    expect(cancelRes.body.cancellation_details.fee_amount).toBe(0);
    expect(cancelRes.body.data.status).toBe('CANCELLED');
  });

});
