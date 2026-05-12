import { Link, useLocation } from 'react-router-dom';
import { Sprout, BarChart3, LayoutDashboard, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const { token, logout, user } = useAuth();

  const navLinks = [
    { name: 'Home', path: '/', icon: <Sprout className="w-4 h-4" /> },
    { name: 'Predict', path: '/input', icon: <BarChart3 className="w-4 h-4" /> },
    { name: 'Analytics', path: '/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
  ];

  return (
    <nav className="sticky top-0 z-50 glass border-b border-white/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <Link to="/" className="flex items-center gap-3 group">
            <motion.div 
              whileHover={{ rotate: 10 }}
              className="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-200 group-hover:bg-emerald-500 transition-colors"
            >
              <Sprout className="text-white w-6 h-6" />
            </motion.div>
            <span className="font-bold text-gray-900 text-xl tracking-tight">
              Farm<span className="text-emerald-600">Yield</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  location.pathname === link.path
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-emerald-600'
                }`}
              >
                {link.icon}
                {link.name}
              </Link>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            {token ? (
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium text-gray-600">Hi, {user?.name || 'Farmer'}</span>
                <button
                  onClick={logout}
                  className="text-gray-500 hover:text-red-500 font-medium text-sm transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="text-gray-600 hover:text-emerald-600 font-medium text-sm px-4 py-2"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-full text-sm font-semibold shadow-md shadow-emerald-100 transition-all hover:scale-105 active:scale-95"
                >
                  Sign up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition"
            >
              {isOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-gray-100 bg-white"
          >
            <div className="px-4 py-6 space-y-4">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl text-base font-medium ${
                    location.pathname === link.path
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {link.icon}
                  {link.name}
                </Link>
              ))}
              <div className="pt-2 flex flex-col gap-3">
                {token ? (
                  <button
                    onClick={() => {
                      logout();
                      setIsOpen(false);
                    }}
                    className="block w-full text-center bg-red-50 text-red-600 px-4 py-3 rounded-xl font-semibold hover:bg-red-100"
                  >
                    Logout
                  </button>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={() => setIsOpen(false)}
                      className="block w-full text-center bg-gray-50 text-gray-700 px-4 py-3 rounded-xl font-semibold"
                    >
                      Log in
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setIsOpen(false)}
                      className="block w-full text-center bg-emerald-600 text-white px-4 py-3 rounded-xl font-semibold shadow-md"
                    >
                      Sign up
                    </Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}