import React from "react";
import {
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Typography,
    FormControlLabel,
    Checkbox,
    Divider,
    Button
} from "@material-ui/core";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import PaletteIcon from '@material-ui/icons/Palette';
import TuneIcon from '@material-ui/icons/Tune';

import "./CourseAdvancedSettings.css"

export class CourseAdvancedSettings extends React.Component{
    handleSurnameCheck(){
        this.props.onSettingsChange({
            checkSurname: !this.props.settings.checkSurname,
            checkDepartment: this.props.settings.checkDepartment,
            checkCollision: this.props.settings.checkCollision,
            disableCourse: this.props.settings.disableCourse,
        });
    }
    handleDepartmentCheck(){
        this.props.onSettingsChange({
            checkSurname: this.props.settings.checkSurname,
            checkDepartment: !this.props.settings.checkDepartment,
            checkCollision: this.props.settings.checkCollision,
            disableCourse: this.props.settings.disableCourse,
        });
    }
    handleCollisionCheck(){
        this.props.onSettingsChange({
            checkSurname: this.props.settings.checkSurname,
            checkDepartment: this.props.settings.checkDepartment,
            checkCollision: !this.props.settings.checkCollision,
            disableCourse: this.props.settings.disableCourse,
        });
    }
    handleDisableCourse(){
        this.props.onSettingsChange({
            checkSurname: this.props.settings.checkSurname,
            checkDepartment: this.props.settings.checkDepartment,
            checkCollision: this.props.settings.checkCollision,
            disableCourse: !this.props.settings.disableCourse,
        });
    }
    render() {
        return (
            <div className={"course-settings-wrapper"}>
                <Accordion style={{background: this.props.color.secondary}}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls={"panel1a-content"}>
                        <div className={"course-settings-row"}>
                            <TuneIcon color={"primary"} fontSize={"large"} />
                            <div className={"settings-typo"}>
                                <Typography>Advanced Settings</Typography>
                            </div>
                        </div>
                    </AccordionSummary>
                    <AccordionDetails>
                        <div className={"settings-accordion"}>
                            <Divider />
                            <div className={"settings-row"}>
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={this.props.settings.checkSurname}
                                            onChange={() => this.handleSurnameCheck()}
                                            color={"primary"}
                                        />}
                                    label={"Check surname"}/>
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={this.props.settings.checkDepartment}
                                            onChange={() => this.handleDepartmentCheck()}
                                            color={"primary"}
                                        />}
                                    label={"Check department"}/>
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={this.props.settings.checkCollision}
                                            onChange={() => this.handleCollisionCheck()}
                                            color={"primary"}
                                        />}
                                    label={"Check collision"}/>
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            checked={this.props.settings.disableCourse}
                                            onChange={() => this.handleDisableCourse()}
                                            color={"primary"}
                                        />}
                                    label={"Disable course"}/>
                            </div>
                            <Divider />
                            <div className={"settings-row"}>
                                <Button variant={"contained"}
                                        color={"primary"}
                                        startIcon={<PaletteIcon />}
                                        style={{marginTop: "6pt"}}
                                        onClick={() => this.props.onPreviousColor()}>
                                    Prev Color
                                </Button>
                                <Button variant={"contained"}
                                        color={"primary"}
                                        startIcon={<PaletteIcon />}
                                        style={{marginTop: "6pt", marginLeft: "6pt"}}
                                        onClick={() => this.props.onNextColor()}>
                                    Next Color
                                </Button>
                            </div>
                        </div>
                    </AccordionDetails>
                </Accordion>
            </div>
        )
    }
}
