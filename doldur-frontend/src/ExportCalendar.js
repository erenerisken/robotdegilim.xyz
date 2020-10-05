import React from "react";
import {Button} from "@material-ui/core";
import BackupIcon from '@material-ui/icons/Backup';
import {gapi} from "gapi-script";

export class ExportCalendar extends React.Component{
    constructor(props) {
        super(props);
        this.gapi = window.gapi;
        this.CLIENT_ID = "531687826330-d2raf921gt5ur2q5lspcv25ceak6v7e7.apps.googleusercontent.com";
        this.API_KEY = "AIzaSyC1JqJ83f1CZ8Otm-lDrpCX443r7OWewbw";
        this.DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"];
        this.SCOPES = "https://www.googleapis.com/auth/calendar.events";
    }
    convertDay(date){
        //           0123456789012345
        //example : '2021-02-20T09:40'
        //2020-10-15T16:30:00+03:00
        //console.log(date);
        //console.log(typeof date);
        const day = parseInt(date.slice(8, 10)) - 14;
        const hour = parseInt(date.slice(11, 13));
        const min = parseInt(date.slice(14));
        return "2020-10-" + (12 + day) + "T" +
            (hour < 10 ? "0" : "") + hour + ":" + (min < 10 ? "0" : "") + min + ":00+03:00";
    }
    convertEvents(){
        /*
        * var event = {
            'summary': info[curr].summary,
            'start': {
              'dateTime': info[curr].start.dateTime,
              'timeZone': info[curr].start.timeZone
            },
            'end': {
              'dateTime': info[curr].end.dateTime,
              'timeZone': info[curr].end.timeZone
            },
            'recurrence': [
              'RRULE:FREQ=WEEKLY;COUNT=14'
            ]
          }
        * */
        const events = Array(0);
        if (this.props.events === undefined){
            return [];
        }
        this.props.events.map(e => {
            if (e.type === "course"){
                events.push({
                    summary: e.title,
                    start: {
                        timeZone: "Turkey",
                        dateTime: this.convertDay(e.startDate)
                    },
                    end: {
                        timeZone: "Turkey",
                        dateTime: this.convertDay(e.endDate)
                    },
                    recurrence: [
                        'RRULE:FREQ=WEEKLY;COUNT=14'
                    ]
                });
            }
        });
        return events;
    }

    handleExport(){
        const events = this.convertEvents();
        events.map(e => console.log(e));
        gapi.load('client:auth2', () => {
            gapi.client.init({
                apiKey: this.API_KEY,
                clientId: this.CLIENT_ID,
                discoveryDocs: this.DISCOVERY_DOCS,
                scope: this.SCOPES,
            });
            gapi.client.load('calendar', 'v3', () => console.log('added to calendar!'))

            gapi.auth2.getAuthInstance().signIn().then(() => {
                events.map(event => {
                    let request = gapi.client.calendar.events.insert({
                        'calendarId': 'primary',
                        'resource': event,
                    });
                    request.execute(e => console.log(e));
                });
            });
        });
    }
    render() {
        return (
            <div className={"export-calendar-wrapper"}>
                <Button variant={"contained"}
                        color={"secondary"}
                        startIcon={<BackupIcon />} onClick={() => this.handleExport()}>
                    Export to Google
                </Button>
            </div>
        )
    }
}