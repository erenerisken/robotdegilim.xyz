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
} from "@material-ui/core";
import {
  FileCopy as ContentCopyIcon,
  Close as CloseIcon,
  Email as EmailIcon,
  EmojiEvents as CelebrationIcon,
} from "@material-ui/icons";
import { withStyles } from "@material-ui/core/styles";
import "./WelcomeDialog.css";

const ModernDialog = withStyles((theme) => ({
  paper: {
    borderRadius: '20px',
    background: theme.palette.background.paper,
    backdropFilter: 'blur(20px)',
    border: theme.palette.type === 'dark' 
      ? '1px solid rgba(255, 255, 255, 0.1)'
      : '1px solid rgba(0, 0, 0, 0.1)',
    boxShadow: theme.palette.type === 'dark'
      ? '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.2)'
      : '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    padding: theme.spacing(2),
    maxWidth: 500,
    maxHeight: '90vh',
    margin: theme.spacing(2),
    overflow: 'hidden',
  },
}))(Dialog);

const ModernDialogTitle = withStyles((theme) => ({
  root: {
    background: theme.palette.type === 'dark'
      ? 'linear-gradient(135deg, #374151 0%, #1f2937 100%)'
      : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
    color: theme.palette.text.primary,
    borderRadius: '12px 12px 0 0',
    margin: theme.spacing(-2, -2, 2, -2),
    padding: theme.spacing(3, 3, 2, 3),
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontSize: '1.5rem',
    fontWeight: 700,
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: theme.palette.type === 'dark'
        ? 'radial-gradient(circle at 70% 30%, rgba(255, 255, 255, 0.05) 0%, transparent 70%)'
        : 'radial-gradient(circle at 70% 30%, rgba(255, 255, 255, 0.2) 0%, transparent 70%)',
      borderRadius: '12px 12px 0 0',
    },
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
    borderRadius: '12px',
    padding: theme.spacing(1.5, 3),
    background: theme.palette.primary.main,
    color: 'white',
    fontWeight: 600,
    textTransform: 'none',
    fontSize: '1rem',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    transition: 'all 0.3s ease',
    '&:hover': {
      background: theme.palette.primary.dark,
      transform: 'translateY(-2px)',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    },
  },
}))(Button);

const CloseButton = withStyles((theme) => ({
  root: {
    borderRadius: '12px',
    padding: theme.spacing(1.5, 3),
    background: theme.palette.primary.dark,
    color: 'white',
    fontWeight: 600,
    textTransform: 'none',
    fontSize: '1rem',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    transition: 'all 0.3s ease',
    '&:hover': {
      background: theme.palette.primary.main,
      transform: 'translateY(-2px)',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
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
          style={{ color: 'inherit', zIndex: 1, position: 'absolute', right: 12, top: 12 }}
        >
          <CloseIcon />
        </IconButton>
      </ModernDialogTitle>
      
      <WelcomeContent>
        <Typography variant="h6" className="colorAnimation" style={{ fontSize: 18 }}>
          RobotDegilim team is looking for new maintainers!
        </Typography>
        <Typography variant="h6" style={{ color: '#6b7280', marginBottom: 24, fontSize: 18 }}>
            We'd love to hear from you!
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

      <DialogActions style={{ padding: 16, justifyContent: 'center' }}>
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
