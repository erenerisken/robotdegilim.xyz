import React, { useState } from "react";
import {
  TextField,
  IconButton,
  FormControl,
  Paper,
  Select,
  MenuItem,
} from "@material-ui/core";
import { Autocomplete } from "@material-ui/lab";
import AddBoxIcon from "@material-ui/icons/AddBox";
import { filterCourses } from "./data/Course";
import "./AddCourseWidget.css";

export const AddCourseWidget = ({ courses, onCourseAdd }) => {
  const [course, setCourse] = useState(null);
  const [category, setCategory] = useState(-1);

  const handleCourseAdd = () => {
    onCourseAdd(course);
    setCourse(null);
    setCategory(-1);
  };

  return (
    <Paper style={styles.paper}>
      <div className="add-course-row">
        <FormControl className="category-form" variant="outlined" size="small">
          <Select
            className="category-select"
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setCourse(null);
            }}
            inputProps={{ id: "category-select" }}
          >
            <MenuItem value={-1}>All courses</MenuItem>
            <MenuItem value={0}>Must</MenuItem>
            <MenuItem value={1}>Technical</MenuItem>
            <MenuItem value={2}>Restricted</MenuItem>
            <MenuItem value={3}>Non-Tech</MenuItem>
          </Select>
        </FormControl>
        <Autocomplete
          className="add-course-name"
          options={filterCourses(courses, category)}
          getOptionLabel={(option) => `${option.abbreviation}: ${option.name}`}
          style={{ width: "60%" }}
          value={course}
          size="small"
          renderInput={(params) => (
            <TextField {...params} label="Course name" variant="outlined" />
          )}
          onChange={(e, v) => setCourse(v)}
        />
        {course !== null && (
          <IconButton onClick={handleCourseAdd}>
            <AddBoxIcon fontSize="large" color="primary" />
          </IconButton>
        )}
      </div>
    </Paper>
  );
};

const styles = {
  paper: {
    backgroundColor: "aliceblue",
    margin: 15,
    padding: 9,
  },
  whiteBackground: {
    backgroundColor: "white",
  },
};
