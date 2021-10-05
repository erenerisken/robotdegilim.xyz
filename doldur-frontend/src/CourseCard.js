import React from "react";
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Typography,
    FormGroup,
    FormControlLabel,
    Checkbox,
    Divider,
    Button,
    IconButton
} from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

import {Colorset} from "./Colorset";
import {SectionInfo} from "./SectionInfo";
import {CourseAdvancedSettings} from "./CourseAdvancedSettings";

import "./CourseCard.css"

export class CourseCard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedSections: this.props.sections.slice(0),
            sectionCount: props.course.sections.length,
            colorset: new Colorset(),

            expanded: false,
        }
    }

    handleToggle(sections){
        this.props.onToggle(sections);
    }
    handleSettingsChange(settings){
        this.props.onSettingsChange(settings);
    }
    handleNextColor(){
        this.props.onColorChange(this.state.colorset.getNextColor());
    }
    handlePreviousColor(){
        this.props.onColorChange(this.state.colorset.getPreviousColor());
    }
    toggleSections(){
        const newSelectedSections = Array(this.state.sectionCount).fill(!this.state.selectedSections[0]);
        this.setState({selectedSections: newSelectedSections});
        this.handleToggle(newSelectedSections);
    }

    renderCheckBoxes() {
        if (this.state.sectionCount <= 0){
            return null;
        }
        const boxes = Array(0);
        for (let i = 0; i < this.state.sectionCount; i++){
            boxes.push(
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={this.state.selectedSections[i]}
                            onChange={_ => {
                                    const newSelectedSections = this.state.selectedSections.slice(0);
                                    newSelectedSections[i] = !newSelectedSections[i];
                                    this.setState({selectedSections: newSelectedSections});
                                    this.handleToggle(newSelectedSections);
                                }
                            }
                            color={"primary"}
                        />
                    }
                    label={this.props.course.sections[i].sectionNumber}
                />);
        }
        return (
            <FormGroup row>
                {boxes}
                <Button
                    color={"primary"}
                    onClick={() => this.toggleSections()}
                >
                    Toggle
                </Button>
            </FormGroup>
        )
    }

    renderSectionDetails(){
        if (!this.state.expanded) {
            return [];
        }

        const ret = Array(0);
        for (let i = 0; i<this.props.course.sections.length; i++){
            ret.push(<SectionInfo
                sectionNo={i+1}
                sectionDetails={this.props.course.sections[i]}
                color={this.props.color}
            />);
        }
        return ret;
    }

    render() {
        return (
            <div className={"course-card"} style={{background: this.props.color.main}}>
                <div className={"course-row"}>
                    <IconButton size={"small"} onClick={() => this.props.onDelete()}>
                        <DeleteIcon fontSize={"inherit"}/>
                    </IconButton>
                    <Accordion className={"course-accordion"}
                               style={{background: this.props.color.main, width: "100%"}}
                               onChange={() => this.setState({expanded: !this.state.expanded})}
                    >
                        <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls={"panel1a-content"}>
                            <div className={"course-row"}>
                                <Typography style={{color: this.props.color.text}}>
                                    {this.props.course.abbreviation + ": " + this.props.course.name}
                                </Typography>
                            </div>
                        </AccordionSummary>
                        <AccordionDetails>
                            <div className={"course-details"}>
                                <div className={"course-left-row"}>
                                    <Typography style={{color: this.props.color.text}}>
                                        {"Course code: " + this.props.course.code}
                                    </Typography>
                                </div>
                                <Divider />
                                <div className={"course-centered-row"}>
                                    <div>
                                        Sections
                                    </div>
                                </div>
                                <Divider />
                                <div className={"course-row"}>
                                    {this.renderCheckBoxes()}
                                </div>
                                <div>
                                    <CourseAdvancedSettings color={this.props.color}
                                                            onSettingsChange={(s) => this.handleSettingsChange(s)}
                                                            onNextColor={() => this.handleNextColor()}
                                                            onPreviousColor={() => this.handlePreviousColor()}
                                                            settings={this.props.settings}/>
                                </div>
                                <Divider />
                                <div className={"course-sections"}>
                                    {this.renderSectionDetails()}
                                </div>
                            </div>
                        </AccordionDetails>
                    </Accordion>
                </div>
            </div>
        )
    }
}
