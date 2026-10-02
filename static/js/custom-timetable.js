/* The planner shares the subject selection and custom editor's persisted state. */
const plannerPalette = ['#4486dd', '#238636', '#8144dd', '#c47616', '#c44862', '#16858a'];
const sourceDays = ['lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì'];
let plannerLessons = [];

// On weekends the planner looks ahead to the coming week.
function plannerWeekDates(today = new Date()) {
    const monday = new Date(today);
    const weekday = today.getDay();
    monday.setDate(today.getDate() - (weekday + 6) % 7 + (weekday % 6 === 0 ? 7 : 0));
    return Array.from({ length: 5 }, (_, day) => {
        const date = new Date(monday);
        date.setDate(monday.getDate() + day);
        return date;
    });
}

const plannerDates = plannerWeekDates();
const plannerToday = plannerDates.findIndex(date => date.toDateString() === new Date().toDateString());
let plannerDay = Math.max(0, plannerToday);
const plannerDateFormat = new Intl.DateTimeFormat(plannerLocale, { day: 'numeric', month: 'long' });
const plannerShortDate = plannerDates[0].getMonth() === plannerDates[4].getMonth()
    ? date => String(date.getDate())
    : new Intl.DateTimeFormat(plannerLocale, { day: 'numeric', month: 'short' }).format;

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

// Times follow the browser's language: 12-hour for en-US, 24-hour for Italian and most others.
const plannerTimeFormat = new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' });
const plannerHourFormat = new Intl.DateTimeFormat(undefined, { hour: 'numeric' });
const plannerClock = minutes => new Date(2000, 0, 1, 0, minutes);

function plannerTimeRange(start, end) {
    return plannerTimeFormat.formatRange(plannerClock(start), plannerClock(end));
}

// Selected subjects get distinct colours before the palette repeats.
function plannerCourseColor(code) {
    const codes = [...new Set([...selectedSubjects].map(id => id.split('-')[0]))].sort();
    return plannerPalette[codes.indexOf(code) % plannerPalette.length];
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
    const time = plannerElement('span', 'planner-lesson-time', plannerTimeRange(lesson.start, lesson.end));
    const name = plannerElement('strong', 'planner-lesson-name', weekly ? lesson.shortName : lesson.name);
    const room = plannerElement('span', 'planner-lesson-room', (weekly ? lesson.room : lesson.roomFull || lesson.room) || plannerLabels.roomPending);
    link.append(time, name, room);
    if (lesson.cancelled) link.append(plannerElement('span', 'planner-lesson-notice', plannerLabels.cancelled));
    if (lesson.alerts) link.append(plannerElement('span', 'planner-lesson-notice', plannerLabels.alerts));
    if (lesson.overlap && weekly) {
        const warning = plannerElement('i', 'fa-solid fa-triangle-exclamation planner-warning-icon');
        warning.setAttribute('aria-hidden', 'true');
        time.append(warning);
    }
    if (weekly) {
        link.title = [lesson.name, lesson.roomFull].filter(Boolean).join(' · ');
        link.setAttribute('aria-label', [customTimetableDays[lesson.dayIndex], time.textContent, lesson.name,
            room.textContent, lesson.cancelled && plannerLabels.cancelled, lesson.overlap && plannerLabels.overlap].filter(Boolean).join(' · '));
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
    week.style.gridTemplateColumns = `3.75rem ${lanes.map(count => `minmax(0, ${count}fr)`).join(' ')}`;
    document.getElementById('plannerWeekHint').hidden = !plannerLessons.some(lesson => lesson.overlap);
    week.append(plannerElement('div', 'planner-week-corner', ''));
    customTimetableDays.forEach((day, index) => {
        const heading = plannerElement('div', 'planner-week-heading', `${day} `);
        heading.append(plannerElement('span', '', plannerShortDate(plannerDates[index])));
        if (index === plannerToday) heading.setAttribute('aria-current', 'date');
        week.append(heading);
    });
    const axis = plannerElement('div', 'planner-time-axis');
    for (let time = start; time < end; time += 60) {
        axis.append(plannerElement('span', 'planner-hour', plannerHourFormat.format(plannerClock(time))));
    }
    week.append(axis);
    for (let day = 0; day < 5; day++) {
        const column = plannerElement('div', 'planner-week-column');
        if (day === plannerToday) column.classList.add('planner-week-column--today');
        for (let time = start; time < end; time += 60) {
            column.append(plannerElement('div', 'planner-hour-rule'));
        }
        for (const lesson of plannerLessons.filter(lesson => lesson.dayIndex === day)) {
            const block = plannerLesson(lesson, true);
            block.style.top = `calc(${(lesson.start - start) / 60} * var(--planner-hour-height) + 2px)`;
            block.style.height = `calc(${(lesson.end - lesson.start) / 60} * var(--planner-hour-height) - 4px)`;
            block.style.left = `calc(${lesson.lane / lesson.lanes * 100}% + 2px)`;
            block.style.width = `calc(${100 / lesson.lanes}% - 4px)`;
            column.append(block);
        }
        week.append(column);
    }
}

function setPlannerDay(day) {
    plannerDay = day;
    const schedule = document.getElementById('plannerDaySchedule');
    const heading = `${customTimetableDays[day]} ${plannerDateFormat.format(plannerDates[day])}`;
    schedule.replaceChildren(plannerElement('h3', 'planner-day-heading', day === plannerToday ? `${plannerLabels.today} · ${heading}` : heading));
    for (const button of document.querySelectorAll('[data-planner-day]')) {
        const selected = Number(button.dataset.plannerDay) === day;
        button.setAttribute('aria-pressed', String(selected));
        button.tabIndex = selected ? 0 : -1;
    }
    const lessons = plannerLessons.filter(lesson => lesson.dayIndex === day);
    if (!lessons.length) {
        const empty = plannerElement('div', 'planner-day-empty');
        empty.append(plannerElement('p', '', plannerLabels.noLessons), plannerElement('small', '', plannerLabels.noLessonsHint));
        schedule.append(empty);
    }
    const now = new Date().getHours() * 60 + new Date().getMinutes();
    const upcoming = day === plannerToday && lessons.find(lesson => !lesson.cancelled && lesson.end > now);
    const list = plannerElement('div', 'planner-day-lessons');
    const card = lesson => {
        const link = plannerLesson(lesson);
        if (lesson === upcoming) {
            link.classList.add('planner-lesson--upcoming');
            link.querySelector('.planner-lesson-time').prepend(plannerElement('span', 'planner-badge', lesson.start <= now ? plannerLabels.now : plannerLabels.next));
        }
        return link;
    };
    for (const group of layoutPlannerDay(lessons)) {
        if (!group.some(lesson => lesson.overlap)) {
            list.append(...group.map(card));
            continue;
        }
        const range = plannerTimeRange(Math.min(...group.map(lesson => lesson.start)), Math.max(...group.map(lesson => lesson.end)));
        const section = plannerElement('section', 'planner-conflict-group');
        const title = plannerElement('h4', 'planner-conflict-heading', `${plannerLabels.overlap} · ${range}`);
        const icon = plannerElement('i', 'fa-solid fa-triangle-exclamation planner-warning-icon');
        icon.setAttribute('aria-hidden', 'true');
        title.prepend(icon);
        const conflicts = plannerElement('div', 'planner-day-lessons');
        conflicts.append(...group.map(card));
        section.append(title, conflicts);
        list.append(section);
    }
    schedule.append(list);
}

function setPlannerView(view) {
    document.getElementById('main').dataset.view = view;
    localStorage.setItem('plannerView', view);
    for (const button of document.querySelectorAll('[data-planner-view]')) {
        button.setAttribute('aria-pressed', String(button.dataset.plannerView === view));
    }
}

function stepPlannerDay(step) {
    setPlannerDay((plannerDay + step + 5) % 5);
    document.querySelector(`[data-planner-day="${plannerDay}"]`).focus();
}

function renderPlanner(customSubjects) {
    plannerLessons = collectPlannerLessons(customSubjects);
    for (let day = 0; day < 5; day++) layoutPlannerDay(plannerLessons.filter(lesson => lesson.dayIndex === day));
    const count = [...selectedSubjects].filter(id => pageDegreeSubjects.has(id.split('-')[0]) && getSubjectButtons(id).length).length + customSubjects.length;
    document.getElementById('plannerTeachingDetails').hidden = selectedSubjects.size === 0;
    document.querySelector('#customSubjectsDetails > h2').hidden = selectedSubjects.size > 0;
    const summary = [plannerLabels.subjectCount.replace('%n', count), plannerLabels.lessonCount.replace('%n', plannerLessons.length)];
    if (plannerLessons.some(lesson => lesson.overlap)) summary.push(plannerLabels.overlap);
    document.getElementById('plannerSummary').textContent = count ? summary.join(' · ') : '';
    document.getElementById('plannerPickerCount').textContent = plannerLabels.subjectCount.replace('%n', selectedSubjects.size);
    const bothChannels = [...selectedSubjects].filter(id => id.endsWith('-1') && selectedSubjects.has(id.replace(/-1$/, '-2')))
        .map(id => COURSES[id.split('-')[0]]?.name).filter(Boolean);
    const channelWarning = document.getElementById('plannerChannelWarning');
    channelWarning.hidden = !bothChannels.length;
    channelWarning.lastChild.textContent = plannerLabels.bothChannels.replace('%s', bothChannels.join(', '));
    document.getElementById('plannerEmpty').hidden = count > 0;
    document.getElementById('plannerManageButton').hidden = count === 0;
    document.querySelector('.planner-view-switch').hidden = !plannerLessons.length;
    document.querySelector('.planner-calendar-footer').hidden = count === 0;
    document.getElementById('plannerLessonTip').hidden = !plannerLessons.length;
    document.getElementById('plannerSchedule').hidden = !plannerLessons.length;
    document.getElementById('plannerUnscheduled').hidden = count === 0 || plannerLessons.length > 0;
    const days = document.getElementById('plannerDays');
    days.replaceChildren();
    customTimetableDayShorts.forEach((day, index) => {
        const button = plannerElement('button', 'planner-day-button', day);
        button.type = 'button';
        button.dataset.plannerDay = index;
        button.setAttribute('aria-label', `${customTimetableDays[index]}, ${plannerDateFormat.format(plannerDates[index])}${index === plannerToday ? `, ${plannerLabels.today}` : ''}`);
        if (index === plannerToday) button.setAttribute('aria-current', 'date');
        button.append(plannerElement('span', '', plannerShortDate(plannerDates[index])));
        button.addEventListener('click', () => setPlannerDay(index));
        days.append(button);
    });
    renderPlannerWeek();
    if (plannerLessons.length) setPlannerDay(plannerDay);
    if (document.getElementById('subjsPopUp').open) filterSubjects(document.getElementById('subjsSearch').value);
}

// Arrow keys and horizontal swipes move between days.
function plannerDaysKeydown(event) {
    const step = { ArrowLeft: -1, ArrowRight: 1 }[event.key];
    if (!step) return;
    event.preventDefault();
    stepPlannerDay(step);
}

let plannerTouch = null;
function plannerSwipe(event) {
    if (event.type === 'touchstart') {
        plannerTouch = event.touches[0];
        return;
    }
    const dx = event.changedTouches[0].clientX - plannerTouch.clientX;
    const dy = event.changedTouches[0].clientY - plannerTouch.clientY;
    if (Math.abs(dx) > 60 && Math.abs(dx) > 2 * Math.abs(dy)) setPlannerDay((plannerDay + (dx < 0 ? 1 : 4)) % 5);
}
