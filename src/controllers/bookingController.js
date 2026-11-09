const { query, getClient } = require('../config/db');

// GET /api/bookings - Get all bookings / calendar view
async function getAllBookings(req, res) {
  try {
    const result = await query(
      `SELECT b.*, r.name AS room_name, r.capacity AS room_capacity, r.price_per_hour
       FROM bookings b
       JOIN rooms r ON b.room_id = r.id
       ORDER BY b.start_time DESC`
    );
    return res.status(200).json({
      success: true,
      data: result.rows,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// GET /api/bookings/calendar - Kalender pemakaian ruang
async function getCalendar(req, res) {
  try {
    const result = await query(
      `SELECT b.id, b.customer_name, b.participants, b.start_time, b.end_time, b.status,
              r.id AS room_id, r.name AS room_name
       FROM bookings b
       JOIN rooms r ON b.room_id = r.id
       WHERE b.status = 'CONFIRMED'
       ORDER BY b.start_time ASC`
    );
    return res.status(200).json({
      success: true,
      data: result.rows,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// POST /api/bookings - Create new booking with full business rule & concurrency protection
async function createBooking(req, res) {
  const client = await getClient();
  try {
    const { room_id, customer_name, participants, start_time, end_time } = req.body;

    // 1. Validasi Keberadaan Field
    if (!room_id || !customer_name || participants === undefined || !start_time || !end_time) {
      return res.status(400).json({
        success: false,
        message: 'Field room_id, customer_name, participants, start_time, dan end_time wajib diisi',
      });
    }

    // 2. Sanitasi & Validasi room_id
    const parsedRoomId = Number(room_id);
    if (!Number.isInteger(parsedRoomId) || parsedRoomId <= 0) {
      return res.status(400).json({
        success: false,
        error_code: 'INVALID_ROOM_ID',
        message: 'room_id harus berupa bilangan bulat positif',
      });
    }

    // 3. Sanitasi customer_name (Anti-Spam & Buffer Overflow)
    const sanitizedCustomerName = typeof customer_name === 'string' ? customer_name.trim() : '';
    if (!sanitizedCustomerName || sanitizedCustomerName.length > 100) {
      return res.status(400).json({
        success: false,
        error_code: 'INVALID_CUSTOMER_NAME',
        message: 'customer_name harus berupa string 1-100 karakter dan tidak boleh hanya berisi spasi',
      });
    }

    // 4. Sanitasi participants: Wajib Integer Positif Murni (Tidak Boleh Pecahan / String)
    const numParticipants = Number(participants);
    if (!Number.isInteger(numParticipants) || numParticipants <= 0) {
      return res.status(400).json({
        success: false,
        error_code: 'INVALID_PARTICIPANTS',
        message: 'Jumlah peserta harus berupa bilangan bulat positif (minimal 1 orang, tidak boleh pecahan)',
      });
    }

    // 5. Validasi Format Tanggal
    const start = new Date(start_time);
    const end = new Date(end_time);

    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      return res.status(400).json({
        success: false,
        message: 'Format tanggal/waktu start_time atau end_time tidak valid',
      });
    }

    if (end <= start) {
      return res.status(400).json({
        success: false,
        message: 'Waktu selesai (end_time) harus lebih besar dari waktu mulai (start_time)',
      });
    }

    // 6. Validasi Past-Date (Tidak boleh booking di masa lampau)
    // Beri toleransi 2 menit untuk clock drift jaringan
    const now = new Date(Date.now() - 2 * 60 * 1000);
    if (start < now) {
      return res.status(400).json({
        success: false,
        error_code: 'PAST_DATE_NOT_ALLOWED',
        message: 'Waktu mulai booking tidak boleh di masa lampau',
      });
    }

    // 7. Validasi Hari Kalender yang Sama (Mencegah Booking Lintas Hari / Subuh)
    const startYear = start.getFullYear();
    const startMonth = start.getMonth();
    const startDate = start.getDate();
    const endYear = end.getFullYear();
    const endMonth = end.getMonth();
    const endDate = end.getDate();

    if (startYear !== endYear || startMonth !== endMonth || startDate !== endDate) {
      return res.status(400).json({
        success: false,
        error_code: 'CROSS_DAY_NOT_ALLOWED',
        message: 'Booking harus dimulai dan selesai pada hari kalender yang sama (tidak diizinkan lintas hari)',
      });
    }

    // 8. ATURAN BISNIS 3: Durasi 1-8 jam di jam operasional 08.00-21.00
    const durationHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
    if (durationHours < 1 || durationHours > 8) {
      return res.status(400).json({
        success: false,
        error_code: 'INVALID_DURATION',
        message: `Durasi booking harus antara 1 hingga 8 jam (permintaan: ${durationHours.toFixed(2)} jam)`,
      });
    }

    const startHour = start.getHours() + start.getMinutes() / 60;
    const endHour = end.getHours() + end.getMinutes() / 60;

    if (startHour < 8 || endHour > 21 || endHour < 8) {
      return res.status(400).json({
        success: false,
        error_code: 'OUTSIDE_OPERATING_HOURS',
        message: 'Booking hanya diizinkan di dalam jam operasional 08.00 - 21.00',
      });
    }

    // =========================================================================
    // MULAI TRANSAKSI DENGAN POSTGRESQL ADVISORY LOCK (ANTI-RACE CONDITION)
    // =========================================================================
    await client.query('BEGIN');

    // Kunci ruangan ini selama transaksi agar request paralel berurutan secara atomik
    await client.query('SELECT pg_advisory_xact_lock($1)', [parsedRoomId]);

    // Ambil data ruangan
    const roomResult = await client.query('SELECT * FROM rooms WHERE id = $1', [parsedRoomId]);
    if (roomResult.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({
        success: false,
        message: 'Ruangan yang dipilih tidak ditemukan',
      });
    }
    const room = roomResult.rows[0];

    // ATURAN BISNIS 2: Jumlah peserta tidak boleh melebihi kapasitas ruangan
    if (numParticipants > room.capacity) {
      await client.query('ROLLBACK');
      return res.status(400).json({
        success: false,
        error_code: 'CAPACITY_EXCEEDED',
        message: `Jumlah peserta (${numParticipants}) melebihi kapasitas maksimal ruangan (${room.capacity} orang)`,
      });
    }

    // ATURAN BISNIS 1: Dua booking pada ruang yang sama tidak boleh tumpang tindih
    const overlapResult = await client.query(
      `SELECT id, customer_name, start_time, end_time FROM bookings 
       WHERE room_id = $1 
         AND status = 'CONFIRMED'
         AND start_time < $2 
         AND end_time > $3`,
      [parsedRoomId, end.toISOString(), start.toISOString()]
    );

    if (overlapResult.rows.length > 0) {
      await client.query('ROLLBACK');
      return res.status(400).json({
        success: false,
        error_code: 'SCHEDULE_OVERLAP',
        message: 'Jadwal booking tumpang tindih dengan reservasi aktif lain pada ruangan ini',
        conflicting_booking: overlapResult.rows[0],
      });
    }

    // Hitung total harga otomatis di server
    const totalPrice = parseFloat((durationHours * parseFloat(room.price_per_hour)).toFixed(2));

    // Simpan ke database
    const insertResult = await client.query(
      `INSERT INTO bookings (room_id, customer_name, participants, start_time, end_time, total_price, status)
       VALUES ($1, $2, $3, $4, $5, $6, 'CONFIRMED') RETURNING *`,
      [parsedRoomId, sanitizedCustomerName, numParticipants, start.toISOString(), end.toISOString(), totalPrice]
    );

    await client.query('COMMIT');

    return res.status(201).json({
      success: true,
      message: 'Booking ruang berhasil dikonfirmasi',
      data: insertResult.rows[0],
    });
  } catch (err) {
    try {
      await client.query('ROLLBACK');
    } catch (_) {}
    return res.status(500).json({ success: false, error: err.message });
  } finally {
    client.release();
  }
}

// POST /api/bookings/:id/cancel - 4. ATURAN BISNIS: Pembatalan kurang dari 2 jam sebelum mulai dikenai denda 50%
async function cancelBooking(req, res) {
  try {
    const { id } = req.params;
    const { cancellation_time } = req.body;

    const parsedId = Number(id);
    if (!Number.isInteger(parsedId) || parsedId <= 0) {
      return res.status(400).json({
        success: false,
        message: 'ID booking harus berupa bilangan bulat positif',
      });
    }

    if (cancellation_time) {
      const parsedTime = new Date(cancellation_time);
      if (isNaN(parsedTime.getTime())) {
        return res.status(400).json({
          success: false,
          message: 'Format cancellation_time tidak valid',
        });
      }
    }

    const bookingResult = await query('SELECT * FROM bookings WHERE id = $1', [parsedId]);
    if (bookingResult.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Booking tidak ditemukan' });
    }

    const booking = bookingResult.rows[0];
    if (booking.status === 'CANCELLED') {
      return res.status(400).json({
        success: false,
        message: 'Booking ini sudah dibatalkan sebelumnya',
      });
    }

    const now = cancellation_time ? new Date(cancellation_time) : new Date();
    const startTime = new Date(booking.start_time);
    const diffHours = (startTime.getTime() - now.getTime()) / (1000 * 60 * 60);

    let fee = 0;
    let feeApplied = false;

    // Jika dibatalkan kurang dari 2 jam sebelum mulai (< 2 jam)
    if (diffHours < 2) {
      fee = parseFloat((parseFloat(booking.total_price) * 0.5).toFixed(2));
      feeApplied = true;
    }

    const updateResult = await query(
      `UPDATE bookings 
       SET status = 'CANCELLED', cancellation_fee = $1 
       WHERE id = $2 RETURNING *`,
      [fee, parsedId]
    );

    return res.status(200).json({
      success: true,
      message: feeApplied
        ? 'Booking berhasil dibatalkan dengan denda 50% karena pembatalan kurang dari 2 jam sebelum jadwal mulai'
        : 'Booking berhasil dibatalkan tanpa denda (pembatalan lebih dari 2 jam sebelum jadwal mulai)',
      data: updateResult.rows[0],
      cancellation_details: {
        hours_before_start: parseFloat(diffHours.toFixed(2)),
        fee_applied: feeApplied,
        fee_amount: fee,
      },
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

module.exports = {
  getAllBookings,
  getCalendar,
  createBooking,
  cancelBooking,
};
