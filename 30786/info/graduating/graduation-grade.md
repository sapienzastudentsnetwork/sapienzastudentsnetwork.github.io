---
title: Graduation Grade
---
# Calculation of Graduation Grade

{{% hint warning %}}
<i class="fa-solid fa-triangle-exclamation" style="color: #FFD43B;"></i> **Warning**

This page is based on the guidelines in effect as per the CAD meeting minutes of 06/22/2016.
{{% /hint %}}

The graduation grade is decided by the Graduation Committee based on the final exam, the evaluators' judgment, and the candidate's curriculum. The grade is expressed out of 110 and is calculated as follows:

## Weighted Average

The weighted average of exam grades is expressed out of 110. The formula to calculate the weighted average is:

$$
\text{Weighted Average} = \frac{\sum (\text{Exam Grade} \times \text{CFU})}{\sum \text{CFU}}
$$

Where:
- \(\text{Exam Grade}\) is the grade obtained in each exam
- \(\text{CFU}\) is the number of European Credit Transfer and Accumulation System credits associated with each exam

## Increment for the Bachelor's Degree in Applied Computer Science and Artificial Intelligence

The maximum increment is 13 points. The Committee can add points to the weighted average according to the following criteria:

1. **Evaluation of the Internship Report**: from 0 to 9 points;
2. **Duration of the Study Program**:
   - 3 points if you graduate within the legal duration of the program (so at most during the last graduation session, which is usually in December);
   - 2 points if you graduate by March after the legal duration of the program;
   - 1 point if you graduate within the first year beyond the legal duration;
3. **Exam Average**: 1 point if your weighted average is at least 27/30;
4. **Honors or Erasmus**: 1 point if you have obtained at least 3 honors or participated in an Erasmus program;

## Graduation Grade

{{< graduationCalculator 
    id="englishCalculator"
    title="Weighted Average"
    placeholder="Enter your average (max 30)"
    checkboxLabel="I have obtained at least three honors (30L) or participated in Erasmus"
    durationLabel="Study Duration"
    resultLabel="Presentation Score"
    durations=`[
        {"label": "Graduation within regular duration (3 years)", "bonus": 3},
        {"label": "Graduation by March after regular duration", "bonus": 2},
        {"label": "Graduation within first year after regular duration", "bonus": 1},
        {"label": "Graduation beyond first extra year", "bonus": 0}
    ]`
>}}

## Part-Time Students

For part-time students, the criterion related to the legal duration of the program applies only if they were still within the legal duration at the time of choosing part-time status.

## Final Grade with Honors

The Committee may decide to award honors (110 cum laude) to recognize outstanding achievements. This decision must be unanimous by the Committee.

## Calculation Example

Suppose you have a weighted average of 102/110 and you meet the following criteria for the Bachelor's Degree in Applied Computer Science and Artificial Intelligence:

- Evaluation of the internship report: 8 points
- Graduation within the legal duration of the program: 3 points
- Exam average of at least 27/30: 1 point

Your graduation grade will be:

$$
102 + 8 + 3 + 1 = 114
$$

Since the maximum grade is 110, your final grade will be 110, and the Committee may decide to award you honors.

We hope this information helps you understand how your graduation grade is calculated. Good luck!
