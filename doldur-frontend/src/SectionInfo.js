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
    renderTimes(){
        const times = Array(0);
        // eslint-disable-next-line
        this.props.sectionDetails.lectureTimes.map(t => {
            times.push(
                <div className={"section-date"}>
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
    render() {
        return (
            <div className={"section-info"}>
                <div>
                    {"Section " + this.props.sectionNo}
                </div>
                <Divider />
                <div className={"section-row"}>
                    {"Instructor: " + this.props.sectionDetails.instructor}
                </div>
                <div className={"section-row"}>
                    {"Surname: " + this.props.sectionDetails.surnameStart + "-" + this.props.sectionDetails.surnameEnd}
                </div>
                <div className={"section-row"}>
                    {this.renderTimes()}
                </div>
            </div>
        )
    }
}