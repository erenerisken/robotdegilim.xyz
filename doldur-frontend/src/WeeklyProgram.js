import React, { useMemo, useState, useCallback, memo } from "react";
import {
  Paper,
  IconButton,
  Typography,
  TextField,
  Button,
  Menu,
  MenuItem,
} from "@material-ui/core";
import CloseIcon from "@material-ui/icons/Close";
import KeyboardArrowRightIcon from "@material-ui/icons/KeyboardArrowRight";
import KeyboardArrowLeftIcon from "@material-ui/icons/KeyboardArrowLeft";
import FastRewindIcon from "@material-ui/icons/FastRewind";
import PhotoCameraIcon from "@material-ui/icons/PhotoCamera";
import FastForwardIcon from "@material-ui/icons/FastForward";
import PaletteIcon from "@material-ui/icons/Palette";
import { ViewState } from "@devexpress/dx-react-scheduler";
import {
  Scheduler,
  WeekView,
  Appointments,
} from "@devexpress/dx-react-scheduler-material-ui";
import { isMobile } from "react-device-detect";
import { Colorset } from "./Colorset";
import { ExportCalendar } from "./ExportCalendar";
import { toJpeg } from "html-to-image";
import "./WeeklyProgram.css";
const currentDate = "2021-02-20";

export const DontFillBlock = ({
  data,
  onDontFillDelete,
  onChangeDontFillColor,
  onChangeDontFillDescription,
}) => {
  const [editing, setEditing] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const colorset = new Colorset();
  const colors = colorset.colors;
  const open = Boolean(anchorEl);

  const handleOpenColorPalette = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleColorSelect = (color) => {
    onChangeDontFillColor(color);
    handleClose();
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDescriptionChange = (e) => {
    onChangeDontFillDescription(e.target.value);
  };

  const handleTextFieldKeyDown = (e) => {
    if (e.keyCode === 13) {
      setEditing(false);
    }
  };

  return (
    <div className="program-text-container-df">
      <div className="program-row-df">
        <IconButton onClick={onDontFillDelete} style={{ padding: 0 }}>
          <CloseIcon fontSize="small" style={{ color: data.color.text }} />
        </IconButton>
        {editing ? (
          <TextField
            value={data.title}
            className="df-description-text-field"
            InputProps={{ style: { color: data.color.text } }}
            onChange={handleDescriptionChange}
            onKeyDown={handleTextFieldKeyDown}
            onBlur={() => setEditing(false)}
          />
        ) : (
          <div
            className="program-title-dont-fill"
            style={{ color: data.color.text }}
            onClick={() => setEditing(true)}
          >
            {data.title}
          </div>
        )}
        <IconButton
          style={{ padding: 0 }}
          id="palette-button"
          aria-controls={open ? "palette-menu" : undefined}
          aria-haspopup="true"
          aria-expanded={open ? "true" : undefined}
          onClick={handleOpenColorPalette}
        >
          <PaletteIcon fontSize="small" style={{ color: data.color.text }} />
        </IconButton>
        <Menu
          id="palette-menu"
          open={open}
          anchorEl={anchorEl}
          onClose={handleClose}
          MenuListProps={{
            "aria-labelledby": "palette-button",
          }}
          PaperProps={{
            style: {
              backgroundColor: "black",
            },
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "5px",
              padding: "5px",
              paddingTop: "0px",
              paddingBottom: "0px",
              backgroundColor: "black",
            }}
          >
            {colors.map((color) => (
              <MenuItem
                key={color.main}
                onClick={() => handleColorSelect(color)}
                style={{ padding: 0 }}
              >
                <div
                  style={{
                    width: "30px",
                    height: "30px",
                    backgroundColor: color.main,
                    borderRadius: "4px",
                  }}
                ></div>
              </MenuItem>
            ))}
          </div>
        </Menu>
      </div>
    </div>
  );
};

export const WeeklyProgram = ({
  scenarios,
  dontFills,
  onDontFillAdd,
  onChangeDontFillColor,
  onChangeDontFillDescription,
  onDontFillDelete,
}) => {
  const [currentScenario, setCurrentScenario] = useState(0);

  const convertTime = useCallback(
    (day, hour, min) =>
      `2021-02-${14 + day}T${hour.toString().padStart(2, "0")}:${min
        .toString()
        .padStart(2, "0")}`,
    []
  );

  const handleScenarioChange = useCallback(
    (delta) => {
      setCurrentScenario((prev) =>
        Math.min(scenarios.length - 1, Math.max(0, prev + delta))
      );
    },
    [scenarios.length]
  );

  const handleScenarioChangeAbsolute = useCallback(
    (val) => {
      const newCurrentScenario = isNaN(val) ? 1 : val;
      setCurrentScenario(
        Math.min(scenarios.length - 1, Math.max(0, newCurrentScenario - 1))
      );
    },
    [scenarios.length]
  );

  const handleDontFillAdd = useCallback(
    (startDate, endDate) => {
      onDontFillAdd(startDate, endDate, "FULL");
    },
    [onDontFillAdd]
  );

  const handleChangeDontFillColor = useCallback(
    (startDate, color) => {
      onChangeDontFillColor(startDate, color);
    },
    [onChangeDontFillColor]
  );

  const handleChangeDontFillDescription = useCallback(
    (startDate, newDescription) => {
      onChangeDontFillDescription(startDate, newDescription);
    },
    [onChangeDontFillDescription]
  );

  const doCapture = useCallback(() => {
    const node = document.getElementById("screenshot");

    toJpeg(node, { quality: 0.95 })
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
  }, [scenarios, currentScenario, dontFills, convertTime]);

  const timeTableCellComponent = useCallback(
    (props2) => <TimeTableCell {...props2} onDontFillAdd={handleDontFillAdd} />,
    [handleDontFillAdd]
  );

  const appointmentContentComponent = useCallback(
    (props2) => (
      <AppointmentContent
        {...props2}
        onDontFillDelete={onDontFillDelete}
        handleChangeDontFillColor={handleChangeDontFillColor}
        handleChangeDontFillDescription={handleChangeDontFillDescription}
      />
    ),
    [
      onDontFillDelete,
      handleChangeDontFillColor,
      handleChangeDontFillDescription,
    ]
  );

  return (
    <div style={isMobile ? styles.mobile : styles.desktop}>
      <Paper id="screenshot">
        <Scheduler id="scheduler" data={data}>
          <ViewState currentDate={currentDate} />
          <WeekView
            startDayHour={7.667}
            endDayHour={17.5}
            cellDuration={60}
            dayScaleRowComponent={DayScaleRow}
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

const DayScaleRow = memo(() => (
  <div className="dayscale-row">
    {["Mon", "Tue", "Wed", "Thu", "Fri"].map((day) => (
      <div key={day} className="dayscale-label">
        {day}
      </div>
    ))}
  </div>
));

const CustomAppointment = memo((props) => (
  <WeekView.AppointmentLayer {...props} className="custom-appointment" />
));

const AppointmentContent = memo(
  ({
    data,
    onDontFillDelete,
    handleChangeDontFillColor,
    handleChangeDontFillDescription,
    ...restProps
  }) => (
    <Appointments.AppointmentContent
      data={data}
      {...restProps}
      className="program-appointment"
      style={{ background: data.color.main }}
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
        <DontFillBlock
          data={data}
          onDontFillDelete={() => onDontFillDelete(data.startDate)}
          onChangeDontFillColor={(color) =>
            handleChangeDontFillColor(data.startDate, color)
          }
          onChangeDontFillDescription={(newDescription) =>
            handleChangeDontFillDescription(data.startDate, newDescription)
          }
        />
      )}
    </Appointments.AppointmentContent>
  )
);

const TimeTableCell = memo(
  ({ startDate, endDate, onDontFillAdd, ...restProps }) =>
    startDate.getDay() > 4 ? (
      <WeekView.TimeTableCell {...restProps} style={{ width: "0" }} />
    ) : (
      <WeekView.TimeTableCell
        {...restProps}
        onClick={() => onDontFillAdd(startDate, endDate)}
      />
    )
);

const styles = {
  mobile: {
    margin: 12,
    width: "100%",
  },
  desktop: {
    margin: 12,
    flex: "1 1 0",
  },
};
