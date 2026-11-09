const { query } = require('../config/db');

async function getHealth(req, res) {
  // Skenario simulasi uji gagal-pulih / rollback otomatis K10
  if (process.env.SIMULATE_HEALTH_FAILURE === 'true') {
    return res.status(500).json({
      status: 'ERROR',
      message: 'Simulated health failure for Jenkins Quality Gate & Auto-Rollback demonstration',
      timestamp: new Date().toISOString(),
    });
  }

  try {
    const dbCheck = await query('SELECT 1 AS alive');
    const isDbConnected = dbCheck.rows && dbCheck.rows.length > 0;

    return res.status(200).json({
      status: 'UP',
      app: 'RuangKita',
      version: process.env.APP_VERSION || '1.0.0',
      database: {
        status: isDbConnected ? 'CONNECTED' : 'DISCONNECTED',
        provider: 'PostgreSQL',
      },
      uptime_seconds: process.uptime(),
      timestamp: new Date().toISOString(),
    });
  } catch (err) {
    return res.status(500).json({
      status: 'DOWN',
      app: 'RuangKita',
      error: 'Database connection failed: ' + err.message,
      timestamp: new Date().toISOString(),
    });
  }
}

module.exports = { getHealth };
