import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import PostScheduler from './components/PostScheduler';
import EngagementAnalytics from './components/EngagementAnalytics';
import ContentOptimizer from './components/ContentOptimizer';

/**
 * Main App component for Social Media Engagement Booster
 * 
 * This component sets up the main routing and layout for the application.
 * GitHub Copilot can suggest additional routes and components based on this structure.
 */
function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>AI Social Media Engagement Booster</h1>
          <nav>
            {/* TODO: Add navigation menu - Copilot can suggest navigation structure */}
          </nav>
        </header>
        
        <main className="App-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scheduler" element={<PostScheduler />} />
            <Route path="/analytics" element={<EngagementAnalytics />} />
            <Route path="/optimizer" element={<ContentOptimizer />} />
            {/* TODO: Add more routes for different platforms - let Copilot suggest based on social media platforms */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;