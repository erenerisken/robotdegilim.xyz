import React from "react";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  FormControlLabel,
  Checkbox,
  Divider,
  Button,
} from "@material-ui/core";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import PaletteIcon from "@material-ui/icons/Palette";
import TuneIcon from "@material-ui/icons/Tune";

import "./CourseAdvancedSettings.css";

export const CourseAdvancedSettings = ({
  settings,
  onSettingsChange,
  color,
  onPreviousColor,
  onNextColor,
}) => {
  const handleChange = (field) => {
    onSettingsChange({
      ...settings,
      [field]: !settings[field],
    });
  };

  return (
    <div className="course-settings-wrapper">
      <Accordion style={{ background: color.secondary }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
        >
          <div className="course-settings-row">
            <TuneIcon color="primary" fontSize="large" />
            <div className="settings-typo">
              <Typography>Advanced Settings</Typography>
            </div>
          </div>
        </AccordionSummary>
        <AccordionDetails>
          <div className="settings-accordion">
            <Divider />
            <div className="settings-row">
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.checkSurname}
                    onChange={() => handleChange("checkSurname")}
                    color="primary"
                  />
                }
                label="Check surname"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.checkDepartment}
                    onChange={() => handleChange("checkDepartment")}
                    color="primary"
                  />
                }
                label="Check department"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.checkCollision}
                    onChange={() => handleChange("checkCollision")}
                    color="primary"
                  />
                }
                label="Check collision"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.disableCourse}
                    onChange={() => handleChange("disableCourse")}
                    color="primary"
                  />
                }
                label="Disable course"
              />
            </div>
            <Divider />
            <div className="settings-row">
              <Button
                variant="contained"
                color="primary"
                startIcon={<PaletteIcon />}
                style={{ marginTop: "6pt" }}
                onClick={onPreviousColor}
              >
                Prev Color
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PaletteIcon />}
                style={{ marginTop: "6pt", marginLeft: "6pt" }}
                onClick={onNextColor}
              >
                Next Color
              </Button>
            </div>
          </div>
        </AccordionDetails>
      </Accordion>
    </div>
  );
};
