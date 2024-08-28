#!/bin/bash

rm ../data/classrooms.json
rm ../data/schedules.json

declare -a degree_programme_codes=("29923" "29932" "30786")
academic_year="2023/2024"
semester="primo"

for ((i=0; i<${#degree_programme_codes[@]}; i++)); do
    export DEGREE_PROGRAMME_CODE="${degree_programme_codes[i]}"
    export ACADEMIC_YEAR="${academic_year}"
    export SEMESTER="${semester}"

    python scrape-degree-programme-schedules.py

    unset DEGREE_PROGRAMME_CODE
    unset ACADEMIC_YEAR
    unset SEMESTER
done