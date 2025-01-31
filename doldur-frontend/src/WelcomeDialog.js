import React from "react";
import {
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    Button,
} from "@material-ui/core";

export class WelcomeDialog extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            open: true,
        };
    }
    render() {
        return (
            <div className={"dialog-wrapper"}>
                <Dialog
                    open={this.state.open}
                    onClose={() => this.setState({ open: false })}
                    aria-labelledby={"alert-dialog-title"}
                    aria-describedby={"alert-dialog-description"}
                >
                    <DialogTitle id={"alert-dialog-title"}>
                        Welcome!
                    </DialogTitle>
                    <DialogContent>
                        <DialogContentText id={"alert-dialog-description"}>
                            Bir süredir yoktum demişler öldü, şimdi yazsınlar
                            bakalım kral geri döndü
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button
                            onClick={() => this.setState({ open: false })}
                            color={"secondary"}
                            variant={"contained"}
                            autoFocus={false}
                        >
                            Close
                        </Button>
                    </DialogActions>
                </Dialog>
            </div>
        );
    }
}
