import React, { useState } from "react";
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

export const WelcomeDialog = () => {
  const [open, setOpen] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopyEmail = () => {
    navigator.clipboard.writeText("info.robotdegilim@gmail.com");
    setCopied(true);

    setTimeout(() => {
      setCopied(false);
    }, 1500);
  };
  return (
    <div className="dialog-wrapper">
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">Welcome!</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Öneriler ve şikayetler için{" "}
            <Tooltip title={"Copied"} open={copied} arrow>
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
                onClick={handleCopyEmail}
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
            onClick={() => setOpen(false)}
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
};
