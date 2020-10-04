import React from "react";
import {Paper, IconButton, Typography} from "@material-ui/core";
import KeyboardArrowRightIcon from '@material-ui/icons/KeyboardArrowRight';
import KeyboardArrowLeftIcon from '@material-ui/icons/KeyboardArrowLeft';
import {ViewState} from "@devexpress/dx-react-scheduler";
import {
    Scheduler,
    WeekView,
    Appointments,
} from '@devexpress/dx-react-scheduler-material-ui';
import {isMobile} from "react-device-detect";

import "./WeeklyProgram.css"

const currentDate = '2021-02-20';



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
        };
    }

    handleScenarioChange(delta){
        this.setState({
            currentScenario: Math.min(this.props.scenarios.length-1, Math.max(0,
                this.state.currentScenario + delta))});
    }
    convertTime(day, hour, min){
        //example : '2021-02-20T09:40'
        return "2021-02-" + (14 + day) + "T" + (hour < 10 ? "0" : "") + hour + ":" + (min < 10 ? "0" : "") + min;
    }
    convertToEntry(){
        if (this.props.scenarios.length <= 0){
            return [];
        }
        const coursesToDisplay = Array(0);
        const scenario = this.props.scenarios[this.state.currentScenario];
        scenario.map(c => {
            //console.log(c);
            c.section.lectureTimes.map(lt => {
                for(let i = lt.startHour; i<lt.endHour; i++){
                    coursesToDisplay.push({
                        title: c.abbreviation,
                        section: c.section.sectionNumber,
                        classroom: lt.classroom !== undefined ? lt.classroom : "-",
                        startDate: this.convertTime(lt.day, i, lt.startMin),
                        endDate: this.convertTime(lt.day, i+1, lt.endMin),
                        color: c.color
                    })
                }
            });
        });
        return coursesToDisplay;
    }
    CustomAppointment({formatDate, ...restProps}){
        return (
            <WeekView.AppointmentLayer {...restProps} formatDate={(_) => ""} className={"custom-appointment"} />
        )
    }
    AppointmentContent = ({data, ...restProps}) => {
        return (
            <Appointments.AppointmentContent data={data}
                                             {...restProps}
                                             className={"program-appointment"} style={{background: data.color.main}}>
                <div className={"program-text-container"}>
                    <div className={"program-title"} style={{color: data.color.text}}>
                        {data.title + "/" + data.section}
                    </div>
                    <div className={"program-title"} style={{color: data.color.text}}>
                        {data.classroom}
                    </div>
                </div>
            </Appointments.AppointmentContent>
        )
    }
    render() {
        const data = this.convertToEntry();
        //console.log(data);
        return (
            <div className={isMobile ? "scheduler-mobile" : "scheduler-wrapper"}>
                <Paper>
                    <Scheduler
                        data={data}
                    >
                        <ViewState
                            currentDate={currentDate}
                        />
                        <WeekView
                            startDayHour={7.667}
                            endDayHour={17.5}
                            cellDuration={60}
                            dayScaleRowComponent={DayScaleRow}
                            appointmentLayerComponent={this.CustomAppointment}
                        />
                        <Appointments appointmentContentComponent={this.AppointmentContent}/>
                    </Scheduler>
                </Paper>
                {this.props.scenarios.length > 0?
                <div className={"program-row"}>
                    <IconButton onClick={() => this.handleScenarioChange(-1)}>
                        <KeyboardArrowLeftIcon fontSize={"small"} />
                    </IconButton>
                    <div className={"program-typo-wrapper"}>
                        <Typography>
                            {"Scenario " + (this.state.currentScenario+1) + " of " + this.props.scenarios.length}
                        </Typography>
                    </div>
                    <IconButton onClick={() => this.handleScenarioChange(1)}>
                        <KeyboardArrowRightIcon fontSize={"small"} />
                    </IconButton>
                </div> : null}
            </div>
        );
    }
}