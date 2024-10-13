---
title: RPC Assistant
weight: 2
bookToc: false
---

# RPC Assistant

<style>
    :root {
        --text-color: #333333;
        --item-bg-color: #f0f0f0;
        --result-bg-color: #f9f9f9;
        --result-border-color: #e0e0e0;
        --coverage-bg-color: #ddeffe;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --text-color: #e0e0e0;
            --item-bg-color: #1e1e1e;
            --result-bg-color: #1e1e1e;
            --result-border-color: #333333;
            --coverage-bg-color: #555555;
        }
    }
    #courseSelection {
        max-width: 1000px;
    }
    #description {
        margin-bottom: 20px;
        font-style: italic;
    }
    #courseList {
        list-style-type: none;
        padding: 0;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 10px;
        margin-bottom: 20px;
    }
    #courseList li {
        background-color: var(--item-bg-color);
        border-radius: 4px;
        padding: 10px;
        height: auto;
        display: flex;
        align-items: center;
    }
    #courseList li label {
        display: flex;
        align-items: center;
        cursor: pointer;
        height: 100%;
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: var(--text-color);
    }
    #courseList li input[type="checkbox"] {
        margin-right: 10px;
        flex-shrink: 0;
    }
    .button-container {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 20px;
        max-width: 1000px;
    }
    button {
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
    }
    .primary-button {
        background-color: #2196f3;
        color: white;
    }
    .primary-button:hover {
        background-color: #1e88e5;
    }
    .secondary-button {
        background-color: #555555;
        color: white;
    }
    .secondary-button:hover {
        background-color: #444444;
    }
    .tertiary-button {
        background-color: #ff9800;
        color: white;
        padding: 8px 12px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .tertiary-button:hover {
        background-color: #fb8c00;
    }
    #results {
        margin-top: 20px;
    }
    .result-item {
        background-color: var(--result-bg-color);
        border: 1px solid var(--result-border-color);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 8px;
    }
    .result-title {
        font-size: 20px;
        font-weight: bold;
        color: #2196f3;
        margin-bottom: 10px;
    }
    .coverage-info {
        font-size: 16px;
        color: var(--text-color);
        background-color: var(--coverage-bg-color);
        padding: 5px 10px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .covered-courses {
        font-style: italic;
        color: var(--text-color);
        margin-top: 10px;
        padding: 5px 0;
    }
    .exam-list {
        display: none;
        margin-top: 10px;
        padding-left: 20px;
    }
    .exam-list li {
        margin-bottom: 5px;
        word-wrap: break-word;
        overflow-wrap: anywhere;
    }
    .exam-list li.covered {
        font-weight: bold;
        color: #388e3c;
    }
    #searchContainer {
        margin-bottom: 20px;
    }
    #searchInput {
        width: 100%;
        max-width: 1000px;
        padding: 10px;
        font-size: 16px;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    @media (prefers-color-scheme: dark) {
        .exam-list li.covered {
            color: #81c784;
        }
    }
    @media (max-width: 600px) {
        body {
            padding: 5px;
        }
        #courseList {
            grid-template-columns: 1fr;
            justify-items: center;
            padding: 0 10px;
        }
        #courseList li {
            font-size: 16px;
            padding: 10px;
            height: auto;
            min-height: 60px;
            width: calc(100% - 20px);
            max-width: 300px;
        }
        #courseList li label {
            display: flex;
            flex-wrap: nowrap;
            align-items: center;
            white-space: normal;
            overflow: visible;
            text-overflow: clip;
        }
        #courseList li input[type="checkbox"] {
            margin-right: 10px;
            flex-shrink: 0;
        }
        .button-container {
            flex-direction: column;
        }
        .button-container button {
            margin-bottom: 10px;
        }
    }
</style>
</head>
<body>
<p id="description">
    Please select all the "characterising" courses you are interested
    in:
</p>
<div id="searchContainer">
    <input
        type="text"
        id="searchInput"
        placeholder="Search for courses..."
    />
</div>
<div id="courseSelection">
    <ul id="courseList"></ul>
</div>
<div id="results" style="display: none">
    <h2>Top 5 Recommended Combinations:</h2>
    <div id="resultsList"></div>
</div>
<div class="button-container">
    <button
        onclick="calculateResults()"
        class="primary-button"
        id="calculateButton"
    >
        Submit
    </button>
    <button
        onclick="resetSelection()"
        class="secondary-button"
        id="resetButton"
    >
        Clear
    </button>
    <button
        onclick="editSelection()"
        class="primary-button"
        id="editButton"
        style="display: none"
    >
        Edit Selection
    </button>
</div>

<script>
    const data = [
        [
            "RPC in Algorithms",
            [
                "Advanced Algorithms",
                "Computational Complexity",
                "Cryptography",
                "Graph Theory",
                "Network Algorithms",
            ],
        ],
        [
            "RPC in Artificial Intelligence",
            [
                "Advanced Machine Learning",
                "Big Data Computing",
                "Computer Vision",
                "Deep Learning and Applied Artificial Intelligence",
                "Formal Methods for AI-Based Systems Engineering",
                "Natural Language Processing",
            ],
        ],
        [
            "RPC in Computational Models for Systems Design",
            [
                "Automatic Verification of Intelligent Systems",
                "Concurrent Systems",
                "Formal Methods for AI-Based Systems Engineering",
                "Mathematical Logic for Computer Science",
                "Models of Computation",
            ],
        ],
        [
            "RPC in Data Science",
            [
                "Advanced Machine Learning",
                "Big Data Computing",
                "Cloud Computing",
                "Data and Network Security",
                "Foundations of Data Science",
            ],
        ],
        [
            "RPC in Multimedia Computing and Interaction",
            [
                "Advanced Machine Learning",
                "Advanced Software Engineering",
                "Biometric Systems",
                "Computer Vision",
                "Deep Learning and Applied Artificial Intelligence",
                "Human-Computer Interaction on The Web",
                "Multimodal Interaction",
                "Natural Language Processing",
            ],
        ],
        [
            "RPC in Networks",
            [
                "Autonomous Networking",
                "Computer Network Performance",
                "Internet of Things",
                "Network Algorithms",
            ],
        ],
        [
            "RPC in Security",
            [
                "Biometric Systems",
                "Blockchain and Distributed Ledger Technologies",
                "Cryptography",
                "Data and Network Security",
                "Practical Network Defense",
                "Security in Software Applications",
            ],
        ],
        [
            "RPC in Software Engineering",
            [
                "Advanced Algorithms",
                "Advanced Software Engineering",
                "Automatic Verification of Intelligent Systems",
                "Blockchain and Distributed Ledger Technologies",
                "Concurrent Systems",
                "Distributed Systems",
                "Formal Methods for AI-Based Systems Engineering",
                "Security in Software Applications",
            ],
        ],
        [
            "RPC in Systems",
            [
                "Advanced Architectures",
                "Cloud Computing",
                "Concurrent Systems",
                "Distributed Systems",
            ],
        ],
    ];

    const allCourses = [
        ...new Set(data.flatMap(([, courses]) => courses)),
    ].sort();

    let results = [];

    function populateCourseList() {
        const courseList = document.getElementById("courseList");
        allCourses.forEach((course) => {
            const li = document.createElement("li");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.id = course;
            checkbox.name = course;
            checkbox.value = course;

            const label = document.createElement("label");
            label.htmlFor = course;
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(course));

            li.appendChild(label);
            courseList.appendChild(li);
        });
    }

    function getSelectedCourses() {
        return Array.from(
            document.querySelectorAll(
                '#courseList input[type="checkbox"]:checked',
            ),
        ).map((cb) => cb.value);
    }

    function combinations(arr, r) {
        if (r === 1) return arr.map((el) => [el]);
        return arr.flatMap((el, i) =>
            combinations(arr.slice(i + 1), r - 1).map((combo) => [
                el,
                ...combo,
            ]),
        );
    }

    function calculateResults() {
        const selectedCourses = getSelectedCourses();
        const groupCombinations = combinations(data, 2);

        results = groupCombinations.map(([group1, group2]) => {
            const set1 = new Set(group1[1]);
            const set2 = new Set(group2[1]);
            const unionSet = new Set([...set1, ...set2]);
            const coveredCourses = selectedCourses.filter((course) =>
                unionSet.has(course),
            );
            return {
                groups: [group1, group2],
                coverage: coveredCourses.length,
                coveredCourses: coveredCourses,
                allCourses: [...unionSet],
            };
        });

        results.sort((a, b) => b.coverage - a.coverage);

        displayResults(results.slice(0, 5), selectedCourses.length);
        document.getElementById("description").style.display = "none";
        document.getElementById("searchContainer").style.display =
            "none";

        window.scrollTo(0, 0);
    }

    function displayResults(results, totalSelected) {
        const resultsDiv = document.getElementById("results");
        const resultsList = document.getElementById("resultsList");
        resultsList.innerHTML = "";

        results.forEach((result, index) => {
            const resultItem = document.createElement("div");
            resultItem.className = "result-item";
            resultItem.innerHTML = `
            <div class="result-title">${result.groups[0][0]} + ${result.groups[1][0]}</div>
            <div class="coverage-info">Selected courses covered: ${result.coverage}/${totalSelected}</div>
            <p class="covered-courses">Covered courses: ${result.coveredCourses.join(", ")}</p>
            <button class="tertiary-button" onclick="toggleExamList(${index})">Show All Courses</button>
            <ul class="exam-list" id="examList${index}">
                ${result.allCourses
                    .map(
                        (course) => `
                    <li class="${result.coveredCourses.includes(course) ? "covered" : ""}">${course}</li>
                `,
                    )
                    .join("")}
            </ul>
        `;
            resultsList.appendChild(resultItem);
        });

        document.getElementById("courseSelection").style.display =
            "none";
        resultsDiv.style.display = "block";
        document.getElementById("calculateButton").style.display =
            "none";
        document.getElementById("resetButton").style.display = "none";
        document.getElementById("editButton").style.display =
            "inline-block";
    }

    function toggleExamList(index) {
        const examList = document.getElementById(`examList${index}`);
        const button = examList.previousElementSibling;

        const result = results[index];
        const sortedCourses = result.allCourses.slice().sort();

        examList.innerHTML = sortedCourses
            .map(
                (course) => `
                        <li class="${result.coveredCourses.includes(course) ? "covered" : ""}">${course}</li>
                    `,
            )
            .join("");

        examList.style.display =
            examList.style.display === "none" ||
            examList.style.display === ""
                ? "block"
                : "none";
        button.textContent =
            examList.style.display === "block"
                ? "Hide All Courses"
                : "Show All Courses";
    }

    function resetSelection() {
        document
            .querySelectorAll('#courseList input[type="checkbox"]')
            .forEach((checkbox) => (checkbox.checked = false));

        const searchInput = document.getElementById("searchInput");
        searchInput.value = "";
        searchCourses();

        window.scrollTo(0, 0);
    }

    function editSelection() {
        document.getElementById("results").style.display = "none";
        document.getElementById("courseSelection").style.display =
            "block";
        document.getElementById("calculateButton").style.display =
            "inline-block";
        document.getElementById("resetButton").style.display =
            "inline-block";
        document.getElementById("editButton").style.display = "none";
        document.getElementById("description").style.display = "block";
        document.getElementById("searchContainer").style.display =
            "block";
    }

    function populateCourseList() {
        const courseList = document.getElementById("courseList");
        allCourses.forEach((course) => {
            const li = document.createElement("li");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.id = course;
            checkbox.name = course;
            checkbox.value = course;

            const label = document.createElement("label");
            label.htmlFor = course;
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(course));

            li.appendChild(label);
            courseList.appendChild(li);
        });
    }

    function searchCourses() {
        const searchInput = document.getElementById("searchInput");
        const filter = searchInput.value.toLowerCase();
        const courseItems = document.querySelectorAll("#courseList li");

        courseItems.forEach((item) => {
            const text = item.textContent || item.innerText;
            if (text.toLowerCase().indexOf(filter) > -1) {
                item.style.display = "";
            } else {
                item.style.display = "none";
            }
        });
    }

    window.onload = function () {
        populateCourseList();
        document
            .getElementById("searchInput")
            .addEventListener("keyup", searchCourses);
    };
</script>
