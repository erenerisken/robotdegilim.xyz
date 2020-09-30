import React from 'react';
import {isMobile} from "react-device-detect";
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import {WeeklyProgram} from "./WeeklyProgram";
import {Controls} from "./Controls";
import {getCoursesToDisplay} from "./CoursesToDisplay";

import './App.css';

const theme = createMuiTheme({
    palette: {
        secondary: {
            main: '#71F154'
        }
    }
});

function App() {
  return (
      <MuiThemeProvider theme={theme}>
        <div className="App">
            <div className={isMobile ? "column" : "row"}>
                <WeeklyProgram coursesToDisplay={getCoursesToDisplay()}/>
                <Controls />
            </div>
        </div>
      </MuiThemeProvider>
  );
}

export default App;
