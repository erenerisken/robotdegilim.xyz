import React from 'react';
import {isMobile} from "react-device-detect";
import {WeeklyProgram} from "./WeeklyProgram";
import {Controls} from "./Controls";
import {getCoursesToDisplay} from "./CoursesToDisplay";

import './App.css';

function App() {
  return (
    <div className="App">
        <div className={isMobile ? "column" : "row"}>
            <WeeklyProgram coursesToDisplay={getCoursesToDisplay()}/>
            <Controls />
        </div>
    </div>
  );
}

export default App;
