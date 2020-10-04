

function applyCriteriaCourses(surname, department, grade, courses) {
    for (var i = 0 ; i < courses.length ; i++) {
        
        courses[i] = applyCriteriaSections(surname, department, grade, courses[i]);

        if(courses[i].sections.length === 0) {
            // Drop Course
            courses.splice(i, 1);
            i--;
        }
    }
    return courses;
}

function surnameCheck(surname, courseSurnameStart, courseSurnameEnd) {
    return ((courseSurnameStart <= surname) && (surname <= courseSurnameEnd));
}
function departmentCheck(department, deptList) {
    for(var i = 0 ; i < deptList.length ; i++) {
        if(department == deptList[i]) {
            return true;
        }
    }
    return false;
}
function applyCriteriaSections(surname, department, grade, course) {
    for(var i = 0 ; i < course.sections.length ; i++) {
        var sectionPassed = false;
        for(var j = 0 ; j < course.sections[i].criteria.length ; j++) {
            criterion = course.section[i].criteria[j];
            var deptPassed = false;
            var surnPassed = false;
            if(course.checkDepartment == false) {
                deptPassed = true;
            } else {
                if(criterion.dept == "ALL" || criterion.dept == department) {
                    deptPassed = true;
                }
            }
            if(course.checkSurname == false) {
                surnPassed = true;
            } else {
                if(surnameCheck(surname, criterion.surnameStart, criterion.surnameEnd) == true) {
                    surnPassed = true;
                }
            }
            
            if(deptPassed == true && surnPassed == true) {
                sectionPassed = true;
            }
        }
        if(sectionPassed == false) {
            course.sections.splice(i, 1);
            i--;
        }
    }
    return course;
}

function lecturesIntersect(lt1, lt2) {
    if (lt1.day != lt2.day                      // Different Days
        || lt1.startHour > lt2.endHour          // L1 starts after L2 ends by hour
        || lt2.startHour > lt1.endHour          // L2 starts after L1 ends by hour
        || (lt1.startHour === lt2.endHour        // L1 starts after L2 ends by min
            && lt1.startMin > lt2.endMin)
        || (lt2.startHour === lt1.endHour        // L2 starts after L1 ends by min
            && lt2.startMin > lt1.endMin)
            ) {
        return false;
    }
    return true;
}

function checkCollision(section1, section2) {
    const s1Lt = section1.lectureTimes;
    const s2Lt = section2.lectureTimes;

    for (var i = 0 ; i < s1Lt.length ; i++) {
        for (var j = 0 ; j < s2Lt.length ; j++) {
            if(lecturesIntersect(s1Lt[i], s2Lt[j]) == true) {
                return true;
            }
        }
    }
    return false;
}


// 
// 
// 
// 
// returns array of code + sections
function computeSchedule(surname, department, grade, courses, callback) {
    courses = applyCriteriaCourses(surname, department, grade, courses);

    scenarios = [];
    recursiveComputation(courses, 0, [], scenarios);

    return scenarios;
}

function recursiveComputation(courses, depth, scenario, scenarios) {
    if(depth == courses.length) {
        scenarios.push(scenario.slice(0));
        return;
    }
    for(var i = 0 ; i < courses[depth].sections.length ; i++) {
        var collision = false;
        for(var j = 0 ; j < scenario.length ; j++) {
            if(checkCollision(courses[depth].sections[i], scenario[j]) == true) {
                collision = true;
            }
        }
        if(collision === false) {
            scenario.push({
                code: courses[depth].code,
                section: courses[depth].sections[i],
            }
            );
            recursiveComputation(courses, depth + 1, scenario, scenarios);
            scenario.pop();
        }
        
    }
}
