import React from "react";

import {
    CircularProgress,
    Dialog,
    DialogContent,
} from "@material-ui/core";

import "./LoadingDialog.css"

export class LoadingDialog extends React.Component {
    render() {
        return (
            <Dialog open={true}>
                <DialogContent>
                    <div className={"loading-circle"}>
                        <CircularProgress />
                    </div>
                    <div className={"loading-text"}>
                        {
                            this.props.text === undefined ? "Loading!" : this.props.text
                        }
                    </div>
                </DialogContent>
            </Dialog>
        )
    }
}