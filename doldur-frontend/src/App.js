import React from 'react';
import {WeeklyProgram} from "./WeeklyProgram";

import {getCoursesToDisplay} from "./CoursesToDisplay";

import './App.css';

function App() {
  return (
    <div className="App">
      <WeeklyProgram coursesToDisplay={getCoursesToDisplay()}/>
    </div>
  );
}

export default App;
