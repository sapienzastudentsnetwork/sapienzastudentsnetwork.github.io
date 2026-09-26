const GROUP_B_CFU_RCP = 54; // Teachings which are in at least one RCP.
const GROUP_C_CFU_RELATED = 12; // Teachings which are either in at least one RCP or in Related".
const GROUP_D_CFU_ELECTIVE = 12; // Elective teachings.
const GROUP_E_CFU_THESIS = 36; // Thesis.
const GROUP_F_CFU_AFC = 6; // AFC (Attività Fromativa Complementare).

const TEACHING_CFU = 6; // Each teaching has 6 CFU.

function generateStudyPlan(internalTeachings, electiveTeachings, group1, group2) {
	const teachings = new Set();
	const info = {};

	const groupsTeachings = new Set([...group1[1], ...group2[1]]);

	Array.from(internalTeachings)
		.filter((teaching) => groupsTeachings.has(teaching))
		.forEach((teaching) => teachings.add(teaching));

	while (groupsTeachings.difference(teachings).size > 4) {
		const remainingTeachings = Array.from(groupsTeachings.difference(teachings)).sort();
		const teaching = remainingTeachings[0];
		teachings.add(teaching);
		(info[teaching] ??= new Set()).add("RCP_REQUIRED");
	}

	const GROUPS = [
		{
			name: "GROUP_B",
			eligibleTeachings: window.TEACHINGS_RCP,
			targetCfu: GROUP_B_CFU_RCP,
			priority: [
				internalTeachings,
				groupsTeachings
			],
		},
		{
			name: "GROUP_C",
			eligibleTeachings: window.TEACHINGS_ALL,
			targetCfu: GROUP_B_CFU_RCP + GROUP_C_CFU_RELATED,
			priority: [
				window.TEACHINGS_ONLY_IN_RELATED.intersection(internalTeachings),
				internalTeachings,
				groupsTeachings
			],
		},
		{
			name: "GROUP_D",
			eligibleTeachings: window.TEACHINGS_ALL.union(electiveTeachings),
			targetCfu: GROUP_B_CFU_RCP + GROUP_C_CFU_RELATED + GROUP_D_CFU_ELECTIVE,
			priority: [
				electiveTeachings,
				internalTeachings,
				groupsTeachings
			],
		},
	]

	for (const { name, eligibleTeachings, targetCfu, priority } of GROUPS) {
		const eligible =
			Array.from(eligibleTeachings.difference(teachings))
				.sort((teaching1, teaching2) => {
					for (const set of priority) {
						const difference = set.has(teaching2) - set.has(teaching1);
						if (difference !== 0) {
							return difference;
						}
					}

					return teaching1.localeCompare(teaching2);
				});

		for (const teaching of eligible) {
			if (teachings.size * TEACHING_CFU >= targetCfu) {
				break;
			}
			teachings.add(teaching);
			(info[teaching] ??= new Set()).add(name)
		}
	}

	for (const teaching of teachings) {
		if (internalTeachings.has(teaching)) {
			(info[teaching] ??= new Set()).add("SELECTED");

		}

		if (groupsTeachings.has(teaching)) {
			(info[teaching] ??= new Set()).add("RCP");
		}

		if (group1[1].includes(teaching)) {
			(info[teaching] ??= new Set()).add("RCP1");
		}

		if (group2[1].includes(teaching)) {
			(info[teaching] ??= new Set()).add("RCP2");
		}

		if (electiveTeachings.has(teaching)) {
			(info[teaching] ??= new Set()).add("SELECTED");
			(info[teaching] ??= new Set()).add("ELECTIVE");
		}
	}

	/*
	const remainingTeachings = (internalTeachings.union(electiveTeachings)).difference(teachings);
	if (remainingTeachings.size > 0) {
		const teaching = remainingTeachings[0]
		teachings.add(teaching);
		(info[teaching] ??= new Set()).add("AFC");
	}
	*/

	return {
		groups: [group1, group2],
		teachings,
		info,
	};
}

function pairs(elements) {
	const result = [];

	for (let index1 = 0; index1 < elements.length; index1++) {
		for (let index2 = index1 + 1; index2 < elements.length; index2++) {
			result.push([elements[index1], elements[index2]])
		}
	}

	return result;
}

function studyPlanScore(studyPlan) {
	let selectedTeachingsCount = 0;
	let selectedTeachingsInRcpCount = 0;

	for (const teaching of studyPlan.teachings) {
		if (studyPlan.info[teaching].has("SELECTED")) {
			selectedTeachingsCount++;

			if (studyPlan.info[teaching].has("RCP")) {
				selectedTeachingsInRcpCount++;
			}
		}
	}

	return [
		selectedTeachingsCount,
		selectedTeachingsInRcpCount
	]
}

function studyPlanCompareFn(studyPlan1, studyPlan2) {
	for (
		const [entry1, entry2] of
		Iterator.zip([studyPlanScore(studyPlan1), studyPlanScore(studyPlan2)])
	) {
		const difference = entry2 - entry1;
		if (difference !== 0) {
			return difference;
		}
	}

	return 0;
}

function generateStudyPlans(selectedTeachings) {
	const internalTeachings = new Set(
		selectedTeachings
			.filter((teaching) => window.TEACHINGS_ALL.has(teaching))
	);

	const electiveTeachings = new Set(
		selectedTeachings
			.filter((teaching) => !internalTeachings.has(teaching))
	);

	return Array.from(
		pairs(window.RCP_GROUPS).map(
			([group1, group2]) =>
				generateStudyPlan(
					internalTeachings,
					electiveTeachings,
					group1,
					group2
				)
		)
	).sort(studyPlanCompareFn);
}
