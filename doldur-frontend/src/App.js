import React from 'react';
import {isMobile} from "react-device-detect";
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import {WeeklyProgram} from "./WeeklyProgram";
import {Controls} from "./Controls";
import {WelcomeDialog} from "./WelcomeDialog";
import {Banner} from "./Banner";

import './App.css';
import {Colorset} from "./Colorset";

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
            dontFills: [],

            loaded: false,
        }

        this.dontFillColorset = new Colorset();
    }
    handleDontFillAdd(startDate, endDate, description){
        const newDontFills = this.state.dontFills.slice(0);
        newDontFills.push({
            startDate: startDate,
            endDate: endDate,
            description: description,
            color: this.dontFillColorset.getBlack(),
        });
        this.setState({dontFills: newDontFills});
    }
    handleDontFillDelete(startDate){
        this.setState({dontFills: this.state.dontFills.filter(df => df.startDate !== startDate)});
    }
    handleLoadingCompleted() {
        this.setState({loaded: true});
    }
    handleChangeDontFillColor(startDate) {
        const dontFills = this.state.dontFills.slice(0);
        this.setState({
            dontFills: dontFills.map(df => {
                if (df.startDate === startDate) {
                    return {
                        ...df,
                        color: this.dontFillColorset.getNextColor(),
                    }
                } else {
                    return df;
                }
            })
        });
    }
    render() {
        //console.log(this.state.scenarios);
        return (
          <MuiThemeProvider theme={theme}>
            <div className="App">
                <Banner />
                { this.state.loaded ? <WelcomeDialog /> : null }
                <div className={isMobile ? "column" : "row"}>
                    <WeeklyProgram dontFills={this.state.dontFills}
                                   scenarios={this.state.scenarios}
                                   onDontFillAdd={(startDate, endDate, desc) =>
                                       this.handleDontFillAdd(startDate, endDate, desc)}
                                   onChangeDontFillColor={startDate => this.handleChangeDontFillColor(startDate)}
                                   onDontFillDelete={startDate => this.handleDontFillDelete(startDate)}/>
                    <Controls onSchedule={s => this.setState({scenarios: s})}
                              dontFills={this.state.dontFills}
                              onDontFillAdd={(startDate, endDate, desc) =>
                                  this.handleDontFillAdd(startDate, endDate, desc)}
                              onLoadingCompleted={() => this.handleLoadingCompleted()}
                    />
                </div>
            </div>
          </MuiThemeProvider>
      );
  }
}

export default App;
