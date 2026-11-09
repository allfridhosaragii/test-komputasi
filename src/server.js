require('dotenv').config();
const app = require('./app');
const { migrate } = require('./db/migrate');
const { seed } = require('./db/seed');

const PORT = process.env.PORT || 8000;

async function bootstrap() {
  try {
    console.log('[Bootstrap] Initializing database...');
    await migrate();
    await seed();
    console.log('[Bootstrap] Database initialization completed.');
  } catch (err) {
    console.warn('[Bootstrap Warning] Database auto-migration skipped or failed:', err.message);
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`=======================================================`);
    console.log(`🚀 RuangKita Server running on port ${PORT}`);
    console.log(`📍 Healthcheck endpoint: http://localhost:${PORT}/health`);
    console.log(`📍 Web Dashboard: http://localhost:${PORT}/`);
    console.log(`=======================================================`);
  });
}

bootstrap();

