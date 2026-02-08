import React, { useState, useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  TextField,
  Select,
  Button,
  FormControl,
  FormHelperText,
  MenuItem,
  InputLabel,
  Paper,
  Snackbar,
  Typography,
  Divider,
} from "@material-ui/core";
import InputAdornment from "@material-ui/core/InputAdornment";
import MuiAlert from "@material-ui/lab/Alert";
import AddIcon from "@material-ui/icons/Add";
import EventAvailableIcon from "@material-ui/icons/EventAvailable";
import ImportContactsIcon from "@material-ui/icons/ImportContacts";
import DeleteIcon from "@material-ui/icons/Delete";
import SaveIcon from "@material-ui/icons/Save";
import SaveAltIcon from "@material-ui/icons/SaveAlt";
import AssignmentIcon from "@material-ui/icons/Assignment";
import { isMobile } from "react-device-detect";
import ls from "local-storage";
import { resetScenarios, setScenarios } from "./slices/scenariosSlice";
import { getAllCourses, getMusts } from "./data/Course";
import { compute_schedule } from "./schedule";
import { Client } from "./Client";
import { CourseCard } from "./CourseCard";
import { AddCourseWidget } from "./AddCourseWidget";
import { AddDontFillWidget } from "./AddDontFillWidget";
import { AdvancedSettings } from "./AdvancedSettings";
import { Colorset } from "./Colorset";
import { LoadingDialog } from "./LoadingDialog/LoadingDialog";
import "./Controls.css";
import { resetDontFills } from "./slices/dontFillsSlice";
import NTEDialog from "./NTEDialog";
import SchoolIcon from "@material-ui/icons/School";
import AccountCircle from "@material-ui/icons/AccountCircle";
import BusinessIcon from "@material-ui/icons/Business";

export const Controls = (props) => {
  const { currentScenario } = props;
  const [surname, setSurname] = useState("");
  const [department, setDepartment] = useState("");
  const [semester, setSemester] = useState(0);
  const [alertMsg, setAlertMsg] = useState("");
  const [errorDept, setErrorDept] = useState(false);
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
  const [nteDialogOpen, setNteDialogOpen] = useState(false);

  const dispatch = useDispatch();
  const scenariosState = useSelector((state) => state.scenariosState);

  const clientRef = useRef(new Client());

  useEffect(() => {
    clientRef.current.sendUpdateRequest();
    document.title = "Robot Değilim *-*";
    setLoading(true);
    setLoadingMessage("Loading...");
    getAllCourses().then((data) => {
      setAllCourses(data);
      restoreData();
      setLoading(false);
      props.onLoadingCompleted();
    });
    clientRef.current.getLastUpdated().then((lu) => setLastUpdated(lu));
    // Remove legacy zoom hack on mobile; rely on responsive CSS instead
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
          }
    );
    setRestoredInfo(
      rInfo !== null
        ? {
            surname: rInfo.surname,
            department: rInfo.department,
            semester: rInfo.semester,
          }
        : { surname: "", department: "", semester: 0 }
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
          Object.keys(course.manualClassrooms).forEach(key => {
            const [sectionIndex, lectureTimeIndex] = key.split('-').map(Number);
            const newClassroom = course.manualClassrooms[key];
            
            // Use setTimeout to avoid immediate state conflicts
            setTimeout(() => {
              handleClassroomUpdate(courseIndex, sectionIndex, lectureTimeIndex, newClassroom);
            }, 100);
          });
        }
      });
    } catch (error) {
      console.error('Error loading restored data:', error);
      setAlertMsg('Kaydedilen veriler yüklenirken bir hata oluştu.');
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

  const renderSemesterSelections = (n) => {
    const ret = [];
    ret.push(
      <MenuItem key="0" value={0}>
        ---
      </MenuItem>
    );
    for (let i = 0; i < n; i++) {
      ret.push(
        <MenuItem key={i + 1} value={i + 1}>
          {i + 1}
        </MenuItem>
      );
    }
    return ret;
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
    getMusts(department, semester)
      .then((data) => {
        if (data && data.length > 0) {
          const newCourses = data
            .filter((code) => !selectedCourses.some((c) => c?.code === code))
            .map((code) => getCourseByCode(code))
            .filter((course) => course !== null);

          handleAddCourses(newCourses);
        }
      })
      .catch((_) => {
        setAlertMsg("Must courses for your department are not available");
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
        })
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

  const handleClassroomUpdate = (courseIndex, sectionIndex, lectureTimeIndex, newClassroom) => {
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
        const updatedScenarios = scenariosState.result.map(scenario => {
          return scenario.map(courseInScenario => {
            if (courseInScenario.section && 
                courseInScenario.section.lectureTimes && 
                courseInScenario.section.lectureTimes[lectureTimeIndex] &&
                getCourseByCode(courseCode)?.abbreviation === courseInScenario.abbreviation &&
                courseInScenario.section.sectionNumber === getCourseByCode(courseCode)?.sections[sectionIndex]?.sectionNumber) {
              const updatedCourse = { ...courseInScenario };
              updatedCourse.section = { ...updatedCourse.section };
              updatedCourse.section.lectureTimes = [...updatedCourse.section.lectureTimes];
              updatedCourse.section.lectureTimes[lectureTimeIndex] = {
                ...updatedCourse.section.lectureTimes[lectureTimeIndex],
                classroom: newClassroom
              };
              return updatedCourse;
            }
            return courseInScenario;
          });
        });
        dispatch(setScenarios(updatedScenarios));
      }
      
      // Update the actual course data in allCourses safely
      setAllCourses(prevCourses => {
        try {
          const updatedCourses = prevCourses.map(course => {
            if (course.code === courseCode) {
              const updatedCourse = { ...course };
              updatedCourse.sections = updatedCourse.sections.map((section, sIdx) => {
                if (sIdx === sectionIndex) {
                  const updatedSection = { ...section };
                  updatedSection.lectureTimes = updatedSection.lectureTimes.map((lectureTime, ltIdx) => {
                    if (ltIdx === lectureTimeIndex) {
                      return { ...lectureTime, classroom: newClassroom };
                    }
                    return lectureTime;
                  });
                  return updatedSection;
                }
                return section;
              });
              return updatedCourse;
            }
            return course;
          });
          return updatedCourses;
        } catch (error) {
          console.error('Error updating course data:', error);
          return prevCourses; // Return previous state if error occurs
        }
      });
    } catch (error) {
      console.error('Error in handleClassroomUpdate:', error);
      setAlertMsg('Derslik güncellenirken bir hata oluştu.');
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
        const currentSection = getSectionByNumber(currentCourse, c.section);
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
        checkCollision: settings.checkCollision && c.settings.checkCollision,
        checkDepartment: settings.checkDepartment && c.settings.checkDepartment,
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
          sectionToPush.lectureTimes.push(t)
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
        dontFillsArr
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

  const handleGetAvailableNTE = () => {
    setNteDialogOpen(true);
  };

  const handleNTEDialogClose = () => {
    setNteDialogOpen(false);
  };

  const handleAddNTECourse = (nteCourse, selectedSectionIndex = 0) => {
    // NTE dersleri için özel handler
    const newSelected = [...selectedCourses];
    let sectionsArray;
    
    if (selectedSectionIndex === -1) {
      // Tüm section'ları aktif et
      sectionsArray = new Array(nteCourse.sections.length).fill(true);
    } else {
      // Tüm section'lar için false array oluştur, sadece seçilen index'i true yap
      sectionsArray = new Array(nteCourse.sections.length).fill(false);
      sectionsArray[selectedSectionIndex] = true;
    }
    
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
    <Paper className="controls-paper" style={isMobile ? styles.mobile : styles.desktop}>
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
      <div className="control-row">
        <div className="textfield-wrapper">
          <TextField
            required={settings.checkSurname}
            error={errorSurname}
            label="Surname"
            value={surname}
            inputProps={{ maxLength: 12 }}
            variant="outlined"
            size="small"
            placeholder="e.g. KORKMAZ"
            className="pretty-textfield"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <AccountCircle fontSize="small" />
                </InputAdornment>
              ),
            }}
            onChange={(e) => setSurname(e.target.value.toUpperCase())}
          />
        </div>
        <div className="textfield-wrapper">
          <TextField
            required={settings.checkDepartment}
            error={errorDept}
            label="Department"
            value={department}
            inputProps={{ maxLength: 12 }}
            variant="outlined"
            size="small"
            placeholder="e.g. IE"
            className="pretty-textfield"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <BusinessIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
            onChange={(e) => setDepartment(e.target.value.toUpperCase())}
          />
        </div>
      </div>
      <div className="control-row">
        <div className="textfield-wrapper">
          <FormControl
            variant="outlined"
            size="small"
            className="form-control pretty-select"
          >
            <InputLabel className="controls-select-label">Semester</InputLabel>
            <Select
              error={errorSemester}
              value={semester}
              onChange={(e) => setSemester(e.target.value)}
              label="Semester"
              displayEmpty
              MenuProps={{
                PaperProps: {
                  style: {
                    borderRadius: 10,
                    boxShadow: "0 10px 24px rgba(0,0,0,0.12)",
                    maxHeight: 320,
                  },
                },
                MenuListProps: { dense: true },
                getContentAnchorEl: null,
                anchorOrigin: { vertical: "bottom", horizontal: "left" },
                transformOrigin: { vertical: "top", horizontal: "left" },
              }}
            >
              {renderSemesterSelections(8)}
            </Select>
            <FormHelperText>Ex: 2nd year Fall semester -{">"} 3</FormHelperText>
          </FormControl>
        </div>
      </div>
      <div className="control-row">
        <div className="control-button">
          <Button
            variant="contained"
            color="secondary"
            className="pretty-button pretty-secondary"
            startIcon={<AddIcon />}
            onClick={handleAddMustCourse}
          >
            Add Must Courses
          </Button>
        </div>
        <div className="control-button">
          <Button
            variant="contained"
            color="primary"
            className="pretty-button pretty-primary"
            startIcon={<EventAvailableIcon />}
            onClick={handleScheduleBegin}
          >
            Schedule
          </Button>
        </div>
        <div className="control-button">
          <Button
            variant="contained"
            className="pretty-button pretty-warning"
            style={{ color: "white" }}
            startIcon={<SchoolIcon style={{ color: "white" }} />}
            onClick={handleGetAvailableNTE}
          >
            Get Available NTE
          </Button>
        </div>
      </div>
      <div className="control-row">
        <div className="control-button">
          <Button
            variant="contained"
            className="pretty-button pretty-ternary"
            startIcon={<ImportContactsIcon />}
            onClick={() => openInNewTab("https://metu-non.tech")}
          >
            NTE Catalog
          </Button>
        </div>
        <div className="control-button">
          <Button
            variant="contained"
            className="pretty-button pretty-danger"
            style={{ color: "white" }}
            startIcon={<DeleteIcon style={{ color: "white" }} />}
            onClick={handleClearCourses}
          >
            Clear
          </Button>
        </div>
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
          style={{ margin: "6pt" }}
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
            style={{ margin: "6pt" }}
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
              onClassroomUpdate={(sectionIndex, lectureTimeIndex, newClassroom) =>
                handleClassroomUpdate(i, sectionIndex, lectureTimeIndex, newClassroom)
              }
            />
          ) : null
        )}
      </div>
      <AddDontFillWidget startHour={8} startMin={40} endHour={17} endMin={30} />
      {loading && <LoadingDialog text={loadingMessage} />}
      {lastUpdated ? (
        <Typography>
          {"Course data is updated at " + lastUpdated.u}
          <br />
          {"   Last added Semester: " + lastUpdated.t.split(":")[1]}
        </Typography>
      ) : null}
      <Divider />
      <div className="controls-section">
        <div className="controls-section-header">Free Electives</div>
        <div className="control-row" style={{ justifyContent: "center" }}>
          <Typography
            variant="body2"
            color="textSecondary"
            style={{ maxWidth: 720 }}
          >
            Help us crowdsource Free Elective courses. Share the elective
            courses you have taken or know about. We will use these submissions
            to build an upcoming Free Electives section for everyone.
          </Typography>
        </div>
        <div className="control-row">
          <div className="control-button">
            <Button
              variant="contained"
              className="pretty-button pretty-secondary"
              startIcon={<AssignmentIcon />}
              onClick={() =>
                openInNewTab("https://forms.gle/RgpEk9vETPKZUGXt5")
              }
            >
              Free Elective Form
            </Button>
          </div>
        </div>
      </div>

      <NTEDialog
        open={nteDialogOpen}
        onClose={handleNTEDialogClose}
        occupiedSlots={calculateOccupiedSlots()}
        onAddCourse={handleAddNTECourse}
      />
    </Paper>
  );
};

const styles = {
  mobile: {
    margin: 12,
    width: "100%",
    paddingBottom: 12,
  },
  desktop: {
    margin: 12,
    flex: "1 1 0",
    height: "fit-content",
    paddingBottom: 12,
  },
};

export default Controls;
