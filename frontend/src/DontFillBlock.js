import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { IconButton, TextField, Menu, MenuItem } from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import PaletteIcon from "@material-ui/icons/Palette";
import { Colorset } from "./Colorset";
import "./WeeklyProgram.css";
import {
  handleChangeDontFillColor,
  handleChangeDontFillDescription,
  handleDontFillDelete,
} from "./slices/dontFillsSlice";

export const DontFillBlock = ({ data }) => {
  const [editing, setEditing] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const dispatch = useDispatch();

  const colorset = new Colorset();
  const colors = colorset.colors;
  const open = Boolean(anchorEl);

  const handleOpenColorPalette = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleColorSelect = (color) => {
    dispatch(
      handleChangeDontFillColor({ startDate: data.startDate, color: color })
    );
    handleClose();
  };
  const handleDeleteDontFill = () => {
    dispatch(handleDontFillDelete({ startDate: data.startDate }));
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDescriptionChange = (e) => {
    dispatch(
      handleChangeDontFillDescription({
        startDate: data.startDate,
        description: e.target.value,
      })
    );
  };

  const handleTextFieldKeyDown = (e) => {
    if (e.keyCode === 13) {
      setEditing(false);
    }
  };

  return (
    <div className="program-text-container-df">
      <div className="program-row-df">
        <IconButton onClick={handleDeleteDontFill} style={{ padding: 0 }}>
          <CloseIcon fontSize="small" style={{ color: data.color.text }} />
        </IconButton>
        {editing ? (
          <TextField
            value={data.title}
            className="df-description-text-field"
            InputProps={{ style: { color: data.color.text } }}
            onChange={handleDescriptionChange}
            onKeyDown={handleTextFieldKeyDown}
            onBlur={() => setEditing(false)}
          />
        ) : (
          <div
            className="program-title-dont-fill"
            style={{ color: data.color.text }}
            onClick={() => setEditing(true)}
          >
            {data.title}
          </div>
        )}
        <IconButton
          style={{ padding: 0 }}
          id="palette-button"
          aria-controls={open ? "palette-menu" : undefined}
          aria-haspopup="true"
          aria-expanded={open ? "true" : undefined}
          onClick={handleOpenColorPalette}
        >
          <PaletteIcon fontSize="small" style={{ color: data.color.text }} />
        </IconButton>
        <Menu
          id="palette-menu"
          open={open}
          anchorEl={anchorEl}
          onClose={handleClose}
          MenuListProps={{
            "aria-labelledby": "palette-button",
          }}
          PaperProps={{
            style: {
              backgroundColor: "black",
            },
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "5px",
              padding: "5px",
              paddingTop: "0px",
              paddingBottom: "0px",
              backgroundColor: "black",
            }}
          >
            {colors.map((color) => (
              <MenuItem
                key={color.main}
                onClick={() => handleColorSelect(color)}
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
  );
};
