import React from "react";
import {Typography} from "@material-ui/core";

import logo from "./img/logo.png"
import title from "./img/title.gif"
import "./Banner.css"


export class Banner extends React.Component {
    render() {
        return (
            <div className={"banner-wrapper"}>
                <img src={logo} width={90} height={90}/>
                <div className={"banner-typo"}>
                    <img src={title} width={330} height={45}/>
                </div>
            </div>
        )
    }
}