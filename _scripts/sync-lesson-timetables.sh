#!/bin/bash

rm ../data/timetables.json

declare -a degree_programme_codes=("33503" "33508" "33516" "33519" "33502")
academic_year="2025/2026"
semester="secondo"

for ((i=0; i<${#degree_programme_codes[@]}; i++)); do
    export DEGREE_PROGRAMME_CODE="${degree_programme_codes[i]}"
    export ACADEMIC_YEAR="${academic_year}"
    export SEMESTER="${semester}"

    python scrape-degree-programme-timetables.py

    unset DEGREE_PROGRAMME_CODE
    unset ACADEMIC_YEAR
    unset SEMESTER
done