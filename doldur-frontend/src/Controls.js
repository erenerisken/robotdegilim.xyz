import React from "react";
import {
    TextField,
    Select,
    Button,
    FormControl,
    FormHelperText,
    MenuItem,
    InputLabel,
    Snackbar,
    Divider
} from "@material-ui/core";
import MuiAlert from '@material-ui/lab/Alert';
import AddIcon from '@material-ui/icons/Add';
import EventAvailableIcon from '@material-ui/icons/EventAvailable';

import {exampleCourses} from "./data/Course";
import {CourseCard} from "./CourseCard";

import "./Controls.css"

export class Controls extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            surname: "",
            department: "",
            semester: 0,
            alertMsg: "",
            errorDept: false,
            errorSemester: false,
            selectedCourses: [
                {
                    code: 5710213,
                    sections: []
                },
                {
                    code: 5710213,
                    sections: []
                },
                {
                    code: 5710140,
                    sections: []
                },
            ]
        }
    }

    getCourseByCode(code){
        for (let i = 0; i<exampleCourses.length; i++){
            if (exampleCourses[i].code === code){
                return exampleCourses[i];
            }
        }
        return null;
    }

    renderSemesterSelections(n){
        const ret = Array(0);
        ret.push(<MenuItem value={0}>---</MenuItem> )
        for (let i = 0; i<n; i++){
            ret.push(<MenuItem value={i+1}>{i+1}</MenuItem> );
        }
        return ret;
    }

    handleAddMustCourse(){
        this.setState({alertMsg: "", errorDept: false, errorSemester: false});
        if (this.state.department.length < 2){
            this.setState({alertMsg: "Please enter a correct department", errorDept: true});
            return;
        }
        if (this.state.semester < 1){
            this.setState({alertMsg: "Please choose a semester", errorSemester: true});
            return;
        }
    }

    handleAlertClose(){
        this.setState({alertMsg: ""});
    }
    handleDeleteCourse(i){
        const newSelectedCourses = this.state.selectedCourses.slice(0);
        newSelectedCourses[i] = null;
        this.setState({selectedCourses: newSelectedCourses});
    }
    render() {
        return (
            <div className={"control-wrapper"}>
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
                            required
                            label={"Surname"}
                            value={this.state.surname}
                            inputProps={{ maxLength: 12 }}
                            variant={"outlined"}
                            onChange={e => this.setState({surname: e.target.value})}
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
                            onChange={e => this.setState({department: e.target.value})}
                        />
                    </div>
                </div>
                <div className={"control-row"}>
                    <div className={"textfield-wrapper"}>
                        <FormControl className={"form-control"}>
                            <InputLabel>Semester</InputLabel>
                            <Select
                                error={this.state.errorSemester}
                                value={this.state.semester}
                                onChange={e => this.setState({semester: e.target.value})}
                            >
                                {this.renderSemesterSelections(8)}
                            </Select>
                            <FormHelperText>Ex: 2nd year Fall semester -> 3</FormHelperText>
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
                            onClick={() => console.log("Scheduling...")}>
                            Schedule
                        </Button>
                    </div>
                </div>
                <Divider />
                <div className={"control-row"}>
                    <div className={"centered-row"}>
                        Added Courses
                    </div>
                </div>
                <Divider />
                {this.state.selectedCourses.map((c, i) => {
                    return (
                        c !== null?
                        <CourseCard course={this.getCourseByCode(c.code)}
                                    onDelete={() => this.handleDeleteCourse(i)}/> : null
                    );
                })}
            </div>
        )
    }
}