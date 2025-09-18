const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

// Import route modules
const dashboardRoutes = require('./routes/dashboard');
const schedulerRoutes = require('./routes/scheduler');
const analyticsRoutes = require('./routes/analytics');
const optimizerRoutes = require('./routes/optimizer');
const platformRoutes = require('./routes/platforms');

/**
 * Main Express server for Social Media Engagement Booster API
 * 
 * This server provides REST API endpoints for:
 * - Dashboard metrics and overview data
 * - Post scheduling and optimization
 * - Engagement analytics and reporting
 * - Content optimization and AI analysis
 * - Multi-platform social media integration
 * 
 * GitHub Copilot can suggest additional middleware, error handling, and API endpoints
 */

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware setup
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS for frontend
app.use(express.json({ limit: '10mb' })); // Parse JSON bodies with larger limit for media
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

/**
 * API Routes
 * Each route module handles specific functionality areas
 * Copilot can suggest additional routes based on social media platform APIs
 */
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/scheduler', schedulerRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/optimizer', optimizerRoutes);
app.use('/api/platforms', platformRoutes);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    service: 'Social Media Engagement Booster API',
    version: '1.0.0'
  });
});

// Root endpoint with API documentation
app.get('/api', (req, res) => {
  res.json({
    message: 'Social Media Engagement Booster API',
    version: '1.0.0',
    endpoints: {
      dashboard: '/api/dashboard - Dashboard metrics and overview',
      scheduler: '/api/scheduler - Post scheduling and management',
      analytics: '/api/analytics - Engagement analytics and reporting',
      optimizer: '/api/optimizer - Content optimization and AI analysis',
      platforms: '/api/platforms - Social media platform integrations',
      health: '/api/health - Service health check'
    },
    documentation: 'https://github.com/your-repo/docs'
  });
});

/**
 * Error handling middleware
 * TODO: Implement comprehensive error handling and logging
 * Copilot can suggest error categorization and monitoring integration
 */
app.use((err, req, res, next) => {
  console.error('API Error:', err);
  
  // Default error response
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  
  res.status(statusCode).json({
    error: {
      message,
      statusCode,
      timestamp: new Date().toISOString(),
      path: req.path
    }
  });
});

// 404 handler for unknown routes
app.use('*', (req, res) => {
  res.status(404).json({
    error: {
      message: 'Route not found',
      statusCode: 404,
      path: req.originalUrl
    }
  });
});

/**
 * Start server
 * TODO: Add database connection setup
 * TODO: Add graceful shutdown handling
 */
const server = app.listen(PORT, () => {
  console.log(`🚀 Social Media Engagement Booster API running on port ${PORT}`);
  console.log(`📊 Dashboard: http://localhost:${PORT}/api/dashboard`);
  console.log(`⏰ Scheduler: http://localhost:${PORT}/api/scheduler`);
  console.log(`📈 Analytics: http://localhost:${PORT}/api/analytics`);
  console.log(`🎯 Optimizer: http://localhost:${PORT}/api/optimizer`);
  console.log(`🔗 Platforms: http://localhost:${PORT}/api/platforms`);
  console.log(`💚 Health: http://localhost:${PORT}/api/health`);
});

// Graceful shutdown handling
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
    // TODO: Close database connections
    process.exit(0);
  });
});

module.exports = app;