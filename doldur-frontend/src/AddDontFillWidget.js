import React, { useState } from "react";
import {
  MenuItem,
  FormControl,
  Paper,
  Select,
  Typography,
  IconButton,
  TextField,
} from "@material-ui/core";
import AddBoxIcon from "@material-ui/icons/AddBox";
import "./AddDontFillWidget.css";
import { handleDontFillAdd } from "./slices/dontFillsSlice";
import { useDispatch } from "react-redux";
import { Colorset } from "./Colorset";

export const AddDontFillWidget = ({ startHour, startMin, endHour, endMin }) => {
  const dispatch = useDispatch();
  const [day, setDay] = useState(0);
  const [startH, setStartH] = useState(startHour);
  const [startM, setStartM] = useState(startMin);
  const [endH, setEndH] = useState(endHour);
  const [endM, setEndM] = useState(endMin);
  const [description, setDescription] = useState("FULL");

  const renderDayPick = (val, onChange) => (
    <div className="df-widget-select">
      <FormControl style={styles.dropdown} variant="outlined" size="small">
        <Select
          value={val}
          onChange={(e) => onChange(e.target.value)}
          style={{ background: "#FFFFFF" }}
        >
          {[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
          ].map((day, index) => (
            <MenuItem key={index} value={index}>
              {day}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );

  const renderHourPick = (val, onChange) => (
    <div className="df-widget-select">
      <FormControl style={styles.dropdown} variant="outlined" size="small">
        <Select
          value={val}
          onChange={(e) => onChange(e.target.value)}
          style={{ background: "#FFFFFF" }}
        >
          {Array.from(
            { length: endHour - startHour + 1 },
            (_, i) => startHour + i
          ).map((i) => (
            <MenuItem key={i} value={i}>
              {i < 10 ? "0" + i : i}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );

  const renderMinPick = (val, onChange) => (
    <div className="df-widget-select">
      <FormControl style={styles.dropdown} variant="outlined" size="small">
        <Select
          value={val}
          onChange={(e) => onChange(e.target.value)}
          style={{ background: "#FFFFFF" }}
        >
          {Array.from({ length: 6 }, (_, i) => i * 10).map((i) => (
            <MenuItem key={i} value={i}>
              {i < 10 ? "0" + i : i}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );

  const handleAddDontFill = () => {
    dispatch(
      handleDontFillAdd({
        startDate: convertTime(day, startH, startM),
        endDate: convertTime(day, endH, endM),
        description: description,
        color: "#FFFFFF",
      })
    );
    setDay(0);
    setStartH(startHour);
    setStartM(startMin);
    setEndH(endHour);
    setEndM(endMin);
    setDescription("FULL");
  };

  const convertTime = (day, hour, min) =>
    new Date(
      `2021-02-${14 + day}T${hour.toString().padStart(2, "0")}:${min
        .toString()
        .padStart(2, "0")}`
    );

  return (
    <Paper style={styles.paper}>
      <div className="add-df-row">
        {renderDayPick(day, setDay)}
        {renderHourPick(startH, setStartH)}
        <div className="df-typo">
          <Typography>:</Typography>
        </div>
        {renderMinPick(startM, setStartM)}
        <div className="df-typo">
          <Typography>-</Typography>
        </div>
        {renderHourPick(endH, setEndH)}
        <div className="df-typo">
          <Typography>:</Typography>
        </div>
        {renderMinPick(endM, setEndM)}
        <div className="df-typo">
          <Typography>is</Typography>
        </div>
        <div className="df-textfield">
          <TextField
            label="Event"
            value={description}
            inputProps={{ maxLength: 8 }}
            variant="outlined"
            size="small"
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <IconButton onClick={handleAddDontFill}>
          <AddBoxIcon fontSize="large" color="primary" />
        </IconButton>
      </div>
    </Paper>
  );
};

const styles = {
  paper: {
    backgroundColor: "aliceblue",
    margin: 15,
    padding: 3,
  },
  dropdown: {
    marginTop: "auto",
    marginBottom: "auto",
  },
};
