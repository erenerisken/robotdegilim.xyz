import React, { useState } from "react";
import {
  TextField,
  IconButton,
  Paper,
} from "@material-ui/core";
import { Autocomplete } from "@material-ui/lab";
import AddBoxIcon from "@material-ui/icons/AddBox";
import SearchIcon from "@material-ui/icons/Search";
import { filterCourses } from "./data/Course";
import "./AddCourseWidget.css";

export const AddCourseWidget = ({ courses, onCourseAdd }) => {
  const [course, setCourse] = useState(null);
  const [category] = useState(-1);

  const handleCourseAdd = () => {
    onCourseAdd(course);
    setCourse(null);
  };

  return (
    <Paper style={styles.paper}>
      <div className="add-course-row">
        <Autocomplete
          className="add-course-name pretty-autocomplete"
          options={filterCourses(courses, category)}
          getOptionLabel={(option) => `${option.abbreviation}: ${option.name}`}
          value={course}
          size="small"
          renderInput={(params) => (
            <TextField
              {...params}
              label="Course name"
              variant="outlined"
              InputProps={{
                ...params.InputProps,
                startAdornment: (
                  <>
                    <SearchIcon style={{ marginRight: 6, color: "#6b7280" }} />
                    {params.InputProps.startAdornment}
                  </>
                ),
              }}
            />
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
    backgroundColor: "white",
    margin: 15,
    padding: 9,
  },
  whiteBackground: {
    backgroundColor: "white",
  },
};
