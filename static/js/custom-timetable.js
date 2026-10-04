/* Subject management stays separate from the shared calendar renderer. */
let customPlanner;

function renderPlanner(customSubjects) {
    const subjectIds = [...selectedSubjects].filter(id => pageDegreeSubjects.has(id.split('-')[0]));
    const count = subjectIds.filter(id => getSubjectButtons(id).length).length + customSubjects.length;
    document.getElementById('plannerTeachingDetails').hidden = selectedSubjects.size === 0;
    document.querySelector('#customSubjectsDetails > h2').hidden = selectedSubjects.size > 0;
    customPlanner.render(collectPlannerLessons(subjectIds, customSubjects), count);
    document.getElementById('plannerPickerCount').textContent = plannerLabels.subjectCount.replace('%n', selectedSubjects.size);
    const bothChannels = [...selectedSubjects].filter(id => id.endsWith('-1') && selectedSubjects.has(id.replace(/-1$/, '-2')))
        .map(id => COURSES[id.split('-')[0]]?.name).filter(Boolean);
    const channelWarning = document.getElementById('plannerChannelWarning');
    channelWarning.hidden = !bothChannels.length;
    channelWarning.lastChild.textContent = plannerLabels.bothChannels.replace('%s', bothChannels.join(', '));
    document.getElementById('plannerEmpty').hidden = count > 0;
    document.getElementById('plannerManageButton').hidden = count === 0;
    document.querySelector('.planner-calendar-footer').hidden = count === 0;
    document.getElementById('plannerUnscheduled').hidden ||= count === 0;
    if (document.getElementById('subjsPopUp').open) filterSubjects(document.getElementById('subjsSearch').value);
}

// Abbreviations are optional when creating a course; imports retain their explicit names.
function customSubjectNames(name, shortName, abbr) {
    name = name.trim();
    return {
        name,
        shortName: shortName.trim() || name,
        abbr: (abbr.trim() || name.split(/\s+/).map(word => word[0]).join('').slice(0, 12)).toUpperCase(),
    };
}
