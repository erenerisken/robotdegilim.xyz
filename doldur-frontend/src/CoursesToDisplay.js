const schedulerData = [
    { startDate: '2018-11-01T09:40', endDate: '2018-11-01T11:30', title: 'Meeting' },
    { startDate: '2018-11-01T12:00', endDate: '2018-11-01T13:30', title: 'Go to a gym' },
    { startDate: '2018-11-02T09:40', endDate: '2018-11-02T11:30', title: 'Meeting' },
];

export function getCoursesToDisplay(){
    return schedulerData;
}