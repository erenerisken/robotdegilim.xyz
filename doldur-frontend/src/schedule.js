function apply_criteria_courses(surname, department, grade, courses) {
    for (var i = 0 ; i < courses.length ; i++) {
        courses[i] = apply_criteria_sections(surname, department, grade, courses[i]);

        if(courses[i].sections.length === 0) {
            // Drop Course
            courses.splice(i, 1);
            i--;
        }
    }
    return courses;
}

function surnameCheck(surname, course_surname_start, course_surname_end) {
    return ((course_surname_start <= surname) && (surname <= course_surname_end));
}
function departmentCheck(department, dept_list) {
    for(var i = 0 ; i < dept_list.length ; i++) {
        if(department === dept_list[i]) {
            return true;
        }
    }
    return false;
}
function apply_criteria_sections(surname, department, grade, course) {
    for(var i = 0 ; i < course.sections.length ; i++) {
        var section_passed = false;
        for(var j = 0 ; j < course.sections[i].criteria.length ; j++) {
            let criterion = course.sections[i].criteria[j];
            var dept_passed = false;
            var surn_passed = false;
            if(course.checkDepartment === false) {
                dept_passed = true;
            } else {
                if(criterion.dept === "ALL" || criterion.dept === department) {
                    dept_passed = true;
                }
            }
            if(course.checkSurname === false) {
                surn_passed = true;
            } else {
                if(surnameCheck(surname, criterion.surnameStart, criterion.surnameEnd) === true) {
                    surn_passed = true;
                }
            }
            
            if(dept_passed === true && surn_passed === true) {
                section_passed = true;
            }
        }
        if(section_passed === false) {
            course.sections.splice(i, 1);
            i--;
        }
    }
    return course;
}


function lectures_intersect(lt1, lt2) {
    if (lt1.day !== lt2.day                      // Different Days
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

function check_collision(section1, section2) {
    const s1_lt = section1.lectureTimes;
    const s2_lt = section2.lectureTimes;

    for (var i = 0 ; i < s1_lt.length ; i++) {
        for (var j = 0 ; j < s2_lt.length ; j++) {
            if(lectures_intersect(s1_lt[i], s2_lt[j]) === true) {
                return true;
            }
        }
    }
    return false;
}

const exampleScenario = {
    sections: [
        {
            code: 5710140,
            section: 2
        },
        {
            code: 5710213,
            section: 1
        }
    ]
}

// 
// 
// 
// 
// returns array of code + sections
export function compute_schedule(surname, department, grade, courses) {
    courses = apply_criteria_courses(surname, department, grade, courses);

    let scenarios = [];
    recursive_computation(courses, 0, [], scenarios);

    return scenarios;
}

function recursive_computation(courses, depth, scenario, scenarios) {
    if(depth === courses.length) {
        const scenarioToPosh = Array(0);
        scenario.map(c => {
            scenarioToPosh.push({
                code: c.code,
                section: c.section.sectionNumber
            });
        });
        scenarios.push(scenarioToPosh);
        return;
    }
    for(var i = 0 ; i < courses[depth].sections.length ; i++) {
        var collision = false;
        for(var j = 0 ; j < scenario.length ; j++) {
            if(check_collision(courses[depth].sections[i], scenario[j].section) === true) {
                collision = true;
            }
        }
        if(collision === false) {
            scenario.push({
                code: courses[depth].code,
                section: courses[depth].sections[i],
            }
            );
            recursive_computation(courses, depth + 1, scenario, scenarios);
            scenario.pop();
        }
        
    }
}
