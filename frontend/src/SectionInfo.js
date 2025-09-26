import React, { useState } from "react";
import { Divider, TextField, IconButton, Tooltip } from "@material-ui/core";
import { Edit as EditIcon, Save as SaveIcon, Cancel as CancelIcon } from "@material-ui/icons";
import "./SectionInfo.css";

export const SectionInfo = ({ sectionDetails, color, onClassroomUpdate }) => {
  const [editingIndex, setEditingIndex] = useState(-1);
  const [tempClassroom, setTempClassroom] = useState("");
  
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


  const handleEditClick = (index, currentClassroom) => {
    setEditingIndex(index);
    setTempClassroom(currentClassroom || "");
  };

  const handleSaveClick = (index) => {
    try {
      if (onClassroomUpdate) {
        onClassroomUpdate(index, tempClassroom);
      }
      setEditingIndex(-1);
      setTempClassroom("");
    } catch (error) {
      console.error('Error saving classroom:', error);
      // Don't reset editing state if error occurs
    }
  };

  const handleCancelClick = () => {
    setEditingIndex(-1);
    setTempClassroom("");
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
        <div className="time-row classroom-row">
          <span>Classroom: </span>
          {editingIndex === index ? (
            <div className="classroom-edit">
              <TextField
                value={tempClassroom}
                onChange={(e) => setTempClassroom(e.target.value)}
                size="small"
                variant="outlined"
                placeholder="Enter classroom"
                style={{ marginLeft: 8, marginRight: 8, minWidth: 120 }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSaveClick(index);
                  }
                }}
              />
              <Tooltip title="Save">
                <IconButton 
                  size="small" 
                  onClick={() => handleSaveClick(index)}
                  style={{ color: '#4caf50' }}
                >
                  <SaveIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Cancel">
                <IconButton 
                  size="small" 
                  onClick={handleCancelClick}
                  style={{ color: '#f44336' }}
                >
                  <CancelIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </div>
          ) : (
            <div className="classroom-display">
              <span>{t.classroom || "TBA"}</span>
              {onClassroomUpdate && (
                <Tooltip title="Edit classroom manually">
                  <IconButton 
                    size="small" 
                    onClick={() => handleEditClick(index, t.classroom)}
                    style={{ marginLeft: 8, color: color?.main }}
                  >
                    <EditIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </div>
          )}
        </div>
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
