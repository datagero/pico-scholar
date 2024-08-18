import React from 'react';
import { BrowserRouter as Router, Route, Routes, NavLink } from 'react-router-dom';
import HomePage from './pages/HomePage';
import FunnelPage from './pages/FunnelPage';
import Header from './components/Common/Header';
import Footer from './components/Common/Footer';
import './App.css';

function App() {
  return (
    <Router>
      <div id="root">
        <Header /> {/* Render Header only once here */}
        <nav className="navbar">
          <ul className="nav-links">
            <li>
              <NavLink 
                to="/" 
                className={({ isActive }) => isActive ? 'active-link' : 'inactive-link'}
              >
                HOME SEARCH
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/results" 
                className={({ isActive }) => isActive ? 'active-link' : 'inactive-link'}
              >
                RESULTS ANALYSER
              </NavLink>
            </li>
          </ul>
        </nav>
        <div className="App">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/results" element={<FunnelPage />} />
          </Routes>
          <div className="content">
            {/* Add your main content here */}
          </div>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
