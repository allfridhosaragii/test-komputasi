const { query } = require('../config/db');

async function migrate() {
  console.log('[Migration] Starting database migration for RuangKita...');
  
  const createRoomsTable = `
    CREATE TABLE IF NOT EXISTS rooms (
      id SERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      capacity INTEGER NOT NULL,
      facilities TEXT NOT NULL,
      price_per_hour NUMERIC(12, 2) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `;

  const createBookingsTable = `
    CREATE TABLE IF NOT EXISTS bookings (
      id SERIAL PRIMARY KEY,
      room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
      customer_name VARCHAR(100) NOT NULL,
      participants INTEGER NOT NULL,
      start_time TIMESTAMP NOT NULL,
      end_time TIMESTAMP NOT NULL,
      total_price NUMERIC(12, 2) NOT NULL,
      status VARCHAR(20) DEFAULT 'CONFIRMED',
      cancellation_fee NUMERIC(12, 2) DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `;

  try {
    await query(createRoomsTable);
    console.log('[Migration] Table "rooms" ready.');
    await query(createBookingsTable);
    console.log('[Migration] Table "bookings" ready.');
    console.log('[Migration] Database migration completed successfully.');
  } catch (err) {
    console.error('[Migration Error]:', err.message);
    throw err;
  }
}

if (require.main === module) {
  migrate()
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
}

module.exports = { migrate };
