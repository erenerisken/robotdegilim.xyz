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

// 
// 
// 
// 
// returns array of code + sections
function compute_schedule(surname, department, grade, courses) {
    apply_criteria(surname, department, grade, courses)

    



}