const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');

const planner = {
    plannerLocale: 'en',
    selectedSubjects: new Set(['course-1', 'course-2', 'obsolete-0']),
    pageDegreeSubjects: new Set(['course']),
    COURSES: { course: { name: 'Course', shortName: 'Short course' } },
    TIMETABLES: { course: { channels: {
        0: { lunedì: [{ timeslot: '08:30 - 09:30', classrooms: { room: 'Room A' } }] },
        1: { martedì: [{ timeslot: '10 - 12' }] },
        2: { mercoledì: { timeslot: '14 - 16', cancelled: true } },
    } } },
    formatClassrooms: rooms => rooms.join(', '),
};
vm.runInNewContext(readFileSync(join(__dirname, '../../static/js/custom-timetable.js'), 'utf8'), planner);

// Shared channel lessons appear once; exact times, rooms and cancellation survive.
let lessons = planner.collectPlannerLessons([]);
assert.equal(lessons.length, 3);
assert.equal(lessons[0].start, 510);
assert.equal(lessons[0].end, 570);
assert.equal(lessons[0].room, 'Room A');
assert.equal(lessons[2].cancelled, true);

lessons = planner.collectPlannerLessons([{
    id: 'custom-test', name: 'Custom course', color: '#238636',
    lessons: [{ dayIndex: 0, startTime: '09:00', endTime: '10:00', roomName: 'Lab' }],
}]);
assert.equal(lessons.length, 4);
assert.equal(lessons[1].href, '#custom-subject-details-custom-test');
assert.equal(lessons[1].start, 540);
assert.equal(lessons[1].room, 'Lab');

// Connected overlaps share lanes; touching and cancelled lessons are not conflicts.
lessons = [{ start: 480, end: 600 }, { start: 540, end: 660 }, { start: 600, end: 720 }, { start: 720, end: 780 }];
const groups = planner.layoutPlannerDay(lessons);
assert.deepEqual(Array.from(groups, group => group.length), [3, 1]);
assert.deepEqual(lessons.map(({ lane, lanes, overlap }) => [lane, lanes, overlap]), [
    [0, 2, true], [1, 2, true], [0, 2, true], [0, 1, false],
]);
lessons = [{ start: 480, end: 600 }, { start: 510, end: 630 }, { start: 540, end: 660 }];
planner.layoutPlannerDay(lessons);
assert.deepEqual(lessons.map(({ lane, lanes, overlap }) => [lane, lanes, overlap]), [[0, 3, true], [1, 3, true], [2, 3, true]]);
lessons = [{ start: 480, end: 600 }, { start: 540, end: 600, cancelled: true }];
planner.layoutPlannerDay(lessons);
assert.ok(lessons.every(lesson => !lesson.overlap));

// Calendar dates cross month/year boundaries; Sunday still belongs to the past week.
for (const [today, expected] of [
    [new Date(2026, 9, 2), ['9/28', '9/29', '9/30', '10/1', '10/2']],
    [new Date(2026, 0, 1), ['12/29', '12/30', '12/31', '1/1', '1/2']],
    [new Date(2026, 9, 4), ['9/28', '9/29', '9/30', '10/1', '10/2']],
]) {
    const dates = planner.plannerWeekDates(today);
    assert.deepEqual(Array.from(dates, date => `${date.getMonth() + 1}/${date.getDate()}`), expected);
}
assert.equal(vm.runInNewContext("plannerDateFormat.format(new Date(2026, 9, 2))", planner), 'October 2');
console.log('Custom timetable checks passed.');
