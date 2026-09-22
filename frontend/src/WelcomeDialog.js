import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tooltip,
  Box,
  Typography,
  IconButton,
} from "@mui/material";
import {
  FileCopy as ContentCopyIcon,
  Close as CloseIcon,
  Email as EmailIcon,
  EmojiEvents as CelebrationIcon,
} from "@mui/icons-material";
import { withStyles } from "@mui/styles";
import "./WelcomeDialog.css";

const ModernDialog = withStyles((theme) => ({
  paper: {
    borderRadius: 'var(--radius-lg)',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    boxShadow: 'var(--shadow-lg)',
    padding: theme.spacing(2),
    maxWidth: 460,
    maxHeight: '90vh',
    margin: theme.spacing(2),
    overflow: 'hidden',
  },
}))(Dialog);

const ModernDialogTitle = withStyles((theme) => ({
  root: {
    background: 'var(--bg-subtle)',
    color: 'var(--text-primary)',
    borderRadius: 'var(--radius) var(--radius) 0 0',
    borderBottom: '1px solid var(--border)',
    margin: theme.spacing(-2, -2, 2, -2),
    padding: theme.spacing(2.25, 3, 2.25, 2.5),
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontSize: '1.15rem',
    fontWeight: 700,
  },
}))(DialogTitle);

const WelcomeContent = withStyles((theme) => ({
  root: {
    padding: theme.spacing(0, 1, 2, 1),
    textAlign: 'center',
    overflow: 'visible',
    '&::-webkit-scrollbar': {
      display: 'none',
    },
    scrollbarWidth: 'none',
  },
}))(DialogContent);

const EmailButton = withStyles((theme) => ({
  root: {
    borderRadius: 'var(--radius)',
    padding: theme.spacing(1.25, 2.5),
    background: 'var(--bg-subtle)',
    border: '1px solid var(--border)',
    color: 'var(--text-primary)',
    fontWeight: 600,
    textTransform: 'none',
    fontSize: '0.95rem',
    boxShadow: 'none',
    transition: 'background-color 0.16s ease, border-color 0.16s ease',
    '&:hover': {
      background: 'var(--bg-hover)',
      borderColor: 'var(--border-strong)',
      boxShadow: 'none',
    },
  },
}))(Button);

const CloseButton = withStyles((theme) => ({
  root: {
    borderRadius: 'var(--radius)',
    padding: theme.spacing(1.1, 2.75),
    background: 'var(--accent)',
    color: '#ffffff',
    fontWeight: 600,
    textTransform: 'none',
    fontSize: '0.95rem',
    boxShadow: 'var(--shadow-xs)',
    transition: 'background-color 0.16s ease',
    '&:hover': {
      background: 'var(--accent-hover)',
      boxShadow: 'var(--shadow-sm)',
    },
  },
}))(Button);

export const WelcomeDialog = () => {
  const [open, setOpen] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopyEmail = () => {
    navigator.clipboard.writeText("info.robotdegilim@gmail.com");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClose = () => setOpen(false);

  return (
    <ModernDialog
      open={open}
      onClose={handleClose}
      aria-labelledby="welcome-dialog-title"
      aria-describedby="welcome-dialog-description"
      maxWidth="sm"
      fullWidth
      scroll="body"
      disableScrollLock
    >
      <ModernDialogTitle id="welcome-dialog-title">
        <Box style={{ display: 'flex', alignItems: 'center', gap: 8, zIndex: 1 }}>
          <CelebrationIcon />
          Welcome to Robot Değilim!
        </Box>
        <IconButton
          onClick={handleClose}
          size="small"
          style={{ color: 'var(--text-secondary)', zIndex: 1, position: 'absolute', right: 10, top: 10 }}
        >
          <CloseIcon />
        </IconButton>
      </ModernDialogTitle>

      <WelcomeContent>
        <Typography
          variant="body2"
          style={{ color: 'var(--text-secondary)', marginBottom: 10 }}
        >
          You can reach us via:
        </Typography>

        <Tooltip
          title={copied ? "Email copied!" : "Click to copy email"}
          arrow
          placement="top"
        >
          <EmailButton
            onClick={handleCopyEmail}
            startIcon={copied ? <ContentCopyIcon /> : <EmailIcon />}
            fullWidth
            variant="contained"
          >
            {copied ? "Email Copied!" : "info.robotdegilim@gmail.com"}
          </EmailButton>
        </Tooltip>
      </WelcomeContent>

      <DialogActions style={{ padding: '8px 8px 4px', justifyContent: 'center' }}>
        <CloseButton
          onClick={handleClose}
          variant="contained"
          size="large"
        >
          Let's Start Scheduling! <span role="img" aria-label="rocket">🚀</span>
        </CloseButton>
      </DialogActions>
    </ModernDialog>
  );
};
