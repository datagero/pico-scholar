import React from 'react';
import logo from '../../assets/images/logo-no-background.png';
import '../../App.css';

const Header = () => {
  return (
    <header className="header">
      <img src={logo} alt="Logo" className="logo" />
      <h1 className="header-text">Empowering Medical Research with Precision.</h1>
      {/* Other header content */}
    </header>
  );
};

export default Header;
