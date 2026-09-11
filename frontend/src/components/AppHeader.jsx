/**
 * App Header Component
 * Global navigation header with team switcher and user menu
 * Empire-1 Cockpit Spec styling
 */

import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import TeamSwitcher from "./TeamSwitcher";

const EmpireMark = () => (
  <svg
    width="30"
    height="30"
    viewBox="0 0 30 30"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect width="30" height="30" rx="4" fill="#050505" />
    <path
      d="M6 8h3v14H6V8zm7 0h3l4 8.5V8h3v14h-3l-4-8.5V22h-3V8z"
      fill="#f2f2f4"
    />
    <rect x="22" y="8" width="3" height="14" fill="#E6007A" />
  </svg>
);

const AppHeader = () => {
  const { user, logout, isAuthenticated, currentTeam } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const getUserInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    if (user?.email) {
      return user.email[0].toUpperCase();
    }
    return "?";
  };

  const isTeamAdmin =
    currentTeam && ["owner", "admin"].includes(currentTeam.role);
  const isSystemAdmin = user?.system_role === "admin";

  if (!isAuthenticated) {
    return (
      <header className="app-header" data-testid="app-header">
        <Link to="/" className="app-logo">
          <span className="logo-icon">
            <EmpireMark />
          </span>
          <span className="logo-text">
            EMPIRE <span>1</span>
          </span>
        </Link>
        <nav className="header-nav">
          <Link to="/login" className="nav-link" data-testid="login-nav">
            Sign In
          </Link>
          <Link
            to="/signup"
            className="nav-link primary"
            data-testid="signup-nav"
          >
            Get Started
          </Link>
        </nav>
      </header>
    );
  }

  return (
    <header className="app-header" data-testid="app-header">
      <Link to="/" className="app-logo">
        <span className="logo-icon">
          <EmpireMark />
        </span>
        <span className="logo-text">
          EMPIRE <span>1</span>
        </span>
      </Link>

      <nav className="header-nav-main">
        <Link to="/engines" className="nav-link" data-testid="engines-nav">
          Engines
        </Link>
        <Link
          to="/pipeline-composer"
          className="nav-link"
          data-testid="composer-nav"
        >
          Composer
        </Link>
        <Link
          to="/founder-copilot"
          className="nav-link"
          data-testid="founder-copilot-nav"
        >
          Copilot
        </Link>
        <Link to="/analytics" className="nav-link" data-testid="analytics-nav">
          Analytics
        </Link>
        <Link to="/history" className="nav-link" data-testid="history-nav">
          History
        </Link>
        <Link to="/licensing" className="nav-link" data-testid="licensing-nav">
          Licensing
        </Link>
      </nav>

      <div className="header-right">
        <TeamSwitcher />

        <div className="user-menu-container" ref={menuRef}>
          <button
            className="user-avatar-btn"
            onClick={() => setShowUserMenu(!showUserMenu)}
            data-testid="user-menu-toggle"
          >
            <span className="user-avatar">{getUserInitials()}</span>
          </button>

          {showUserMenu && (
            <div className="user-dropdown" data-testid="user-dropdown">
              <div className="user-info">
                <span className="user-name">
                  {user?.first_name} {user?.last_name}
                </span>
                <span className="user-email">{user?.email}</span>
              </div>

              <div className="dropdown-divider"></div>

              <Link
                to="/profile"
                className="dropdown-item"
                onClick={() => setShowUserMenu(false)}
                data-testid="profile-link"
              >
                <span>Profile Settings</span>
              </Link>

              {isTeamAdmin && (
                <>
                  <Link
                    to="/billing"
                    className="dropdown-item"
                    onClick={() => setShowUserMenu(false)}
                    data-testid="billing-link"
                  >
                    <span>Billing</span>
                  </Link>

                  <Link
                    to="/settings/api-keys"
                    className="dropdown-item"
                    onClick={() => setShowUserMenu(false)}
                    data-testid="api-keys-link"
                  >
                    <span>API Keys</span>
                  </Link>
                </>
              )}

              {isSystemAdmin && (
                <>
                  <div className="dropdown-divider"></div>
                  <Link
                    to="/admin/overview"
                    className="dropdown-item admin-link"
                    onClick={() => setShowUserMenu(false)}
                    data-testid="admin-link"
                  >
                    <span>Admin Dashboard</span>
                  </Link>
                </>
              )}

              <div className="dropdown-divider"></div>

              <button
                className="dropdown-item logout"
                onClick={handleLogout}
                data-testid="logout-btn"
              >
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
