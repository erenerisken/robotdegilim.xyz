import React from "react";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  FormControlLabel,
  Checkbox,
  Divider,
} from "@material-ui/core";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import TuneIcon from "@material-ui/icons/Tune";
import "./AdvancedSettings.css";

export const AdvancedSettings = ({ settings, onSettingsChange }) => {
  const handleSettingChange = (key) => {
    onSettingsChange({ ...settings, [key]: !settings[key] });
  };

  return (
    <div className="course-settings-wrapper">
      <Accordion style={{ background: "aliceblue" }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
        >
          <div className="course-settings-row">
            <TuneIcon color="primary" fontSize="large" />
            <div className="course-settings-typo">
              <Typography>Advanced Settings</Typography>
            </div>
          </div>
        </AccordionSummary>
        <AccordionDetails>
          <div className="course-settings-accordion">
            <Divider />
            <div className="course-settings-row">
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.checkSurname}
                    onChange={() => handleSettingChange("checkSurname")}
                    color="primary"
                  />
                }
                label="Check surname"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.checkDepartment}
                    onChange={() => handleSettingChange("checkDepartment")}
                    color="primary"
                  />
                }
                label="Check department"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.checkCollision}
                    onChange={() => handleSettingChange("checkCollision")}
                    color="primary"
                  />
                }
                label="Check collision"
              />
            </div>
          </div>
        </AccordionDetails>
      </Accordion>
    </div>
  );
};
