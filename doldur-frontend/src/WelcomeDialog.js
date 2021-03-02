import React from "react";
import {
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    Button
} from "@material-ui/core";

export class WelcomeDialog extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            open: true
        }
    }
    render() {
        return (
        <div className={"dialog-wrapper"}>
            <Dialog open={this.state.open}
                    onClose={() => this.setState({open: false})}
                    aria-labelledby={"alert-dialog-title"}
                    aria-describedby={"alert-dialog-description"}>
                <DialogTitle id={"alert-dialog-title"}>
                    Welcome!
                </DialogTitle>
                <DialogContent>
                    <DialogContentText id={"alert-dialog-description"}>
                        Nasıl ders çakışmasına bu site gibi bir çözüm bulduysak, diğer sorunlara da beraber çözüm bulabiliriz.
                        Uzaktan eğitimin sorunlarına çözüm bulmak için gelin, siz de fikirlerinizi anketi doldurarak,
                        doldurtarak bizimle paylaşın.
                        <br/>
                        <br/>
                        Anket Linki : <a href={"https://forms.gle/B72tScNCGypExQN3A"}>https://forms.gle/B72tScNCGypExQN3A</a>
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => this.setState({open: false})}
                            color={"secondary"}
                            variant={"contained"}
                            autoFocus={false}>
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </div>);
    }
}