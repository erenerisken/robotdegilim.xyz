import React, { useState } from "react";
import {
  TextField,
  Paper,
} from "@material-ui/core";
import { Autocomplete } from "@material-ui/lab";
import SearchIcon from "@material-ui/icons/Search";
import { filterCourses } from "./data/Course";
import "./AddCourseWidget.css";

export const AddCourseWidget = ({ courses, onCourseAdd }) => {
  const [course, setCourse] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [category] = useState(-1);

  const handleCourseAdd = (selectedCourse) => {
    if (selectedCourse) {
      onCourseAdd(selectedCourse);
      setCourse(null);
      setInputValue(""); // Text box'ı temizle
    }
  };

  return (
    <Paper style={styles.paper}>
      <div className="add-course-row">
        <Autocomplete
          className="add-course-name pretty-autocomplete"
          options={filterCourses(courses, category)}
          getOptionLabel={(option) => `${option.abbreviation}: ${option.name}`}
          value={course}
          inputValue={inputValue}
          onInputChange={(e, newInputValue) => setInputValue(newInputValue)}
          size="small"
          renderInput={(params) => (
            <TextField
              {...params}
              placeholder="Course name"
              variant="outlined"
              InputProps={{
                ...params.InputProps,
                startAdornment: (
                  <>
                    <SearchIcon style={{ marginRight: 6, color: "var(--text-secondary)" }} />
                    {params.InputProps.startAdornment}
                  </>
                ),
              }}
            />
          )}
          onChange={(e, v) => {
            if (v) {
              handleCourseAdd(v);
            } else {
              setCourse(v);
            }
          }}
        />
      </div>
    </Paper>
  );
};

const styles = {
  paper: {
    backgroundColor: "transparent",
    margin: 15,
    padding: 0,
    boxShadow: "none",
  },
  transparentBackground: {
    backgroundColor: "transparent",
  },
};
