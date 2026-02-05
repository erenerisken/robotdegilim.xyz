import React from "react";
import { Box, Container, IconButton, Tooltip } from "@material-ui/core";
import { withStyles } from "@material-ui/core/styles";
import Brightness4Icon from "@material-ui/icons/Brightness4";
import Brightness7Icon from "@material-ui/icons/Brightness7";
import { useDispatch, useSelector } from "react-redux";
import { toggleTheme } from "./slices/themeSlice";

import logo from "./img/logo.png";
import title from "./img/title.gif";
import "./Banner.css";

const StyledBanner = withStyles((theme) => ({
  root: {
    background: theme.palette.type === 'dark'
      ? 'linear-gradient(135deg, #374151 0%, #1f2937 100%)'
      : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
    padding: theme.spacing(3, 0),
    boxShadow: theme.palette.type === 'dark'
      ? '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.15)'
      : '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    borderBottom: theme.palette.type === 'dark'
      ? '1px solid rgba(255, 255, 255, 0.1)'
      : '1px solid rgba(0, 0, 0, 0.1)',
    position: 'relative',
    overflow: 'hidden',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: theme.palette.type === 'dark'
        ? 'radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 70%)'
        : 'radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.3) 0%, transparent 70%)',
      zIndex: 1,
    },
  },
}))(Box);

const BannerContent = withStyles((theme) => ({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: theme.spacing(3),
    position: 'relative',
    zIndex: 2,
    [theme.breakpoints.down('md')]: {
      flexDirection: 'column',
      gap: theme.spacing(2),
    },
  },
}))(Box);

const LogoContainer = withStyles((theme) => ({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: theme.palette.type === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(10px)',
    borderRadius: '50%',
    padding: theme.spacing(2),
    border: theme.palette.type === 'dark'
      ? '2px solid rgba(255, 255, 255, 0.1)'
      : '2px solid rgba(0, 0, 0, 0.1)',
    boxShadow: theme.palette.type === 'dark'
      ? '0 8px 32px 0 rgba(0, 0, 0, 0.5)'
      : '0 8px 32px 0 rgba(0, 0, 0, 0.1)',
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'scale(1.05)',
      boxShadow: theme.palette.type === 'dark'
        ? '0 12px 40px 0 rgba(0, 0, 0, 0.7)'
        : '0 12px 40px 0 rgba(0, 0, 0, 0.15)',
    },
  },
}))(Box);

const TitleContainer = withStyles((theme) => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
}))(Box);



// ThemeToggle is now handled by the neumorphic switch in Banner.css


export const Banner = () => {
  const dispatch = useDispatch();
  const themeMode = useSelector((state) => state.themeState.mode);

  return (
    <StyledBanner className="banner-wrapper">
      <Container maxWidth="lg">
        <BannerContent>
          <LogoContainer className="fade-in">
            <img
              src={logo}
              width={80}
              height={80}
              alt="Logo"
              style={{ borderRadius: '50%' }}
            />
          </LogoContainer>

          <TitleContainer className="fade-in">
            <img
              src={title}
              width={320}
              height={45}
              alt="Course Scheduler"
              style={{
                filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))',
                maxWidth: '100%',
                height: 'auto'
              }}
            />
          </TitleContainer>

          <div className="theme-switch-container">
            <Tooltip title={themeMode === 'dark' ? "Switch to Light Mode" : "Switch to Dark Mode"}>
              <div
                className={`theme-switch-track ${themeMode === 'dark' ? 'active' : ''}`}
                onClick={() => dispatch(toggleTheme())}
              >
                <div className="theme-switch-thumb">
                  {themeMode === 'dark' ? (
                    <Brightness4Icon className="theme-icon" />
                  ) : (
                    <Brightness7Icon className="theme-icon" />
                  )}
                </div>
                <div className="theme-switch-text">
                  {themeMode === 'dark' ? 'Dark Mode' : 'Light Mode'}
                </div>
              </div>
            </Tooltip>
          </div>
        </BannerContent>
      </Container>
    </StyledBanner>
  );
};
