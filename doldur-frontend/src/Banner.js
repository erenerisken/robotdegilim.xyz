import React from "react";

import logo from "./img/logo.png"
import title from "./img/title.gif"
import "./Banner.css"


export class Banner extends React.Component {
    render() {
        return (
            <div className={"banner-wrapper"}>
                <img src={logo} width={90} height={90} alt="wrapper"/>
                <div className={"banner-typo"}>
                    <img src={title} width={330} height={45} alt="banner"/>
                </div>
            </div>
        )
    }
}