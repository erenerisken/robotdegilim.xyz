import {Client} from "../Client";
// eslint-disable-next-line
const exampleCourses = [
    {
        code: 5710213,
        abbreviation: "CENG213",
        name: "Data Structures",
        category: 0,
        sections: [
            {
                instructor: "Yusuf Sahillioğlu",
                criteria: [
                    {
                        dept: "CENG",
                        surnameStart: "AA",
                        surnameEnd: "FF"
                    },
                    {
                        dept: "EE",
                        surnameStart: "AA",
                        surnameEnd: "ZZ"
                    }
                ],
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
                criteria: [
                    {
                        dept: "CENG",
                        surnameStart: "FG",
                        surnameEnd: "ZZ"
                    },
                    {
                        dept: "ME",
                        surnameStart: "AA",
                        surnameEnd: "ZZ"
                    }
                ],
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
                criteria: [
                    {
                        dept: "CENG",
                        surnameStart: "AA",
                        surnameEnd: "ZZ"
                    }
                ],
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

export async function getAllCourses(){
    const client = new Client();
    return await client.getCourses();
}
export async function getMusts(dept, semester){
    const client = new Client();
    return client.getMusts(dept, semester);
}

// NTE fonksiyonları
export async function getNTECourses(){
    const client = new Client();
    return await client.getNTEs();
}

export function filterAvailableNTEs(nteData, occupiedSlots) {
    return nteData.map(course => {
        // Her ders için sadece uygun şubeleri filtrele
        const availableSections = course.sections.filter(section => {
            // "No Timestamp Added Yet" olan bölümleri atla
            if (section.times.some(time => time.day === "No Timestamp Added Yet")) {
                return false;
            }
            
            // Bu bölümün hiçbir zamanı mevcut derslerle çakışmıyor mu kontrol et
            return section.times.every(time => {
                const nteSlot = convertNTETimeToSlot(time);
                if (!nteSlot) return false;
                
                return !occupiedSlots.some(occupied => 
                    isTimeSlotConflict(nteSlot, occupied)
                );
            });
        });
        
        // Eğer en az bir uygun şube varsa dersi döndür
        if (availableSections.length > 0) {
            return {
                ...course,
                sections: availableSections
            };
        }
        return null;
    }).filter(course => course !== null); // null olanları filtrele
}

function convertNTETimeToSlot(nteTime) {
    if (nteTime.day === "No Timestamp Added Yet" || !nteTime.start || !nteTime.end) {
        return null;
    }
    
    const dayMap = {
        "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6
    };
    
    const day = dayMap[nteTime.day];
    if (day === undefined) return null;
    
    const startTime = parseTimeString(nteTime.start);
    const endTime = parseTimeString(nteTime.end);
    
    if (!startTime || !endTime) return null;
    
    return {
        day: day,
        startHour: startTime.hour,
        startMin: startTime.min,
        endHour: endTime.hour,
        endMin: endTime.min,
        room: nteTime.room || "TBA"
    };
}

function parseTimeString(timeStr) {
    if (!timeStr) return null;
    const parts = timeStr.split(':');
    if (parts.length !== 2) return null;
    
    const hour = parseInt(parts[0]);
    const min = parseInt(parts[1]);
    
    if (isNaN(hour) || isNaN(min)) return null;
    
    return { hour, min };
}

function isTimeSlotConflict(slot1, slot2) {
    if (slot1.day !== slot2.day) return false;
    
    // Zaman çakışması kontrolü
    const slot1Start = slot1.startHour * 60 + slot1.startMin;
    const slot1End = slot1.endHour * 60 + slot1.endMin;
    const slot2Start = slot2.startHour * 60 + slot2.startMin;
    const slot2End = slot2.endHour * 60 + slot2.endMin;
    
    return !(slot1End <= slot2Start || slot2End <= slot1Start);
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
