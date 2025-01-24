import React from "react";
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

export class AddDontFillWidget extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            day: 0,
            startHour: this.props.startHour,
            startMin: this.props.startMin,
            endHour: this.props.endHour,
            endMin: this.props.endMin,
            description: "FULL",
        };
    }

    renderDayPick(val, onChange) {
        return (
            <div className={"df-widget-select"}>
                <FormControl
                    style={styles.dropdown}
                    variant={"outlined"}
                    size={"small"}
                >
                    <Select
                        labelId={"df-select-label-day"}
                        id={"df-select-day"}
                        value={val}
                        onChange={(e) => onChange(e.target.value)}
                        style={{ background: "#FFFFFF" }}
                    >
                        <MenuItem value={0}>Monday</MenuItem>
                        <MenuItem value={1}>Tuesday</MenuItem>
                        <MenuItem value={2}>Wednesday</MenuItem>
                        <MenuItem value={3}>Thursday</MenuItem>
                        <MenuItem value={4}>Friday</MenuItem>
                        <MenuItem value={5}>Saturday</MenuItem>
                        <MenuItem value={6}>Sunday</MenuItem>
                    </Select>
                </FormControl>
            </div>
        );
    }

    renderHourPick(val, onChange) {
        const menuItems = Array(0);
        for (let i = this.props.startHour; i <= this.props.endHour; i++) {
            menuItems.push(
                <MenuItem value={i}>{i < 10 ? "0" + i : i}</MenuItem>
            );
        }
        return (
            <div className={"df-widget-select"}>
                <FormControl
                    style={styles.dropdown}
                    variant={"outlined"}
                    size={"small"}
                >
                    <Select
                        labelId={"df-select-label-min"}
                        id={"df-select-min"}
                        value={val}
                        onChange={(e) => onChange(e.target.value)}
                        style={{ background: "#FFFFFF" }}
                    >
                        {menuItems}
                    </Select>
                </FormControl>
            </div>
        );
    }

    renderMinPick(val, onChange) {
        const menuItems = Array(0);
        for (let i = 0; i <= 59; i += 10) {
            menuItems.push(
                <MenuItem value={i}>{i < 10 ? "0" + i : i}</MenuItem>
            );
        }
        return (
            <div className={"df-widget-select"}>
                <FormControl
                    style={styles.dropdown}
                    variant={"outlined"}
                    size={"small"}
                >
                    <Select
                        labelId={"df-select-label-min"}
                        id={"df-select-min"}
                        value={val}
                        onChange={(e) => onChange(e.target.value)}
                        style={{ background: "#FFFFFF" }}
                    >
                        {menuItems}
                    </Select>
                </FormControl>
            </div>
        );
    }

    handleAddDontFill() {
        this.props.onDontFillAdd(
            this.convertTime(
                this.state.day,
                this.state.startHour,
                this.state.startMin
            ),
            this.convertTime(
                this.state.day,
                this.state.endHour,
                this.state.endMin
            ),
            this.state.description
        );
        this.setState({
            day: 0,
            startHour: this.props.startHour,
            startMin: this.props.startMin,
            endHour: this.props.endHour,
            endMin: this.props.endMin,
            description: "FULL",
        });
    }
    convertTime(day, hour, min) {
        //example : '2021-02-20T09:40'
        return new Date(
            "2021-02-" +
                (14 + day) +
                "T" +
                (hour < 10 ? "0" : "") +
                hour +
                ":" +
                (min < 10 ? "0" : "") +
                min
        );
    }
    render() {
        return (
            <Paper style={styles.paper}>
                <div className={"add-df-row"}>
                    {this.renderDayPick(this.state.day, (val) =>
                        this.setState({ day: val })
                    )}
                    {this.renderHourPick(this.state.startHour, (val) =>
                        this.setState({ startHour: val })
                    )}
                    <div className={"df-typo"}>
                        <Typography>:</Typography>
                    </div>
                    {this.renderMinPick(this.state.startMin, (val) =>
                        this.setState({ startMin: val })
                    )}
                    <div className={"df-typo"}>
                        <Typography>-</Typography>
                    </div>
                    {this.renderHourPick(this.state.endHour, (val) =>
                        this.setState({ endHour: val })
                    )}
                    <div className={"df-typo"}>
                        <Typography>:</Typography>
                    </div>
                    {this.renderMinPick(this.state.endMin, (val) =>
                        this.setState({ endMin: val })
                    )}
                    <div className={"df-typo"}>
                        <Typography>is</Typography>
                    </div>
                    <div className={"df-textfield"}>
                        <TextField
                            label={"Event"}
                            value={this.state.description}
                            inputProps={{ maxLength: 8 }}
                            variant={"outlined"}
                            size={"small"}
                            onChange={(e) =>
                                this.setState({ description: e.target.value })
                            }
                        />
                    </div>
                    <IconButton onClick={() => this.handleAddDontFill()}>
                        <AddBoxIcon fontSize={"large"} color={"primary"} />
                    </IconButton>
                </div>
            </Paper>
        );
    }
}

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
