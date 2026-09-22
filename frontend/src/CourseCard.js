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
} from "@mui/material";
import {
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  School as SchoolIcon,
} from "@mui/icons-material";
import { withStyles } from "@mui/styles";

import { SectionInfo } from "./SectionInfo";
import { CourseAdvancedSettings } from "./CourseAdvancedSettings";

import "./CourseCard.css";

const ModernCard = withStyles((theme) => ({
  root: {
    borderRadius: 'var(--radius-lg)',
    boxShadow: 'var(--shadow-xs)',
    transition: 'box-shadow 0.2s ease, border-color 0.2s ease',
    '&:hover': {
      boxShadow: 'var(--shadow-md)',
    },
    margin: theme.spacing(0.75, 0),
    position: 'relative',
    overflow: 'hidden',
  },
}))(Card);

// Box ignores a `classes` prop, so these two are styled from CourseCard.css
// rather than through withStyles.
const CardHeader = ({ children }) => (
  <div className="course-card-header">{children}</div>
);

const CourseTitle = withStyles((theme) => ({
  root: {
    fontWeight: 600,
    fontSize: '1rem',
    letterSpacing: '0.01em',
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

const SectionSelector = ({ children }) => (
  <div className="course-section-selector">{children}</div>
);

const ModernButton = withStyles((theme) => ({
  root: {
    borderRadius: 'var(--radius-sm)',
    fontWeight: 600,
    fontSize: '0.78rem',
    textTransform: 'none',
    padding: theme.spacing(0.25, 1.25),
    boxShadow: 'none',
    transition: 'background-color 0.16s ease',
    marginLeft: theme.spacing(0.5),
  },
}))(Button);

const ModernIconButton = withStyles((theme) => ({
  root: {
    backgroundColor: 'transparent',
    borderRadius: 'var(--radius-sm)',
    padding: theme.spacing(0.5),
    '&:hover': {
      backgroundColor: 'rgba(224, 82, 74, 0.12)',
    },
    transition: 'background-color 0.16s ease',
  },
}))(IconButton);

const SectionTitle = withStyles((theme) => ({
  root: {
    fontWeight: 600,
    fontSize: '0.72rem',
    letterSpacing: '0.07em',
    textTransform: 'uppercase',
    color: 'var(--text-muted)',
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
  onClassroomUpdate,
  settings,
}) => {
  const [selectedSections, setSelectedSections] = useState(sections.slice(0));
  const [expanded, setExpanded] = useState(false);

  const handleToggle = (sections) => {
    onToggle(sections);
  };

  const handleSettingsChange = (settings) => {
    onSettingsChange(settings);
  };

  const handleColorChange = (color) => {
    onColorChange(color);
  };

  const handleClassroomUpdate = (sectionIndex, lectureTimeIndex, newClassroom) => {
    if (onClassroomUpdate) {
      onClassroomUpdate(sectionIndex, lectureTimeIndex, newClassroom);
    }
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
          onClick={(e) => { e.stopPropagation(); toggleSections(); }}
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
    border: '1px solid var(--border)',
    background: 'var(--bg-card)',
    cursor: 'pointer',
  };

  // A thin rail in the course colour: the card stays neutral, the colour still
  // ties it to its block in the schedule.
  const beforeStyle = {
    background: color.main,
  };

  const handleCardClick = (event) => {
    // Eğer delete butonu veya diğer interactive elementlere tıklanmışsa, card click'i çalıştırma
    if (event.target.closest('.MuiIconButton-root') || 
        event.target.closest('.MuiAccordionSummary-root') ||
        event.target.closest('.MuiAccordion-root') ||
        event.target.closest('.MuiButton-root') ||
        event.target.closest('.MuiCheckbox-root') ||
        event.target.closest('.MuiFormControlLabel-root')) {
      return;
    }
    setExpanded(!expanded);
  };

  return (
    <ModernCard style={cardStyle} className="course-card fade-in" onClick={handleCardClick}>
      <div style={beforeStyle} className="course-card-top-border" />
      <CardHeader>
        <div className="course-card-identity">
          <SchoolIcon style={{ color: color.main, flexShrink: 0 }} />
          <div className="course-card-names">
            <CourseTitle>
              {course.abbreviation}
            </CourseTitle>
            <Typography variant="body2" color="textSecondary" className="course-card-name">
              {course.name}
            </Typography>
          </div>
        </div>
        <div className="course-card-actions">
          <CourseCode
            style={{
              backgroundColor: color.main,
              color: color.contrastText || 'white',
            }}
            label={course.code}
            size="small"
          />
          <ModernIconButton onClick={(e) => { e.stopPropagation(); onDelete(); }} size="small">
            <DeleteIcon fontSize="small" style={{ color: '#e0524a' }} />
          </ModernIconButton>
        </div>
      </CardHeader>

      <ModernAccordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
        <ModernAccordionSummary expandIcon={<ExpandMoreIcon />}>
          <SectionTitle className="course-card-toggle">
            Course Details &amp; Sections
          </SectionTitle>
        </ModernAccordionSummary>
        <ModernAccordionDetails>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
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
                <Divider style={{ marginBottom: 12 }} />
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
                      onClassroomUpdate={(lectureTimeIndex, newClassroom) =>
                        handleClassroomUpdate(i, lectureTimeIndex, newClassroom)
                      }
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
