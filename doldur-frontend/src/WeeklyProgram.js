import React from "react";
import {Paper, IconButton} from "@material-ui/core";
import ArrowBackIosIcon from '@material-ui/icons/ArrowBackIos';
import {ViewState} from "@devexpress/dx-react-scheduler";
import {
    Scheduler,
    WeekView,
    Appointments,
} from '@devexpress/dx-react-scheduler-material-ui';
import {isMobile} from "react-device-detect";

import "./WeeklyProgram.css"

const currentDate = '2018-11-01';

class DayScaleRow extends React.Component{
    render() {
        return (
            <div className={"dayscale-row"}>
                <div className={"dayscale-label"}>
                    Mon
                </div>
                <div className={"dayscale-label"}>
                    Tue
                </div>
                <div className={"dayscale-label"}>
                    Wed
                </div>
                <div className={"dayscale-label"}>
                    Thu
                </div>
                <div className={"dayscale-label"}>
                    Fri
                </div>
                <div className={"dayscale-label"}>
                    Sat
                </div>
                <div className={"dayscale-label"}>
                    Sun
                </div>
            </div>
        )
    }
}

export class WeeklyProgram extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            currentScenario: 0
        }
    }
    render() {
        return (
            <div className={isMobile ? "scheduler-mobile" : "scheduler-wrapper"}>
                <Paper>
                    <Scheduler
                        data={this.props.coursesToDisplay}
                    >
                        <ViewState
                            currentDate={currentDate}
                        />
                        <WeekView
                            startDayHour={7.667}
                            endDayHour={17.5}
                            cellDuration={60}
                            dayScaleRowComponent={DayScaleRow}
                        />
                        <Appointments/>
                    </Scheduler>
                </Paper>
                <div className={"program-row"}>

                </div>
            </div>
        );
    }
}