import React from "react";
import {TextField} from "@material-ui/core";

import "./Controls.css"

export class Controls extends React.Component{
    render() {
        return (
            <div className={"control-wrapper"}>
                <div className={"control-row"}>
                    <TextField required label={"Surname"} variant={"outlined"}/>
                </div>
            </div>
        )
    }
}