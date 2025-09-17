import React, { useState } from "react";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Typography,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Button,
  IconButton,
  Box,
  Card,
  Chip,
} from "@material-ui/core";
import {
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  School as SchoolIcon,
} from "@material-ui/icons";
import { withStyles } from "@material-ui/core/styles";

import { Colorset } from "./Colorset";
import { SectionInfo } from "./SectionInfo";
import { CourseAdvancedSettings } from "./CourseAdvancedSettings";

import "./CourseCard.css";

const ModernCard = withStyles((theme) => ({
  root: {
    borderRadius: '16px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    backdropFilter: 'blur(10px)',
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 8px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    },
    margin: theme.spacing(1),
    position: 'relative',
    overflow: 'hidden',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: '4px',
      zIndex: 1,
    },
  },
}))(Card);

const CardHeader = withStyles((theme) => ({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: theme.spacing(2, 2, 0, 2),
    position: 'relative',
    zIndex: 2,
  },
}))(Box);

const CourseTitle = withStyles((theme) => ({
  root: {
    fontWeight: 600,
    fontSize: '1.1rem',
    lineHeight: 1.3,
    color: theme.palette.text.primary,
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
}))(Typography);

const CourseCode = withStyles((theme) => ({
  root: {
    fontWeight: 600,
    fontSize: '0.75rem',
    height: 24,
  },
}))(Chip);

const ModernAccordion = withStyles((theme) => ({
  root: {
    boxShadow: 'none',
    background: 'transparent',
    '&:before': {
      display: 'none',
    },
    '&.Mui-expanded': {
      margin: 0,
    },
  },
}))(Accordion);

const ModernAccordionSummary = withStyles((theme) => ({
  root: {
    padding: theme.spacing(1, 2),
    minHeight: 'auto',
    '&.Mui-expanded': {
      minHeight: 'auto',
    },
  },
  content: {
    margin: theme.spacing(1, 0),
    '&.Mui-expanded': {
      margin: theme.spacing(1, 0),
    },
  },
}))(AccordionSummary);

const ModernAccordionDetails = withStyles((theme) => ({
  root: {
    padding: theme.spacing(0, 2, 2, 2),
    paddingTop: 0,
  },
}))(AccordionDetails);

const SectionSelector = withStyles((theme) => ({
  root: {
    backgroundColor: theme.palette.type === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(255, 255, 255, 0.5)',
    borderRadius: '12px',
    padding: theme.spacing(2),
    marginTop: theme.spacing(2),
    backdropFilter: 'blur(10px)',
    border: theme.palette.type === 'dark'
      ? '1px solid rgba(255, 255, 255, 0.1)'
      : '1px solid rgba(255, 255, 255, 0.2)',
  },
}))(Box);

const ModernButton = withStyles((theme) => ({
  root: {
    borderRadius: '8px',
    fontWeight: 600,
    textTransform: 'none',
    padding: theme.spacing(0.5, 2),
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    '&:hover': {
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
    },
    transition: 'all 0.2s ease',
    marginLeft: theme.spacing(1),
  },
}))(Button);

const ModernIconButton = withStyles((theme) => ({
  root: {
    backgroundColor: theme.palette.type === 'dark'
      ? 'rgba(255, 255, 255, 0.1)'
      : 'rgba(255, 255, 255, 0.8)',
    borderRadius: '8px',
    padding: theme.spacing(0.5),
    '&:hover': {
      backgroundColor: theme.palette.type === 'dark'
        ? 'rgba(255, 255, 255, 0.2)'
        : 'rgba(255, 255, 255, 0.95)',
      transform: 'scale(1.05)',
    },
    transition: 'all 0.2s ease',
  },
}))(IconButton);

const SectionTitle = withStyles((theme) => ({
  root: {
    fontWeight: 600,
    fontSize: '0.9rem',
    color: theme.palette.text.primary,
    marginBottom: theme.spacing(1),
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
  },
}))(Typography);

export const CourseCard = ({
  course,
  color,
  sections,
  onToggle,
  onSettingsChange,
  onColorChange,
  onDelete,
  settings,
}) => {
  const [selectedSections, setSelectedSections] = useState(sections.slice(0));
  const [expanded, setExpanded] = useState(false);
  const [colorset] = useState(new Colorset());

  const handleToggle = (sections) => {
    onToggle(sections);
  };

  const handleSettingsChange = (settings) => {
    onSettingsChange(settings);
  };

  const handleColorChange = (color) => {
    onColorChange(color);
  };

  const toggleSections = () => {
    const newSelectedSections = Array(course.sections.length).fill(
      !selectedSections[0]
    );
    setSelectedSections(newSelectedSections);
    handleToggle(newSelectedSections);
  };

  const renderCheckBoxes = () => {
    if (course.sections.length <= 0) return null;
    return (
      <FormGroup row>
        {course.sections.map((section, i) => (
          <FormControlLabel
            key={i}
            control={
              <Checkbox
                checked={selectedSections[i]}
                onChange={() => {
                  const newSelectedSections = [...selectedSections];
                  newSelectedSections[i] = !newSelectedSections[i];
                  setSelectedSections(newSelectedSections);
                  handleToggle(newSelectedSections);
                }}
                style={{
                  color: color.main,
                }}
                size="small"
              />
            }
            label={
              <Typography variant="body2" style={{ fontWeight: 500 }}>
                {section.sectionNumber}
              </Typography>
            }
          />
        ))}
        <ModernButton
          variant="outlined"
          size="small"
          onClick={toggleSections}
          style={{
            borderColor: color.main,
            color: color.main,
          }}
        >
          Toggle All
        </ModernButton>
      </FormGroup>
    );
  };

  const cardStyle = {
    border: `2px solid ${color.main}`,
    background: `linear-gradient(135deg, ${color.main}10, ${color.main}05)`,
  };

  const beforeStyle = {
    background: `linear-gradient(90deg, ${color.main}, ${color.light || color.main})`,
  };

  return (
    <ModernCard style={cardStyle} className="fade-in">
      <div style={beforeStyle} className="course-card-top-border" />
      <CardHeader>
        <Box style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
          <SchoolIcon style={{ color: color.main }} />
          <Box>
            <CourseTitle>
              {course.abbreviation}
            </CourseTitle>
            <Typography variant="body2" color="textSecondary" style={{ marginTop: 4 }}>
              {course.name}
            </Typography>
          </Box>
        </Box>
        <Box style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <CourseCode
            style={{
              backgroundColor: color.main,
              color: color.contrastText || 'white',
            }}
            label={course.code}
            size="small"
          />
          <ModernIconButton onClick={onDelete} size="small">
            <DeleteIcon fontSize="small" style={{ color: '#ef4444' }} />
          </ModernIconButton>
        </Box>
      </CardHeader>

      <ModernAccordion onChange={() => setExpanded(!expanded)}>
        <ModernAccordionSummary expandIcon={<ExpandMoreIcon />}>
          <SectionTitle>
            Course Details & Sections
          </SectionTitle>
        </ModernAccordionSummary>
        <ModernAccordionDetails>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <SectionSelector>
              <SectionTitle variant="body2">
                Available Sections
              </SectionTitle>
              {renderCheckBoxes()}
            </SectionSelector>

            <CourseAdvancedSettings
              color={color}
              onSettingsChange={handleSettingsChange}
              onColorChange={handleColorChange}
              settings={settings}
            />

            {expanded && (
              <Box>
                <Divider style={{ marginBottom: 16 }} />
                <SectionTitle variant="body2">
                  Section Information
                </SectionTitle>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {course.sections.map((section, i) => (
                    <SectionInfo
                      key={i}
                      sectionNo={i + 1}
                      sectionDetails={section}
                      color={color}
                    />
                  ))}
                </div>
              </Box>
            )}
          </div>
        </ModernAccordionDetails>
      </ModernAccordion>
    </ModernCard>
  );
};
