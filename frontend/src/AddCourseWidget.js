import React, { useState } from "react";
import {
  TextField,
  Paper,
  createFilterOptions,
} from "@mui/material";
import { Autocomplete } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { courseNumber } from "./helpers/courseCode";
import "./AddCourseWidget.css";

const courseLabel = (course) =>
  `${course.abbreviation} ${courseNumber(course.code)}: ${course.name}`;

// Match however the course is typed: "CENG 213", "CENG213", "5710213" or a
// piece of the name. Only a handful of the ~5000 courses can be read at once,
// so cap what the popup renders.
const filterCourses = createFilterOptions({
  limit: 50,
  stringify: (course) =>
    `${courseLabel(course)} ${course.abbreviation}${courseNumber(course.code)} ${course.code}`,
});

export const AddCourseWidget = ({ courses, onCourseAdd }) => {
  const [course, setCourse] = useState(null);
  const [inputValue, setInputValue] = useState("");

  const handleCourseAdd = (selectedCourse) => {
    if (selectedCourse) {
      onCourseAdd(selectedCourse);
      setCourse(null);
      setInputValue(""); // Text box'ı temizle
    }
  };

  return (
    <Paper className="add-course-paper" style={styles.paper}>
      <div className="add-course-row">
        <Autocomplete
          className="add-course-name pretty-autocomplete"
          options={courses}
          filterOptions={filterCourses}
          getOptionLabel={courseLabel}
          // Courses share names freely ("EE: ADVANCED STUDIES" covers 59 of
          // them), so the label cannot stand in as the list key.
          renderOption={(props, option) => (
            <li {...props} key={option.code}>
              {courseLabel(option)}
            </li>
          )}
          isOptionEqualToValue={(option, selected) => option.code === selected.code}
          value={course}
          inputValue={inputValue}
          onInputChange={(e, newInputValue) => setInputValue(newInputValue)}
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
    margin: 15,
    padding: 9,
  },
};
