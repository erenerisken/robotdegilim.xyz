import React from "react";
import { Divider } from "@material-ui/core";
import "./SectionInfo.css";

export const SectionInfo = ({ sectionDetails, color }) => {
  const days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  const formatTime = (t) => {
    return t > 9 ? t.toString() : "0" + t.toString();
  };


  const renderTimes = () => {
    return sectionDetails.lectureTimes.map((t, index) => (
      <div className="section-date" key={index}>
        <div className="time-row">
          {days[t.day] +
            " " +
            t.startHour +
            "." +
            formatTime(t.startMin) +
            "-" +
            t.endHour +
            "." +
            formatTime(t.endMin)}
        </div>
        <div className="time-row">{"Classroom: " + t.classroom}</div>
      </div>
    ));
  };

  const renderCriteria = (c, index) => (
    <div className="section-row" key={index}>
      {"Department: " +
        c.dept +
        " Surname: " +
        c.surnameStart +
        "-" +
        c.surnameEnd}
    </div>
  );

  return (
    <div className="section-info">
      <div className="section-title">{"Section " + sectionDetails.sectionNumber}</div>
      <Divider />
      <div className="section-row">
        {"Instructor: " + sectionDetails.instructor}
      </div>
      {sectionDetails.criteria.map((c, index) => renderCriteria(c, index))}
      <div className="section-row">{renderTimes()}</div>
    </div>
  );
};
