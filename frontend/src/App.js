import React, { useState, useMemo } from "react";
import { isMobile } from "react-device-detect";
import { ThemeProvider as MuiThemeProvider, adaptV4Theme, createTheme } from "@mui/material/styles";
import { WeeklyProgram } from "./WeeklyProgram";
import { Controls } from "./Controls";
import { WelcomeDialog } from "./WelcomeDialog";
import { Banner } from "./Banner";
import "./App.css";
import { useSelector } from "react-redux";
import { useTheme } from "./contexts/ThemeContext";

const App = () => {
  const { darkMode } = useTheme();
  // Mirror of the CSS custom properties in index.css, so MUI's own surfaces
  // (menus, dialogs, the scheduler grid) sit on the same palette as everything
  // styled through the tokens.
  const theme = useMemo(
    () =>
      createTheme(adaptV4Theme({
        palette: {
          type: darkMode ? "dark" : "light",
          primary: { main: darkMode ? "#3b82f6" : "#2563eb" },
          secondary: { main: "#0f9d70" },
          error: { main: "#e0524a" },
          warning: { main: "#d97706" },
          background: {
            default: darkMode ? "#0e1420" : "#f6f7f9",
            paper: darkMode ? "#161d2b" : "#ffffff",
          },
          text: {
            primary: darkMode ? "#e8ecf3" : "#131720",
            secondary: darkMode ? "#a3adbd" : "#5b6472",
          },
          divider: darkMode ? "#263042" : "#e3e7ee",
        },
        shape: { borderRadius: 10 },
        typography: {
          fontFamily:
            '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
          button: { textTransform: "none", fontWeight: 600 },
        },
      })),
    [darkMode]
  );

  const [loaded, setLoaded] = useState(false);
  const [currentScenario, setCurrentScenario] = useState(0);
  const handleLoadingCompleted = () => {
    setLoaded(true);
  };
  const dontFillsState = useSelector((state) => state.dontFillsState);

  return (
    <MuiThemeProvider theme={theme}>
      <div className="App">
        <Banner />
        {loaded && <WelcomeDialog />}
        <div className={isMobile ? "column" : "row"}>
          <WeeklyProgram 
            currentScenario={currentScenario}
            setCurrentScenario={setCurrentScenario}
          />
          <Controls
            dontFills={dontFillsState.result}
            onLoadingCompleted={handleLoadingCompleted}
            currentScenario={currentScenario}
          />
        </div>
      </div>
    </MuiThemeProvider>
  );
};

export default App;
