import React from "react";
import {Paper, IconButton, Typography, TextField, Button, Tooltip} from "@material-ui/core";
import CloseIcon from '@material-ui/icons/Close';
import KeyboardArrowRightIcon from '@material-ui/icons/KeyboardArrowRight';
import KeyboardArrowLeftIcon from '@material-ui/icons/KeyboardArrowLeft';
import FastRewindIcon from '@material-ui/icons/FastRewind';
import PhotoCameraIcon from '@material-ui/icons/PhotoCamera';
import FastForwardIcon from '@material-ui/icons/FastForward';
import PaletteIcon from '@material-ui/icons/Palette';
import {ViewState} from "@devexpress/dx-react-scheduler";
import {
    Scheduler,
    WeekView,
    Appointments,
} from '@devexpress/dx-react-scheduler-material-ui';
import {isMobile} from "react-device-detect";

import {ExportCalendar} from "./ExportCalendar";

import "./WeeklyProgram.css"
import html2canvas from 'html2canvas';

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


    doCapture() {
        window.scrollTo(0, 0);

        // Convert the div to image (canvas)
        html2canvas(document.getElementById("screenshot")).then(function (canvas) {

            // Get the image data as JPEG and 0.9 quality (0.0 - 1.0)
            console.log(canvas.toDataURL("image/jpeg", 0.9));
            const a = document.createElement('a');
            document.body.appendChild(a);
            a.href = canvas.toDataURL("image/jpeg", 0.9);
            a.download = "schedule.jpeg";
            a.click();
            document.body.removeChild(a);
        });
    }

    handleScenarioChange(delta){
        this.setState({
            currentScenario: Math.min(this.props.scenarios.length-1, Math.max(0,
                this.state.currentScenario + delta))});
    }
    handleScenarioChangeAbsolute(val){
        const newCurrentScenario = isNaN(val) ? 1 : val;
        this.setState({currentScenario: Math.min(this.props.scenarios.length-1, Math.max(0,
                newCurrentScenario-1))});
    }
    handleDontFillAdd(startDate, endDate){
        this.props.onDontFillAdd(startDate, endDate, "FULL");
    }
    handleChangeDontFillColor(startDate) {
        this.props.onChangeDontFillColor(startDate);
    }
    convertTime(day, hour, min){
        //example : '2021-02-20T09:40'
        return "2021-02-" + (14 + day) + "T" + (hour < 10 ? "0" : "") + hour + ":" + (min < 10 ? "0" : "") + min;
    }
    convertToEntry(){
        /*if (this.props.scenarios.length <= 0){
            return [];
        }*/
        const coursesToDisplay = Array(0);
        let scenario = Array(0);
        let currentScenarioChanged = false;
        if (this.props.scenarios.length > 0 && this.state.currentScenario >= this.props.scenarios.length){
            this.setState({currentScenario: 0});
            currentScenarioChanged = true;
        }
        scenario = currentScenarioChanged ? this.props.scenarios[0] :
            this.props.scenarios[this.state.currentScenario];
        if (this.props.scenarios.length === 0){
            scenario = [];
        }
        scenario.map(c => {
            //console.log(c);
            c.section.lectureTimes.map(lt => {
                for(let i = lt.startHour; i<lt.endHour; i++){
                    coursesToDisplay.push({
                        type: "course",
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
        this.props.dontFills.map(df => {
            coursesToDisplay.push({
                type: "dontFill",
                title: df.description,
                color: {
                    main: df.color.main,
                    text: df.color.text,
                },
                startDate: df.startDate,
                endDate: df.endDate
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
                {data.type === "course"?
                    <div className={"program-text-container"}>
                        <div className={"program-title"} style={{color: data.color.text}}>
                            {data.title + "/" + data.section}
                        </div>
                        <div className={"program-title"} style={{color: data.color.text}}>
                            {data.classroom}
                        </div>
                    </div> :
                    <div className={"program-text-container"}>
                        <Tooltip title={data.title}>
                            <div className={"program-row"}>
                                <IconButton
                                    onClick={() => this.props.onDontFillDelete(data.startDate)}
                                    style={{padding: 0, marginLeft: 9}}
                                >
                                    <CloseIcon className={"dont-fill-button"} fontSize={"small"} style={{color: data.color.text}}/>
                                </IconButton>
                                <div className={"program-title-dont-fill"} style={{color: data.color.text}}>
                                    {data.title}
                                </div>
                                <IconButton style={{padding: 0, marginLeft: 9}}
                                            onClick={() => this.handleChangeDontFillColor(data.startDate)}
                                >
                                    <PaletteIcon className={"dont-fill-button"} fontSize={"small"} style={{color: data.color.text}} />
                                </IconButton>
                            </div>
                        </Tooltip>
                    </div>}
            </Appointments.AppointmentContent>
        )
    }
    TimeTableCell = ({startDate, endDate, onDontFillAdd, ...restProps}) => {
        if (startDate.getDay() > 4){
            return <WeekView.TimeTableCell {...restProps} style={{width: "0"}}/>
        }
        return (
            <WeekView.TimeTableCell
                                    {...restProps}
                                    onClick={() => this.handleDontFillAdd(startDate, endDate)}/>
        )
    }
    render() {
        const data = this.convertToEntry();
        return (
            <div style={isMobile ? styles.mobile : styles.desktop}>
                <Paper id="screenshot">
                    <Scheduler
                        id={"scheduler"}
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
                            timeTableCellComponent={this.TimeTableCell}
                        />
                        <Appointments appointmentContentComponent={this.AppointmentContent}/>
                    </Scheduler>
                </Paper>
                <div className={"program-vertical"}>
                    {this.props.scenarios.length > 0?
                    <div className={"program-row"}>
                        <IconButton onClick={() => this.handleScenarioChange(-10)}>
                            <FastRewindIcon fontSize={"small"} />
                        </IconButton>
                        <IconButton onClick={() => this.handleScenarioChange(-1)}>
                            <KeyboardArrowLeftIcon fontSize={"small"} />
                        </IconButton>
                        <div className={"program-typo-wrapper"}>
                            <Typography>
                                {"Scenario "}
                            </Typography>
                        </div>
                        <div className={"program-textfield-wrapper"}>
                            <TextField className={"program-textfield"}
                                       type={"number"}
                                       value={this.state.currentScenario+1}
                                       onChange={e => this.handleScenarioChangeAbsolute(parseInt(e.target.value))}/>
                        </div>
                        <div className={"program-typo-wrapper"}>
                            <Typography>
                                {" of " + this.props.scenarios.length}
                            </Typography>
                        </div>
                        <IconButton onClick={() => this.handleScenarioChange(1)}>
                            <KeyboardArrowRightIcon fontSize={"small"} />
                        </IconButton>
                        <IconButton onClick={() => this.handleScenarioChange(10)}>
                            <FastForwardIcon fontSize={"small"} />
                        </IconButton>
                    </div> : null}
                    {this.props.scenarios.length > 0 && !isMobile ? <div className={"program-calendar-wrapper"}>
                        <ExportCalendar events={data} />
                    </div> : null}
                    <Button
                        variant={"contained"}
                        color={"primary"}
                        style={{margin: "6pt"}}
                        startIcon={<PhotoCameraIcon />}
                        onClick={() => this.doCapture()}
                        >
                        Save as image
                    </Button>
                </div>
            </div>
        );
    }
}

const styles = {
    mobile: {
        margin: 12,
        width: "100%",
    },
    desktop: {
        margin: 12,
        width: "60%",
    },
}
