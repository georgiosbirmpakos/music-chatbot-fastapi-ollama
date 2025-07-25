import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/ragchatbot', label: 'RagChat' },
    { path: '/chatbot', label: 'Chat' },
    { path: '/guide', label: 'Guide' },
    { path: '/about', label: 'About' },
  ];

  return (
    <nav className="bg-neutral-950 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-wide text-green-400">
          🎵 Music ChatBot
        </h1>
        <ul className="flex space-x-6 text-lg sm:text-xl font-medium">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`transition duration-300 ${
                  location.pathname === item.path
                    ? 'text-green-400 underline underline-offset-4'
                    : 'text-gray-300 hover:text-green-400'
                }`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
