/* Shared calendar and agenda for fixed and customizable course timetables. */
const plannerPalette = ['#4486dd', '#238636', '#8144dd', '#c47616', '#c44862', '#16858a'];
const sourceDays = ['lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì'];
const timetablePlanners = [];

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

// Automatic follows the browser locale; explicit formats also handle midnight consistently.
function plannerTimeFormats(format) {
    const options = format === 'auto' ? {} : { hourCycle: format === '12' ? 'h12' : 'h23' };
    return [
        new Intl.DateTimeFormat(undefined, { ...options, hour: 'numeric', minute: '2-digit' }),
        new Intl.DateTimeFormat(undefined, { ...options, hour: 'numeric' }),
    ];
}
let [plannerTimeFormat, plannerHourFormat] = plannerTimeFormats(localStorage.getItem('plannerTimeFormat') || 'auto');

function setPlannerTimeFormat(format) {
    localStorage.setItem('plannerTimeFormat', format);
    [plannerTimeFormat, plannerHourFormat] = plannerTimeFormats(format);
    timetablePlanners.forEach(planner => planner.refreshTimeFormat());
}
const plannerClock = minutes => new Date(2000, 0, 1, 0, minutes);

function plannerTimeRange(start, end, compact = false) {
    const format = compact && start % 60 === 0 && end % 60 === 0 ? plannerHourFormat : plannerTimeFormat;
    return format.formatRange(plannerClock(start), plannerClock(end));
}

// Selected subjects get distinct colours before the palette repeats.
function plannerCourseColor(code, subjectIds) {
    const codes = [...new Set([...subjectIds].map(id => id.split('-')[0]))].sort();
    return plannerPalette[codes.indexOf(code) % plannerPalette.length];
}

function collectPlannerLessons(subjectIds, customSubjects = []) {
    const lessons = new Map();
    for (const subjectId of subjectIds) {
        const [code, channel] = subjectId.split('-');
        if (!TIMETABLES[code]) continue;
        const course = COURSES[code] || { name: TIMETABLES[code].subject };
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
                        name: course.name, shortName: course.shortName || course.name, abbr: course.abbr || course.shortName || course.name,
                        start, end, dayIndex, room, roomFull: rooms.join(', '),
                        color: plannerCourseColor(code, subjectIds), href: `#${code}`,
                        cancelled: slot.cancelled === true,
                        alerts: course.alerts?.[channel]?.[day],
                    });
                }
            }
        }
    }
    for (const subject of customSubjects) {
        subject.lessons.forEach((lesson, index) => lessons.set(`${subject.id}-${index}`, {
            name: subject.name, shortName: subject.shortName || subject.name, abbr: subject.abbr || subject.shortName || subject.name,
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

// Start fitted, then add only the width missing from overlapping acronyms.
function fitPlannerWeek(week) {
    week.style.removeProperty('--planner-min-width');
    if (!week.clientWidth) return;
    const axisWidth = week.querySelector('.planner-time-axis').offsetWidth;
    const expansion = Math.max(0, ...[...week.querySelectorAll('.planner-lesson:has(.planner-warning-icon) .planner-lesson-abbr')]
        .map(abbr => (abbr.scrollWidth - abbr.clientWidth) / (abbr.parentElement.offsetWidth + 4)));
    if (expansion) week.style.setProperty('--planner-min-width', `${Math.ceil(week.clientWidth + (week.clientWidth - axisWidth) * expansion)}px`);
}

function createTimetablePlanner(root) {
    const find = id => root.querySelector(`[data-planner="${id}"]`);
    let plannerLessons = [], plannerDay = Math.max(0, plannerToday);
    const weekFormat = new Intl.DateTimeFormat(plannerLocale, { day: 'numeric', month: 'long', year: 'numeric' });
    find('plannerWeekRange').textContent = weekFormat.formatRange(plannerDates[0], plannerDates[4]);

    function plannerLesson(lesson, weekly = false) {
        const link = plannerElement('a', `planner-lesson${lesson.cancelled ? ' planner-lesson--cancelled' : ''}`);
        if (weekly && lesson.end - lesson.start <= 60) link.classList.add('planner-lesson--short');
        link.href = lesson.href;
        link.style.setProperty('--lesson-color', lesson.color);
        const time = plannerElement('span', 'planner-lesson-time', plannerTimeRange(lesson.start, lesson.end, weekly && lesson.end - lesson.start <= 60));
        const name = plannerElement('strong', 'planner-lesson-name', weekly ? lesson.shortName : lesson.name);
        const room = plannerElement('span', 'planner-lesson-room', (weekly ? lesson.room : lesson.roomFull || lesson.room) || plannerLabels.roomPending);
        room.hidden = weekly && lesson.end - lesson.start <= 60 && !lesson.room;
        link.append(time, name, room);
        if (weekly) link.append(plannerElement('strong', 'planner-lesson-abbr', lesson.abbr));
        if (lesson.cancelled) link.append(plannerElement('span', 'planner-lesson-notice', plannerLabels.cancelled));
        if (lesson.alerts) link.append(plannerElement('span', 'planner-lesson-notice', plannerLabels.alerts));
        if (lesson.overlap && weekly) {
            const warning = plannerElement('i', 'fa-solid fa-triangle-exclamation planner-warning-icon');
            warning.setAttribute('aria-hidden', 'true');
            time.append(warning);
        }
        if (weekly) {
            link.title = [lesson.name, lesson.roomFull].filter(Boolean).join(' · ');
            link.setAttribute('aria-label', [plannerDays[lesson.dayIndex], time.textContent, lesson.name,
                room.textContent, lesson.cancelled && plannerLabels.cancelled, lesson.overlap && plannerLabels.overlap].filter(Boolean).join(' · '));
        }
        return link;
    }

    function renderPlannerWeek() {
        const week = find('plannerWeek');
        week.replaceChildren();
        if (!plannerLessons.length) return;
        const start = Math.floor(Math.min(...plannerLessons.map(lesson => lesson.start)) / 60) * 60;
        const end = Math.ceil(Math.max(...plannerLessons.map(lesson => lesson.end)) / 60) * 60;
        week.style.setProperty('--planner-hours', (end - start) / 60);
        const lanes = Array.from({ length: 5 }, (_, day) => Math.max(1, ...plannerLessons.filter(lesson => lesson.dayIndex === day).map(lesson => lesson.lanes)));
        week.style.setProperty('--planner-lanes', lanes.reduce((sum, count) => sum + count, 0));
        week.style.setProperty('--planner-columns', lanes.map(count => `minmax(0, ${count}fr)`).join(' '));
        find('plannerWeekHint').hidden = !plannerLessons.some(lesson => lesson.overlap);
        week.append(plannerElement('div', 'planner-week-corner', ''));
        plannerDays.forEach((day, index) => {
            const heading = plannerElement('div', 'planner-week-heading');
            heading.append(plannerElement('span', 'planner-day-full', day), plannerElement('span', 'planner-day-short', plannerDayShorts[index]),
                plannerElement('span', 'planner-week-date', plannerShortDate(plannerDates[index])));
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
        fitPlannerWeek(week);
    }

    // Days sit side by side in a scroll-snapped track, so swipes follow the finger like phone home screens.
    function renderPlannerDays() {
        find('plannerDaySchedule').replaceChildren(...plannerDays.map((_, day) => plannerDayPage(day)));
        setPlannerDay(plannerDay, 'instant');
    }

    function setPlannerDay(day, behavior) {
        const schedule = find('plannerDaySchedule');
        showPlannerDay(day);
        schedule.scrollTo({ left: day * schedule.clientWidth, behavior });
    }

    function showPlannerDay(day) {
        plannerDay = day;
        for (const button of root.querySelectorAll('[data-planner-day]')) {
            const selected = Number(button.dataset.plannerDay) === day;
            button.setAttribute('aria-pressed', String(selected));
            button.tabIndex = selected ? 0 : -1;
        }
        [...find('plannerDaySchedule').children].forEach((page, index) => page.inert = index !== day);
    }

    function plannerDayScroll(event) {
        if (!event.target.clientWidth) return;
        const day = Math.round(event.target.scrollLeft / event.target.clientWidth);
        if (day !== plannerDay) showPlannerDay(day);
    }

    function plannerDayPage(day) {
        const schedule = plannerElement('section', 'planner-day-page');
        const heading = `${plannerDays[day]} ${plannerDateFormat.format(plannerDates[day])}`;
        schedule.append(plannerElement('h3', 'planner-day-heading', day === plannerToday ? `${plannerLabels.today} · ${heading}` : heading));
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
        return schedule;
    }

    const plannerSmallScreen = matchMedia('(max-width: 760px)');
    const plannerViewStorageKey = () => `plannerView-${plannerSmallScreen.matches ? 'mobile' : 'desktop'}`;

    function applyPlannerView() {
        setPlannerView(localStorage.getItem(plannerViewStorageKey()) || (plannerSmallScreen.matches ? 'agenda' : 'week'));
    }

    function initPlannerPreferences() {
        find('plannerTimeFormat').value = localStorage.getItem('plannerTimeFormat') || 'auto';
        applyPlannerView();
        plannerSmallScreen.addEventListener('change', applyPlannerView);
    }

    function setPlannerView(view) {
        root.dataset.view = view;
        localStorage.setItem(plannerViewStorageKey(), view);
        for (const button of root.querySelectorAll('[data-planner-view]')) {
            button.setAttribute('aria-pressed', String(button.dataset.plannerView === view));
        }
        if (view === 'agenda') setPlannerDay(plannerDay, 'instant');
        if (view === 'week' && plannerLessons.length) fitPlannerWeek(find('plannerWeek'));
    }

    function stepPlannerDay(step) {
        setPlannerDay((plannerDay + step + 5) % 5);
        root.querySelector(`[data-planner-day="${plannerDay}"]`).focus();
    }

    function render(lessons, count) {
        plannerLessons = lessons;
        for (let day = 0; day < 5; day++) layoutPlannerDay(plannerLessons.filter(lesson => lesson.dayIndex === day));
        const summary = [plannerLabels.subjectCount.replace('%n', count), plannerLabels.lessonCount.replace('%n', plannerLessons.length)];
        if (plannerLessons.some(lesson => lesson.overlap)) summary.push(plannerLabels.overlap);
        find('plannerSummary').textContent = count ? summary.join(' · ') : '';
        root.querySelector('.planner-view-switch').hidden = !plannerLessons.length;
        find('plannerLessonTip').hidden = !plannerLessons.length;
        find('plannerSchedule').hidden = !plannerLessons.length;
        find('plannerUnscheduled').hidden = plannerLessons.length > 0;
        const days = find('plannerDays');
        days.replaceChildren();
        plannerDayShorts.forEach((day, index) => {
            const button = plannerElement('button', 'planner-day-button', day);
            button.type = 'button';
            button.dataset.plannerDay = index;
            button.setAttribute('aria-label', `${plannerDays[index]}, ${plannerDateFormat.format(plannerDates[index])}${index === plannerToday ? `, ${plannerLabels.today}` : ''}`);
            if (index === plannerToday) button.setAttribute('aria-current', 'date');
            button.append(plannerElement('span', '', plannerShortDate(plannerDates[index])));
            button.addEventListener('click', () => setPlannerDay(index));
            days.append(button);
        });
        renderPlannerWeek();
        renderPlannerDays();
    }

    // Arrow keys move between days.
    function plannerDaysKeydown(event) {
        const step = { ArrowLeft: -1, ArrowRight: 1 }[event.key];
        if (!step) return;
        event.preventDefault();
        stepPlannerDay(step);
    }

    root.querySelectorAll('[data-planner-view]').forEach(button => {
        button.addEventListener('click', () => setPlannerView(button.dataset.plannerView));
    });
    find('plannerTimeFormat').addEventListener('change', event => setPlannerTimeFormat(event.target.value));
    find('plannerDays').addEventListener('keydown', plannerDaysKeydown);
    const track = find('plannerDaySchedule');
    track.addEventListener('scroll', plannerDayScroll);
    let trackWidth = 0;
    const weekScroll = root.querySelector('.planner-week-scroll');
    let weekWidth = 0;
    const resizeObserver = new ResizeObserver(() => {
        if (track.clientWidth && track.clientWidth !== trackWidth) {
            trackWidth = track.clientWidth;
            setPlannerDay(plannerDay, 'instant');
        }
        if (weekScroll.clientWidth && weekScroll.clientWidth !== weekWidth && plannerLessons.length) {
            weekWidth = weekScroll.clientWidth;
            fitPlannerWeek(find('plannerWeek'));
        }
    });
    resizeObserver.observe(track);
    resizeObserver.observe(weekScroll);
    initPlannerPreferences();
    const planner = {
        render,
        refreshTimeFormat() {
            find('plannerTimeFormat').value = localStorage.getItem('plannerTimeFormat') || 'auto';
            renderPlannerWeek();
            renderPlannerDays();
        },
    };
    timetablePlanners.push(planner);
    return planner;
}
