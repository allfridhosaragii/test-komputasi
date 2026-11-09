const { query } = require('../config/db');

async function seed() {
  console.log('[Seeder] Seeding initial rooms data for RuangKita...');
  
  const seedRooms = [
    {
      name: 'Ruang Kolaborasi Alpha',
      capacity: 8,
      facilities: 'Proyektor 4K, Smart TV, Whiteboard, High-Speed WiFi, AC',
      price_per_hour: 75000,
    },
    {
      name: 'Executive Boardroom Beta',
      capacity: 16,
      facilities: 'Video Conference System, Sound System, Dual Display, Ergonomic Chairs',
      price_per_hour: 150000,
    },
    {
      name: 'Creative Studio Gamma',
      capacity: 6,
      facilities: 'Podcasting Mic, Acoustic Foam, Whiteboard, Smart TV',
      price_per_hour: 60000,
    },
  ];

  try {
    for (const r of seedRooms) {
      const existing = await query('SELECT id FROM rooms WHERE name = $1', [r.name]);
      if (existing.rows.length === 0) {
        await query(
          'INSERT INTO rooms (name, capacity, facilities, price_per_hour) VALUES ($1, $2, $3, $4)',
          [r.name, r.capacity, r.facilities, r.price_per_hour]
        );
        console.log(`[Seeder] Room "${r.name}" inserted.`);
      } else {
        console.log(`[Seeder] Room "${r.name}" already exists.`);
      }
    }
    console.log('[Seeder] Database seeding completed successfully.');
  } catch (err) {
    console.error('[Seeder Error]:', err.message);
    throw err;
  }
}

if (require.main === module) {
  seed()
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
}

module.exports = { seed };

