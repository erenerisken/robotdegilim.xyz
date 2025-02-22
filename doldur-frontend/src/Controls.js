import React, { useState, useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
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
import MuiAlert from "@material-ui/lab/Alert";
import AddIcon from "@material-ui/icons/Add";
import EventAvailableIcon from "@material-ui/icons/EventAvailable";
import ImportContactsIcon from "@material-ui/icons/ImportContacts";
import DeleteIcon from "@material-ui/icons/Delete";
import SaveIcon from "@material-ui/icons/Save";
import SaveAltIcon from "@material-ui/icons/SaveAlt";
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

export const Controls = (props) => {
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

  const dispatch = useDispatch();

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
    if (isMobile) {
      document.body.style.zoom = "60%";
    }
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
    setSelectedCourses(restoredCourses);
    setSettings(restoredSettings);
    setSurname(restoredInfo.surname);
    setSemester(restoredInfo.semester);
    setDepartment(restoredInfo.department);
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
            .map(getCourseByCode);

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

  return (
    <Paper style={isMobile ? styles.mobile : styles.desktop}>
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
            onChange={(e) => setDepartment(e.target.value.toUpperCase())}
          />
        </div>
      </div>
      <div className="control-row">
        <div className="textfield-wrapper">
          <FormControl variant="outlined" size="small" className="form-control">
            <InputLabel style={{ background: "white" }}>Semester</InputLabel>
            <Select
              error={errorSemester}
              value={semester}
              onChange={(e) => setSemester(e.target.value)}
              label="Semester"
            >
              {renderSemesterSelections(8)}
            </Select>
            <FormHelperText>Ex: 2nd year Fall semester -{">"} 3</FormHelperText>
          </FormControl>
        </div>
        <div className="control-button">
          <Button
            variant="contained"
            color="secondary"
            startIcon={<AddIcon />}
            onClick={handleAddMustCourse}
          >
            Add Must Courses
          </Button>
        </div>
        <div className="control-button">
          <Button
            variant="contained"
            style={{ backgroundColor: "#0DAEEE", color: "white" }}
            startIcon={<ImportContactsIcon style={{ color: "white" }} />}
            onClick={() => openInNewTab("https://metu-non.tech")}
          >
            NTE Catalog
          </Button>
        </div>
        <div className="control-button">
          <Button
            variant="contained"
            color="primary"
            startIcon={<EventAvailableIcon />}
            onClick={handleScheduleBegin}
          >
            Schedule
          </Button>
        </div>
        <div className="control-button">
          <Button
            variant="contained"
            style={{ backgroundColor: "red", color: "white" }}
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
            onClick={loadRestoredData}
            startIcon={<SaveAltIcon />}
            style={{ margin: "6pt" }}
          >
            Load
          </Button>
        )}
      </div>
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
            />
          ) : null
        )}
      </div>
      <AddCourseWidget
        courses={allCourses}
        onCourseAdd={(c) => handleAddCourses([c])}
      />
      <AddDontFillWidget startHour={8} startMin={40} endHour={17} endMin={30} />
      {loading && <LoadingDialog text={loadingMessage} />}
      {lastUpdated ? (
        <Typography>
          {"Course data is updated at " + lastUpdated.u}
          <br />
          {"   Last added Semester: " + lastUpdated.t.split(":")[1]}
        </Typography>
      ) : null}
    </Paper>
  );
};

const styles = {
  mobile: {
    background: "white",
    margin: 12,
    width: "100%",
    paddingBottom: 12,
  },
  desktop: {
    background: "white",
    margin: 12,
    flex: "1 1 0",
    height: "fit-content",
    paddingBottom: 12,
  },
};

export default Controls;
