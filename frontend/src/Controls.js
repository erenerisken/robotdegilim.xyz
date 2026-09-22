import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
    TextField,
    Select,
    Button,
    Grid,
    Paper,
    Snackbar,
    Typography,
    Divider,
    FormControl,
    InputLabel,
    MenuItem,
} from "@mui/material";
import InputAdornment from "@mui/material/InputAdornment";
import MuiAlert from "@mui/material/Alert";
import AddIcon from "@mui/icons-material/Add";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import ImportContactsIcon from "@mui/icons-material/ImportContacts";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import SaveAltIcon from "@mui/icons-material/SaveAlt";
import { isMobile } from "react-device-detect";
import ls from "./utils/storage";
import { resetScenarios, setScenarios } from "./slices/scenariosSlice";
import { getAllCourses, getCurriculumUrl, getMusts } from "./data/Course";
import { compute_schedule } from "./schedule";
import { client } from "./Client";
import { CourseCard } from "./CourseCard";
import { AddCourseWidget } from "./AddCourseWidget";
import { AddDontFillWidget } from "./AddDontFillWidget";
import { AdvancedSettings } from "./AdvancedSettings";
import { Colorset } from "./Colorset";
import { LoadingDialog } from "./LoadingDialog/LoadingDialog";
import { LoadErrorDialog } from "./LoadErrorDialog";
import { withDeadline } from "./helpers/withDeadline";
import "./Controls.css";
import { resetDontFills } from "./slices/dontFillsSlice";
import NTEDialog from "./NTEDialog";
import DepartmentsDialog from "./DepartmentsDialog";
import SchoolIcon from "@mui/icons-material/School";
import AccountCircle from "@mui/icons-material/AccountCircle";
import BusinessIcon from "@mui/icons-material/Business";
import CalendarToday from "@mui/icons-material/CalendarToday";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import ApartmentIcon from "@mui/icons-material/Apartment";

// Long enough for the multi-megabyte catalogue on a slow connection, short
// enough that a request which will never arrive does not hold the app hostage.
const LOAD_TIMEOUT_MS = 35000;

export const Controls = (props) => {
    const { currentScenario } = props;
    const [surname, setSurname] = useState("");
    const [department, setDepartment] = useState("");
    const [semester, setSemester] = useState(0);
    const [alertMsg, setAlertMsg] = useState("");
    const [errorDept, setErrorDept] = useState(false);
    const [departmentsDialogOpen, setDepartmentsDialogOpen] = useState(false);
    const [errorSemester, setErrorSemester] = useState(false);
    const [errorSurname, setErrorSurname] = useState(false);
    const [restoreAvailable, setRestoreAvailable] = useState(false);
    const [restoredInfo, setRestoredInfo] = useState({
        surname: "",
        department: "",
        semester: 0,
    });
    const [selectedCourses, setSelectedCourses] = useState([]);
    const [restoredCourses, setRestoredCourses] = useState([]);
    const [allCourses, setAllCourses] = useState([]);
    const [settings, setSettings] = useState({
        checkSurname: true,
        checkDepartment: true,
        checkCollision: true,
    });
    const [restoredSettings, setRestoredSettings] = useState({
        checkSurname: true,
        checkDepartment: true,
        checkCollision: true,
        disableCourse: false,
    });
    const [colorset] = useState(new Colorset());
    const [lastUpdated, setLastUpdated] = useState(0);
    const [loading, setLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState("Loading...");
    const [loadFailed, setLoadFailed] = useState(false);
    const [nteDialogOpen, setNteDialogOpen] = useState(false);

    const dispatch = useDispatch();
    const scenariosState = useSelector((state) => state.scenariosState);

    const loadCourses = () => {
        setLoadFailed(false);
        setLoading(true);
        setLoadingMessage("Loading...");
        withDeadline(getAllCourses(), LOAD_TIMEOUT_MS)
            .then((data) => {
                setAllCourses(data);
                restoreData();
                setLoading(false);
                props.onLoadingCompleted();
            })
            .catch((error) => {
                console.error("Could not load course data:", error);
                setLoading(false);
                setLoadFailed(true);
            });
    };

    useEffect(() => {
        client.sendUpdateRequest();
        document.title = "Robot Değilim *-*";
        loadCourses();
        client
            .getLastUpdated()
            .then((lu) => setLastUpdated(lu))
            .catch((error) =>
                console.error("Could not read the data timestamp:", error),
            );
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const restoreData = () => {
        const rCourses = ls.get("restoredCourses");
        const rInfo = ls.get("restoredInfo");
        const rSettings = ls.get("restoredSettings");
        setRestoredCourses(rCourses !== null ? rCourses : []);
        setRestoredSettings(
            rSettings !== null
                ? rSettings
                : {
                      checkSurname: true,
                      checkDepartment: true,
                      checkCollision: true,
                      disableCourse: false,
                  },
        );
        setRestoredInfo(
            rInfo !== null
                ? {
                      surname: rInfo.surname,
                      department: rInfo.department,
                      semester: rInfo.semester,
                  }
                : { surname: "", department: "", semester: 0 },
        );
        setRestoreAvailable(rSettings !== null);
    };

    const loadRestoredData = () => {
        try {
            // First set the courses without applying manual classrooms
            setSelectedCourses(restoredCourses);
            setSettings(restoredSettings);
            setSurname(restoredInfo.surname);
            setSemester(restoredInfo.semester);
            setDepartment(restoredInfo.department);

            // Then apply manual classrooms safely
            restoredCourses.forEach((course, courseIndex) => {
                if (course && course.manualClassrooms) {
                    Object.keys(course.manualClassrooms).forEach((key) => {
                        const [sectionIndex, lectureTimeIndex] = key
                            .split("-")
                            .map(Number);
                        const newClassroom = course.manualClassrooms[key];

                        // Use setTimeout to avoid immediate state conflicts
                        setTimeout(() => {
                            handleClassroomUpdate(
                                courseIndex,
                                sectionIndex,
                                lectureTimeIndex,
                                newClassroom,
                            );
                        }, 100);
                    });
                }
            });
        } catch (error) {
            console.error("Error loading restored data:", error);
            setAlertMsg("Kaydedilen veriler yüklenirken bir hata oluştu.");
        }
    };

    const getCourseByCode = (code) => {
        for (let course of allCourses) {
            if (course.code === code) return course;
        }
        return null;
    };

    const getSectionByNumber = (c, n) => {
        for (let section of c.sections) {
            if (section.sectionNumber === n) return section;
        }
        return null;
    };

    const getColorByCourseCode = (code) => {
        for (let course of selectedCourses) {
            if (course === null) continue;
            if (course.code === code) return course.color;
        }
        return null;
    };

    const handleAddMustCourse = () => {
        // Reset error states
        setAlertMsg("");
        setErrorDept(false);
        setErrorSemester(false);
        setErrorSurname(false);
        if (department.length < 2) {
            setAlertMsg("Please enter a correct department");
            setErrorDept(true);
            return;
        }
        if (semester < 1) {
            setAlertMsg("Please choose a semester");
            setErrorSemester(true);
            return;
        }
        if (semester > 8) {
            setAlertMsg("Semester value cannot be greater than 8");
            setErrorSemester(true);
            return;
        }
        getMusts(department, semester)
            .then((data) => {
                if (data && data.length > 0) {
                    const newCourses = data
                        .filter(
                            (code) =>
                                !selectedCourses.some((c) => c?.code === code),
                        )
                        .map((code) => getCourseByCode(code))
                        .filter((course) => course !== null);

                    handleAddCourses(newCourses);
                }
            })
            .catch((_) => {
                setAlertMsg(
                    "Must courses for your department are not available",
                );
                setErrorDept(true);
            });
    };

    const handleAlertClose = () => {
        setAlertMsg("");
    };

    const handleDeleteCourse = (i) => {
        const newSelected = [...selectedCourses];
        newSelected[i] = null;
        setSelectedCourses(newSelected);
    };

    const handleToggle = (i, sections) => {
        const newSelected = [...selectedCourses];
        newSelected[i].sections = sections;
        setSelectedCourses(newSelected);
    };

    const handleAddCourses = (courses) => {
        if (courses && courses.length > 0) {
            const newSelected = [...selectedCourses];
            courses.forEach((c) =>
                newSelected.push({
                    code: c.code,
                    sections: Array(c.sections.length).fill(true),
                    color: colorset.getNextColor(),
                    settings: {
                        checkSurname: true,
                        checkDepartment: true,
                        checkCollision: true,
                        disableCourse: false,
                    },
                    manualClassrooms: {},
                }),
            );
            setSelectedCourses(newSelected);
        }
    };

    const handleCourseSettings = (i, s) => {
        const newSelected = [...selectedCourses];
        newSelected[i].settings = s;
        setSelectedCourses(newSelected);
    };

    const handleCourseColor = (i, c) => {
        const newSelected = [...selectedCourses];
        newSelected[i].color = c;
        setSelectedCourses(newSelected);
    };

    const handleClassroomUpdate = (
        courseIndex,
        sectionIndex,
        lectureTimeIndex,
        newClassroom,
    ) => {
        try {
            const newSelected = [...selectedCourses];
            const courseCode = newSelected[courseIndex].code;

            // Initialize manual classrooms if not exists
            if (!newSelected[courseIndex].manualClassrooms) {
                newSelected[courseIndex].manualClassrooms = {};
            }

            // Store the manual classroom override
            const key = `${sectionIndex}-${lectureTimeIndex}`;
            newSelected[courseIndex].manualClassrooms[key] = newClassroom;

            setSelectedCourses(newSelected);

            // Also update the scenario data if schedule is already computed
            if (scenariosState.result && scenariosState.result.length > 0) {
                const updatedScenarios = scenariosState.result.map(
                    (scenario) => {
                        return scenario.map((courseInScenario) => {
                            if (
                                courseInScenario.section &&
                                courseInScenario.section.lectureTimes &&
                                courseInScenario.section.lectureTimes[
                                    lectureTimeIndex
                                ] &&
                                getCourseByCode(courseCode)?.abbreviation ===
                                    courseInScenario.abbreviation &&
                                courseInScenario.section.sectionNumber ===
                                    getCourseByCode(courseCode)?.sections[
                                        sectionIndex
                                    ]?.sectionNumber
                            ) {
                                const updatedCourse = { ...courseInScenario };
                                updatedCourse.section = {
                                    ...updatedCourse.section,
                                };
                                updatedCourse.section.lectureTimes = [
                                    ...updatedCourse.section.lectureTimes,
                                ];
                                updatedCourse.section.lectureTimes[
                                    lectureTimeIndex
                                ] = {
                                    ...updatedCourse.section.lectureTimes[
                                        lectureTimeIndex
                                    ],
                                    classroom: newClassroom,
                                };
                                return updatedCourse;
                            }
                            return courseInScenario;
                        });
                    },
                );
                dispatch(setScenarios(updatedScenarios));
            }

            // Update the actual course data in allCourses safely
            setAllCourses((prevCourses) => {
                try {
                    const updatedCourses = prevCourses.map((course) => {
                        if (course.code === courseCode) {
                            const updatedCourse = { ...course };
                            updatedCourse.sections = updatedCourse.sections.map(
                                (section, sIdx) => {
                                    if (sIdx === sectionIndex) {
                                        const updatedSection = { ...section };
                                        updatedSection.lectureTimes =
                                            updatedSection.lectureTimes.map(
                                                (lectureTime, ltIdx) => {
                                                    if (
                                                        ltIdx ===
                                                        lectureTimeIndex
                                                    ) {
                                                        return {
                                                            ...lectureTime,
                                                            classroom:
                                                                newClassroom,
                                                        };
                                                    }
                                                    return lectureTime;
                                                },
                                            );
                                        return updatedSection;
                                    }
                                    return section;
                                },
                            );
                            return updatedCourse;
                        }
                        return course;
                    });
                    return updatedCourses;
                } catch (error) {
                    console.error("Error updating course data:", error);
                    return prevCourses; // Return previous state if error occurs
                }
            });
        } catch (error) {
            console.error("Error in handleClassroomUpdate:", error);
            setAlertMsg("Derslik güncellenirken bir hata oluştu.");
        }
    };

    const handleChangeSettings = (s) => {
        setSettings(s);
    };

    const handleScheduleComplete = (scenariosArr) => {
        if (scenariosArr.length <= 0) {
            setAlertMsg("There is no available schedule for this criteria.");
            return;
        }
        const scenariosToSubmit = [];
        scenariosArr.forEach((s) => {
            const scenarioToPush = [];
            s.forEach((c) => {
                const currentCourse = getCourseByCode(c.code);
                const currentSection = getSectionByNumber(
                    currentCourse,
                    c.section,
                );
                const currentColor = getColorByCourseCode(c.code);
                scenarioToPush.push({
                    abbreviation: currentCourse.abbreviation,
                    section: currentSection,
                    color: currentColor,
                });
            });
            scenariosToSubmit.push(scenarioToPush);
        });
        dispatch(setScenarios(scenariosToSubmit));
    };

    const formatDf = (df) => {
        // Example input: '2021-02-20T09:40'
        return {
            day: df.startDate.getDay(),
            startHour: df.startDate.getHours(),
            startMin: df.startDate.getMinutes(),
            endHour: df.endDate.getHours(),
            endMin: df.endDate.getMinutes() - 1,
        };
    };

    const saveData = () => {
        ls.set("restoredCourses", selectedCourses);
        ls.set("restoredSettings", settings);
        ls.set("restoredInfo", { surname, department, semester });
    };

    const handleScheduleBegin = () => {
        setAlertMsg("");
        setErrorDept(false);
        setErrorSemester(false);
        setErrorSurname(false);
        if (settings.checkDepartment && department.length < 2) {
            setAlertMsg("Please enter a correct department");
            setErrorDept(true);
            return;
        }
        if (settings.checkSurname && surname.length < 2) {
            setAlertMsg("Please enter at least 2 letters of your surname");
            setErrorSurname(true);
            return;
        }
        const courseData = [];
        const dontFillsArr = [];
        selectedCourses.forEach((c) => {
            if (c === null || c.settings.disableCourse) return;
            const currentCourse = getCourseByCode(c.code);
            const courseToPush = {
                code: c.code,
                category: currentCourse.category,
                checkSurname: settings.checkSurname && c.settings.checkSurname,
                checkCollision:
                    settings.checkCollision && c.settings.checkCollision,
                checkDepartment:
                    settings.checkDepartment && c.settings.checkDepartment,
                sections: [],
            };
            for (let i = 0; i < currentCourse.sections.length; i++) {
                const sectionToPush = {
                    sectionNumber: currentCourse.sections[i].sectionNumber,
                    minYear: currentCourse.sections[i].minYear,
                    maxYear: currentCourse.sections[i].maxYear,
                    toggle: c.sections[i],
                    criteria: currentCourse.sections[i].criteria,
                    lectureTimes: [],
                };
                currentCourse.sections[i].lectureTimes.forEach((t) =>
                    sectionToPush.lectureTimes.push(t),
                );
                if (sectionToPush.criteria.length <= 0) {
                    sectionToPush.criteria = [
                        {
                            dept: "ALL",
                            surnameStart: "AA",
                            surnameEnd: "ZZ",
                        },
                    ];
                }
                if (sectionToPush.lectureTimes && sectionToPush.lectureTimes[0])
                    courseToPush.sections.push(sectionToPush);
            }
            if (courseToPush.sections && courseToPush.sections.length > 0) {
                courseData.push(courseToPush);
            }
        });
        props.dontFills.forEach((df) => {
            const formattedDf = formatDf(df);
            dontFillsArr.push({ times: [formattedDf] });
        });
        setLoading(true);
        setLoadingMessage("Computing schedule...");
        setTimeout(() => {
            const calculatedSchedule = compute_schedule(
                surname.slice(0, 2),
                department,
                0,
                courseData,
                dontFillsArr,
            );
            setLoading(false);
            handleScheduleComplete(calculatedSchedule);
        }, 500);
    };

    const handleClearCourses = () => {
        setSelectedCourses([]);
        dispatch(resetScenarios());
        dispatch(resetDontFills());
    };

    const openInNewTab = (url) => {
        const newWindow = window.open(url, "_blank", "noopener,noreferrer");
        if (newWindow) newWindow.opener = null;
    };

    const calculateOccupiedSlots = () => {
        const occupiedSlots = [];

        // Eğer schedule hesaplanmışsa, aktif scenario'yu kullan
        if (
            scenariosState.result &&
            scenariosState.result.length > currentScenario
        ) {
            const currentScenarioData = scenariosState.result[currentScenario]; // Aktif scenario'yu kullan

            currentScenarioData.forEach((courseInScenario) => {
                courseInScenario.section.lectureTimes.forEach((lectureTime) => {
                    occupiedSlots.push({
                        day: lectureTime.day,
                        startHour: lectureTime.startHour,
                        startMin: lectureTime.startMin,
                        endHour: lectureTime.endHour,
                        endMin: lectureTime.endMin,
                        source: "scheduled_course",
                        courseCode: courseInScenario.abbreviation,
                        sectionNumber: courseInScenario.section.sectionNumber,
                    });
                });
            });

            // console.log('Using SCHEDULED courses for NTE filtering:', occupiedSlots);
        } else {
            // Schedule henüz hesaplanmamışsa, seçili derslerin aktif şubelerini kullan
            selectedCourses.forEach((c) => {
                if (c === null || c.settings?.disableCourse) return;
                const currentCourse = getCourseByCode(c.code);
                if (!currentCourse) return;

                currentCourse.sections.forEach((section, sectionIndex) => {
                    if (!c.sections[sectionIndex]) return; // Bu section seçili değil

                    section.lectureTimes.forEach((lectureTime) => {
                        occupiedSlots.push({
                            day: lectureTime.day,
                            startHour: lectureTime.startHour,
                            startMin: lectureTime.startMin,
                            endHour: lectureTime.endHour,
                            endMin: lectureTime.endMin,
                            source: "selected_course",
                            courseCode: currentCourse.abbreviation,
                            sectionNumber: section.sectionNumber,
                        });
                    });
                });
            });

            // console.log('Using SELECTED courses for NTE filtering:', occupiedSlots);
        }

        // DontFill bloklarını da ekle
        props.dontFills.forEach((df) => {
            occupiedSlots.push({
                day: df.startDate.getDay(),
                startHour: df.startDate.getHours(),
                startMin: df.startDate.getMinutes(),
                endHour: df.endDate.getHours(),
                endMin: df.endDate.getMinutes(),
                source: "dontfill",
            });
        });

        return occupiedSlots;
    };

    const handleOpenCurriculum = async () => {
        const dept = department.trim();

        if (dept.length < 2) {
            setErrorDept(true);
            setAlertMsg(
                "Please enter your department first to see its curriculum."
            );
            return;
        }

        // The programme list is eight megabytes and is only downloaded when a
        // feature needs it, so the address is rarely ready when the button is
        // clicked. Claim the tab inside the click, while the browser still
        // credits the gesture, and send it on once the lookup answers.
        const tab = window.open("", "_blank");
        if (tab) tab.opener = null;

        setLoadingMessage("Looking up your curriculum...");
        setLoading(true);

        try {
            const url = await getCurriculumUrl(dept);

            if (!url) {
                if (tab) tab.close();
                setErrorDept(true);
                setAlertMsg(
                    `The catalog has no undergraduate curriculum for ${dept}.`
                );
                return;
            }

            if (tab) tab.location = url;
            else openInNewTab(url);
        } catch (error) {
            if (tab) tab.close();
            setAlertMsg("Could not reach the curriculum. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleGetAvailableNTE = () => {
        if (!department || department.length < 2) {
            setAlertMsg("Please enter your department first to see electives.");
            setErrorDept(true);
            return;
        }
        setNteDialogOpen(true);
    };

    const handleNTEDialogClose = () => {
        setNteDialogOpen(false);
    };

    // The dialog hands back the sections the department is let into, as indexes
    // on the course, so a section held for another department never arrives
    // switched on.
    const handleAddNTECourse = (nteCourse, sectionIndexes) => {
        const newSelected = [...selectedCourses];
        const sectionsArray = new Array(nteCourse.sections.length).fill(false);
        sectionIndexes.forEach((index) => {
            sectionsArray[index] = true;
        });

        newSelected.push({
            code: nteCourse.code,
            sections: sectionsArray,
            color: colorset.getNextColor(),
            settings: {
                checkSurname: true,
                checkDepartment: true,
                checkCollision: true,
                disableCourse: false,
            },
            manualClassrooms: {},
        });
        setSelectedCourses(newSelected);
        setNteDialogOpen(false);
    };

    return (
        <Paper
            className="controls-paper"
            style={isMobile ? styles.mobile : styles.desktop}
        >
            <Snackbar
                open={alertMsg !== ""}
                autoHideDuration={5000}
                onClose={handleAlertClose}
            >
                <MuiAlert
                    elevation={6}
                    variant="filled"
                    onClose={handleAlertClose}
                    severity="error"
                >
                    {alertMsg}
                </MuiAlert>
            </Snackbar>
            <div className="controls-section">
            <div className="controls-section-header">Your Details</div>
            <Grid container spacing={2} className="button-grid">
                <Grid item xs={12} md={12} lg={4}>
                    <TextField
                        fullWidth
                        required={settings.checkSurname}
                        error={errorSurname}
                        label="Surname"
                        value={surname}
                        inputProps={{ maxLength: 12 }}
                        variant="outlined"
                        placeholder="e.g. GUNDUZ"
                        className="pretty-textfield"
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <AccountCircle fontSize="small" />
                                </InputAdornment>
                            ),
                        }}
                        onChange={(e) =>
                            setSurname(e.target.value.toUpperCase())
                        }
                    />
                </Grid>
                <Grid item xs={12} md={12} lg={4}>
                    <TextField
                        fullWidth
                        required={settings.checkDepartment}
                        error={errorDept}
                        label="Department"
                        value={department}
                        inputProps={{ maxLength: 12 }}
                        variant="outlined"
                        placeholder="e.g. IE"
                        className="pretty-textfield"
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <BusinessIcon fontSize="small" />
                                </InputAdornment>
                            ),
                        }}
                        onChange={(e) =>
                            setDepartment(e.target.value.toUpperCase())
                        }
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <TextField
                        fullWidth
                        select
                        required
                        error={errorSemester}
                        label="Semester"
                        value={semester || ""}
                        variant="outlined"
                        size="small"
                        className="pretty-textfield"
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <CalendarToday fontSize="small" />
                                </InputAdornment>
                            ),
                        }}
                        onChange={(e) =>
                            setSemester(parseInt(e.target.value || "0", 10))
                        }
                        SelectProps={{
                            displayEmpty: true,
                        }}
                    >
                        <MenuItem value="" disabled left>
                            <Typography variant="body2" color="textSecondary">
                                e.g. 2nd year Spring -&gt; 4th
                            </Typography>
                        </MenuItem>
                        {[...Array(8)].map((_, idx) => (
                            <MenuItem key={idx + 1} value={idx + 1}>
                                {idx + 1}
                            </MenuItem>
                        ))}
                    </TextField>
                </Grid>
            </Grid>
            </div>
            <div className="controls-section">
            <div className="controls-section-header">Actions</div>
            <Grid container spacing={2} className="button-grid">
                <Grid item xs={12} sm={12} md={12} lg={4}>
                    <Button
                        fullWidth
                        variant="contained"
                        color="secondary"
                        className="pretty-button pretty-secondary"
                        startIcon={<AddIcon />}
                        onClick={handleAddMustCourse}
                    >
                        Add Must Courses
                    </Button>
                </Grid>
                <Grid item xs={12} sm={12} md={12} lg={4}>
                    <Button
                        fullWidth
                        variant="contained"
                        color="primary"
                        className="pretty-button pretty-primary"
                        startIcon={<EventAvailableIcon />}
                        onClick={handleScheduleBegin}
                    >
                        Schedule
                    </Button>
                </Grid>
                <Grid item xs={12} sm={12} md={12} lg={4}>
                    <Button
                        fullWidth
                        variant="contained"
                        className="pretty-button pretty-danger"
                        style={{ color: "white" }}
                        startIcon={<DeleteIcon style={{ color: "white" }} />}
                        onClick={handleClearCourses}
                    >
                        Clear
                    </Button>
                </Grid>
                <Grid item xs={12} sm={12} md={12} lg={6}>
                    <Button
                        fullWidth
                        variant="contained"
                        className="pretty-button pretty-warning"
                        style={{ color: "white" }}
                        startIcon={<SchoolIcon style={{ color: "white" }} />}
                        onClick={handleGetAvailableNTE}
                    >
                        Get Available Electives
                    </Button>
                </Grid>
                <Grid item xs={12} sm={12} md={12} lg={6}>
                    <Button
                        fullWidth
                        variant="contained"
                        className="pretty-button pretty-ternary"
                        startIcon={<MenuBookIcon />}
                        onClick={handleOpenCurriculum}
                    >
                        My Curriculum
                    </Button>
                </Grid>
                <Grid item xs={12} sm={12} md={12} lg={6}>
                    <Button
                        fullWidth
                        variant="contained"
                        className="pretty-button pretty-ternary"
                        startIcon={<ApartmentIcon />}
                        onClick={() => setDepartmentsDialogOpen(true)}
                    >
                        Departments
                    </Button>
                </Grid>
                <Grid item xs={12} sm={12} md={12} lg={6}>
                    <Button
                        fullWidth
                        variant="contained"
                        className="pretty-button pretty-ternary"
                        startIcon={<ImportContactsIcon />}
                        onClick={() => openInNewTab("https://metu-non.tech")}
                    >
                        NTE Catalog
                    </Button>
                </Grid>
            </Grid>
            </div>
            <AdvancedSettings
                settings={settings}
                onSettingsChange={handleChangeSettings}
            />
            <div className="control-row">
                <Button
                    variant="contained"
                    color="primary"
                    className="pretty-button pretty-primary"
                    onClick={saveData}
                    startIcon={<SaveIcon />}
                >
                    Save
                </Button>
                {restoreAvailable && (
                    <Button
                        variant="contained"
                        color="primary"
                        className="pretty-button pretty-primary"
                        onClick={loadRestoredData}
                        startIcon={<SaveAltIcon />}
                    >
                        Load
                    </Button>
                )}
            </div>
            <Divider />
            <AddCourseWidget
                courses={allCourses}
                onCourseAdd={(c) => handleAddCourses([c])}
            />
            <Divider />
            <div className="control-row">
                <div className="centered-row">Added Courses</div>
            </div>
            <Divider />
            <div className="control-courses">
                {selectedCourses.map((c, i) =>
                    c !== null ? (
                        <CourseCard
                            key={i}
                            course={getCourseByCode(c.code)}
                            onDelete={() => handleDeleteCourse(i)}
                            onToggle={(sections) => handleToggle(i, sections)}
                            color={c.color}
                            settings={c.settings}
                            sections={c.sections}
                            onSettingsChange={(s) => handleCourseSettings(i, s)}
                            onColorChange={(col) => handleCourseColor(i, col)}
                            onClassroomUpdate={(
                                sectionIndex,
                                lectureTimeIndex,
                                newClassroom,
                            ) =>
                                handleClassroomUpdate(
                                    i,
                                    sectionIndex,
                                    lectureTimeIndex,
                                    newClassroom,
                                )
                            }
                        />
                    ) : null,
                )}
            </div>
            <AddDontFillWidget
                startHour={8}
                startMin={40}
                endHour={17}
                endMin={30}
            />
            {loading && <LoadingDialog text={loadingMessage} />}
            {loadFailed && <LoadErrorDialog onRetry={loadCourses} />}
            {lastUpdated ? (
                <Typography>
                    {"Course data is updated at " + lastUpdated.u}
                    <br />
                    {"   Last added Semester: " + lastUpdated.t.split(":")[1]}
                </Typography>
            ) : null}

            <DepartmentsDialog
                open={departmentsDialogOpen}
                onClose={() => setDepartmentsDialogOpen(false)}
            />

            <NTEDialog
                open={nteDialogOpen}
                onClose={handleNTEDialogClose}
                occupiedSlots={calculateOccupiedSlots()}
                onAddCourse={handleAddNTECourse}
                department={department}
                allCourses={allCourses}
            />
        </Paper>
    );
};

const styles = {
    mobile: {
        width: "100%",
        minWidth: 0,
    },
    desktop: {
        flex: "1 1 480px",
        minWidth: 0,
        height: "fit-content",
    },
};

export default Controls;
