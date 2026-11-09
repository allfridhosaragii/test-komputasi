const { query } = require('../config/db');

// GET /api/rooms - List all rooms
async function getAllRooms(req, res) {
  try {
    const result = await query('SELECT * FROM rooms ORDER BY id ASC');
    return res.status(200).json({
      success: true,
      data: result.rows,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// GET /api/rooms/:id - Get room by ID
async function getRoomById(req, res) {
  try {
    const { id } = req.params;
    const parsedId = Number(id);
    if (!Number.isInteger(parsedId) || parsedId <= 0) {
      return res.status(400).json({
        success: false,
        message: 'ID ruangan harus berupa bilangan bulat positif',
      });
    }

    const result = await query('SELECT * FROM rooms WHERE id = $1', [parsedId]);
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Ruangan tidak ditemukan' });
    }
    return res.status(200).json({ success: true, data: result.rows[0] });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// POST /api/rooms - Create new room (CRUD Ruang)
async function createRoom(req, res) {
  try {
    const { name, capacity, facilities, price_per_hour } = req.body;
    if (!name || capacity === undefined || !facilities || price_per_hour === undefined) {
      return res.status(400).json({
        success: false,
        message: 'Field name, capacity, facilities, dan price_per_hour wajib diisi',
      });
    }

    const trimmedName = typeof name === 'string' ? name.trim() : '';
    if (!trimmedName || trimmedName.length > 100) {
      return res.status(400).json({
        success: false,
        message: 'Nama ruangan harus berupa string 1-100 karakter',
      });
    }

    const numCapacity = Number(capacity);
    if (!Number.isInteger(numCapacity) || numCapacity <= 0) {
      return res.status(400).json({
        success: false,
        message: 'Kapasitas harus berupa bilangan bulat positif',
      });
    }

    const numPrice = Number(price_per_hour);
    if (isNaN(numPrice) || numPrice <= 0 || !isFinite(numPrice)) {
      return res.status(400).json({
        success: false,
        message: 'Tarif harga per jam harus berupa angka positif',
      });
    }

    const result = await query(
      `INSERT INTO rooms (name, capacity, facilities, price_per_hour)
       VALUES ($1, $2, $3, $4) RETURNING *`,
      [trimmedName, numCapacity, typeof facilities === 'string' ? facilities.trim() : JSON.stringify(facilities), numPrice]
    );

    return res.status(201).json({
      success: true,
      message: 'Ruangan berhasil ditambahkan',
      data: result.rows[0],
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// PUT /api/rooms/:id - Update room
async function updateRoom(req, res) {
  try {
    const { id } = req.params;
    const parsedId = Number(id);
    if (!Number.isInteger(parsedId) || parsedId <= 0) {
      return res.status(400).json({
        success: false,
        message: 'ID ruangan harus berupa bilangan bulat positif',
      });
    }

    const { name, capacity, facilities, price_per_hour } = req.body;

    const check = await query('SELECT id FROM rooms WHERE id = $1', [parsedId]);
    if (check.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Ruangan tidak ditemukan' });
    }

    let parsedCapacity = null;
    if (capacity !== undefined) {
      parsedCapacity = Number(capacity);
      if (!Number.isInteger(parsedCapacity) || parsedCapacity <= 0) {
        return res.status(400).json({
          success: false,
          message: 'Kapasitas harus berupa bilangan bulat positif',
        });
      }
    }

    let parsedPrice = null;
    if (price_per_hour !== undefined) {
      parsedPrice = Number(price_per_hour);
      if (isNaN(parsedPrice) || parsedPrice <= 0 || !isFinite(parsedPrice)) {
        return res.status(400).json({
          success: false,
          message: 'Tarif harga per jam harus berupa angka positif',
        });
      }
    }

    const result = await query(
      `UPDATE rooms 
       SET name = COALESCE($1, name),
           capacity = COALESCE($2, capacity),
           facilities = COALESCE($3, facilities),
           price_per_hour = COALESCE($4, price_per_hour)
       WHERE id = $5 RETURNING *`,
      [
        name ? name.trim() : null,
        parsedCapacity,
        facilities ? (typeof facilities === 'string' ? facilities.trim() : JSON.stringify(facilities)) : null,
        parsedPrice,
        parsedId,
      ]
    );

    return res.status(200).json({
      success: true,
      message: 'Ruangan berhasil diperbarui',
      data: result.rows[0],
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// DELETE /api/rooms/:id - Delete room
async function deleteRoom(req, res) {
  try {
    const { id } = req.params;
    const parsedId = Number(id);
    if (!Number.isInteger(parsedId) || parsedId <= 0) {
      return res.status(400).json({
        success: false,
        message: 'ID ruangan harus berupa bilangan bulat positif',
      });
    }

    const result = await query('DELETE FROM rooms WHERE id = $1 RETURNING *', [parsedId]);
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Ruangan tidak ditemukan' });
    }
    return res.status(200).json({
      success: true,
      message: 'Ruangan berhasil dihapus',
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

// GET /api/rooms/availability?date=YYYY-MM-DD - Cek ketersediaan per tanggal
async function checkAvailability(req, res) {
  try {
    const { date } = req.query;
    if (!date) {
      return res.status(400).json({
        success: false,
        message: 'Parameter date (YYYY-MM-DD) wajib disertakan',
      });
    }

    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || isNaN(Date.parse(date))) {
      return res.status(400).json({
        success: false,
        message: 'Format tanggal date harus YYYY-MM-DD yang valid',
      });
    }

    const startOfDay = `${date} 00:00:00`;
    const endOfDay = `${date} 23:59:59`;

    const roomsResult = await query('SELECT * FROM rooms ORDER BY id ASC');
    const bookingsResult = await query(
      `SELECT * FROM bookings 
       WHERE status = 'CONFIRMED' 
         AND start_time >= $1 AND start_time <= $2
       ORDER BY start_time ASC`,
      [startOfDay, endOfDay]
    );

    const roomsWithAvailability = roomsResult.rows.map((room) => {
      const roomBookings = bookingsResult.rows.filter((b) => b.room_id === room.id);
      return {
        ...room,
        booked_slots: roomBookings.map((b) => ({
          booking_id: b.id,
          customer_name: b.customer_name,
          start_time: b.start_time,
          end_time: b.end_time,
        })),
        is_fully_booked: roomBookings.length >= 8, // jam operasional 08.00-21.00
      };
    });

    return res.status(200).json({
      success: true,
      date,
      data: roomsWithAvailability,
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
}

module.exports = {
  getAllRooms,
  getRoomById,
  createRoom,
  updateRoom,
  deleteRoom,
  checkAvailability,
};

