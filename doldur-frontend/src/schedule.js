function apply_criteria_courses(surname, department, grade, courses) {
    for (var i = 0 ; i < courses.length ; i++) {
        apply_criteria_sections(surname, department, grade, courses[i]);
        if(courses[i].sections.length() == 0) {
            // Drop Course
            courses.splice(i, 1);
            i--;
        }
    }
}

function surnameCheck(surname, course_surname_start, course_surname_end) {
    return ((course_surname_start <= surname) && (surname <= course_surname_end));
}
function departmentCheck(department, dept_list) {
    for(var i = 0 ; i < dept_list.length ; i++) {
        if(department == dept_list[i]) {
            return true;
        }
    }
    return false;
}
function apply_criteria_sections(surname, department, grade, course) {
    for(var i = 0 ; i < course.sections.length ; i++) {
        if(check_surname == true) {
            if(surnameCheck(surname, course.sections[i].surnameStart, course.sections[i].surnameEnd) == false) {
                // Drop section
                course.sections.splice(i, 1);
                i--;
            }
        }
        if(check_department == true) {
            if(departmentCheck(department, course.sections[i].dept) == false) {
                // Drop section
                course.sections.splice(i, 1);
                i--;
            }
        }
    }
}

function lectures_intersect(lt1, lt2) {
    if (lt1.day != lt2.day                      // Different Days
        || lt1.startHour > lt2.endHour          // L1 starts after L2 ends by hour
        || lt2.startHour > lt1.endHour          // L2 starts after L1 ends by hour
        || (lt1.startHour == lt2.endHour        // L1 starts after L2 ends by min
            && lt1.startMinute > lt2.endMinute)
        || (lt2.startHour == lt1.endHour        // L2 starts after L1 ends by min
            && lt2.startMinute > lt1.endMinute)
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
            if(lectures_intersect(s1_lt[i], s2_lt[j]) == true) {
                return true;
            }
        }
    }
    return false;
}

const example_course = {
    code : 0,                       // int
    category: 0,                    // int
    check_surname: false,           // bool               
    check_collision: false,         // bool
    check_department: false,        // bool
    sections: [
        {
            day: 0,                 // int
            startHour: 0,           // int
            startMin: 0,            // int
            endHour: 0,             // int
            endMin: 0,              // int
            toggle: false,          // bool
            dept: ["", ""],         // string array
            surnameStart: "",       // string
            surnameEnd: "",         // string
            minYear: 0,             // int
            maxYear: 0,             // int
        },
        {
            day: 0,                 // int
            startHour: 0,           // int
            startMin: 0,            // int
            endHour: 0,             // int
            endMin: 0,              // int
            toggle: false,          // bool
            dept: ["", ""],         // string array
            surnameStart: "",       // string
            surnameEnd: "",         // string
            minYear: 0,             // int
            maxYear: 0,             // int
        },
    ],

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
function compute_schedule(surname, department, grade, courses, callback) {
    apply_criteria(surname, department, grade, courses);

    scenario = recursive_computation(courses, 0, [], callback);
    
    callback(scenario)
}

function recursive_computation(courses, depth, scenario) {
    if(depth == courses.length) {
        return scenario;
    }
    for(var i = 0 ; i < courses[depth].sections.length ; i++) {
        var collision = false;
        for(var j = 0 ; j < scenario.length ; j++) {
            if(check_collision(courses[depth].sections[i], scenario[j]) == true) {
                collision = true;
            }
        }
        if(collision == false) {
            scenario.push(courses[depth].sections[i]);
            recursive_computation(courses, depth + 1, scenario);
            scenario.pop();
        }
        
    }
}