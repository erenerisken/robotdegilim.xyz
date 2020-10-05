import React from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  var gapi = window.gapi
  /* 
    Update with your own Client Id and Api key 
  */
  var CLIENT_ID = "531687826330-d2raf921gt5ur2q5lspcv25ceak6v7e7.apps.googleusercontent.com"
  var API_KEY = "AIzaSyC1JqJ83f1CZ8Otm-lDrpCX443r7OWewbw"
  var DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"]
  var SCOPES = "https://www.googleapis.com/auth/calendar.events"

  const handleClick = () => {
    gapi.load('client:auth2', () => {
      console.log('loaded client')

      gapi.client.init({
        apiKey: API_KEY,
        clientId: CLIENT_ID,
        discoveryDocs: DISCOVERY_DOCS,
        scope: SCOPES,
      })

      gapi.client.load('calendar', 'v3', () => console.log('added to calendar!'))

      gapi.auth2.getAuthInstance().signIn()
      .then(() => {

        var info = {   
          "1": {
              "summary": "ENG211/1",
              "start": {
                  "dateTime": "2020-10-12T08:40:00+03:00",
                  "timeZone": "Turkey"
              },
              "end": {
                  "dateTime": "2020-10-12T08:40:00+03:00",
                  "timeZone": "Turkey"
              },
              "recurrence": [
                  "RRULE:FREQ=WEEKLY;COUNT=1"
              ],
          },
      
          "2": {
              "summary": "MATH219/3",
              "start": {
                  "dateTime": "2020-10-13T13:40:00+03:00",
                  "timeZone": "Turkey"
              },
              "end": {
                  "dateTime": "2020-10-13T15:30:00+03:00",
                  "timeZone": "Turkey"
              },
              "recurrence": [
                  "RRULE:FREQ=WEEKLY;COUNT=1"
              ]
          },
      
          "3": {
              "summary": "EE281/3",
              "start": {
                  "dateTime": "2020-10-13T15:40:00+03:00",
                  "timeZone": "Turkey"
              },
              "end": {
                  "dateTime": "2020-10-13T17:30:00+03:00",
                  "timeZone": "Turkey"
              },
              "recurrence": [
                  "RRULE:FREQ=WEEKLY;COUNT=1"
              ]
          },
      
          "4": {
              "summary": "ENG211/1",
              "start": {
                  "dateTime": "2020-10-14T14:40:00+03:00",
                  "timeZone": "Turkey"
              },
              "end": {
                  "dateTime": "2020-10-14T15:30:00+03:00",
                  "timeZone": "Turkey"
              },
              "recurrence": [
                  "RRULE:FREQ=WEEKLY;COUNT=1"
              ]
          },
      
          "5": {
              "summary": "EE281/3",
              "start": {
                  "dateTime": "2020-10-15T15:40:00+03:00",
                  "timeZone": "Turkey"
              },
              "end": {
                  "dateTime": "2020-10-15T16:30:00+03:00",
                  "timeZone": "Turkey"
              },
              "recurrence": [
                  "RRULE:FREQ=WEEKLY;COUNT=1"
              ]
          },
      
          "6": {
              "summary": "MATH291/3",
              "start": {
                  "dateTime": "2020-10-16T08:40:00+03:00",
                  "timeZone": "Turkey"
              },
              "end": {
                  "dateTime": "2020-10-16T10:30:00+03:00",
                  "timeZone": "Turkey"
              },
              "recurrence": [
                  "RRULE:FREQ=WEEKLY;COUNT=1"
              ]
          }
      }
  
  
        for(var i = 1; i < Object.keys(info).length + 1; i++) {
          var curr = i.toString();
          
          var event = {
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
  
          var request = gapi.client.calendar.events.insert({
            'calendarId': 'primary',
            'resource': event,
          })
  
          request.execute(event => {
            console.log(event)
          })
        }
    

      })
    })
  }


  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Click export schedule to connect Google Calendar</p>
        <button style={{width: 100, height: 50}} onClick={handleClick}>Export Schedule</button>
      </header>
    </div>
  );
}

export default App;
