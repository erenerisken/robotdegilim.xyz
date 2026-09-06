import React, { useMemo, useCallback, memo } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Paper,
  IconButton,
  Typography,
  TextField,
  Button,
} from "@mui/material";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import KeyboardArrowLeftIcon from "@mui/icons-material/KeyboardArrowLeft";
import FastRewindIcon from "@mui/icons-material/FastRewind";
import PhotoCameraIcon from "@mui/icons-material/PhotoCamera";
import FastForwardIcon from "@mui/icons-material/FastForward";
import { ViewState } from "@devexpress/dx-react-scheduler";
import { convertTime } from "./helpers/convertTime";
import {
  Scheduler,
  WeekView,
  Appointments,
} from "@devexpress/dx-react-scheduler-material-ui";
import {
  handleDontFillAdd,
  handleChangeDontFillColor,
  handleDontFillDelete,
} from "./slices/dontFillsSlice";
import { isMobile } from "react-device-detect";
import { Colorset } from "./Colorset";
import { ExportCalendar } from "./ExportCalendar";
import { toJpeg } from "html-to-image";
import "./WeeklyProgram.css";
import { DontFillBlock } from "./DontFillBlock";

const currentDate = "2021-02-20";
const colorset = new Colorset();

export const WeeklyProgram = ({ currentScenario, setCurrentScenario }) => {
  const dispatch = useDispatch();
  const scenariosState = useSelector((state) => state.scenariosState);
  const dontFillsState = useSelector((state) => state.dontFillsState);
  const scenarios = scenariosState.result;
  const dontFills = dontFillsState.result;
  const onColorChange = (color) => {
    dispatch(handleChangeDontFillColor(color));
  };

  const handleScenarioChange = useCallback(
    (delta) => {
      setCurrentScenario((prev) =>
        Math.min(scenarios.length - 1, Math.max(0, prev + delta))
      );
    },
    [scenarios.length, setCurrentScenario]
  );

  const handleScenarioChangeAbsolute = useCallback(
    (val) => {
      const newCurrentScenario = isNaN(val) ? 1 : val;
      setCurrentScenario(
        Math.min(scenarios.length - 1, Math.max(0, newCurrentScenario - 1))
      );
    },
    [scenarios.length, setCurrentScenario]
  );

  const doCapture = useCallback(() => {
    const node = document.getElementById("screenshot");

    toJpeg(node, {
      quality: 0.95,
      cacheBust: true,
      skipFonts: true,
    })
      .then((dataUrl) => {
        const link = document.createElement("a");
        link.download = "schedule.jpeg";
        link.href = dataUrl;
        link.click();
      })
      .catch((error) => {
        console.error("Oops, something went wrong!", error);
      });
  }, []);

  const data = useMemo(() => {
    const scenario = scenarios.length
      ? scenarios[Math.min(scenarios.length - 1, currentScenario)]
      : [];
    const coursesToDisplay = scenario.reduce((acc, c) => {
      c.section.lectureTimes.forEach((lt) => {
        const length = lt.endHour - lt.startHour;
        for (let i = 0; i < length; i++) {
          acc.push({
            type: "course",
            title: c.abbreviation,
            section: c.section.sectionNumber,
            classroom: lt.classroom ?? "-",
            startDate: convertTime(lt.day, lt.startHour + i, lt.startMin + 3),
            endDate: convertTime(lt.day, lt.startHour + i + 1, lt.endMin + 5),
            color: c.color,
          });
        }
      });
      return acc;
    }, []);

    return [
      ...coursesToDisplay,
      ...dontFills.map((df) => ({
        type: "dontFill",
        title: df.description,
        color: df.color,
        startDate: df.startDate,
        endDate: df.endDate,
      })),
    ];
  }, [scenarios, currentScenario, dontFills]);

  const timeTableCellComponent = useCallback(
    (props2) => <TimeTableCell {...props2} />,
    []
  );

  const appointmentContentComponent = useCallback(
    (props2) => {
      return (
        <AppointmentContent
          {...props2}
          onDontFillDelete={() => dispatch(handleDontFillDelete(props2.data))}
          handleChangeDontFillColor={onColorChange}
        />
      );
    },
    [dispatch, onColorChange]
  );

  return (
    <div className="weekly-program" style={isMobile ? styles.mobile : styles.desktop}>
      <Paper id="screenshot" className="scheduler-card">
        <Scheduler id="scheduler" data={data} height="auto">
          <ViewState currentDate={currentDate} />
          <WeekView
            startDayHour={7.667}
            endDayHour={17.5}
            cellDuration={60}
            excludedDays={[0, 6]}
            dayScaleCellComponent={DayScaleCell}
            appointmentLayerComponent={CustomAppointment}
            timeTableCellComponent={timeTableCellComponent}
          />
          <Appointments
            appointmentContentComponent={appointmentContentComponent}
          />
        </Scheduler>
      </Paper>
      <div className="program-vertical">
        {scenarios.length > 0 && (
          <div className="program-row">
            <IconButton onClick={() => handleScenarioChange(-10)}>
              <FastRewindIcon fontSize="small" />
            </IconButton>
            <IconButton onClick={() => handleScenarioChange(-1)}>
              <KeyboardArrowLeftIcon fontSize="small" />
            </IconButton>
            <div className={"program-typo-wrapper"}>
              <Typography>{"Scenario "}</Typography>
            </div>
            <div className={"program-textfield-wrapper"}>
              <TextField
                className={"program-textfield"}
                type={"number"}
                value={currentScenario + 1}
                onChange={(e) =>
                  handleScenarioChangeAbsolute(parseInt(e.target.value))
                }
              />
            </div>
            <div className={"program-typo-wrapper"}>
              <Typography>{" of " + scenarios.length}</Typography>
            </div>
            <IconButton onClick={() => handleScenarioChange(1)}>
              <KeyboardArrowRightIcon fontSize={"small"} />
            </IconButton>
            <IconButton onClick={() => handleScenarioChange(10)}>
              <FastForwardIcon fontSize={"small"} />
            </IconButton>
          </div>
        )}
        {scenarios.length > 0 && !isMobile && (
          <div className="program-calendar-wrapper">
            <ExportCalendar events={data} />
          </div>
        )}
        <Button
          variant="contained"
          color="primary"
          className="pretty-button pretty-primary"
          style={{ margin: "6pt" }}
          startIcon={<PhotoCameraIcon />}
          onClick={() => doCapture()}
        >
          Save as image
        </Button>
      </div>
    </div>
  );
};

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const DayScaleCell = memo(({ startDate, colSpan }) => (
  <th colSpan={colSpan} className="responsive-day-cell" scope="col">
    {DAY_LABELS[startDate.getDay()]}
  </th>
));

const CustomAppointment = memo((props) => (
  <WeekView.AppointmentLayer {...props} className="custom-appointment" />
));

const AppointmentContent = memo(({ data, ...restProps }) => {
  return (
    <Appointments.AppointmentContent
      data={data}
      {...restProps}
      className="program-appointment"
      style={{ background: data?.color?.main, borderRadius: "4px" }}
    >
      {data.type === "course" ? (
        <div className="program-text-container">
          <div className="program-title" style={{ color: data.color.text }}>
            {`${data.title}/${data.section}`}
          </div>
          <div
            className="program-title-bottom"
            style={{ color: data.color.text }}
          >
            {data.classroom}
          </div>
        </div>
      ) : (
        <DontFillBlock data={data} />
      )}
    </Appointments.AppointmentContent>
  );
});

const TimeTableCell = memo(({ startDate, endDate, ...restProps }) => {
  const dispatch = useDispatch();

  return (
    <WeekView.TimeTableCell
      {...restProps}
      onClick={() => {
        dispatch(
          handleDontFillAdd({
            startDate: startDate,
            endDate: endDate,
            description: "FULL",
            color: colorset.blackDontFill,
          })
        );
      }}
    />
  );
});

const styles = {
  mobile: {
    margin: 12,
    width: "calc(100% - 24px)",
    minWidth: 0,
  },
  desktop: {
    margin: 12,
    flex: "1 1 480px",
    minWidth: 0,
  },
};
