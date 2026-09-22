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
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import PaletteIcon from "@mui/icons-material/Palette";
import TuneIcon from "@mui/icons-material/Tune";
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
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const colorset = new Colorset();
  const colors = colorset.colors;
  const open = Boolean(anchorEl);
  const isDark = theme.palette.mode === "dark";
  const accordionBg = isDark ? undefined : color?.secondary;

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
    <div className="course-settings-wrapper course-adv-settings">
      <Accordion className="course-adv-accordion" style={accordionBg ? { background: accordionBg } : undefined}>
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
            <div
              className="settings-row"
            >
              <IconButton
                className="course-color-button"
                id="palette-button"
                aria-controls={open ? "palette-menu" : undefined}
                aria-haspopup="true"
                aria-expanded={open ? "true" : undefined}
                onClick={handleOpenColorPalette}
              >
                <PaletteIcon fontSize="small" />
                <Typography component="span">Change Color</Typography>
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
                PaperProps={{ className: "course-palette-paper" }}
              >
                <div className="course-palette-grid">
                  {colors.map((color) => (
                    <MenuItem
                      key={color.main}
                      onClick={() => handleColorChange(color)}
                      className="course-palette-item"
                    >
                      <span
                        className="course-palette-swatch"
                        style={{ backgroundColor: color.main }}
                      />
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
