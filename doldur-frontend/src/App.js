import React from 'react';
import {isMobile} from "react-device-detect";
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import {WeeklyProgram} from "./WeeklyProgram";
import {Controls} from "./Controls";
import {WelcomeDialog} from "./WelcomeDialog";

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
    handleDontFillAdd(startDate, endDate, description){
        const newDontFills = this.state.dontFills.slice(0);
        newDontFills.push({
            startDate: startDate,
            endDate: endDate,
            description: description
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
                <WelcomeDialog />
                <div className={isMobile ? "column" : "row"}>
                    <WeeklyProgram dontFills={this.state.dontFills}
                                   scenarios={this.state.scenarios}
                                   onDontFillAdd={(startDate, endDate, desc) =>
                                       this.handleDontFillAdd(startDate, endDate, desc)}
                                   onDontFillDelete={startDate => this.handleDontFillDelete(startDate)}/>
                    <Controls onSchedule={s => this.setState({scenarios: s})}
                              dontFills={this.state.dontFills}
                              onDontFillAdd={(startDate, endDate, desc) =>
                                  this.handleDontFillAdd(startDate, endDate, desc)}/>
                </div>
            </div>
          </MuiThemeProvider>
      );
  }
}

export default App;
