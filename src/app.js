const express = require('express');
const cors = require('cors');
const path = require('path');
const { getHealth } = require('./controllers/healthController');
const roomController = require('./controllers/roomController');
const bookingController = require('./controllers/bookingController');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Wajib: Endpoint GET /health
app.get('/health', getHealth);
app.get('/api/health', getHealth);

// Ruang (Room) Endpoints
app.get('/api/rooms', roomController.getAllRooms);
app.get('/api/rooms/availability', roomController.checkAvailability);
app.get('/api/rooms/:id', roomController.getRoomById);
app.post('/api/rooms', roomController.createRoom);
app.put('/api/rooms/:id', roomController.updateRoom);
app.delete('/api/rooms/:id', roomController.deleteRoom);

// Booking Endpoints
app.get('/api/bookings', bookingController.getAllBookings);
app.get('/api/bookings/calendar', bookingController.getCalendar);
app.post('/api/bookings', bookingController.createBooking);
app.post('/api/bookings/:id/cancel', bookingController.cancelBooking);

// Catch-all route for frontend dashboard
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// 404 Handler
app.use((req, res) => {
  res.status(404).json({ success: false, message: 'Endpoint tidak ditemukan' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('[Internal Server Error]:', err.stack);
  res.status(500).json({ success: false, error: err.message });
});

module.exports = app;
