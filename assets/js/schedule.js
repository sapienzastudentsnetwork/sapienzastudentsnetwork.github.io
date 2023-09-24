function fillTimetables(timetablesContainerId, schedule, subjects) {
    const COLORS = ['red', 'yellow', 'green', 'blue', 'purple', 'orange', 'emerald', 'cyan', 'fuchsia', 'teal']

    let classesStartTime = undefined,
        classesEndTime = undefined;

    for (const events of Object.values(schedule))
        for (const { startTime, endTime } of events) {
            classesStartTime = Math.min(classesStartTime, startTime) || startTime;
            classesEndTime = Math.max(classesEndTime, endTime) || endTime;
        }

    let subjectsColors = {}, nextColorIndex = 0;

    const desktopTbody = document.querySelector(`#${timetablesContainerId} .desktop tbody`);
    const mobileTbody = document.querySelector(`#${timetablesContainerId} .mobile tbody`);

    for (let time = classesStartTime; time < classesEndTime; time++) {
        const desktopTimeTd = document.createElement('td');
        desktopTimeTd.classList.add('font-light', 'italic');
        desktopTimeTd.innerHTML = `${time} - ${time + 1}`;

        const desktopTr = document.createElement('tr');
        desktopTr.append(desktopTimeTd);

        const mobileTimeTd = document.createElement('td');
        mobileTimeTd.classList.add('font-light', 'italic');
        mobileTimeTd.innerHTML = `${time} - ${time + 1}`;

        const mobileTr = document.createElement('tr');
        mobileTr.append(mobileTimeTd);

        for (const day of ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']) {
            if (!schedule[day])
                continue;

            const desktopTd = document.createElement('td');
            const mobileTd = document.createElement('td');

            const courses = schedule[day]
                .filter(({ startTime, endTime }) => startTime <= time && endTime > time);

            for (const { code } of courses) {
                desktopCourseLink = document.createElement('a');
                desktopCourseLink.href = `#${code}`
                desktopCourseLink.textContent =
                    subjects[code] ?
                        (
                            subjects[code].shortName ?
                                subjects[code].shortName :
                                subjects[code].name
                        )
                        :
                        code;

                mobileCourseLink = document.createElement('a');
                mobileCourseLink.href = `#${code}`
                mobileCourseLink.textContent =
                    subjects[code] ?
                        (
                            subjects[code].abbr ?
                                subjects[code].abbr :
                                subjects[code].name.substring(0, 2).toUpperCase()
                        )
                        :
                        code;


                desktopTd.append(desktopCourseLink);
                mobileTd.append(mobileCourseLink);

                if (!subjectsColors[code])
                    subjectsColors[code] = COLORS[nextColorIndex++ % COLORS.length];

                desktopCourseLink.classList.add(subjectsColors[code], 'font-bold');
                mobileCourseLink.classList.add(subjectsColors[code], 'font-bold');
            }

            desktopTr.append(desktopTd);
            mobileTr.append(mobileTd);

        }

        desktopTbody.append(desktopTr);
        mobileTbody.append(mobileTr);
    }
}
