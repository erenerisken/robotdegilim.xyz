import React from "react";
import {
    Paper,
    IconButton,
    Typography,
    TextField,
    Button,
    Menu,
    MenuItem,
} from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import KeyboardArrowRightIcon from "@material-ui/icons/KeyboardArrowRight";
import KeyboardArrowLeftIcon from "@material-ui/icons/KeyboardArrowLeft";
import FastRewindIcon from "@material-ui/icons/FastRewind";
import PhotoCameraIcon from "@material-ui/icons/PhotoCamera";
import FastForwardIcon from "@material-ui/icons/FastForward";
import PaletteIcon from "@material-ui/icons/Palette";
import { ViewState } from "@devexpress/dx-react-scheduler";
import {
    Scheduler,
    WeekView,
    Appointments,
} from "@devexpress/dx-react-scheduler-material-ui";
import { isMobile } from "react-device-detect";
import { Colorset } from "./Colorset";
import { ExportCalendar } from "./ExportCalendar";
import { toJpeg } from "html-to-image";
import "./WeeklyProgram.css";
import { selectedGridRowsCountSelector } from "@material-ui/data-grid";

const currentDate = "2021-02-20";

class DayScaleRow extends React.Component {
    render() {
        return (
            <div className={"dayscale-row"}>
                <div className={"dayscale-label"}>Mon</div>
                <div className={"dayscale-label"}>Tue</div>
                <div className={"dayscale-label"}>Wed</div>
                <div className={"dayscale-label"}>Thu</div>
                <div className={"dayscale-label"}>Fri</div>
            </div>
        );
    }
}

class DontFillBlock extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            editing: false,
            anchorEl: null,
            selectedColor: null,
        };
        this.colorset = new Colorset();
    }

    handleOpenColorPalette = (event) => {
        this.setState({ anchorEl: event.currentTarget });
    };

    handleColorSelect = (color) => {
        this.setState({ selectedColor: color });
        this.props.onChangeDontFillColor(color);
        this.handleClose();
    };

    handleClose = () => {
        this.setState({ anchorEl: null });
    };

    handleDescriptionChange(e) {
        this.props.onChangeDontFillDescription(e.target.value);
    }

    handleTextFieldKeyDown(e) {
        if (e.keyCode === 13) {
            this.setState({ editing: false });
        }
    }

    render() {
        const open = Boolean(this.state.anchorEl);
        const colors = this.colorset.colors;
        return (
            <div className={"program-text-container-df"}>
                <div className={"program-row-df"}>
                    <IconButton
                        onClick={() => this.props.onDontFillDelete()}
                        style={{ padding: 0 }}
                    >
                        <CloseIcon
                            fontSize={"small"}
                            style={{ color: this.props.data.color.text }}
                        />
                    </IconButton>
                    {this.state.editing ? (
                        <TextField
                            value={this.props.data.title}
                            className={"df-description-text-field"}
                            InputProps={{
                                style: { color: this.props.data.color.text },
                            }}
                            onChange={(e) => this.handleDescriptionChange(e)}
                            onKeyDown={(e) => this.handleTextFieldKeyDown(e)}
                            onBlur={() => this.setState({ editing: false })}
                        />
                    ) : (
                        <div
                            className={"program-title-dont-fill"}
                            style={{ color: this.props.data.color.text }}
                            onClick={() => this.setState({ editing: true })}
                        >
                            {this.props.data.title}
                        </div>
                    )}
                    <IconButton
                        style={{ padding: 0 }}
                        id="palette-button"
                        aria-controls={open ? "palette-menu" : undefined}
                        aria-haspopup="true"
                        aria-expanded={open ? "true" : undefined}
                        onClick={this.handleOpenColorPalette}
                    >
                        <PaletteIcon
                            fontSize={"small"}
                            style={{ color: this.props.data.color.text }}
                        />
                    </IconButton>
                    <Menu
                        id="palette-menu"
                        open={open}
                        anchorEl={this.state.anchorEl}
                        onClose={this.handleClose}
                        MenuListProps={{
                            "aria-labelledby": "palette-button",
                        }}
                        PaperProps={{
                            style: {
                                backgroundColor: "black",
                            },
                        }}
                    >
                        <div
                            style={{
                                display: "grid",
                                gridTemplateColumns: "repeat(3, 1fr)",
                                gap: "5px",
                                padding: "5px",
                                paddingTop: "0px",
                                paddingBottom: "0px",
                                backgroundColor: "black",
                            }}
                        >
                            {colors.map((color) => (
                                <MenuItem
                                    key={color.main}
                                    onClick={() =>
                                        this.handleColorSelect(color)
                                    }
                                    style={{ padding: 0 }}
                                >
                                    <div
                                        style={{
                                            width: "30px",
                                            height: "30px",
                                            backgroundColor: color.main,
                                            borderRadius: "4px",
                                        }}
                                    ></div>
                                </MenuItem>
                            ))}
                        </div>
                    </Menu>
                </div>
            </div>
        );
    }
}

export class WeeklyProgram extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentScenario: 0,
        };
    }

    doCapture() {
        const node = document.getElementById("screenshot");

        toJpeg(node, { quality: 0.95 })
            .then((dataUrl) => {
                const link = document.createElement("a");
                link.download = "schedule.jpeg";
                link.href = dataUrl;
                link.click();
            })
            .catch((error) => {
                console.error("Oops, something went wrong!", error);
            });
    }

    handleScenarioChange(delta) {
        this.setState({
            currentScenario: Math.min(
                this.props.scenarios.length - 1,
                Math.max(0, this.state.currentScenario + delta)
            ),
        });
    }
    handleScenarioChangeAbsolute(val) {
        const newCurrentScenario = isNaN(val) ? 1 : val;
        this.setState({
            currentScenario: Math.min(
                this.props.scenarios.length - 1,
                Math.max(0, newCurrentScenario - 1)
            ),
        });
    }
    handleDontFillAdd(startDate, endDate) {
        this.props.onDontFillAdd(startDate, endDate, "FULL");
    }
    handleChangeDontFillColor(startDate, color) {
        this.props.onChangeDontFillColor(startDate, color);
    }
    handleChangeDontFillDescription(startDate, newDescription) {
        this.props.onChangeDontFillDescription(startDate, newDescription);
    }
    convertTime(day, hour, min) {
        //example : '2021-02-20T09:40'
        return (
            "2021-02-" +
            (14 + day) +
            "T" +
            (hour < 10 ? "0" : "") +
            hour +
            ":" +
            (min < 10 ? "0" : "") +
            min
        );
    }
    convertToEntry() {
        /*if (this.props.scenarios.length <= 0){
            return [];
        }*/
        const coursesToDisplay = Array(0);
        let scenario = Array(0);
        let currentScenarioChanged = false;
        if (
            this.props.scenarios.length > 0 &&
            this.state.currentScenario >= this.props.scenarios.length
        ) {
            this.setState({ currentScenario: 0 });
            currentScenarioChanged = true;
        }
        scenario = currentScenarioChanged
            ? this.props.scenarios[0]
            : this.props.scenarios[this.state.currentScenario];
        if (this.props.scenarios.length === 0) {
            scenario = [];
        }
        scenario.map((c) => {
            //console.log(c);
            c.section.lectureTimes.map((lt) => {
                for (let i = lt.startHour; i < lt.endHour; i++) {
                    coursesToDisplay.push({
                        type: "course",
                        title: c.abbreviation,
                        section: c.section.sectionNumber,
                        classroom:
                            lt.classroom !== undefined ? lt.classroom : "-",
                        startDate: this.convertTime(lt.day, i, lt.startMin + 3),
                        endDate: this.convertTime(lt.day, i + 1, lt.endMin + 5),
                        color: c.color,
                    });
                }
            });
        });
        this.props.dontFills.map((df) => {
            coursesToDisplay.push({
                type: "dontFill",
                title: df.description,
                color: {
                    main: df.color.main,
                    text: df.color.text,
                },
                startDate: df.startDate,
                endDate: df.endDate,
            });
        });
        return coursesToDisplay;
    }
    CustomAppointment({ formatDate, ...restProps }) {
        return (
            <WeekView.AppointmentLayer
                {...restProps}
                formatDate={(_) => ""}
                className={"custom-appointment"}
            />
        );
    }
    AppointmentContent = ({ data, ...restProps }) => {
        return (
            <Appointments.AppointmentContent
                data={data}
                {...restProps}
                className={"program-appointment"}
                style={{ background: data.color.main }}
            >
                {data.type === "course" ? (
                    <div className={"program-text-container"}>
                        <div
                            className={"program-title"}
                            style={{ color: data.color.text }}
                        >
                            {data.title + "/" + data.section}
                        </div>
                        <div
                            className={"program-title-bottom"}
                            style={{ color: data.color.text }}
                        >
                            {data.classroom}
                        </div>
                    </div>
                ) : (
                    <DontFillBlock
                        data={data}
                        onDontFillDelete={() =>
                            this.props.onDontFillDelete(data.startDate)
                        }
                        onChangeDontFillColor={(color) =>
                            this.handleChangeDontFillColor(
                                data.startDate,
                                color
                            )
                        }
                        onChangeDontFillDescription={(newDescription) =>
                            this.handleChangeDontFillDescription(
                                data.startDate,
                                newDescription
                            )
                        }
                    />
                )}
            </Appointments.AppointmentContent>
        );
    };
    TimeTableCell = ({ startDate, endDate, onDontFillAdd, ...restProps }) => {
        if (startDate.getDay() > 4) {
            return (
                <WeekView.TimeTableCell {...restProps} style={{ width: "0" }} />
            );
        }
        return (
            <WeekView.TimeTableCell
                {...restProps}
                onClick={() => this.handleDontFillAdd(startDate, endDate)}
            />
        );
    };
    render() {
        const data = this.convertToEntry();
        return (
            <div style={isMobile ? styles.mobile : styles.desktop}>
                <Paper id="screenshot">
                    <Scheduler id={"scheduler"} data={data}>
                        <ViewState currentDate={currentDate} />
                        <WeekView
                            startDayHour={7.667}
                            endDayHour={17.5}
                            cellDuration={60}
                            dayScaleRowComponent={DayScaleRow}
                            appointmentLayerComponent={this.CustomAppointment}
                            timeTableCellComponent={this.TimeTableCell}
                        />
                        <Appointments
                            appointmentContentComponent={
                                this.AppointmentContent
                            }
                        />
                    </Scheduler>
                </Paper>
                <div className={"program-vertical"}>
                    {this.props.scenarios.length > 0 ? (
                        <div className={"program-row"}>
                            <IconButton
                                onClick={() => this.handleScenarioChange(-10)}
                            >
                                <FastRewindIcon fontSize={"small"} />
                            </IconButton>
                            <IconButton
                                onClick={() => this.handleScenarioChange(-1)}
                            >
                                <KeyboardArrowLeftIcon fontSize={"small"} />
                            </IconButton>
                            <div className={"program-typo-wrapper"}>
                                <Typography>{"Scenario "}</Typography>
                            </div>
                            <div className={"program-textfield-wrapper"}>
                                <TextField
                                    className={"program-textfield"}
                                    type={"number"}
                                    value={this.state.currentScenario + 1}
                                    onChange={(e) =>
                                        this.handleScenarioChangeAbsolute(
                                            parseInt(e.target.value)
                                        )
                                    }
                                />
                            </div>
                            <div className={"program-typo-wrapper"}>
                                <Typography>
                                    {" of " + this.props.scenarios.length}
                                </Typography>
                            </div>
                            <IconButton
                                onClick={() => this.handleScenarioChange(1)}
                            >
                                <KeyboardArrowRightIcon fontSize={"small"} />
                            </IconButton>
                            <IconButton
                                onClick={() => this.handleScenarioChange(10)}
                            >
                                <FastForwardIcon fontSize={"small"} />
                            </IconButton>
                        </div>
                    ) : null}
                    {this.props.scenarios.length > 0 && !isMobile ? (
                        <div className={"program-calendar-wrapper"}>
                            <ExportCalendar events={data} />
                        </div>
                    ) : null}
                    <Button
                        variant={"contained"}
                        color={"primary"}
                        style={{ margin: "6pt" }}
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
        flex: "1 1 0",
    },
};
