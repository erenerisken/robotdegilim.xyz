import React, { useState } from "react";
import {
  MenuItem,
  FormControl,
  Paper,
  Select,
  Typography,
  IconButton,
  TextField,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import AddBoxIcon from "@mui/icons-material/AddBox";
import "./AddDontFillWidget.css";
import { handleDontFillAdd } from "./slices/dontFillsSlice";
import { useDispatch } from "react-redux";
import { convertTime } from "./helpers/convertTime";

// Values follow Date.getDay(), the numbering lecture times use.
const DAY_OPTIONS = [
  { label: "Monday", value: 1 },
  { label: "Tuesday", value: 2 },
  { label: "Wednesday", value: 3 },
  { label: "Thursday", value: 4 },
  { label: "Friday", value: 5 },
  { label: "Saturday", value: 6 },
  { label: "Sunday", value: 0 },
];

export const AddDontFillWidget = ({ startHour, startMin, endHour, endMin }) => {
  const dispatch = useDispatch();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [day, setDay] = useState(DAY_OPTIONS[0].value);
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
          className="df-widget-select-input"
        >
          {DAY_OPTIONS.map(({ label, value }) => (
            <MenuItem key={value} value={value}>
              {label}
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
          className="df-widget-select-input"
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
          className="df-widget-select-input"
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
    setDay(DAY_OPTIONS[0].value);
    setStartH(startHour);
    setStartM(startMin);
    setEndH(endHour);
    setEndM(endMin);
    setDescription("FULL");
  };

  return (
    <Paper className="df-widget-paper" style={styles.paper}>
      <div className="df-header">
        <Typography variant="subtitle2" className="df-title">Don't Fill Blocks</Typography>
        <Typography variant="caption" color="textSecondary">
        Add times when you are unavailable; the program will not schedule classes during these times.
        </Typography>
      </div>
      <div className="add-df-row">
        {isMobile ? (
          <>
            <div className="df-time-row">
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
            </div>
            <div className="df-action-row">
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
              <IconButton 
                className="df-add-button"
                onClick={handleAddDontFill}
              >
                <AddBoxIcon style={{ color: 'white' }} />
              </IconButton>
            </div>
          </>
        ) : (
          <>
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
            <IconButton 
              className="df-add-button"
              onClick={handleAddDontFill}
            >
              <AddBoxIcon style={{ color: 'white' }} />
            </IconButton>
          </>
        )}
      </div>
    </Paper>
  );
};

const styles = {
  paper: {
    margin: 15,
    padding: 9,
  },
  dropdown: {
    marginTop: "auto",
    marginBottom: "auto",
  },
};
