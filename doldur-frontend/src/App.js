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

class App extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            scenarios: []
        }
    }
    render() {
        console.log(this.state.scenarios);
        return (
          <MuiThemeProvider theme={theme}>
            <div className="App">
                <div className={isMobile ? "column" : "row"}>
                    <WeeklyProgram coursesToDisplay={getCoursesToDisplay()} scenarios={this.state.scenarios}/>
                    <Controls onSchedule={s => this.setState({scenarios: s})}/>
                </div>
            </div>
          </MuiThemeProvider>
      );
  }
}

export default App;
