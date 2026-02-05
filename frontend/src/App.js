import React, { useState } from "react";
import { isMobile } from "react-device-detect";
import { MuiThemeProvider, createMuiTheme } from "@material-ui/core/styles";
import { WeeklyProgram } from "./WeeklyProgram";
import { Controls } from "./Controls";
import { WelcomeDialog } from "./WelcomeDialog";
import { Banner } from "./Banner";
import "./App.css";
import { useSelector } from "react-redux";

import { CssBaseline } from "@material-ui/core";

const App = () => {
  const [loaded, setLoaded] = useState(false);
  const [currentScenario, setCurrentScenario] = useState(0);
  const handleLoadingCompleted = () => {
    setLoaded(true);
  };
  const dontFillsState = useSelector((state) => state.dontFillsState);
  const themeMode = useSelector((state) => state.themeState.mode);

  const theme = createMuiTheme({
    palette: {
      type: themeMode,
      primary: {
        main: "#1976d2",
      },
      secondary: {
        main: "#71F154",
      },
      background: {
        default: themeMode === "dark" ? "#121212" : "#ffffff",
        paper: themeMode === "dark" ? "#1e1e1e" : "#ffffff",
      },
    },
  });

  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App" data-theme={themeMode}>
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
