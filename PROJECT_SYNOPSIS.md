# Project Synopsis: LearnSmart E-Learning Recommendation Portal

## Abstract
LearnSmart is a web-based portal that helps students discover learning resources aligned with their interests, skill level, learning goals and preferred format. Students can create accounts, set preferences, receive ranked recommendations, browse courses and maintain a saved learning list. Administrators can add learning resources to the catalogue.

## Problem statement
Online learning catalogues contain many options, and students may find it difficult to identify relevant beginner or advanced resources. The project provides a simple personalized discovery experience.

## Objectives
1. Build a user-friendly course discovery portal.
2. Collect learning preferences from students.
3. Rank resources using a transparent content-based scoring method.
4. Allow students to save courses and track their status.
5. Provide a basic administrative course-management interface.

## Methodology
The application uses Flask for server-side routes, SQLite for persistent data, Jinja templates for page rendering, and a rule-based scoring algorithm for recommendations. Scores are calculated from subject, level, goal and format matches.

## Modules
- Authentication: registration, login and logout.
- Course catalogue: browse, search and filter.
- Preferences: select subject interests and learning preferences.
- Recommendation engine: score and sort courses.
- Learning list: save courses and update status.
- Administration: add courses to the catalogue.

## Software requirements
Python 3.10+, Flask, SQLite, HTML/CSS, modern browser and VS Code (optional).

## Future scope
Machine-learning ranking, course feedback, learner analytics, verified course metadata, richer progress tracking and external learning-platform integration.

## Conclusion
LearnSmart demonstrates how a web application can combine student profiles, a course catalogue and a transparent recommendation algorithm to make course discovery more focused.
