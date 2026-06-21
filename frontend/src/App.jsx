import { Routes, Route, NavLink } from "react-router-dom";
import { History, LayoutDashboard } from "lucide-react";
import { FaGithub } from "react-icons/fa";

import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import HistoryPage from "./pages/History";

export default function App() {
  const navLinkClass = ({ isActive }) =>
    `flex items-center gap-2 rounded-lg px-4 py-2 transition-all duration-200 ${
      isActive
        ? "bg-primary text-white"
        : "text-[var(--text)] hover:bg-white/10"
    }`;

  return (
    <div className="flex min-h-screen flex-col">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b border-theme bg-[rgba(26,31,26,0.75)] backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between px-6">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <FaGithub size={28} className="text-primary" />
            <h1 className="font-heading text-2xl font-bold tracking-tight">
              GitHub Repository Analyzer
            </h1>
          </div>

          {/* Navigation */}
          <nav className="flex items-center gap-3">
            <NavLink to="/" className={navLinkClass}>
              <LayoutDashboard size={18} />
              Dashboard
            </NavLink>

            <NavLink to="/history" className={navLinkClass}>
              <History size={18} />
              History
            </NavLink>
          </nav>
        </div>
      </header>

      {/* Main */}
      <main className="mx-auto w-full max-w-[1400px] flex-1 px-6 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="mt-8 border-t border-theme">
        <div className="mx-auto flex h-14 max-w-[1400px] items-center justify-center px-6">
          <a
            href="https://github.com/yashvi-jain"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-[var(--accent)] transition hover:text-[var(--primary)]"
          >
            yashvi-jain
          </a>
        </div>
      </footer>
    </div>
  );
}