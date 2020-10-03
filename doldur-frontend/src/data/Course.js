const exampleCourses = [
    {
        code: 5710213,
        abbreviation: "CENG213",
        name: "Data Structures",
        category: 0,
        sections: [
            {
                instructor: "Yusuf Sahillioğlu",
                dept: ["CENG", "EE"],
                surnameStart: "AA",
                surnameEnd: "FF",
                minYear: 0,
                maxYear: 0,
                lectureTimes: [
                    {
                        classroom: "BMB-1",
                        day: 0,
                        startHour: 8,
                        startMin: 40,
                        endHour: 10,
                        endMin: 30
                    },
                    {
                        classroom: "BMB-4",
                        day: 2,
                        startHour: 15,
                        startMin: 40,
                        endHour: 17,
                        endMin: 30
                    }
                ]
            },
            {
                instructor: "Cevat Şener",
                dept: ["CENG", "ME"],
                surnameStart: "FG",
                surnameEnd: "ZZ",
                minYear: 0,
                maxYear: 0,
                lectureTimes: [
                    {
                        classroom: "U-3",
                        day: 2,
                        startHour: 10,
                        startMin: 40,
                        endHour: 12,
                        endMin: 30
                    },
                    {
                        classroom: "CZ-14",
                        day: 6,
                        startHour: 15,
                        startMin: 40,
                        endHour: 17,
                        endMin: 30
                    }
                ]
            }
        ]
    },
    {
        code: 5710140,
        abbreviation: "CENG140",
        name: "C Programming",
        category: 1,
        sections: [
            {
                instructor: "Göktürk Üçoluk",
                dept: ["CENG"],
                surnameStart: "AA",
                surnameEnd: "ZZ",
                minYear: 0,
                maxYear: 0,
                lectureTimes: [
                    {
                        classroom: "BMB-1",
                        day: 0,
                        startHour: 8,
                        startMin: 40,
                        endHour: 10,
                        endMin: 30
                    },
                    {
                        classroom: "BMB-5",
                        day: 2,
                        startHour: 15,
                        startMin: 40,
                        endHour: 17,
                        endMin: 30
                    }
                ]
            }
        ]
    }
]

export function getAllCourses(){
    return exampleCourses;
}
export function getCourseByCategory(category){
    if (category < 0){
        return getAllCourses();
    }
    return getAllCourses().filter(c => c.category === category);
}
export function filterCourses(courses, category){
    if (category < 0){
        return courses;
    }
    return courses.filter(c => c.category === category);
}