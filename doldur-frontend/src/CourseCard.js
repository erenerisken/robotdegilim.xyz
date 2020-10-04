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

import {SectionInfo} from "./SectionInfo";

import "./CourseCard.css"

export class CourseCard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedSections: Array(props.course.sections.length).fill(true),
            sectionCount: props.course.sections.length
        }
    }

    handleToggle(sections){
        this.props.onToggle(sections);
    }

    toggleSections(){
        this.setState({selectedSections: Array(this.state.sectionCount).fill(!this.state.selectedSections[0])});
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
                            onChange={e => {
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
                    <Accordion style={{background: this.props.color.main}}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls={"panel1a-content"}>
                            <Typography style={{color: this.props.color.text}}>
                                {this.props.course.abbreviation + ": " + this.props.course.name}
                            </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <div className={"course-details"}>
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
                                <Divider />
                                {this.renderSectionDetails()}
                            </div>
                        </AccordionDetails>
                    </Accordion>
                </div>
            </div>
        )
    }
}