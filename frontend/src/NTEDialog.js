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
import { getNTECourses, filterAvailableNTEs } from './data/Course';

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
        padding: theme.spacing(2, 3, 3, 3), // top, right, bottom, left
        borderRadius: '16px 16px 0 0',
        margin: '-24px 0 24px 0',
        width: '100%',
        boxSizing: 'border-box',
    },
}))(Box);

const NTEDialog = ({ open, onClose, occupiedSlots, onAddCourse }) => {
    const [nteData, setNteData] = useState([]);
    const [availableNTEs, setAvailableNTEs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (open) {
            loadNTEData();
        }
    }, [open]);

    useEffect(() => {
        if (nteData.length > 0 && occupiedSlots.length >= 0) {
            const filtered = filterAvailableNTEs(nteData, occupiedSlots);
            setAvailableNTEs(filtered);
        }
    }, [nteData, occupiedSlots]);

    const loadNTEData = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await getNTECourses();
            setNteData(data);
        } catch (err) {
            setError('Error loading NTE courses.');
            console.error('Error loading NTE data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddNTE = (nteCourse, section) => {
        // NTE'yi mevcut ders formatına dönüştür
        const convertedCourse = convertNTEToCourse(nteCourse, section);
        // Seçilen section'ın index'ini bul
        const selectedSectionIndex = nteCourse.sections.findIndex(s => s.section_id === section.section_id);
        onAddCourse(convertedCourse, selectedSectionIndex);
    };

    const handleAddAllSections = (nteCourse) => {
        // Tüm section'ları aktif olarak ekle
        const convertedCourse = convertNTEToCourse(nteCourse, nteCourse.sections[0]);
        // Tüm section'ları seçili olarak işaretle (-1 = all sections)
        onAddCourse(convertedCourse, -1);
    };

    const convertNTEToCourse = (nteCourse, selectedSection) => {
        // Tüm available section'ları derse ekle, sadece seçilen section'ı toggle=true yap
        const allSections = nteCourse.sections.map(section => ({
            instructor: section.instructors.join(', '),
            sectionNumber: section.section_id,
            criteria: [{
                dept: "ALL",
                surnameStart: "AA",
                surnameEnd: "ZZ"
            }],
            minYear: 0,
            maxYear: 0,
            lectureTimes: section.times
                .filter(time => time.day !== "No Timestamp Added Yet" && time.start && time.end)
                .map(time => ({
                    classroom: time.room || "TBA",
                    day: getDayNumber(time.day),
                    startHour: parseInt(time.start.split(':')[0]),
                    startMin: parseInt(time.start.split(':')[1]),
                    endHour: parseInt(time.end.split(':')[0]),
                    endMin: parseInt(time.end.split(':')[1])
                }))
        }));

        return {
            code: nteCourse.code.numeric,
            abbreviation: nteCourse.code.departmental,
            name: nteCourse.name.split(' - ')[1] || nteCourse.name,
            category: 0, // NTE kategorisi
            sections: allSections
        };
    };

    const getDayNumber = (dayName) => {
        const dayMap = {
            "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6
        };
        return dayMap[dayName] || 0;
    };

    const formatTime = (time) => {
        if (!time.start || !time.end) return "Time not specified";
        return `${time.start} - ${time.end}`;
    };

    const formatDay = (day) => {
        const dayNames = {
            "Mon": "Monday",
            "Tue": "Tuesday",
            "Wed": "Wednesday",
            "Thu": "Thursday",
            "Fri": "Friday",
            "Sat": "Saturday",
            "Sun": "Sunday"
        };
        return dayNames[day] || day;
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
                                    Available NTE Courses
                                </Typography>
                                <Typography variant="body2" style={{ opacity: 0.9 }}>
                                    Non-Technical Electives for your schedule
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
                            <Typography variant="body1" color="textSecondary" gutterBottom style={{ marginBottom: 24 }}>
                                Found <strong>{availableNTEs.length}</strong> NTE courses that fit your current schedule.
                            </Typography>

                            {availableNTEs.length === 0 ? (
                                <Alert severity="info" style={{ borderRadius: '12px' }}>
                                    No NTE courses available for your current schedule.
                                    Create free time slots in your program or modify existing courses.
                                </Alert>
                            ) : (
                                <Grid container spacing={2}>
                                    {availableNTEs.map((course, index) => (
                                        <Grid item xs={12} key={`${course.code.numeric}-${index}`}>
                                            <CourseCard>
                                                <CardContent>
                                                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                                        <Box>
                                                            <Typography variant="h6" style={{ fontWeight: 600, marginBottom: 8 }}>
                                                                {course.code.departmental}
                                                            </Typography>
                                                            <Typography variant="body1" color="textSecondary" style={{ marginBottom: 8 }}>
                                                                {course.name.split(' - ')[1] || course.name}
                                                            </Typography>
                                                            <SectionChip
                                                                label={`${course.credits} Credits`}
                                                                size="small"
                                                                color="primary"
                                                                variant="outlined"
                                                            />
                                                        </Box>
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
                                                    </Box>

                                                    <Divider style={{ margin: '16px 0' }} />

                                                    <Typography variant="subtitle2" style={{ fontWeight: 600, marginBottom: 12 }}>
                                                        Available Sections:
                                                    </Typography>

                                                    <Grid container spacing={2}>
                                                        {course.sections.map((section, sectionIndex) => (
                                                            <Grid item xs={12} sm={6} md={4} key={sectionIndex}>
                                                                <Box
                                                                    p={2}
                                                                    borderRadius="8px"
                                                                    style={{
                                                                        backgroundColor: 'var(--bg-page)',
                                                                        border: '1px solid var(--border)'
                                                                    }}
                                                                >
                                                                    <Typography variant="body2" style={{ fontWeight: 600, marginBottom: 4 }}>
                                                                        Section {section.section_id}
                                                                    </Typography>
                                                                    <Typography variant="caption" color="textSecondary" display="block" style={{ marginBottom: 8 }}>
                                                                        {section.instructors.join(', ') || 'Instructor TBA'}
                                                                    </Typography>

                                                                    {section.times.map((time, timeIndex) => (
                                                                        time.day !== "No Timestamp Added Yet" && (
                                                                            <Typography key={timeIndex} variant="caption" display="block" style={{ marginBottom: 2 }}>
                                                                                <strong>{formatDay(time.day)}</strong> {formatTime(time)}
                                                                                <br />
                                                                                📍 {time.room || "Room TBA"}
                                                                            </Typography>
                                                                        )
                                                                    ))}

                                                                    <ModernButton
                                                                        size="small"
                                                                        variant="outlined"
                                                                        startIcon={<AddIcon />}
                                                                        onClick={() => handleAddNTE(course, section)}
                                                                        fullWidth
                                                                        style={{ marginTop: 8 }}
                                                                    >
                                                                        Add Section
                                                                    </ModernButton>
                                                                </Box>
                                                            </Grid>
                                                        ))}
                                                    </Grid>
                                                </CardContent>
                                            </CourseCard>
                                        </Grid>
                                    ))}
                                </Grid>
                            )}
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