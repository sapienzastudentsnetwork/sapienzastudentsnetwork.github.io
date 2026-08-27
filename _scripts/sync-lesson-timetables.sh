#!/bin/bash

if [ -f ../data/timetables.json ]; then
    cp ../data/timetables.json ../data/timetables_backup.json
fi

rm -f ../data/timetables.json

declare -a degree_programme_codes=("33503" "33508" "33516" "33519" "33502")
academic_year="2026/2027"
semester="primo"

for ((i=0; i<${#degree_programme_codes[@]}; i++)); do
    export DEGREE_PROGRAMME_CODE="${degree_programme_codes[i]}"
    export ACADEMIC_YEAR="${academic_year}"
    export SEMESTER="${semester}"

    python scrape-degree-programme-timetables.py

    unset DEGREE_PROGRAMME_CODE
    unset ACADEMIC_YEAR
    unset SEMESTER
done

# AIRO: scrape only Machine Learning (10629336) from degree programme 33514.
# TARGET_COURSE_CODES also restricts the corresponding raw JSON output.
export DEGREE_PROGRAMME_CODE="33514"
export ACADEMIC_YEAR="${academic_year}"
export SEMESTER="${semester}"
export TARGET_COURSE_CODES="10629336"

python scrape-degree-programme-timetables.py

unset DEGREE_PROGRAMME_CODE
unset ACADEMIC_YEAR
unset SEMESTER
unset TARGET_COURSE_CODES

rm -f ../data/timetables_backup.json