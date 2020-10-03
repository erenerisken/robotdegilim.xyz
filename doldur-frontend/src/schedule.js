function apply_criteria_courses(surname, department, grade, courses) {
    for (var i = 0 ; i < courses.length ; i++) {
        
        courses[i] = apply_criteria_sections(surname, department, grade, courses[i]);

        if(courses[i].sections.length == 0) {
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
        if(department == dept_list[i]) {
            return true;
        }
    }
    return false;
}
function apply_criteria_sections(surname, department, grade, course) {
    for(var i = 0 ; i < course.sections.length ; i++) {
        var section_passed = false;
        for(var j = 0 ; j < course.sections[i].criteria.length ; j++) {
            criterion = course.section[i].criteria[j];
            var dept_passed = false;
            var surn_passed = false;
            if(course.check_department == false) {
                dept_passed = true;
            } else {
                if(criterion.dept == "ALL" || criterion.dept == department) {
                    dept_passed = true;
                }
            }
            if(course.check_surname == false) {
                surn_passed = true;
            } else {
                if(surnameCheck(surname, criterion.surnameStart, criterion.surnameEnd) == true) {
                    surn_passed = true;
                }
            }
            
            if(dept_passed == true && surn_passed == true) {
                section_passed = true;
            }
        }
        if(section_passed == false) {
            course.sections.splice(i, 1);
            i--;
        }
    }
    return course;
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
    courses = apply_criteria_courses(surname, department, grade, courses);

    scenarios = [];
    recursive_computation(courses, 0, [], scenarios);

    callback(scenarios)
}

function recursive_computation(courses, depth, scenario, scenarios) {
    if(depth == courses.length) {
        scenarios.push(scenario.slice(0));
        return;
    }
    for(var i = 0 ; i < courses[depth].sections.length ; i++) {
        var collision = false;
        for(var j = 0 ; j < scenario.length ; j++) {
            if(check_collision(courses[depth].sections[i], scenario[j]) == true) {
                collision = true;
            }
        }
        if(collision == false) {
            scenario.push({
                code: courses[depth].code,
                section: courses[depth].sections[i].sectionNumber,
            }
            );
            recursive_computation(courses, depth + 1, scenario, scenarios);
            scenario.pop();
        }
        
    }
}

function testSurnameCheck() {
    // Surname, SurnameStart, SurnameEnd
    const surnameTests = [
        [
            ["BA", "AA", "ZZ"], true
        ],
        [
            ["BA", "BA", "ZZ"], true
        ],
        [
            ["BA", "BB", "ZZ"], false
        ],
        [
            ["ZY", "AA", "ZZ"], true
        ],
        [
            ["ZY", "AA", "ZY"], true
        ],
        [
            ["ZY", "AA", "YZ"], false
        ],
    ];
    for(var i = 0 ; i < surnameTests.length ; i++) {
        if(surnameTests[i][1] != surnameCheck.apply(this, surnameTests[i][0])) {
            console.log(surnameTests[i]);
            return false;
        }
    }
    return true;
}

function testDepartmentCheck() {
    // dept, [dept]
    const tests = [
        [
            ["CENG", ["CENG", "EE", "ME"]], true
        ],
        [
            ["EE", ["CENG", "EE", "ME"]], true
        ],
        [
            ["ME", ["CENG", "EE", "ME"]], true
        ],
        [
            ["CENG", ["EE", "ME"]], false
        ],
        [
            ["CENG", ["ME"]], false
        ],
        [
            ["CENG", []], false
        ],
    ];
    for(var i = 0 ; i < tests.length ; i++) {
        if(tests[i][1] != departmentCheck.apply(this, tests[i][0])) {
            console.log(tests[i]);
            return false;
        }
    }
    return true;
}

function test_apply_criteria_sections() {
    // surname, department, grade, course
    const course_1 = {
        code : 0,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE", "CENG"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
         
            }
        ]
    }
    const course_2 = {
        code : 0,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE", "CENG"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            }
        ]
    }
    const course_3 = {
        code : 0,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            }
        ]
    }
    const course_4 = {
        code : 0,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: []
    }
    const course_5 = {
        code : 0,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            },
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["CENG"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            }
        ]
    }
    const course_6 = {
        code : 0,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [            {
            minYear: 1,             // int
            maxYear: 4,             // int
            toggle: false,          // bool
            dept: ["CENG"],         // string array
            surnameStart: "AA",       // string
            surnameEnd: "ZZ",         // string
            lectureTimes : [
                {
                    day: 0,                 // int
                    startHour: 8,           // int
                    startMin: 40,            // int
                    endHour: 10,             // int
                    endMin: 30,              // int
                },
                {
                    day: 4,                 // int
                    startHour: 13,           // int
                    startMin: 40,            // int
                    endHour: 15,             // int
                    endMin: 30,              // int
                },
            ]
        }
    ]
    }
    const tests = [
            [
                [
                    "KE", 
                    "CENG", 
                    3, 
                    course_1,
                ],
                course_2
            ],
            [
                [
                    "KE", 
                    "CENG", 
                    3, 
                    course_3,
                ],
                course_4
            ],
            [
                [
                    "KE", 
                    "CENG", 
                    3, 
                    course_5,
                ],
                course_6
            ],
    ];
    for(var i = 0 ; i < tests.length ; i++) {
        if(JSON.stringify(tests[i][1]) != JSON.stringify(apply_criteria_sections.apply(this, tests[i][0]))) {
            console.log(JSON.stringify(tests[i][1]))
            console.log(JSON.stringify(apply_criteria_sections.apply(this, tests[i][0])))
            return false;
        }
    }
    return true;
}

function test_apply_criteria_courses() {
    // surname, department, grade, courses
    const course_1 = {
        code : 1,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE", "CENG"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
         
            }
        ]
    }
    const course_2 = {
        code : 1,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE", "CENG"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            }
        ]
    }
    const course_3 = {
        code : 2,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            }
        ]
    }
    const course_4 = {
        code : 2,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: []
    }
    const course_5 = {
        code : 3,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["EE"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            },
            {
                minYear: 1,             // int
                maxYear: 4,             // int
                toggle: false,          // bool
                dept: ["CENG"],         // string array
                surnameStart: "AA",       // string
                surnameEnd: "ZZ",         // string
                lectureTimes : [
                    {
                        day: 0,                 // int
                        startHour: 8,           // int
                        startMin: 40,            // int
                        endHour: 10,             // int
                        endMin: 30,              // int
                    },
                    {
                        day: 4,                 // int
                        startHour: 13,           // int
                        startMin: 40,            // int
                        endHour: 15,             // int
                        endMin: 30,              // int
                    },
                ]
            }
        ]
    }
    const course_6 = {
        code : 3,                       // int
        category: 0,                    // int
        check_surname: true,           // bool               
        check_collision: true,         // bool
        check_department: true,        // bool
        sections: [            {
            minYear: 1,             // int
            maxYear: 4,             // int
            toggle: false,          // bool
            dept: ["CENG"],         // string array
            surnameStart: "AA",       // string
            surnameEnd: "ZZ",         // string
            lectureTimes : [
                {
                    day: 0,                 // int
                    startHour: 8,           // int
                    startMin: 40,            // int
                    endHour: 10,             // int
                    endMin: 30,              // int
                },
                {
                    day: 4,                 // int
                    startHour: 13,           // int
                    startMin: 40,            // int
                    endHour: 15,             // int
                    endMin: 30,              // int
                },
            ]
        }
    ]
    }
    const courses_1 = [course_1, course_3, course_5];
    const courses_2 = [course_2, course_6];
    const tests = [
        [
            [
                "KE", 
                "CENG", 
                3, 
                courses_1,
            ],
            courses_2
        ],
    ];
    for(var i = 0 ; i < tests.length ; i++) {
        if(JSON.stringify(tests[i][1]) != JSON.stringify(apply_criteria_courses.apply(this, tests[i][0]))) {
            console.log("Error Log Here:")
            console.log(JSON.stringify(tests[i][1]))
            console.log(JSON.stringify(apply_criteria_courses.apply(this, tests[i][0])))
            return false;
        }
    }
    return true;
}
function main() {

    var surnameCheckRes = testSurnameCheck();
    console.log("surnameCheck function is", surnameCheckRes == true);
    
    var departmenCheckRes = testDepartmentCheck();
    console.log("departmenCheck function is", departmenCheckRes == true);

    var apply_criteria_sectionsRes = test_apply_criteria_sections();
    console.log("apply_criteria_sections function is", apply_criteria_sectionsRes == true);

    var apply_criteria_coursesRes = test_apply_criteria_courses();
    console.log("apply_criteria_courses function is", apply_criteria_coursesRes == true);


}




main();