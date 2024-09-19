import React from "react";
import {
    TextField,
    Select,
    Button,
    FormControl,
    FormHelperText,
    MenuItem,
    InputLabel,
    Paper,
    Snackbar,
    Typography,
    Divider,
} from "@material-ui/core";
import MuiAlert from '@material-ui/lab/Alert';
import AddIcon from '@material-ui/icons/Add';
import EventAvailableIcon from '@material-ui/icons/EventAvailable';
import Delete from "@material-ui/icons/Delete";
import SaveIcon from '@material-ui/icons/Save';
import SaveAltIcon from '@material-ui/icons/SaveAlt';
import { isMobile } from "react-device-detect";
import ls from "local-storage";

import { getAllCourses, getMusts } from "./data/Course";
import { compute_schedule } from "./schedule";
import { Client } from "./Client";
import { CourseCard } from "./CourseCard";
import { AddCourseWidget } from "./AddCourseWidget";
import { AddDontFillWidget } from "./AddDontFillWidget";
import { AdvancedSettings } from "./AdvancedSettings";
import { Colorset } from "./Colorset";
import { LoadingDialog } from "./LoadingDialog/LoadingDialog";

import "./Controls.css"

export class Controls extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            surname: "",
            department: "",
            semester: 0,
            alertMsg: "",
            errorDept: false,
            errorSemester: false,
            errorSurname: false,
            restoreAvailable: false,
            restoredInfo: {
                surname: "",
                department: "",
                semester: 0
            },
            selectedCourses: [],
            restoredCourses: [],
            allCourses: [],
            settings: {
                checkSurname: true,
                checkDepartment: true,
                checkCollision: true
            },
            restoredSettings: {
                checkSurname: true,
                checkDepartment: true,
                checkCollision: true
            },
            scenarios: [],
            colorset: new Colorset(),

            lastUpdated: 0,

            loading: false,
            loadingMessage: "Loading...",
        }

        this.client = new Client();
    }
    componentDidMount() {
        this.client.sendUpdateRequest();
        document.title = "Robot Değilim *-*";
        this.setState({ loading: true, loadingMessage: "Loading..." });
        getAllCourses().then(data => {
            this.setState({ allCourses: data });
            this.restoreData();
            this.setState({ loading: false });
            this.props.onLoadingCompleted();
        });
        this.client.getLastUpdated().then(lastUpdated => this.setState({ lastUpdated: lastUpdated }));
        if (isMobile) {
            document.body.style.zoom = "60%";
        }
        else {
            console.log(window.innerWidth);
            console.log(((window.outerWidth - 10) / window.innerWidth) * 100);
            document.body.style.zoom = parseInt(100 * window.innerWidth / 1920) + "%";
        }
    }
    loadRestoredData() {
        this.setState({
            selectedCourses: this.state.restoredCourses,
            settings: this.state.restoredSettings,
            surname: this.state.restoredInfo.surname,
            semester: this.state.restoredInfo.semester,
            department: this.state.restoredInfo.department,
        });
    }
    restoreData() {
        const restoredCourses = ls.get("restoredCourses");
        const restoredInfo = ls.get("restoredInfo");
        const restoredSettings = ls.get("restoredSettings");
        console.log(restoredCourses);
        this.setState({
            restoredCourses: restoredCourses !== null ? restoredCourses : [],
            restoredSettings: restoredSettings !== null ? restoredSettings : {
                checkSurname: true,
                checkDepartment: true,
                checkCollision: true,
                disableCourse: false
            },
            restoredInfo: restoredInfo !== null ? {
                surname: restoredInfo.surname,
                department: restoredInfo.department,
                semester: restoredInfo.semester
            } : {
                surname: "",
                department: "",
                semester: 0
            },
            restoreAvailable: restoredSettings !== null
        });
        console.log(restoredSettings);
        console.log(restoredInfo);
    }
    getCourseByCode(code) {
        for (let i = 0; i < this.state.allCourses.length; i++) {
            if (this.state.allCourses[i].code === code) {
                return this.state.allCourses[i];
            }
        }
        return null;
    }
    getSectionByNumber(c, n) {
        for (let i = 0; i < c.sections.length; i++) {
            if (c.sections[i].sectionNumber === n) {
                return c.sections[i];
            }
        }
        return null;
    }
    getColorByCourseCode(code) {
        for (let i = 0; i < this.state.selectedCourses.length; i++) {
            if (this.state.selectedCourses[i] === null) {
                continue;
            }
            if (this.state.selectedCourses[i].code === code) {
                return this.state.selectedCourses[i].color;
            }
        }
        return null;
    }
    renderSemesterSelections(n) {
        const ret = Array(0);
        ret.push(<MenuItem value={0}>---</MenuItem>)
        for (let i = 0; i < n; i++) {
            ret.push(<MenuItem value={i + 1}>{i + 1}</MenuItem>);
        }
        return ret;
    }

    handleAddMustCourse() {
        this.setState({ alertMsg: "", errorDept: false, errorSemester: false, errorSurname: false });
        if (this.state.department.length < 2) {
            this.setState({ alertMsg: "Please enter a correct department", errorDept: true });
            return;
        }
        if (this.state.semester < 1) {
            this.setState({ alertMsg: "Please choose a semester", errorSemester: true });
            return;
        }
        getMusts(this.state.department, this.state.semester).then(data => {
            if (data !== undefined) {
                // eslint-disable-next-line
                data.map(code => {
                    let exists = false;
                    this.state.selectedCourses.map(c => {
                        if (c !== null && c.code === code) {
                            exists = true;
                            return;
                        }
                    });
                    if (!exists) {
                        this.handleAddCourse(this.getCourseByCode(code));
                    }
                });
            }
        }).catch(_ => {
            this.setState({ alertMsg: "Must courses for your department are not available", errorDept: true });
        });
    }

    handleAlertClose() {
        this.setState({ alertMsg: "" });
    }
    handleDeleteCourse(i) {
        const newSelectedCourses = this.state.selectedCourses.slice(0);
        newSelectedCourses[i] = null;
        this.setState({ selectedCourses: newSelectedCourses });
    }
    handleToggle(i, sections) {
        const newSelectedCourses = this.state.selectedCourses.slice(0);
        newSelectedCourses[i].sections = sections;
        this.setState({ selectedCourses: newSelectedCourses });
        console.log("Course " + i + " sections:" + sections);
    }
    handleAddCourse(c) {
        if (c === null) {
            return;
        }
        const newSelectedCourses = this.state.selectedCourses.slice(0);
        newSelectedCourses.push({
            code: c.code,
            sections: Array(c.sections.length).fill(true),
            color: this.state.colorset.getNextColor(),
            settings: {
                checkSurname: true,
                checkDepartment: true,
                checkCollision: true,
                disableCourse: false
            }
        });
        this.setState({ selectedCourses: newSelectedCourses });
    }
    handleCourseSettings(i, s) {
        const newSelectedCourses = this.state.selectedCourses.slice(0);
        newSelectedCourses[i].settings = s;
        this.setState({ selectedCourses: newSelectedCourses });
    }
    handleCourseColor(i, c) {
        const newSelectedCourses = this.state.selectedCourses.slice(0);
        newSelectedCourses[i].color = c;
        this.setState({ selectedCourses: newSelectedCourses });
    }
    handleChangeSettings(s) {
        this.setState({ settings: s });
    }
    handleScheduleComplete(scenarios) {
        if (scenarios.length <= 0) {
            console.log("Fail!");
            this.setState({ alertMsg: "There is no available schedule for this criteria." });
        }
        const scenariosToSubmit = Array(0);
        scenarios.map(s => {
            const scenarioToPush = Array(0);
            s.map(c => {
                const currentCourse = this.getCourseByCode(c.code);
                const currentSection = this.getSectionByNumber(currentCourse, c.section);
                const currentColor = this.getColorByCourseCode(c.code);
                scenarioToPush.push({
                    abbreviation: currentCourse.abbreviation,
                    section: currentSection,
                    color: currentColor
                });
            });
            scenariosToSubmit.push(scenarioToPush);
        });
        this.props.onSchedule(scenariosToSubmit);
    }
    formatDf(df) {
        //           0123456789012345
        //example : '2021-02-20T09:40'
        return {
            day: df.startDate.getDay(),
            startHour: df.startDate.getHours(),
            startMin: df.startDate.getMinutes(),
            endHour: df.endDate.getHours(),
            endMin: df.endDate.getMinutes() - 1
        };
    }
    saveData() {
        ls.set("restoredCourses", this.state.selectedCourses);
        ls.set("restoredSettings", this.state.settings);
        ls.set("restoredInfo", {
            surname: this.state.surname,
            department: this.state.department,
            semester: this.state.semester
        });
    }
    handleScheduleBegin() {
        this.setState({ alertMsg: "", errorDept: false, errorSemester: false, errorSurname: false });
        if (this.state.department.length < 2) {
            this.setState({ alertMsg: "Please enter a correct department", errorDept: true });
            return;
        }
        if (this.state.surname.length < 2 && this.state.settings.checkSurname) {
            this.setState({ alertMsg: "Please enter at least 2 letters of your surname", errorSurname: true });
            return;
        }
        const courseData = Array(0);
        const dontFills = Array(0);
        // eslint-disable-next-line
        this.state.selectedCourses.map(c => {
            if (c === null || c.settings.disableCourse) {
                return null;
            }
            const currentCourse = this.getCourseByCode(c.code);
            const courseToPush = {
                code: c.code,
                category: currentCourse.category,
                checkSurname: this.state.settings.checkSurname && c.settings.checkSurname,
                checkCollision: this.state.settings.checkCollision && c.settings.checkCollision,
                checkDepartment: this.state.settings.checkDepartment && c.settings.checkDepartment,
                sections: Array(0)
            };
            for (let i = 0; i < currentCourse.sections.length; i++) {
                const sectionToPush = {
                    sectionNumber: currentCourse.sections[i].sectionNumber,
                    minYear: currentCourse.sections[i].minYear,
                    maxYear: currentCourse.sections[i].maxYear,
                    toggle: c.sections[i],
                    criteria: currentCourse.sections[i].criteria,
                    lectureTimes: Array(0)
                };
                currentCourse.sections[i].lectureTimes.map(t => sectionToPush.lectureTimes.push(t));
                if (sectionToPush.criteria.length <= 0) {
                    sectionToPush.criteria = [{
                        dept: "ALL",
                        surnameStart: "AA",
                        surnameEnd: "ZZ"
                    }];
                }
                if (sectionToPush.lectureTimes && sectionToPush.lectureTimes[0])
                    courseToPush.sections.push(sectionToPush);
            }
            if (courseToPush.sections && courseToPush.sections.length > 0) {
                console.log(courseToPush.code);

                courseData.push(courseToPush)
            }

        });
        this.props.dontFills.map(df => {
            const formattedDf = this.formatDf(df);
            dontFills.push({
                times: [formattedDf]
            })
        });
        //console.log(courseData);
        console.log(dontFills);
        this.setState({ loading: true, loadingMessage: "Computing schedule..." });
        setTimeout(() => {
            const calculatedSchedule = compute_schedule(
                this.state.surname.slice(0, 2),
                this.state.department,
                0,
                courseData,
                dontFills
            );
            //console.log(calculatedSchedule);
            this.setState({ scenario: calculatedSchedule, loading: false });
            this.handleScheduleComplete(calculatedSchedule);
        }, 500);
    }
    handleClearCourses() {
        this.setState({ selectedCourses: [] });
    }
    render() {
        return (
            <Paper style={isMobile ? styles.mobile : styles.desktop}>
                <Snackbar
                    open={this.state.alertMsg !== ""}
                    autoHideDuration={5000}
                    onClose={() => this.handleAlertClose()}
                >
                    <MuiAlert elevation={6} variant={"filled"} onClose={() => this.handleAlertClose()} severity={"error"}>
                        {this.state.alertMsg}
                    </MuiAlert>
                </Snackbar>
                <div className={"control-row"}>
                    <div className={"textfield-wrapper"}>
                        <TextField
                            required={this.state.settings.checkSurname}
                            error={this.state.errorSurname}
                            label={"Surname"}
                            value={this.state.surname}
                            inputProps={{ maxLength: 12 }}
                            variant={"outlined"}
                            size={'small'}
                            onChange={e => this.setState({ surname: e.target.value.toUpperCase() })}
                        />
                    </div>
                    <div className={"textfield-wrapper"}>
                        <TextField
                            required
                            error={this.state.errorDept}
                            label={"Department"}
                            value={this.state.department}
                            inputProps={{ maxLength: 12 }}
                            variant={"outlined"}
                            size={'small'}
                            onChange={e => this.setState({ department: e.target.value.toUpperCase() })}
                        />
                    </div>
                </div>
                <div className={"control-row"}>
                    <div className={"textfield-wrapper"}>
                        <FormControl className={"form-control"} variant={"outlined"} size={"small"}>
                            <InputLabel style={{ background: 'white' }}>Semester</InputLabel>
                            <Select
                                error={this.state.errorSemester}
                                value={this.state.semester}
                                onChange={e => this.setState({ semester: e.target.value })}
                            >
                                {this.renderSemesterSelections(8)}
                            </Select>
                            <FormHelperText>Ex: 2nd year Fall semester -{">"} 3</FormHelperText>
                        </FormControl>
                    </div>
                    <div className={"control-button"}>
                        <Button
                            variant={"contained"}
                            color={"secondary"}
                            startIcon={<AddIcon />}
                            onClick={() => this.handleAddMustCourse()}>
                            Add Must Courses
                        </Button>
                    </div>
                    <div className={"control-button"}>
                        <Button
                            variant={"contained"}
                            color={"primary"}
                            startIcon={<EventAvailableIcon />}
                            onClick={() => this.handleScheduleBegin()}>
                            Schedule
                        </Button>
                    </div>
                    <div className={"control-button"}>
                        <Button
                            variant={"contained"}
                            style={{ backgroundColor: "red", color: "white" }}
                            startIcon={<Delete style={{ color: "white" }} />}
                            onClick={() => this.handleClearCourses()}>
                            Clear
                        </Button>
                    </div>
                </div>
                <AdvancedSettings settings={this.state.settings} onSettingsChange={s => this.handleChangeSettings(s)} />
                <div className={"control-row"}>
                    <Button variant={"contained"}
                        color={"primary"}
                        onClick={() => this.saveData()}
                        startIcon={<SaveIcon />} style={{ margin: "6pt" }}>
                        Save
                    </Button>
                    {this.state.restoreAvailable ?
                        <Button
                            variant={"contained"}
                            color={"primary"}
                            onClick={() => this.loadRestoredData()}
                            startIcon={<SaveAltIcon />} style={{ margin: "6pt" }}>
                            Load
                        </Button> : null}
                </div>
                <Divider />
                <div className={"control-row"}>
                    <div className={"centered-row"}>
                        Added Courses
                    </div>
                </div>
                <Divider />
                <div className={"control-courses"}>
                    {this.state.selectedCourses.map((c, i) => {
                        return (
                            c !== null ?
                                <CourseCard course={this.getCourseByCode(c.code)}
                                    onDelete={() => this.handleDeleteCourse(i)}
                                    onToggle={sections => this.handleToggle(i, sections)}
                                    color={c.color}
                                    settings={c.settings}
                                    sections={c.sections}
                                    onSettingsChange={(s) => this.handleCourseSettings(i, s)}
                                    onColorChange={(c) => this.handleCourseColor(i, c)} /> : null
                        );
                    })}
                </div>
                <AddCourseWidget
                    courses={this.state.allCourses}
                    onCourseAdd={c => this.handleAddCourse(c)} />
                <AddDontFillWidget startHour={8}
                    startMin={40}
                    endHour={17}
                    endMin={30}
                    onDontFillAdd={(startDate, endDate, desc) =>
                        this.props.onDontFillAdd(startDate, endDate, desc)} />
                {
                    this.state.loading ? <LoadingDialog text={this.state.loadingMessage} /> : null
                }
                {console.log(this.state.lastUpdated)}
                {
                    this.state.lastUpdated ?
                        <Typography>
                            {
                                "Course data is updated at " +
                                this.state?.lastUpdated?.u
                            }
                            <br />
                            {
                                "   Last added Semester: " +
                                this.state?.lastUpdated?.t.split(":")[1]
                            }
                        </Typography> :
                        null
                }
            </Paper>
        )
    }
}

const styles = {
    mobile: {
        background: "white",
        margin: 12,
        width: "100%",
        paddingBottom: 12,
    },
    desktop: {
        background: "white",
        margin: 12,
        width: "fit-content",
        height: "fit-content",
        paddingBottom: 12,
    },
}
