import React from "react";
import {Paper} from "@material-ui/core";
import {ViewState} from "@devexpress/dx-react-scheduler";
import {
    Scheduler,
    WeekView,
    Appointments,
} from '@devexpress/dx-react-scheduler-material-ui';

const currentDate = '2018-11-01';

export class WeeklyProgram extends React.Component{

    render() {
        return (
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
                        dayScaleLayoutComponent={() => null}
                    />
                    <Appointments/>
                </Scheduler>
            </Paper>
        );
    }
}