import React, { useState, useEffect, useMemo } from 'react';
import {
    Dialog,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Box,
    Divider,
    CircularProgress,
    Card,
    CardContent,
    Checkbox,
    FormControlLabel,
    FormGroup,
    Grid,
    Switch,
    Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SchoolIcon from '@mui/icons-material/School';
import LibraryAddIcon from '@mui/icons-material/LibraryAdd';
import { withStyles } from '@mui/styles';
import { getElectives } from './data/Course';

// Styled Components
const StyledDialog = withStyles((theme) => ({
    paper: {
        borderRadius: 'var(--radius-lg)',
        maxHeight: '90vh',
    },
}))(Dialog);

const CourseCard = withStyles((theme) => ({
    root: {
        borderRadius: 'var(--radius)',
        marginBottom: theme.spacing(1.5),
        border: '1px solid var(--border)',
        boxShadow: 'none',
        transition: 'border-color 0.16s ease, box-shadow 0.16s ease',
        '&:hover': {
            borderColor: 'var(--border-strong)',
            boxShadow: 'var(--shadow-sm)',
        },
    },
}))(Card);

const ModernButton = withStyles((theme) => ({
    root: {
        borderRadius: 'var(--radius)',
        fontWeight: 600,
        textTransform: 'none',
        padding: theme.spacing(0.85, 2),
        boxShadow: 'none',
        '&:hover': {
            boxShadow: 'var(--shadow-xs)',
        },
        transition: 'background-color 0.16s ease, box-shadow 0.16s ease',
        margin: theme.spacing(0.5),
    },
}))(Button);

const filterBarSx = {
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: (theme) => theme.spacing(1.5, 2),
    marginBottom: 1,
    // A department can list hundreds of electives, so the filter has to stay
    // reachable without scrolling back to the top.
    position: 'sticky',
    top: 0,
    zIndex: 2,
    backgroundColor: 'background.paper',
};

// Which elective types a department offers is up to its curriculum: some list a
// single one, others seven. Read them off the data rather than naming them.
const categoryOf = (course) => course.category || 'General Electives';

const conflictsWithSchedule = (section, occupiedSlots) =>
    (section.lectureTimes || []).some((time) =>
        occupiedSlots.some((occupied) => {
            if (time.day !== occupied.day) return false;
            const tStart = time.startHour * 60 + time.startMin;
            const tEnd = time.endHour * 60 + time.endMin;
            const oStart = occupied.startHour * 60 + occupied.startMin;
            const oEnd = occupied.endHour * 60 + occupied.endMin;
            return !(tEnd <= oStart || oEnd <= tStart);
        })
    );

// Box ignores a `classes` prop in MUI v5, so this header is styled inline.
const headerBoxStyle = {
    background: 'var(--bg-subtle)',
    color: 'var(--text-primary)',
    borderBottom: '1px solid var(--border)',
    padding: '18px 24px',
    borderRadius: 'var(--radius-lg) var(--radius-lg) 0 0',
    width: '100%',
    boxSizing: 'border-box',
};

const HeaderBox = ({ children }) => <div style={headerBoxStyle}>{children}</div>;

const NTEDialog = ({ open, onClose, occupiedSlots, onAddCourse, department, allCourses }) => {
    const [electivesData, setElectivesData] = useState([]);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [showConflicts, setShowConflicts] = useState(true);
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
            // Returns the electives the department may take this semester, as
            // [{ code, stringCode, name, category, sectionNumbers }].
            const data = await getElectives(department);
            const coursesByCode = new Map(allCourses.map((course) => [course.code, course]));

            // Sections keep the index they have on the course, because that is
            // what gets handed back when one is added and the sections held for
            // other departments never make it into this list.
            const linked = data
                .map((elective) => {
                    const fullCourse = coursesByCode.get(elective.code);
                    if (!fullCourse) return null;

                    const sections = fullCourse.sections
                        .map((section, index) => ({ section, index }))
                        .filter(({ section }) =>
                            elective.sectionNumbers.includes(section.sectionNumber)
                        );

                    return sections.length ? { ...elective, fullCourse, sections } : null;
                })
                .filter((elective) => elective !== null);

            linked.sort(
                (a, b) =>
                    categoryOf(a).localeCompare(categoryOf(b)) ||
                    a.stringCode.localeCompare(b.stringCode)
            );

            setElectivesData(linked);
            // Every type starts ticked, and a department switch re-reads them.
            setSelectedCategories([...new Set(linked.map(categoryOf))]);
        } catch (err) {
            setError('Error loading electives.');
            console.error('Error loading electives:', err);
        } finally {
            setLoading(false);
        }
    };

    const categories = useMemo(() => {
        const counts = new Map();
        electivesData.forEach((course) => {
            const category = categoryOf(course);
            counts.set(category, (counts.get(category) || 0) + 1);
        });
        return [...counts.entries()]
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => a.name.localeCompare(b.name));
    }, [electivesData]);

    const visibleElectives = useMemo(
        () =>
            electivesData
                .filter((course) => selectedCategories.includes(categoryOf(course)))
                .map((course) => ({
                    ...course,
                    visibleSections: showConflicts
                        ? course.sections
                        : course.sections.filter(
                              ({ section }) => !conflictsWithSchedule(section, occupiedSlots)
                          ),
                }))
                .filter((course) => showConflicts || course.visibleSections.length > 0),
        [electivesData, selectedCategories, showConflicts, occupiedSlots]
    );

    const toggleCategory = (category) => {
        setSelectedCategories((selected) =>
            selected.includes(category)
                ? selected.filter((name) => name !== category)
                : [...selected, category]
        );
    };

    const handleAddElective = (course, sectionIndex) => {
        onAddCourse(course.fullCourse, [sectionIndex]);
    };

    // "All" means the sections on screen: the ones the department is let into,
    // minus any the clash filter is currently hiding.
    const handleAddAllSections = (course) => {
        onAddCourse(
            course.fullCourse,
            course.visibleSections.map(({ index }) => index)
        );
    };

    const formatTime = (t) => {
        const pad = (n) => n.toString().padStart(2, '0');
        return `${pad(t.startHour)}:${pad(t.startMin)} - ${pad(t.endHour)}:${pad(t.endMin)}`;
    };

    const formatDay = (dayNum) => {
        // Indexed by Date.getDay(), the numbering lecture times use.
        const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        return dayNames[dayNum] || "Unknown";
    };

    const renderCategoryFilter = () => {
        if (categories.length === 0) return null;
        return (
            <Box sx={filterBarSx}>
                <Typography variant="subtitle2" style={{ fontWeight: 600, marginBottom: 4 }}>
                    Elective types
                </Typography>
                <FormGroup row>
                    {categories.map(({ name, count }) => (
                        <FormControlLabel
                            key={name}
                            control={
                                <Checkbox
                                    size="small"
                                    color="primary"
                                    checked={selectedCategories.includes(name)}
                                    onChange={() => toggleCategory(name)}
                                />
                            }
                            label={
                                <Typography variant="body2">
                                    {name} ({count})
                                </Typography>
                            }
                        />
                    ))}
                </FormGroup>
                <Divider style={{ margin: '4px 0' }} />
                <FormControlLabel
                    control={
                        <Switch
                            size="small"
                            color="primary"
                            checked={showConflicts}
                            onChange={() => setShowConflicts((shown) => !shown)}
                        />
                    }
                    label={
                        <Typography variant="body2">
                            Show sections that clash with your schedule
                        </Typography>
                    }
                />
            </Box>
        );
    };

    // Grouping for render
    const renderElectivesList = () => {
        if (electivesData.length === 0) {
            return (
                <Alert severity="info" style={{ borderRadius: 'var(--radius)' }}>
                    None of {department}'s electives are open to it this semester.
                </Alert>
            );
        }

        if (visibleElectives.length === 0) {
            return (
                <Alert severity="info" style={{ borderRadius: 'var(--radius)' }}>
                    {selectedCategories.length === 0
                        ? 'Tick an elective type to see courses.'
                        : 'Every elective of the ticked types clashes with your schedule.'}
                </Alert>
            );
        }

        let currentCategory = "";

        return visibleElectives.map((course, index) => {
            const isNewGroup = index === 0 || categoryOf(course) !== currentCategory;
            if (isNewGroup) {
                currentCategory = categoryOf(course);
            }

            return (
                <Box key={`${course.code}-${categoryOf(course)}`}>
                    {isNewGroup && (
                        <Typography variant="subtitle1" style={{ marginTop: 20, marginBottom: 10, fontWeight: 700, color: 'var(--accent)' }}>
                            {currentCategory}
                        </Typography>
                    )}
                    
                    <CourseCard>
                        <CardContent>
                            <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                <Box>
                                    <Typography variant="subtitle1" style={{ fontWeight: 600, marginBottom: 6 }}>
                                        {course.stringCode}
                                    </Typography>
                                    <Typography variant="body1" color="textSecondary" style={{ marginBottom: 8 }}>
                                        {course.name}
                                    </Typography>
                                </Box>
                                {course.visibleSections.length > 0 && (
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

                            {course.visibleSections.length > 0 && (
                                <>
                                    <Divider style={{ margin: '16px 0' }} />
                                    <Typography variant="subtitle2" style={{ fontWeight: 600, marginBottom: 12 }}>
                                        Available Sections:
                                    </Typography>
                                    <Grid container spacing={2}>
                                        {course.visibleSections.map(({ section, index: sectionIndex }) => {
                                            const isConflict = conflictsWithSchedule(section, occupiedSlots);

                                            return (
                                                <Grid item xs={12} sm={6} md={4} key={sectionIndex}>
                                                    <Box
                                                        p={2}
                                                        borderRadius="var(--radius-sm)"
                                                        style={{
                                                            backgroundColor: isConflict ? 'rgba(224, 82, 74, 0.12)' : 'var(--bg-subtle)',
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
                    <Box display="flex" justifyContent="center" alignItems="center">
                        <Box display="flex" alignItems="center" gap={2}>
                            <SchoolIcon style={{ color: 'var(--accent)' }} />
                            <Box textAlign="center">
                                <Typography variant="h6" style={{ fontWeight: 700, marginBottom: '4px' }}>
                                    Available Electives for {department}
                                </Typography>
                                <Typography variant="body2" style={{ color: 'var(--text-secondary)' }}>
                                    Offered this semester and open to your department
                                </Typography>
                            </Box>
                        </Box>
                    </Box>
                </HeaderBox>

                <Box p={{ xs: 2, sm: 3 }}>
                    {loading ? (
                        <Box display="flex" justifyContent="center" p={3}>
                            <CircularProgress size={44} />
                        </Box>
                    ) : error ? (
                        <Alert severity="error">{error}</Alert>
                    ) : (
                        <>
                            {renderCategoryFilter()}
                            {renderElectivesList()}
                        </>
                    )}
                </Box>
            </DialogContent>

            <DialogActions style={{ padding: '12px 24px', borderTop: '1px solid var(--border)' }}>
                <ModernButton onClick={onClose} variant="outlined" color="primary">
                    Close
                </ModernButton>
            </DialogActions>
        </StyledDialog>
    );
};

export default NTEDialog;
