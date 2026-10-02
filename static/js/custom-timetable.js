/* The planner shares the subject selection and custom editor's persisted state. */
const plannerPalette = ['#4486dd', '#238636', '#8144dd', '#c47616', '#c44862', '#16858a'];
const sourceDays = ['lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì'];
let plannerDay = Math.max(0, Math.min(4, new Date().getDay() - 1));
let plannerLessons = [];

function plannerWeekDates(today = new Date()) {
    const monday = new Date(today);
    monday.setDate(today.getDate() - (today.getDay() + 6) % 7);
    return Array.from({ length: 5 }, (_, day) => {
        const date = new Date(monday);
        date.setDate(monday.getDate() + day);
        return date;
    });
}

const plannerDates = plannerWeekDates();
const plannerDateFormat = new Intl.DateTimeFormat(plannerLocale, { day: 'numeric', month: 'long' });

function plannerElement(tag, className, text) {
    const element = document.createElement(tag);
    element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
}

function plannerMinutes(time) {
    const [hour, minute = 0] = time.trim().split(':').map(Number);
    return hour * 60 + minute;
}

function plannerTime(minutes) {
    return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`;
}

function plannerCourseColor(code) {
    return plannerPalette[[...pageDegreeSubjects].indexOf(code) % plannerPalette.length];
}

function collectPlannerLessons(customSubjects) {
    const lessons = new Map();
    for (const subjectId of selectedSubjects) {
        const [code, channel] = subjectId.split('-');
        if (!pageDegreeSubjects.has(code) || !TIMETABLES[code]) continue;
        const course = COURSES[code];
        const channels = channel === '0' ? ['0'] : [channel, '0'];
        for (const channelId of channels) {
            for (const [day, slots] of Object.entries(TIMETABLES[code].channels[channelId] || {})) {
                const dayIndex = sourceDays.indexOf(day);
                if (dayIndex < 0) continue;
                for (const slot of [slots].flat()) {
                    const [start, end] = slot.timeslot.split('-').map(plannerMinutes);
                    const rooms = slot.classroomInfo ? [slot.classroomInfo] : Object.values(slot.classrooms || {});
                    const room = formatClassrooms(rooms) || rooms.join(', ');
                    const key = JSON.stringify([code, day, start, end, rooms, slot.cancelled]);
                    lessons.set(key, {
                        name: course.name, shortName: course.shortName || course.name,
                        start, end, dayIndex, room, roomFull: rooms.join(', '),
                        color: plannerCourseColor(code), href: `#${code}`,
                        cancelled: slot.cancelled === true,
                        alerts: course.alerts?.[channel]?.[day],
                    });
                }
            }
        }
    }
    for (const subject of customSubjects) {
        subject.lessons.forEach((lesson, index) => lessons.set(`${subject.id}-${index}`, {
            name: subject.name, shortName: subject.shortName || subject.name,
            start: plannerMinutes(lesson.startTime), end: plannerMinutes(lesson.endTime),
            dayIndex: lesson.dayIndex, room: lesson.roomAbbr || lesson.roomName,
            roomFull: lesson.roomName, color: subject.color,
            href: `#custom-subject-details-${subject.id}`, cancelled: false,
        }));
    }
    return [...lessons.values()].sort((a, b) => a.dayIndex - b.dayIndex || a.start - b.start || a.end - b.end);
}

// Each connected group of overlapping lessons gets its own parallel lanes.
// ponytail: quadratic scans suit a student week; use a sweep line for a large shared calendar.
function layoutPlannerDay(lessons) {
    const groups = [];
    let cluster = [], clusterEnd = 0;
    const finishCluster = () => {
        if (!cluster.length) return;
        groups.push(cluster);
        const laneEnds = [];
        for (const lesson of cluster) {
            let lane = laneEnds.findIndex(end => end <= lesson.start);
            if (lane < 0) lane = laneEnds.length;
            laneEnds[lane] = lesson.end;
            lesson.lane = lane;
        }
        for (const lesson of cluster) {
            lesson.lanes = laneEnds.length;
            lesson.overlap = !lesson.cancelled && lessons.some(other => other !== lesson && !other.cancelled
                && other.start < lesson.end && other.end > lesson.start);
        }
    };
    for (const lesson of lessons) {
        if (cluster.length && lesson.start >= clusterEnd) {
            finishCluster();
            cluster = [];
            clusterEnd = 0;
        }
        cluster.push(lesson);
        clusterEnd = Math.max(clusterEnd, lesson.end);
    }
    finishCluster();
    return groups;
}

function plannerLesson(lesson, weekly = false) {
    const link = plannerElement('a', `planner-lesson${lesson.cancelled ? ' planner-lesson--cancelled' : ''}`);
    link.href = lesson.href;
    link.style.setProperty('--lesson-color', lesson.color);
    link.title = [lesson.name, lesson.roomFull, lesson.overlap && plannerLabels.overlap].filter(Boolean).join(' · ');
    const time = plannerElement('span', 'planner-lesson-time', `${plannerTime(lesson.start)} – ${plannerTime(lesson.end)}`);
    const name = plannerElement('strong', 'planner-lesson-name', weekly ? lesson.shortName : lesson.name);
    const room = plannerElement('span', 'planner-lesson-room', (weekly ? lesson.room : lesson.roomFull || lesson.room) || plannerLabels.roomPending);
    link.append(time, name, room);
    if (lesson.cancelled) link.append(plannerElement('span', 'planner-lesson-notice', plannerLabels.cancelled));
    if (lesson.alerts) link.append(plannerElement('span', 'planner-lesson-notice', plannerLabels.alerts));
    if (lesson.overlap && weekly) {
        const warning = plannerElement('i', 'fa-solid fa-circle-exclamation');
        warning.setAttribute('aria-hidden', 'true');
        time.append(warning);
        link.setAttribute('aria-label', [time.textContent, lesson.name, room.textContent, plannerLabels.overlap].join(' · '));
    }
    return link;
}

function renderPlannerWeek() {
    const week = document.getElementById('plannerWeek');
    week.replaceChildren();
    if (!plannerLessons.length) return;
    const start = Math.floor(Math.min(...plannerLessons.map(lesson => lesson.start)) / 60) * 60;
    const end = Math.ceil(Math.max(...plannerLessons.map(lesson => lesson.end)) / 60) * 60;
    week.style.setProperty('--planner-hours', (end - start) / 60);
    const lanes = Array.from({ length: 5 }, (_, day) => Math.max(1, ...plannerLessons.filter(lesson => lesson.dayIndex === day).map(lesson => lesson.lanes)));
    week.style.setProperty('--planner-lanes', lanes.reduce((sum, count) => sum + count, 0));
    week.style.gridTemplateColumns = `3.75rem ${lanes.map(count => `${count}fr`).join(' ')}`;
    document.getElementById('plannerWeekHint').hidden = !plannerLessons.some(lesson => lesson.overlap);
    week.append(plannerElement('div', 'planner-week-corner', ''));
    customTimetableDays.forEach(day => week.append(plannerElement('div', 'planner-week-heading', day)));
    const axis = plannerElement('div', 'planner-time-axis');
    for (let time = start; time < end; time += 60) {
        axis.append(plannerElement('span', 'planner-hour', plannerTime(time)));
    }
    week.append(axis);
    for (let day = 0; day < 5; day++) {
        const column = plannerElement('div', 'planner-week-column');
        column.setAttribute('aria-label', customTimetableDays[day]);
        for (let time = start; time < end; time += 60) {
            column.append(plannerElement('div', 'planner-hour-rule'));
        }
        for (const lesson of plannerLessons.filter(lesson => lesson.dayIndex === day)) {
            const block = plannerLesson(lesson, true);
            block.style.top = `calc(${(lesson.start - start) / 60} * var(--planner-hour-height) + 3px)`;
            block.style.height = `calc(${(lesson.end - lesson.start) / 60} * var(--planner-hour-height) - 6px)`;
            block.style.left = `calc(${lesson.lane / lesson.lanes * 100}% + 3px)`;
            block.style.width = `calc(${100 / lesson.lanes}% - 6px)`;
            column.append(block);
        }
        week.append(column);
    }
}

function setPlannerDay(day) {
    plannerDay = day;
    const schedule = document.getElementById('plannerDaySchedule');
    schedule.replaceChildren(plannerElement('h3', 'planner-day-heading', `${customTimetableDays[day]} ${plannerDateFormat.format(plannerDates[day])}`));
    for (const button of document.querySelectorAll('[data-planner-day]')) {
        button.setAttribute('aria-pressed', String(Number(button.dataset.plannerDay) === day));
    }
    const lessons = plannerLessons.filter(lesson => lesson.dayIndex === day);
    if (!lessons.length) {
        const empty = plannerElement('div', 'planner-day-empty');
        empty.append(plannerElement('p', '', plannerLabels.noLessons), plannerElement('small', '', plannerLabels.noLessonsHint));
        schedule.append(empty);
    }
    const list = plannerElement('div', 'planner-day-lessons');
    for (const group of layoutPlannerDay(lessons)) {
        if (group.some(lesson => lesson.overlap)) {
            const section = plannerElement('section', 'planner-conflict-group');
            const heading = plannerElement('h4', 'planner-conflict-heading', plannerLabels.overlap);
            const icon = plannerElement('i', 'fa-solid fa-circle-exclamation');
            icon.setAttribute('aria-hidden', 'true');
            heading.prepend(icon);
            section.setAttribute('aria-label', plannerLabels.overlap);
            section.append(heading, plannerElement('p', 'planner-conflict-explanation', plannerLabels.overlapExplanation));
            const conflicts = plannerElement('div', 'planner-day-lessons');
            for (const lesson of group) conflicts.append(plannerLesson(lesson));
            section.append(conflicts);
            list.append(section);
        } else {
            for (const lesson of group) list.append(plannerLesson(lesson));
        }
    }
    schedule.append(list);
}

function setPlannerView(view) {
    document.getElementById('main').dataset.view = view;
    for (const button of document.querySelectorAll('[data-planner-view]')) {
        button.setAttribute('aria-pressed', String(button.dataset.plannerView === view));
    }
}

function renderPlanner(customSubjects) {
    plannerLessons = collectPlannerLessons(customSubjects);
    for (let day = 0; day < 5; day++) layoutPlannerDay(plannerLessons.filter(lesson => lesson.dayIndex === day));
    const count = [...selectedSubjects].filter(id => pageDegreeSubjects.has(id.split('-')[0]) && getSubjectButtons(id).length).length + customSubjects.length;
    document.getElementById('plannerTeachingDetails').hidden = selectedSubjects.size === 0;
    const summary = [plannerLabels.subjectCount.replace('%n', count), plannerLabels.lessonCount.replace('%n', plannerLessons.length)];
    if (plannerLessons.some(lesson => lesson.overlap)) summary.push(plannerLabels.overlap);
    document.getElementById('plannerSummary').textContent = summary.join(' · ');
    document.getElementById('plannerPickerCount').textContent = plannerLabels.subjectCount.replace('%n', selectedSubjects.size);
    document.getElementById('plannerEmpty').hidden = count > 0;
    document.getElementById('plannerSchedule').hidden = !plannerLessons.length;
    document.getElementById('plannerUnscheduled').hidden = count === 0 || plannerLessons.length > 0;
    const days = document.getElementById('plannerDays');
    days.replaceChildren();
    customTimetableDayShorts.forEach((day, index) => {
        const button = plannerElement('button', 'planner-day-button', day);
        button.type = 'button';
        button.dataset.plannerDay = index;
        button.setAttribute('aria-label', `${customTimetableDays[index]}, ${plannerDateFormat.format(plannerDates[index])}`);
        button.append(plannerElement('span', '', plannerDates[index].getDate()));
        button.addEventListener('click', () => setPlannerDay(index));
        days.append(button);
    });
    renderPlannerWeek();
    if (plannerLessons.length) setPlannerDay(plannerDay);
    if (document.getElementById('subjsPopUp').open) filterSubjects(document.getElementById('subjsSearch').value);
}
