import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Tooltip,
  Box,
  Typography,
} from "@material-ui/core";

export class WelcomeDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open: true,
      copied: false,
    };
  }

  handleCopyEmail = () => {
    navigator.clipboard.writeText("info.robotdegilim@gmail.com");
    this.setState({ copied: true });

    setTimeout(() => {
      this.setState({ copied: false });
    }, 1500);
  };

  render() {
    return (
      <div className="dialog-wrapper">
        <Dialog
          open={this.state.open}
          onClose={() => this.setState({ open: false })}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">Welcome!</DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              Öneriler ve şikayetler için{" "}
              <Tooltip
                title={this.state.copied ? "Copied" : "Click to copy"}
                open={this.state.copied}
                arrow
              >
                <Box
                  component="span"
                  sx={{
                    cursor: "pointer",
                    fontWeight: "bold",
                    color: "blue",
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                    "&:hover": { textDecoration: "underline" },
                  }}
                  onClick={this.handleCopyEmail}
                >
                  <Typography style={{ color: "blue" }}>
                    {" "}
                    info.robotdegilim@gmail.com{" "}
                  </Typography>
                </Box>
              </Tooltip>
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => this.setState({ open: false })}
              color="secondary"
              variant="contained"
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
