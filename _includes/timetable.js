const COURSES = JSON.parse(`{{ site.data.courses | jsonify }}`);
const SCHEDULES = JSON.parse(`{{ site.data.schedules | jsonify }}`);
const COLORS = ['red', 'yellow', 'green', 'blue', 'purple', 'orange', 'emerald', 'cyan', 'fuchsia', 'teal'];
const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

function fillTimetable(tableId, coursesCodes, channel) {
    let classesStartTime = undefined,
        classesEndTime = undefined;

    const schedule = Object.fromEntries(DAYS.map(day => [day, []]))

    for (const course of coursesCodes) {
        const [courseCode, _channel] = course.toString().split('-')

        const days = SCHEDULES[courseCode]['channels'][_channel || channel] || []
        for (const [day, { hours }] of Object.entries(days)) {
            // In custom schedule we have to specify the channel with a - (dash)
            const [startTime, endTime] = hours.split('-').map(time => parseInt(time))
            schedule[day].push({ courseCode: courseCode, startTime, endTime });

            classesStartTime = Math.min(classesStartTime, startTime) || startTime;
            classesEndTime = Math.max(classesEndTime, endTime) || endTime;
        }
    }

    let subjectsColors = {}, nextColorIndex = 0;

    const desktopTbody = document.querySelector(`#${tableId} tbody.desktop`);
    const mobileTbody = document.querySelector(`#${tableId} tbody.mobile`);

    desktopTbody.innerHTML = '';
    mobileTbody.innerHTML = '';

    for (let time = classesStartTime; time < classesEndTime; time++) {
        const timeTd = document.createElement('td');
        timeTd.classList.add('font-light', 'italic');
        timeTd.innerHTML = `${time} - ${time + 1}`;

        const desktopTr = document.createElement('tr');
        desktopTr.append(timeTd);

        const mobileTr = document.createElement('tr');
        mobileTr.append(timeTd.cloneNode(true));

        for (const day of DAYS) {
            if (!schedule[day])
                continue;

            const desktopTd = document.createElement('td');
            const mobileTd = document.createElement('td');

            const courses = schedule[day]
                .filter(({ startTime, endTime }) => startTime <= time && endTime > time);

            let hasMoreThanACourse = false;
            for (const { courseCode } of courses) {
                const course = COURSES[courseCode];

                desktopCourseLink = document.createElement('a');
                if (!subjectsColors[courseCode])
                    subjectsColors[courseCode] = COLORS[nextColorIndex++ % COLORS.length];

                desktopCourseLink.classList.add(subjectsColors[courseCode], 'font-bold');
                desktopCourseLink.href = `#${courseCode}`
                desktopCourseLink.textContent = course ?
                    course.shortName || course.name : courseCode;

                mobileCourseLink = desktopCourseLink.cloneNode(true);
                mobileCourseLink.textContent = course ?
                    course.abbr || course.name.substring(0, 2).toUpperCase() : courseCode;

                if (hasMoreThanACourse) {
                    desktopTd.append(document.createElement('br'));
                    mobileTd.append(document.createElement('br'));
                }

                desktopTd.append(desktopCourseLink);
                mobileTd.append(mobileCourseLink);
                hasMoreThanACourse = true;
            }

            desktopTr.append(desktopTd);
            mobileTr.append(mobileTd);
        }

        desktopTbody.append(desktopTr);
        mobileTbody.append(mobileTr);
    }
}
