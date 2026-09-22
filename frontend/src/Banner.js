import React from "react";

import logo from "./img/logo.png";
import title from "./img/title.gif";
import { DarkModeToggle } from "./DarkModeToggle";
import "./Banner.css";

export const Banner = () => {
  return (
    <header className="banner-wrapper">
      <div className="banner-inner">
        <div className="banner-brand">
          <span className="banner-logo">
            <img src={logo} width={56} height={56} alt="Logo" />
          </span>
          <img
            className="banner-title"
            src={title}
            width={320}
            height={45}
            alt="Course Scheduler"
          />
        </div>

        <div className="banner-actions">
          <DarkModeToggle />
        </div>
      </div>
    </header>
  );
};
