import React from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  Typography,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import CloudOffIcon from "@mui/icons-material/CloudOff";
import "./LoadErrorDialog.css";

export const LoadErrorDialog = ({ onRetry }) => (
  <Dialog open={true} maxWidth="xs">
    <DialogContent className="load-error-content">
      <CloudOffIcon className="load-error-icon" />
      <Typography variant="h6" className="load-error-title">
        Course data could not be loaded
      </Typography>
      <Typography variant="body2" color="textSecondary">
        The request took too long or the data service is unreachable. Check your
        connection and try again.
      </Typography>
    </DialogContent>
    <DialogActions className="load-error-actions">
      <Button
        variant="contained"
        className="pretty-button pretty-primary"
        startIcon={<RefreshIcon />}
        onClick={onRetry}
      >
        Try again
      </Button>
    </DialogActions>
  </Dialog>
);
