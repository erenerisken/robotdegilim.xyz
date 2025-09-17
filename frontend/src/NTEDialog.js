import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    List,
    ListItem,
    ListItemText,

    IconButton,
    Typography,
    Chip,
    Box,
    Divider,
    CircularProgress
} from '@material-ui/core';
import { Alert } from '@material-ui/lab';
import AddIcon from '@material-ui/icons/Add';
import CloseIcon from '@material-ui/icons/Close';
import { getNTECourses, filterAvailableNTEs } from './data/Course';

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
        onAddCourse(convertedCourse);
    };

    const convertNTEToCourse = (nteCourse, selectedSection) => {
        return {
            code: nteCourse.code.numeric,
            abbreviation: nteCourse.code.departmental,
            name: nteCourse.name.split(' - ')[1] || nteCourse.name,
            category: 0, // NTE kategorisi
            sections: [{
                instructor: selectedSection.instructors.join(', '),
                sectionNumber: selectedSection.section_id,
                criteria: [{
                    dept: "ALL",
                    surnameStart: "AA",
                    surnameEnd: "ZZ"
                }],
                minYear: 0,
                maxYear: 0,
                lectureTimes: selectedSection.times
                    .filter(time => time.day !== "No Timestamp Added Yet" && time.start && time.end)
                    .map(time => ({
                        classroom: time.room || "TBA",
                        day: getDayNumber(time.day),
                        startHour: parseInt(time.start.split(':')[0]),
                        startMin: parseInt(time.start.split(':')[1]),
                        endHour: parseInt(time.end.split(':')[0]),
                        endMin: parseInt(time.end.split(':')[1])
                    }))
            }]
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
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="h6">
                        Available NTE Courses
                    </Typography>
                    <IconButton onClick={onClose} size="small">
                        <CloseIcon />
                    </IconButton>
                </Box>
            </DialogTitle>
            
            <DialogContent>
                {loading ? (
                    <Box display="flex" justifyContent="center" p={3}>
                        <CircularProgress />
                    </Box>
                ) : error ? (
                    <Alert severity="error">{error}</Alert>
                ) : (
                    <>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                            Found {availableNTEs.length} NTE courses that fit your current schedule.
                        </Typography>
                        
                        {availableNTEs.length === 0 ? (
                            <Alert severity="info">
                                No NTE courses available for your current schedule. 
                                Create free time slots in your program or modify existing courses.
                            </Alert>
                        ) : (
                            <List>
                                {availableNTEs.map((course, index) => (
                                    <React.Fragment key={`${course.code.numeric}-${index}`}>
                                        <ListItem>
                                            <ListItemText
                                                primary={
                                                    <Box>
                                                        <Typography variant="subtitle1" component="div">
                                                            <strong>{course.code.departmental}</strong> - {course.name.split(' - ')[1] || course.name}
                                                        </Typography>
                                                        <Chip 
                                                            label={`${course.credits} Credits`} 
                                                            size="small" 
                                                            color="primary"
                                                            style={{ marginTop: 4 }}
                                                        />
                                                    </Box>
                                                }
                                                secondary={
                                                    <Box mt={1}>
                                                        {course.sections.map((section, sectionIndex) => (
                                                                <Box key={sectionIndex} mb={1}>
                                                                    <Typography variant="body2" color="textSecondary">
                                                                        <strong>Section {section.section_id}:</strong> {section.instructors.join(', ')}
                                                                    </Typography>
                                                                    {section.times.map((time, timeIndex) => (
                                                                        time.day !== "No Timestamp Added Yet" && (
                                                                            <Typography key={timeIndex} variant="caption" display="block">
                                                                                {formatDay(time.day)} {formatTime(time)} - {time.room || "Room not specified"}
                                                                            </Typography>
                                                                        )
                                                                    ))}
                                                                    <Button
                                                                        size="small"
                                                                        startIcon={<AddIcon />}
                                                                        onClick={() => handleAddNTE(course, section)}
                                                                        style={{ marginTop: 4 }}
                                                                    >
                                                                        Add Section {section.section_id}
                                                                    </Button>
                                                                </Box>
                                                            ))
                                                        }
                                                    </Box>
                                                }
                                            />
                                        </ListItem>
                                        {index < availableNTEs.length - 1 && <Divider />}
                                    </React.Fragment>
                                ))}
                            </List>
                        )}
                    </>
                )}
            </DialogContent>
            
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default NTEDialog; 