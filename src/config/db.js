const { Pool } = require('pg');
require('dotenv').config();

// In-memory mock store for testing without needing external PostgreSQL during 'docker build --target test'
const inMemoryStore = {
  rooms: [
    {
      id: 1,
      name: 'Ruang Kolaborasi Alpha',
      capacity: 8,
      facilities: 'Proyektor 4K, Smart TV, Whiteboard, High-Speed WiFi, AC',
      price_per_hour: 75000,
      created_at: new Date(),
    },
    {
      id: 2,
      name: 'Executive Boardroom Beta',
      capacity: 16,
      facilities: 'Video Conference System, Sound System, Dual Display, Ergonomic Chairs',
      price_per_hour: 150000,
      created_at: new Date(),
    },
    {
      id: 3,
      name: 'Creative Studio Gamma',
      capacity: 6,
      facilities: 'Podcasting Mic, Acoustic Foam, Whiteboard, Smart TV',
      price_per_hour: 60000,
      created_at: new Date(),
    },
  ],
  bookings: [],
  bookingIdCounter: 1,
};

let pool = null;

if (process.env.NODE_ENV !== 'test' || process.env.TEST_WITH_REAL_DB === 'true') {
  pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    user: process.env.DB_USER || 'ruangkita_user',
    password: process.env.DB_PASSWORD || 'ruangkita_secret_password',
    database: process.env.DB_NAME || 'ruangkita_db',
    max: 25, // Diperbesar untuk menangani lonjakan request konkurensi ekstrem
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 5000,
  });

  pool.on('error', (err) => {
    console.error('[Database Pool Error]:', err.message);
  });
}

// Emulated query handler for standalone unit tests during docker build
async function mockQuery(text, params = []) {
  const normalized = text.trim().replace(/\s+/g, ' ');

  // Healthcheck SELECT 1
  if (normalized.includes('SELECT 1')) {
    return { rows: [{ alive: 1 }] };
  }

  // Transaction control & Advisory Locks
  if (normalized.startsWith('BEGIN') || normalized.startsWith('COMMIT') || normalized.startsWith('ROLLBACK')) {
    return { rows: [] };
  }
  if (normalized.includes('pg_advisory_xact_lock')) {
    return { rows: [] };
  }

  // CREATE TABLE
  if (normalized.startsWith('CREATE TABLE')) {
    return { rows: [] };
  }

  // SELECT * FROM rooms ORDER BY id ASC
  if (normalized.includes('FROM rooms') && normalized.includes('ORDER BY id ASC')) {
    return { rows: [...inMemoryStore.rooms] };
  }

  // SELECT * FROM rooms WHERE id = $1
  if (normalized.includes('FROM rooms WHERE id = $1')) {
    const r = inMemoryStore.rooms.find((item) => item.id === parseInt(params[0], 10));
    return { rows: r ? [r] : [] };
  }

  // SELECT id FROM rooms WHERE name = $1
  if (normalized.includes('FROM rooms WHERE name = $1')) {
    const r = inMemoryStore.rooms.find((item) => item.name === params[0]);
    return { rows: r ? [r] : [] };
  }

  // INSERT INTO rooms
  if (normalized.startsWith('INSERT INTO rooms')) {
    const newRoom = {
      id: inMemoryStore.rooms.length + 1,
      name: params[0],
      capacity: parseInt(params[1], 10),
      facilities: params[2],
      price_per_hour: parseFloat(params[3]),
      created_at: new Date(),
    };
    inMemoryStore.rooms.push(newRoom);
    return { rows: [newRoom] };
  }

  // SELECT * FROM bookings (join rooms)
  if (normalized.includes('FROM bookings b') && normalized.includes('JOIN rooms r')) {
    const rows = inMemoryStore.bookings.map((b) => {
      const room = inMemoryStore.rooms.find((r) => r.id === b.room_id) || {};
      return {
        ...b,
        room_name: room.name,
        room_capacity: room.capacity,
        price_per_hour: room.price_per_hour,
      };
    });
    return { rows };
  }

  // Overlap query
  if (normalized.includes('FROM bookings') && normalized.includes('status = \'CONFIRMED\'') && normalized.includes('start_time < $2')) {
    const roomId = parseInt(params[0], 10);
    const newEnd = new Date(params[1]);
    const newStart = new Date(params[2]);

    const conflicts = inMemoryStore.bookings.filter((b) => {
      if (b.room_id !== roomId || b.status !== 'CONFIRMED') return false;
      const bStart = new Date(b.start_time);
      const bEnd = new Date(b.end_time);
      return newStart < bEnd && newEnd > bStart;
    });

    return { rows: conflicts };
  }

  // SELECT * FROM bookings WHERE id = $1
  if (normalized.includes('FROM bookings WHERE id = $1')) {
    const b = inMemoryStore.bookings.find((item) => item.id === parseInt(params[0], 10));
    return { rows: b ? [b] : [] };
  }

  // INSERT INTO bookings
  if (normalized.startsWith('INSERT INTO bookings')) {
    const newBooking = {
      id: inMemoryStore.bookingIdCounter++,
      room_id: parseInt(params[0], 10),
      customer_name: params[1],
      participants: parseInt(params[2], 10),
      start_time: new Date(params[3]),
      end_time: new Date(params[4]),
      total_price: parseFloat(params[5]),
      status: 'CONFIRMED',
      cancellation_fee: 0,
      created_at: new Date(),
    };
    inMemoryStore.bookings.push(newBooking);
    return { rows: [newBooking] };
  }

  // UPDATE bookings SET status = 'CANCELLED'
  if (normalized.includes('UPDATE bookings SET status = \'CANCELLED\'')) {
    const fee = parseFloat(params[0]);
    const id = parseInt(params[1], 10);
    const b = inMemoryStore.bookings.find((item) => item.id === id);
    if (b) {
      b.status = 'CANCELLED';
      b.cancellation_fee = fee;
      return { rows: [b] };
    }
    return { rows: [] };
  }

  return { rows: [] };
}

async function query(text, params) {
  if (process.env.NODE_ENV === 'test' && !process.env.TEST_WITH_REAL_DB) {
    return mockQuery(text, params);
  }
  return pool.query(text, params);
}

async function getClient() {
  if (process.env.NODE_ENV === 'test' && !process.env.TEST_WITH_REAL_DB) {
    return {
      query: mockQuery,
      release: () => {},
    };
  }
  return pool.connect();
}

module.exports = {
  pool,
  query,
  getClient,
  inMemoryStore,
};
