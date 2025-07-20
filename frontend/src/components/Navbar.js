import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-black text-white flex items-center justify-between px-6 py-4 shadow-md">
      <div className="text-xl font-bold flex items-center gap-2">
        <span role="img" aria-label="music">🎵</span> Music Chatbot
      </div>
      <ul className="flex space-x-6 text-sm font-medium">
        <li>
          <Link to="/" className="hover:text-green-500 transition">User Guide</Link>
        </li>
        <li>
          <Link to="/chatbot" className="hover:text-green-500 transition">Chatbot</Link>
        </li>
        <li>
          <Link to="/about" className="hover:text-green-500 transition">About</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
