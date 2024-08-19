import React from 'react';
import logo from '../../assets/images/logo-no-background.png';
import '../../App.css';
import { FaFacebook, FaTwitter, FaLinkedin, FaGithub } from 'react-icons/fa';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-section footer-logo">
        <img src={logo} alt="Logo" className="footer-logo-img" />
      </div>
      <div className="footer-section footer-links">
        <ul>
          <li><a href="#terms">Terms of Service</a></li>
          <li><a href="#privacy">Privacy Policy</a></li>
        </ul>
      </div>
      <div className="footer-section footer-social">
        <a href="https://facebook.com" aria-label="Facebook"><FaFacebook /></a>
        <a href="https://twitter.com" aria-label="Twitter"><FaTwitter /></a>
        <a href="https://linkedin.com" aria-label="LinkedIn"><FaLinkedin /></a>
        <a href="https://github.com" aria-label="GitHub"><FaGithub /></a>
      </div>
    </footer>
  );
};

export default Footer;
