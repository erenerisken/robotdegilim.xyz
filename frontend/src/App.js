import React, { useState } from "react";
import { isMobile } from "react-device-detect";
import { MuiThemeProvider, createMuiTheme } from "@material-ui/core/styles";
import { WeeklyProgram } from "./WeeklyProgram";
import { Controls } from "./Controls";
import { WelcomeDialog } from "./WelcomeDialog";
import { Banner } from "./Banner";
import "./App.css";
import { useSelector } from "react-redux";

const theme = createMuiTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#71F154",
    },
  },
});

const App = () => {
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
