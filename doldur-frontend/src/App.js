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
            scenarios: [],
            dontFills: []
        }
    }
    handleDontFillAdd(startDate, endDate){
        const newDontFills = this.state.dontFills.slice(0);
        newDontFills.push({
            startDate: startDate,
            endDate: endDate
        });
        this.setState({dontFills: newDontFills});
    }
    handleDontFillDelete(startDate){
        this.setState({dontFills: this.state.dontFills.filter(df => df.startDate !== startDate)});
    }
    render() {
        //console.log(this.state.scenarios);
        return (
          <MuiThemeProvider theme={theme}>
            <div className="App">
                <div className={isMobile ? "column" : "row"}>
                    <WeeklyProgram dontFills={this.state.dontFills}
                                   scenarios={this.state.scenarios}
                                   onDontFillAdd={(startDate, endDate) => this.handleDontFillAdd(startDate, endDate)}
                                   onDontFillDelete={startDate => this.handleDontFillDelete(startDate)}/>
                    <Controls onSchedule={s => this.setState({scenarios: s})} dontFills={this.state.dontFills}/>
                </div>
            </div>
          </MuiThemeProvider>
      );
  }
}

export default App;
