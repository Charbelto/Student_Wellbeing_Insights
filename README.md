Student_Wellbeing_Insights

# Notes
# Possible types of data university would collect:
  - Surveys for well being
    - Survey example:
      - Rating 1 - 5 (1 - Strongly Disagree, 2 - Disagree, 3 - Neutral, 4 - Agree, 5 - Stronly Agree)
      - The course is engaging
      - I feel supported in my career prospects
      - I feel encouraged to ask questions in class
  - Lecture attendance
  - Coursework submission
  - Student contribution
  - Extra-curricular classes, e.g. societies
  - Gym/sports attendance

# User Requirements
  - CRUD - create, read, update, and delete
    - create new entry into tables - new possible data from data types above
    - read different type of data
    - update different fields
    - delete entries

  - create graphs and diagrams from the data
  - show analytics
    - average: 
      - attendance per student
      - average amount of times students with a membership attend the gym per week
      - proportion of students going to the university gym vs not
      
    - attendance rate throughout the term (week 1 to week 10) - bar

    - average stress level throughout the term (week 1 to week 10) - line

      This stat would show if stress increasing correlates with students attending less lectures. University could use this information to implement something that helps destress students later in the semester or to provide extra support and encourage students to attend their lectures later into the term.

    - based on module feedback spreadsheet, create an average rating for each student. 
	    > engaging_content,
	    > comfortable_asking_questions,
	    > pace_rating,
	    > prepared_for_exams
	    take these four stats and create an average, compare this to other metrics, for example avg_stress from risk indicators

    - average commute time vs avg_stress- scatter

      See if there is a correlation between commuting and stress, maybe offer students free bus passes or something to help reduce their commute times.

    - types of commutes vs avg_stress

      MAYBE ADD A TYPE OF COMMUTE TO SPREADSHEET

      For example, the university could use this info to encourage students to walk or use a bicycle more, if the data correlates with this.

    - average screen time vs extracurricular p/w - if there is negative correlation, the university could encourage more students to engage with more extracurriculars, maybe reference an article that mentions increased social media usage with negative mental health

    - semester vs mark vs difference between deadline and submitted datetime. - 3x scatter overlayed (mark vs difference in time for each semester)

      This would help the university understand if, as the year goes on, people are submitting assignments closer to the deadline and how this reflects on the mark they achieved. Possibly compare this to stress level. Maybe we can assume that a lower mark increases a student's stress level, unsure if we would need a reference for this.

    - degree vs module feedback average

      University could use this to help target groups of students that may be under more stress and feel less satisfied by their course.

    - hours outside class vs mark achieved

      Help the university to understand if there's a correlation between mark achieved and hours spent individually revising. Possible plan of action, encourage students to study more.

    - mark vs module feedback average

      University could use this to help support staff in providing better and more engaging lecture sessions, which in turn benefits the students who would feel more satisfied with their course.

    - certain stats we could further break down into UK vs Europe vs International, this would allow the university to target groups that need more support, for example, international students may have a higher stress level and may go home a lot less frequently, so the university could provide additional support to these students. 
        
    
# SQL Code Notes
- average attendance at different time intervals, make a graph from this data, does a later start time result in a higher attendance?
- percentage of students showing signs of high stress
- hours slept vs stress level
- hours slept vs mood level
- week number vs stress level
- difficulty level vs attendance vs lecture start time
    - This would help identify if the difficulty of a module influences the attendance rate at different times of the day. Are students more likely to attend a class later in the day?

