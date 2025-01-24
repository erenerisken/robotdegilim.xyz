import React from "react";
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

export class AddCourseWidget extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            course: null,
            category: -1,
        };
    }
    handleCourseAdd() {
        this.props.onCourseAdd(this.state.course);
        this.setState({ course: null, category: -1 });
    }
    render() {
        return (
            <Paper style={styles.paper}>
                <div className={"add-course-row"}>
                    <FormControl
                        className={"category-form"}
                        variant={"outlined"}
                        size={"small"}
                    >
                        <Select
                            className={"category-select"}
                            value={this.state.category}
                            onChange={(e) =>
                                this.setState({
                                    category: e.target.value,
                                    course: null,
                                })
                            }
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
                        className={"add-course-name"}
                        options={filterCourses(
                            this.props.courses,
                            this.state.category
                        )}
                        getOptionLabel={(option) =>
                            option.abbreviation + ": " + option.name
                        }
                        style={{ width: "60%" }}
                        value={this.state.course}
                        size={"small"}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                label={"Course name"}
                                variant={"outlined"}
                            />
                        )}
                        onChange={(e, v) => this.setState({ course: v })}
                    />
                    {this.state.course !== null ? (
                        <IconButton onClick={() => this.handleCourseAdd()}>
                            <AddBoxIcon fontSize={"large"} color={"primary"} />
                        </IconButton>
                    ) : null}
                </div>
            </Paper>
        );
    }
}

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
