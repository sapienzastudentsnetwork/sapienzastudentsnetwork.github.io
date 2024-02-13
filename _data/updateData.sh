#!/bin/bash

rm classrooms.json
rm schedules.json

semester="secondo"
declare -a degree_program_codes=("29923" "30786")
declare -a suffixes=("" "-acsai")

for ((i=0; i<${#degree_program_codes[@]}; i++)); do
    export SEMESTER="${semester}"
    export DEGREEPROGRAMCODE="${degree_program_codes[i]}"
    export SUFFIX="${suffixes[i]}"

    python extract_degree_program_timetables.py

    unset SEMESTER
    unset DEGREEPROGRAMCODE
    unset SUFFIX
done