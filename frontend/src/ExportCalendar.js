import React, { useEffect, useState } from "react";
import { Button, Tooltip } from "@material-ui/core";
import BackupIcon from "@material-ui/icons/Backup";

const CLIENT_ID =
  "531687826330-d2raf921gt5ur2q5lspcv25ceak6v7e7.apps.googleusercontent.com";
const API_KEY = "AIzaSyC1JqJ83f1CZ8Otm-lDrpCX443r7OWewbw";
const DISCOVERY_DOCS = [
  "https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest",
];
const SCOPES = "https://www.googleapis.com/auth/calendar.events";

export const ExportCalendar = ({ events }) => {
  const [, setGapiLoaded] = useState(false);

  useEffect(() => {
    // Load gapi script dynamically
    const loadGapi = () => {
      const script = document.createElement("script");
      script.src = "https://apis.google.com/js/api.js";
      script.async = true;
      script.onload = () => {
        window.gapi.load("client:auth2", async () => {
          try {
            await window.gapi.client.init({
              apiKey: API_KEY,
              clientId: CLIENT_ID,
              discoveryDocs: DISCOVERY_DOCS,
              scope: SCOPES,
            });
            setGapiLoaded(true);
          } catch (error) {
            console.error("GAPI initialization error:", error);
          }
        });
      };
      document.body.appendChild(script);
    };

    if (!window.gapi) {
      loadGapi();
    } else {
      setGapiLoaded(true);
    }
  }, []);

  const convertDay = (date) => {
    const day = parseInt(date.slice(8, 10)) - 14;
    const hour = parseInt(date.slice(11, 13));
    const min = parseInt(date.slice(14));
    return `2020-10-${12 + day}T${hour.toString().padStart(2, "0")}:${min
      .toString()
      .padStart(2, "0")}:00+03:00`;
  };

  const convertEvents = () => {
    if (!events || events.length === 0) return [];
    return events
      .filter((e) => e.type === "course")
      .map((e) => ({
        summary: e.title,
        start: { timeZone: "Turkey", dateTime: convertDay(e.startDate) },
        end: { timeZone: "Turkey", dateTime: convertDay(e.endDate) },
        recurrence: ["RRULE:FREQ=WEEKLY;COUNT=14"],
      }));
  };

  const handleExport = async () => {
    if (!window.gapi || !window.gapi.auth2) {
      console.error("Google API not initialized");
      return;
    }

    const authInstance = window.gapi.auth2.getAuthInstance();
    if (!authInstance) {
      console.error("Auth instance not found");
      return;
    }

    try {
      await authInstance.signIn();
      const convertedEvents = convertEvents();

      convertedEvents.forEach((event) => {
        window.gapi.client.calendar.events
          .insert({
            calendarId: "primary",
            resource: event,
          })
          .then((response) => {
            console.log("Event added:", response);
            if (response.result.htmlLink) {
              window.open(response.result.htmlLink);
            }
          })
          .catch((error) => console.error("Error adding event:", error));
      });
    } catch (error) {
      console.error("Sign-in error:", error);
    }
  };

  return (
    <div className="export-calendar-wrapper">
      <Tooltip
        title="Still in development."
        arrow
        placement="top"
        disableInteractive
      >
        <span>
          <Button
            variant="contained"
            color="secondary"
            className="pretty-button pretty-secondary"
            startIcon={<BackupIcon />}
            onClick={handleExport}
            disabled={true}
          >
            Export to Google
          </Button>
        </span>
      </Tooltip>
    </div>
  );
};
