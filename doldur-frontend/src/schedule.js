function apply_criteria_courses(surname, department, grade, courses) {
    for (var i = courses.length - 1 ; i >= 0 ; i--) {
        courses[i] = apply_criteria_sections(surname, department, grade, courses[i]);

        if(courses[i].sections.length === 0) {
            // Drop Course
            courses.splice(i, 1);
        }
    }
    return courses;
}

function surnameCheck(surname, course_surname_start, course_surname_end) {
    var alphabet = {
        A : 1,
        B : 2,
        C : 3,
        Ç : 4,
        D : 5,
        E : 6,
        F : 7,
        G : 8,
        Ğ : 9,
        H : 10,
        I : 11,
        İ : 12,
        J : 13,
        K : 14,
        L : 15,
        M : 16,
        N : 17,
        O : 18,
        Ö : 19,
        P : 20,
        Q : 21,
        R : 22,
        S : 23,
        Ş : 24,
        T : 25,
        U : 26,
        Ü : 27,
        V : 28,
        W : 29,
        X : 30,
        Y : 31,
        Z : 32
    }
    
    var surFirstVal = alphabet[surname[0]];
    var surSecondVal = alphabet[surname[1]];
    var surStartFirstVal = alphabet[course_surname_start[0]];
    var surStartSecondVal = alphabet[course_surname_start[1]];
    var surEndFirstVal = alphabet[course_surname_end[0]];
    var surEndSecondVal = alphabet[course_surname_end[1]];

    if(surStartFirstVal < surFirstVal && surFirstVal < surEndFirstVal) {
        return true;
    }
    if((surStartFirstVal === surFirstVal && surFirstVal < surEndFirstVal)
        && (surStartSecondVal <= surStartSecondVal)) {
        return true;
    }
    if((surStartFirstVal < surFirstVal && surFirstVal === surEndFirstVal)
        && (surSecondVal <= surEndSecondVal)) {
        return true;
    }
    return false;
}

function apply_criteria_sections(surname, department, grade, course) {
    for(var i = course.sections.length - 1; i >= 0 ; i--) {
        var section_passed = false;
        if(course.sections[i].toggle === true) {
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
        }
        
        if(section_passed === false) {
            course.sections.splice(i, 1);
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

function check_collision_df(section1, df) {
    const s1_lt = section1.lectureTimes;
    const df_t = df.times;

    for (var i = 0 ; i < s1_lt.length ; i++) {
        for (var j = 0 ; j < df_t.length ; j++) {
            if(lectures_intersect(s1_lt[i], df_t[j]) === true) {
                return true;
            }
        }
    }
    return false;
}


// returns array of code + sections
export function compute_schedule(surname, department, grade, courses, dontFills) {
    let courseNumber = courses.length;
    console.log(courseNumber)
    courses = apply_criteria_courses(surname, department, grade, courses);
    console.log(courseNumber)
    let scenarios = [];
    recursive_computation(courses, dontFills, 0, [], scenarios, courseNumber);

    return scenarios;
}

function recursive_computation(courses, dontFills, depth, scenario, scenarios, courseNumber) {
    if(depth === courses.length) {
        const scenarioToPosh = Array(0);
        scenario.map(c => {
            scenarioToPosh.push({
                code: c.code,
                section: c.section.sectionNumber
            });
        });
        if(scenarioToPosh.length == courseNumber) {
            scenarios.push(scenarioToPosh);
        }
        return;
    }
    for(var i = 0 ; i < courses[depth].sections.length ; i++) {
        var collision = false;
        for(var j = 0 ; j < scenario.length ; j++) {
            if(courses[depth].checkCollision == true 
                && check_collision(courses[depth].sections[i], scenario[j].section) === true) {
                collision = true;
            }
        }
        for(var j = 0 ; j < dontFills.length ; j++) {
            if(check_collision_df(courses[depth].sections[i], dontFills[j]) === true) {
                collision = true;
            }  
        }
        if(collision === false) {
            scenario.push({
                code: courses[depth].code,
                section: courses[depth].sections[i],
            }
            );
            recursive_computation(courses, dontFills, depth + 1, scenario, scenarios, courseNumber);
            scenario.pop();
        }
        
    }
}
