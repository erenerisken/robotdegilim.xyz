import React from "react";
import {
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Typography,
    FormControlLabel,
    Checkbox,
    Divider
} from "@material-ui/core";

import "./AdvancedSettings.css"
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import TuneIcon from '@material-ui/icons/Tune';

export class AdvancedSettings extends React.Component {

    handleSurnameCheck(){
        this.props.onSettingsChange({
            checkSurname: !this.props.settings.checkSurname,
            checkDepartment: this.props.settings.checkDepartment,
            checkCollision: this.props.settings.checkCollision
        });
    }
    handleDepartmentCheck(){
        this.props.onSettingsChange({
            checkSurname: this.props.settings.checkSurname,
            checkDepartment: !this.props.settings.checkDepartment,
            checkCollision: this.props.settings.checkCollision
        });
    }
    handleCollisionCheck(){
        this.props.onSettingsChange({
            checkSurname: this.props.settings.checkSurname,
            checkDepartment: this.props.settings.checkDepartment,
            checkCollision: !this.props.settings.checkCollision
        });
    }

    render() {
        return (
            <div className={"settings-wrapper"}>
                <Accordion style={{background: "aliceblue"}}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls={"panel1a-content"}>
                        <div className={"settings-row"}>
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
                            </div>
                        </div>
                    </AccordionDetails>
                </Accordion>
            </div>
        )
    }
}