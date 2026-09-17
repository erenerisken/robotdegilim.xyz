import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Chip,
    Box,
    Divider,
    CircularProgress,
    Card,
    CardContent,
    Grid
} from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import AddIcon from '@material-ui/icons/Add';
import SchoolIcon from '@material-ui/icons/School';
import LibraryAddIcon from '@material-ui/icons/LibraryAdd';
import { withStyles } from '@material-ui/core/styles';
import { getElectives, filterAvailableElectives } from './data/Course';

// Styled Components
const StyledDialog = withStyles((theme) => ({
    paper: {
        borderRadius: '16px',
        maxHeight: '90vh',
    },
}))(Dialog);

const CourseCard = withStyles((theme) => ({
    root: {
        borderRadius: '12px',
        marginBottom: theme.spacing(2),
        border: '1px solid var(--border)',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        transition: 'all 0.2s ease',
        '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
            transform: 'translateY(-1px)',
        },
    },
}))(Card);

const SectionChip = withStyles((theme) => ({
    root: {
        margin: theme.spacing(0.5, 0.5, 0.5, 0),
        borderRadius: '6px',
    },
}))(Chip);

const ModernButton = withStyles((theme) => ({
    root: {
        borderRadius: '8px',
        fontWeight: 600,
        textTransform: 'none',
        padding: theme.spacing(1, 2),
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
        },
        transition: 'all 0.2s ease',
        margin: theme.spacing(0.5),
    },
}))(Button);

const HeaderBox = withStyles((theme) => ({
    root: {
        background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
        color: 'white',
        padding: theme.spacing(2, 3, 3, 3),
        borderRadius: '16px 16px 0 0',
        margin: '-24px 0 24px 0',
        width: '100%',
        boxSizing: 'border-box',
    },
}))(Box);

const NTEDialog = ({ open, onClose, occupiedSlots, onAddCourse, department, allCourses }) => {
    const [electivesData, setElectivesData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (open && department) {
            loadElectivesData();
        }
    }, [open, department]);

    const loadElectivesData = async () => {
        setLoading(true);
        setError('');
        try {
            // Returns [{ code, stringCode, name, category, isOpen }]
            const data = await getElectives(department);
            
            // Link to full courses to get sections and time info for 'isOpen' ones
            const fullyLinkedData = data.map(elective => {
               if (elective.isOpen) {
                  const fullCourse = allCourses.find(c => c.code === elective.code);
                  if (fullCourse) {
                      return { ...elective, sections: fullCourse.sections, fullCourse };
                  }
               }
               return elective;
            });
            
            // Sort: open courses first, then grouped by category
            fullyLinkedData.sort((a, b) => {
               if (a.isOpen && !b.isOpen) return -1;
               if (!a.isOpen && b.isOpen) return 1;
               if (a.category < b.category) return -1;
               if (a.category > b.category) return 1;
               return 0;
            });

            setElectivesData(fullyLinkedData);
        } catch (err) {
            setError('Error loading electives.');
            console.error('Error loading electives:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddElective = (course, sectionIndex) => {
        onAddCourse(course.fullCourse, sectionIndex);
    };

    const handleAddAllSections = (course) => {
        onAddCourse(course.fullCourse, -1);
    };

    const formatTime = (t) => {
        const pad = (n) => n.toString().padStart(2, '0');
        return `${pad(t.startHour)}:${pad(t.startMin)} - ${pad(t.endHour)}:${pad(t.endMin)}`;
    };

    const formatDay = (dayNum) => {
        const dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        return dayNames[dayNum] || "Unknown";
    };

    // Grouping for render
    const renderElectivesList = () => {
        if (electivesData.length === 0) {
            return (
                <Alert severity="info" style={{ borderRadius: '12px' }}>
                    No electives found for {department}.
                </Alert>
            );
        }

        let currentCategory = "";
        let currentIsOpen = true;

        return electivesData.map((course, index) => {
            const isNewGroup = course.isOpen !== currentIsOpen || course.category !== currentCategory || index === 0;
            if (isNewGroup) {
                currentCategory = course.category;
                currentIsOpen = course.isOpen;
            }

            return (
                <Box key={`${course.code}-${index}`}>
                    {isNewGroup && (
                        <Typography variant="h6" style={{ marginTop: 24, marginBottom: 12, fontWeight: 700, color: currentIsOpen ? '#1d4ed8' : '#6b7280' }}>
                            {currentIsOpen ? "🟢 Open: " : "🔴 Closed: "} {currentCategory || "General Electives"}
                        </Typography>
                    )}
                    
                    <CourseCard style={{ opacity: currentIsOpen ? 1 : 0.6 }}>
                        <CardContent>
                            <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                <Box>
                                    <Typography variant="h6" style={{ fontWeight: 600, marginBottom: 8 }}>
                                        {course.stringCode}
                                    </Typography>
                                    <Typography variant="body1" color="textSecondary" style={{ marginBottom: 8 }}>
                                        {course.name}
                                    </Typography>
                                    {!currentIsOpen && (
                                        <SectionChip
                                            label="Not Offered This Semester"
                                            size="small"
                                            color="secondary"
                                            variant="outlined"
                                        />
                                    )}
                                </Box>
                                {currentIsOpen && (
                                    <Box display="flex" gap={1}>
                                        <ModernButton
                                            variant="contained"
                                            color="primary"
                                            startIcon={<LibraryAddIcon />}
                                            onClick={() => handleAddAllSections(course)}
                                        >
                                            Add All Sections
                                        </ModernButton>
                                    </Box>
                                )}
                            </Box>

                            {currentIsOpen && course.sections && (
                                <>
                                    <Divider style={{ margin: '16px 0' }} />
                                    <Typography variant="subtitle2" style={{ fontWeight: 600, marginBottom: 12 }}>
                                        Available Sections:
                                    </Typography>
                                    <Grid container spacing={2}>
                                        {course.sections.map((section, sectionIndex) => {
                                            // Check time conflict dynamically
                                            let isConflict = false;
                                            if (section.lectureTimes) {
                                                isConflict = !section.lectureTimes.every(time => {
                                                    return !occupiedSlots.some(occupied => {
                                                        if (time.day !== occupied.day) return false;
                                                        const tStart = time.startHour * 60 + time.startMin;
                                                        const tEnd = time.endHour * 60 + time.endMin;
                                                        const oStart = occupied.startHour * 60 + occupied.startMin;
                                                        const oEnd = occupied.endHour * 60 + occupied.endMin;
                                                        return !(tEnd <= oStart || oEnd <= tStart);
                                                    });
                                                });
                                            }

                                            return (
                                                <Grid item xs={12} sm={6} md={4} key={sectionIndex}>
                                                    <Box
                                                        p={2}
                                                        borderRadius="8px"
                                                        style={{
                                                            backgroundColor: isConflict ? '#fee2e2' : 'var(--bg-page)',
                                                            border: '1px solid var(--border)'
                                                        }}
                                                    >
                                                        <Typography variant="body2" style={{ fontWeight: 600, marginBottom: 4 }}>
                                                            Section {section.sectionNumber}
                                                        </Typography>
                                                        <Typography variant="caption" color="textSecondary" display="block" style={{ marginBottom: 8 }}>
                                                            {section.instructor || 'Instructor TBA'}
                                                        </Typography>

                                                        {section.lectureTimes.map((time, timeIndex) => (
                                                            <Typography key={timeIndex} variant="caption" display="block" style={{ marginBottom: 2 }}>
                                                                <strong>{formatDay(time.day)}</strong> {formatTime(time)}
                                                                <br />
                                                                📍 {time.classroom || "Room TBA"}
                                                            </Typography>
                                                        ))}
                                                        
                                                        {isConflict && (
                                                            <Typography variant="caption" color="error" display="block" style={{ marginTop: 8, fontWeight: 600 }}>
                                                                Conflicts with schedule
                                                            </Typography>
                                                        )}

                                                        <ModernButton
                                                            size="small"
                                                            variant="outlined"
                                                            startIcon={<AddIcon />}
                                                            onClick={() => handleAddElective(course, sectionIndex)}
                                                            fullWidth
                                                            style={{ marginTop: 8 }}
                                                        >
                                                            Add Section
                                                        </ModernButton>
                                                    </Box>
                                                </Grid>
                                            );
                                        })}
                                    </Grid>
                                </>
                            )}
                        </CardContent>
                    </CourseCard>
                </Box>
            );
        });
    };

    return (
        <StyledDialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
            <DialogContent style={{ padding: 0 }}>
                <HeaderBox>
                    <Box display="flex" justifyContent="center" alignItems="center" style={{ paddingTop: '16px' }}>
                        <Box display="flex" alignItems="center" gap={2}>
                            <SchoolIcon fontSize="large" />
                            <Box textAlign="center">
                                <Typography variant="h5" style={{ fontWeight: 600, marginBottom: '8px' }}>
                                    Available Electives for {department}
                                </Typography>
                                <Typography variant="body2" style={{ opacity: 0.9 }}>
                                    Electives curated for your department
                                </Typography>
                            </Box>
                        </Box>
                    </Box>
                </HeaderBox>

                <Box p={3}>
                    {loading ? (
                        <Box display="flex" justifyContent="center" p={3}>
                            <CircularProgress size={60} />
                        </Box>
                    ) : error ? (
                        <Alert severity="error">{error}</Alert>
                    ) : (
                        <>
                            {renderElectivesList()}
                        </>
                    )}
                </Box>
            </DialogContent>

            <DialogActions style={{ padding: '16px 24px' }}>
                <ModernButton onClick={onClose} variant="outlined" color="primary">
                    Close
                </ModernButton>
            </DialogActions>
        </StyledDialog>
    );
};

export default NTEDialog;
