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
                        Siteyi ders seçimine yetiştirmek için hızlı bir şekilde yazdığımızdan,
                        her türlü hata bildirimi bizim için çok faydalı olacaktır.
                        Fark ettiğiniz herhangi bir sıkıntıda lütfen bizle iletişime geçin.
                        <br/>
                        <br/>
                        Eren Erişken: erenerisken@gmail.com
                        <br/>
                        Alperen Keleş: alpkeles99@gmail.com
                        <br/>
                        Alp Eren Yılmaz: ylmz.alp.e@gmail.com
                        <br/>
                        <br/>
                        Önemli: Yeni özellik olarak eklenen Google Calendar export'u kullanmak için gelişmiş
                        kısmından izin vermeniz gerekmektedir.
                        <br/>
                        <br/>
                        doldur.xyz anısına! (Saygılar @baskinburak)
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