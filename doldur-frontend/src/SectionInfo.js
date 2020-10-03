import React from "react";
import {Divider} from "@material-ui/core";

import "./SectionInfo.css"

export class SectionInfo extends React.Component {
    constructor(props) {
        super(props);
        this.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    }
    formatTime(t){
        return t > 9 ? t.toString() : "0" + t.toString();
    }
    getDepartmentCriteria(){
        let ret = "";
        for (let i = 0; i<this.props.sectionDetails.dept.length; i++){
            ret += this.props.sectionDetails.dept[i] + " ";
        }
        return ret;
    }
    renderTimes(){
        const times = Array(0);
        // eslint-disable-next-line
        this.props.sectionDetails.lectureTimes.map(t => {
            times.push(
                <div className={"section-date"} style={{background: this.props.color.ternary}}>
                    <div className={"time-row"}>
                        {this.days[t.day] + " " + t.startHour + "." + this.formatTime(t.startMin) + "-" +
                            t.endHour + "." + this.formatTime(t.endMin)
                        }
                    </div>
                    <div className={"time-row"}>
                        {"Classroom: " + t.classroom}
                    </div>
                </div>);
        });
        return times;
    }
    renderCriteria(c){
        return (
            <div className={"section-row"}>
                {"Department: " + c.dept + " Surname: " + c.surnameStart + "-" + c.surnameEnd}
            </div>
        )
    }
    render() {
        return (
            <div className={"section-info"} style={{background: this.props.color.secondary}}>
                <div>
                    {"Section " + this.props.sectionNo}
                </div>
                <Divider />
                <div className={"section-row"}>
                    {"Instructor: " + this.props.sectionDetails.instructor}
                </div>
                {this.props.sectionDetails.criteria.map(c => this.renderCriteria(c))}
                <div className={"section-row"}>
                    {this.renderTimes()}
                </div>
            </div>
        )
    }
}