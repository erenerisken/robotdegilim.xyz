import React, { useState } from "react";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  FormControlLabel,
  Checkbox,
  Divider,
  Menu,
  MenuItem,
  IconButton,
} from "@material-ui/core";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import PaletteIcon from "@material-ui/icons/Palette";
import TuneIcon from "@material-ui/icons/Tune";
import { Colorset } from "./Colorset";

import "./CourseAdvancedSettings.css";

export const CourseAdvancedSettings = ({
  settings,
  onSettingsChange,
  color,
  onColorChange,
}) => {
  const handleChange = (field) => {
    onSettingsChange({
      ...settings,
      [field]: !settings[field],
    });
  };
  const [anchorEl, setAnchorEl] = useState(null);
  const colorset = new Colorset();
  const colors = colorset.colors;
  const open = Boolean(anchorEl);

  const handleOpenColorPalette = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleColorChange = (color) => {
    onColorChange(color);
    handleClose();
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  return (
    <div className="course-settings-wrapper">
      <Accordion style={{ background: 'var(--bg-overlay-1)', border: '1px solid var(--border-color)', boxShadow: 'none' }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
        >
          <div className="course-settings-row">
            <TuneIcon style={{ color: color.main }} fontSize="large" />
            <div className="settings-typo">
              <Typography style={{ color: 'var(--text-primary)' }}>Advanced Settings</Typography>
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
            <div
              className="settings-row"
            >
              <IconButton
                style={{
                  marginTop: "5px",
                  backgroundColor: "var(--bg-secondary)",
                  padding: "8px 12px",
                  borderRadius: "8px",
                  border: "1px solid var(--border-color)",
                  boxShadow: "0px 2px 4px var(--shadow-color)",
                }}
                id="palette-button"
                aria-controls={open ? "palette-menu" : undefined}
                aria-haspopup="true"
                aria-expanded={open ? "true" : undefined}
                onClick={handleOpenColorPalette}
              >
                <PaletteIcon fontSize="20" style={{ color: "var(--text-primary)" }} />
                <Typography style={{ color: "var(--text-primary)", marginLeft: 8 }}>Change Color</Typography>
              </IconButton>
              <Menu
                id="palette-menu"
                open={open}
                anchorEl={anchorEl}
                getContentAnchorEl={null}
                anchorOrigin={{
                  vertical: "bottom",
                  horizontal: "center",
                }}
                transformOrigin={{
                  vertical: "top",
                  horizontal: "center",
                }}
                onClose={handleClose}
                MenuListProps={{
                  "aria-labelledby": "palette-button",
                }}
                PaperProps={{
                  style: {
                    backgroundColor: "var(--bg-primary)",
                    border: "1px solid var(--border-color)",
                    boxShadow: "0 10px 15px -3px var(--shadow-color)",
                  },
                }}
              >
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(3, 1fr)",
                    gap: "5px",
                    padding: "10px",
                    backgroundColor: "transparent",
                  }}
                >
                  {colors.map((color) => (
                    <MenuItem
                      key={color.main}
                      onClick={() => handleColorChange(color)}
                      style={{ padding: 0 }}
                    >
                      <div
                        style={{
                          width: "30px",
                          height: "30px",
                          backgroundColor: color.main,
                          borderRadius: "4px",
                        }}
                      ></div>
                    </MenuItem>
                  ))}
                </div>
              </Menu>
            </div>
          </div>
        </AccordionDetails>
      </Accordion>
    </div>
  );
};
