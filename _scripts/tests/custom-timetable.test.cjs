const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');

const preferences = new Map();
const screen = { matches: false, listeners: [], addEventListener: (_, listener) => screen.listeners.push(listener) };
const planner = {
    localStorage: { getItem: key => preferences.get(key), setItem: (key, value) => preferences.set(key, value) },
    matchMedia: () => screen,
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
for (const file of ['timetable-planner.js', 'custom-timetable.js']) {
    vm.runInNewContext(readFileSync(join(__dirname, '../../static/js', file), 'utf8'), planner);
}

// Shared channel lessons appear once; exact times, rooms and cancellation survive.
let lessons = planner.collectPlannerLessons(planner.selectedSubjects);
assert.equal(lessons.length, 3);
assert.equal(lessons[0].start, 510);
assert.equal(lessons[0].end, 570);
assert.equal(lessons[0].room, 'Room A');
assert.equal(lessons[2].cancelled, true);

lessons = planner.collectPlannerLessons(planner.selectedSubjects, [{
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

// Calendar dates cross month/year boundaries; weekends look ahead to the coming week.
for (const [today, expected] of [
    [new Date(2026, 9, 2), ['9/28', '9/29', '9/30', '10/1', '10/2']],
    [new Date(2026, 0, 1), ['12/29', '12/30', '12/31', '1/1', '1/2']],
    [new Date(2026, 9, 3), ['10/5', '10/6', '10/7', '10/8', '10/9']],
    [new Date(2026, 9, 4), ['10/5', '10/6', '10/7', '10/8', '10/9']],
]) {
    const dates = planner.plannerWeekDates(today);
    assert.deepEqual(Array.from(dates, date => `${date.getMonth() + 1}/${date.getDate()}`), expected);
}
assert.equal(vm.runInNewContext("plannerDateFormat.format(new Date(2026, 9, 2))", planner), 'October 2');
// Explicit clock formats retain AM/PM in 12-hour mode and use 00 at midnight in 24-hour mode.
const clock = new Date(2000, 0, 1, 13, 30);
const [twelve] = planner.plannerTimeFormats('12');
const [twentyFour] = planner.plannerTimeFormats('24');
assert.equal(twelve.resolvedOptions().hourCycle, 'h12');
assert.equal(twentyFour.resolvedOptions().hourCycle, 'h23');
assert.ok(twelve.formatToParts(clock).some(part => part.type === 'dayPeriod'));
assert.equal(twentyFour.format(new Date(2000, 0, 1)), '00:00');
assert.equal(planner.plannerTimeFormats('auto')[0].resolvedOptions().hourCycle,
    new Intl.DateTimeFormat(undefined, { hour: 'numeric' }).resolvedOptions().hourCycle);

// Several fixed calendars keep view state scoped to their own controls.
const element = () => ({
    dataset: {}, children: [], clientWidth: 0, listeners: {},
    scrollTo() {}, setAttribute() {},
    addEventListener(type, listener) { this.listeners[type] = listener; },
});
function calendarRoot() {
    const root = element();
    const fields = new Map();
    const buttons = ['week', 'agenda'].map(view => Object.assign(element(), { dataset: { plannerView: view } }));
    root.querySelector = selector => {
        if (!fields.has(selector)) fields.set(selector, element());
        return fields.get(selector);
    };
    root.querySelectorAll = () => buttons;
    return { root, buttons };
}
planner.ResizeObserver = class { observe() {} };
const first = calendarRoot(), second = calendarRoot();
planner.createTimetablePlanner(first.root);
planner.createTimetablePlanner(second.root);
assert.equal(first.root.dataset.view, 'week');
first.buttons[1].listeners.click();
assert.equal(first.root.dataset.view, 'agenda');
assert.equal(second.root.dataset.view, 'week');
screen.matches = true;
screen.listeners.forEach(listener => listener());
assert.equal(first.root.dataset.view, 'agenda');
first.buttons[0].listeners.click();
screen.matches = false;
screen.listeners.forEach(listener => listener());
assert.equal(first.root.dataset.view, 'agenda');
screen.matches = true;
screen.listeners.forEach(listener => listener());
assert.equal(first.root.dataset.view, 'week');
// Fixed channel filters include the common channel, but exclude the other channel.
const fixedLessons = planner.collectPlannerLessons(['course-1']);
assert.equal(fixedLessons.length, 2);
assert.ok(fixedLessons.every(lesson => !lesson.cancelled));
assert.equal(fixedLessons[0].start, 510);

// Cancelling lesson removal keeps the editor row and its save state intact.
const template = readFileSync(join(__dirname, '../../layouts/page/custom-timetable.html'), 'utf8');
const removeButton = template.slice(template.indexOf('    function removeRowButton('), template.indexOf('    function updateCustomLessonNumbers('))
    .replace(/{{ T "(\w+)" \| jsonify \| safeJS }}/g, '"$1"').replace(/{{ T "(\w+)" }}/g, '$1');
let confirmed = false, removed = false, updated = false;
const editor = {
    document: { createElement: () => ({ setAttribute() {} }), querySelector: () => ({ focus() {} }) },
    confirmCustomRemoval: (message, onConfirm) => { if (confirmed) onConfirm(); },
    updateCustomSubjectSaveVisibility: () => { updated = true; },
    updateCustomLessonNumbers() {},
};
vm.runInNewContext(removeButton, editor);
const button = editor.removeRowButton({ remove: () => { removed = true; } });
button.onclick();
assert.equal(removed, false);
assert.equal(updated, false);
confirmed = true;
button.onclick();
assert.equal(removed, true);
assert.equal(updated, true);
// A new course needs one name; explicit abbreviations survive edits and imports.
assert.deepEqual({ ...planner.customSubjectNames('  Machine Learning  ', '', '') },
    { name: 'Machine Learning', shortName: 'Machine Learning', abbr: 'ML' });
assert.deepEqual({ ...planner.customSubjectNames('Machine Learning', '  ML course ', ' ml ') },
    { name: 'Machine Learning', shortName: 'ML course', abbr: 'ML' });
// Escape shares Close/Back's discard guard, keeping a cancelled draft intact.
const closeEditor = template.slice(template.indexOf('    function closeCustomSubjectDialog('), template.indexOf('    function saveCustomSubject('));
const cancelHandler = template.match(/id="customSubjectDialog"[^>]*oncancel="([^"]+)"/)[1];
let discarded = false, closed = false, prevented = false;
const dismissal = {
    confirmDiscardCustomSubjectChanges: () => discarded,
    document: { getElementById: () => ({ close: () => { closed = true; } }) },
    pendingCustomSubjectImport: 'draft import',
    customSubjectEditorInitialState: 'draft state',
    event: { preventDefault: () => { prevented = true; } },
};
vm.runInNewContext(closeEditor, dismissal);
vm.runInNewContext(cancelHandler, dismissal);
assert.equal(prevented, true);
assert.equal(closed, false);
assert.equal(dismissal.customSubjectEditorInitialState, 'draft state');
discarded = true;
vm.runInNewContext(cancelHandler, dismissal);
assert.equal(closed, true);
assert.equal(dismissal.customSubjectEditorInitialState, null);
assert.equal(dismissal.pendingCustomSubjectImport, null);
console.log('Custom timetable checks passed.');
