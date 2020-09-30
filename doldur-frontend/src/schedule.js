function apply_criteria(surname, department, grade, courses) {

}


function check_collision(course1, course2) {
    
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
    apply_criteria(surname, department, grade, courses)

    

//  callback(scenario)

}