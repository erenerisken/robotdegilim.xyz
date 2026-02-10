import React from "react";
import { useTheme } from "./contexts/ThemeContext";
import "./DarkModeToggle.css";

const SunIcon = () => (
  <svg className="dark-toggle-icon sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
);

const MoonIcon = () => (
  <svg className="dark-toggle-icon moon-icon" viewBox="0 0 24 24" fill="currentColor">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);

export const DarkModeToggle = () => {
  const { darkMode, toggleDarkMode } = useTheme();

  return (
    <button
      type="button"
      className="dark-mode-toggle"
      onClick={toggleDarkMode}
      aria-label={darkMode ? "Açık moda geç" : "Karanlık moda geç"}
      title={darkMode ? "Açık mod" : "Karanlık mod"}
    >
      <span className="dark-toggle-track">
        <span className="dark-toggle-thumb" data-dark={darkMode} />
        <span className="dark-toggle-sun-slot" aria-hidden>
          <SunIcon />
        </span>
        <span className="dark-toggle-moon-slot" aria-hidden>
          <MoonIcon />
        </span>
      </span>
    </button>
  );
};
