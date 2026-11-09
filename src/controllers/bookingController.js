const { query } = require('../config/db');

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

// POST /api/bookings - Create new booking with full business rule validation
async function createBooking(req, res) {
  try {
    const { room_id, customer_name, participants, start_time, end_time } = req.body;

    if (!room_id || !customer_name || !participants || !start_time || !end_time) {
      return res.status(400).json({
        success: false,
        message: 'Field room_id, customer_name, participants, start_time, dan end_time wajib diisi',
      });
    }

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

    // 1. ATURAN BISNIS: Jam operasional 08.00–21.00 & durasi 1–8 jam
    const durationHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
    if (durationHours < 1 || durationHours > 8) {
      return res.status(400).json({
        success: false,
        error_code: 'INVALID_DURATION',
        message: `Durasi booking harus antara 1 hingga 8 jam (permintaan: ${durationHours.toFixed(1)} jam)`,
      });
    }

    const startHour = start.getHours() + start.getMinutes() / 60;
    const endHour = end.getHours() + end.getMinutes() / 60;

    if (startHour < 8 || endHour > 21) {
      return res.status(400).json({
        success: false,
        error_code: 'OUTSIDE_OPERATING_HOURS',
        message: 'Booking hanya diizinkan di dalam jam operasional 08.00 - 21.00',
      });
    }

    // Ambil data ruangan
    const roomResult = await query('SELECT * FROM rooms WHERE id = $1', [room_id]);
    if (roomResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Ruangan yang dipilih tidak ditemukan',
      });
    }
    const room = roomResult.rows[0];

    // 2. ATURAN BISNIS: Jumlah peserta tidak boleh melebihi kapasitas ruangan
    const parsedParticipants = parseInt(participants, 10);
    if (parsedParticipants <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Jumlah peserta harus minimal 1 orang',
      });
    }
    if (parsedParticipants > room.capacity) {
      return res.status(400).json({
        success: false,
        error_code: 'CAPACITY_EXCEEDED',
        message: `Jumlah peserta (${parsedParticipants}) melebihi kapasitas maksimal ruangan (${room.capacity} orang)`,
      });
    }

    // 3. ATURAN BISNIS: Dua booking pada ruang yang sama tidak boleh tumpang tindih (overlap protection)
    const overlapResult = await query(
      `SELECT * FROM bookings 
       WHERE room_id = $1 
         AND status = 'CONFIRMED'
         AND start_time < $2 
         AND end_time > $3`,
      [room_id, end.toISOString(), start.toISOString()]
    );

    if (overlapResult.rows.length > 0) {
      return res.status(400).json({
        success: false,
        error_code: 'SCHEDULE_OVERLAP',
        message: 'Jadwal booking tumpang tindih dengan reservasi aktif lain pada ruangan ini',
        conflicting_booking: overlapResult.rows[0],
      });
    }

    // Hitung total harga otomatis di server
    const totalPrice = durationHours * parseFloat(room.price_per_hour);

    // Simpan ke database
    const insertResult = await query(
      `INSERT INTO bookings (room_id, customer_name, participants, start_time, end_time, total_price, status)
       VALUES ($1, $2, $3, $4, $5, $6, 'CONFIRMED') RETURNING *`,
      [room_id, customer_name, parsedParticipants, start.toISOString(), end.toISOString(), totalPrice]
    );

    return res.status(201).json({
      success: true,
      message: 'Booking ruang berhasil dikonfirmasi',
      data: insertResult.rows[0],
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// POST /api/bookings/:id/cancel - 4. ATURAN BISNIS: Pembatalan kurang dari 2 jam sebelum mulai dikenai denda 50%
async function cancelBooking(req, res) {
  try {
    const { id } = req.params;
    const { cancellation_time } = req.body; // opsional untuk keperluan testing waktu tertentu

    const bookingResult = await query('SELECT * FROM bookings WHERE id = $1', [id]);
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

    // Jika dibatalkan kurang dari 2 jam sebelum mulai (atau setelah waktu mulai)
    if (diffHours < 2) {
      fee = parseFloat(booking.total_price) * 0.5;
      feeApplied = true;
    }

    const updateResult = await query(
      `UPDATE bookings 
       SET status = 'CANCELLED', cancellation_fee = $1 
       WHERE id = $2 RETURNING *`,
      [fee, id]
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
