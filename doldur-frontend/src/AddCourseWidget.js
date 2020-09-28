import React from "react";
import {TextField, IconButton} from "@material-ui/core";
import {Autocomplete} from "@material-ui/lab";
import AddBoxIcon from '@material-ui/icons/AddBox';

import "./AddCourseWidget.css"

export class AddCourseWidget extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            course: null
        }
    }
    render() {
        return (
            <div className={"add-course-wrapper"}>
                <div className={"add-course-row"}>
                    <Autocomplete
                        options={this.props.courses}
                        getOptionLabel={(option => option.abbreviation + ": " + option.name)}
                        style={{width: "300pt"}}
                        renderInput={(params => <TextField {...params} label={"Course name"} variant={"outlined"}/>)}
                        onChange={(e, v) =>
                            this.setState({course: v})}
                    />
                    {this.state.course !== null ? <IconButton onClick={() => this.props.onCourseAdd(this.state.course)} >
                        <AddBoxIcon fontSize={"large"} color={"primary"} />
                    </IconButton> : null}
                </div>
            </div>
        )
    }
}