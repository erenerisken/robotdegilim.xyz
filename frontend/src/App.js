import React, { useState } from "react";
import { isMobile } from "react-device-detect";
import { MuiThemeProvider, createMuiTheme } from "@material-ui/core/styles";
import { WeeklyProgram } from "./WeeklyProgram";
import { Controls } from "./Controls";
import { WelcomeDialog } from "./WelcomeDialog";
import { Banner } from "./Banner";
import "./App.css";
import { Colorset } from "./Colorset";

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
  const [scenarios, setScenarios] = useState([]);
  const [dontFills, setDontFills] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const dontFillColorset = new Colorset();

  const handleDontFillAdd = (startDate, endDate, description) => {
    setDontFills((prev) => {
      const isOverlapping = prev.some((df) => startDate == df.startDate);
      return isOverlapping
        ? [...prev]
        : [
            ...prev,
            {
              startDate,
              endDate,
              description,
              color: dontFillColorset.getBlack(),
            },
          ];
    });
  };

  const handleDontFillDelete = (startDate) => {
    setDontFills((prev) => prev.filter((df) => df.startDate !== startDate));
  };

  const handleLoadingCompleted = () => {
    setLoaded(true);
  };

  const handleChangeDontFillColor = (startDate, color) => {
    setDontFills((prev) =>
      prev.map((df) => (df.startDate === startDate ? { ...df, color } : df))
    );
  };

  const handleChangeDontFillDescription = (startDate, newDescription) => {
    setDontFills((prev) =>
      prev.map((df) =>
        df.startDate === startDate ? { ...df, description: newDescription } : df
      )
    );
  };

  return (
    <MuiThemeProvider theme={theme}>
      <div className="App">
        <Banner />
        {loaded && <WelcomeDialog />}
        <div className={isMobile ? "column" : "row"}>
          <WeeklyProgram
            dontFills={dontFills}
            scenarios={scenarios}
            onDontFillAdd={handleDontFillAdd}
            onChangeDontFillColor={handleChangeDontFillColor}
            onChangeDontFillDescription={handleChangeDontFillDescription}
            onDontFillDelete={handleDontFillDelete}
          />
          <Controls
            onSchedule={setScenarios}
            dontFills={dontFills}
            onDontFillAdd={handleDontFillAdd}
            onLoadingCompleted={handleLoadingCompleted}
          />
        </div>
      </div>
    </MuiThemeProvider>
  );
};

export default App;
