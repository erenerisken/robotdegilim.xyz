import React, { useState } from "react";
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
  IconButton,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";

import { Colorset } from "./Colorset";
import { SectionInfo } from "./SectionInfo";
import { CourseAdvancedSettings } from "./CourseAdvancedSettings";

import "./CourseCard.css";

export const CourseCard = ({
  course,
  color,
  sections,
  onToggle,
  onSettingsChange,
  onColorChange,
  onDelete,
  settings,
}) => {
  const [selectedSections, setSelectedSections] = useState(sections.slice(0));
  const [expanded, setExpanded] = useState(false);
  const [colorset] = useState(new Colorset());

  const handleToggle = (sections) => {
    onToggle(sections);
  };

  const handleSettingsChange = (settings) => {
    onSettingsChange(settings);
  };

  const handleNextColor = () => {
    onColorChange(colorset.getNextColor());
  };

  const handlePreviousColor = () => {
    onColorChange(colorset.getPreviousColor());
  };

  const toggleSections = () => {
    const newSelectedSections = Array(course.sections.length).fill(
      !selectedSections[0]
    );
    setSelectedSections(newSelectedSections);
    handleToggle(newSelectedSections);
  };

  const renderCheckBoxes = () => {
    if (course.sections.length <= 0) return null;
    return (
      <FormGroup row>
        {course.sections.map((section, i) => (
          <FormControlLabel
            key={i}
            control={
              <Checkbox
                checked={selectedSections[i]}
                onChange={() => {
                  const newSelectedSections = [...selectedSections];
                  newSelectedSections[i] = !newSelectedSections[i];
                  setSelectedSections(newSelectedSections);
                  handleToggle(newSelectedSections);
                }}
                color="primary"
              />
            }
            label={section.sectionNumber}
          />
        ))}
        <Button color="primary" onClick={toggleSections}>
          Toggle
        </Button>
      </FormGroup>
    );
  };

  return (
    <div className="course-card" style={{ background: color.main }}>
      <div className="course-row">
        <IconButton size="small" onClick={onDelete}>
          <DeleteIcon fontSize="inherit" />
        </IconButton>
        <Accordion
          className="course-accordion"
          style={{ background: color.main, width: "100%" }}
          onChange={() => setExpanded(!expanded)}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <div className="course-row">
              <Typography style={{ color: color.text }}>
                {course.abbreviation + ": " + course.name}
              </Typography>
            </div>
          </AccordionSummary>
          <AccordionDetails>
            <div className="course-details">
              <div className="course-left-row">
                <Typography style={{ color: color.text }}>
                  {"Course code: " + course.code}
                </Typography>
              </div>
              <Divider />
              <div className="course-centered-row">Sections</div>
              <Divider />
              <div className="course-row">{renderCheckBoxes()}</div>
              <CourseAdvancedSettings
                color={color}
                onSettingsChange={handleSettingsChange}
                onNextColor={handleNextColor}
                onPreviousColor={handlePreviousColor}
                settings={settings}
              />
              <Divider />
              <div className="course-sections">
                {expanded &&
                  course.sections.map((section, i) => (
                    <SectionInfo
                      key={i}
                      sectionNo={i + 1}
                      sectionDetails={section}
                      color={color}
                    />
                  ))}
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
    </div>
  );
};
