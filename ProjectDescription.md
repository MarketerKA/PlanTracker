Application for day planning, activity tracking and automatic/manual time tracking with integration of external services.
Functional requirements
1. Manually enter the time of activities (including future activities).
2. Timer with Start/Pause/Stop/Save buttons to record activities in the real time.
3. Support for multiple users.
4. Ability to add custom tags to activities.
5. Ability to add multiple tags to a single activity.
6. Registration with email validation.
7. Filter records by tags, date and recorded time.
8. Pagination of the list of records (no more than 15 records per page).
9. Integration with Telegram Bot API for notifications about current activity.


Quality attributes
1. Maintainability
Testability:
Test coverage ≥ 70% (unit + E2E, pytest + Selenium).
Analysability:
Flake8 without warning.
SonarCloud: Grade A in all categories (Bugs, Vulnerabilities, Hotspots, Code Smells).
Reusability:
Documentation of API (OpenAPI) and general system architecture.
2. Reliability
Availability:
99.0% uptime (monitored via uptimerobot).
Rollback to previous version ≤ 10 minutes via CI/CD pipeline
3. Performance
Time Behavior:
Average API response time ≤ 500 ms, and no more than 2.5 seconds during load testing (k6 testing for 1 hour and 500 concurrent users).
4. Security
Accountability:
Every recorded activity must be unambiguously traceable to the user and be private.
SonarCloud: 0 High/Medium vulnerabilities.
All confidential data (e.g. passwords) should be stored in an encrypted state.
5. Usability
User Error Protection:
Confirmation of record deletion.
Confirmation of timer stop.

CI/CD
GitHub Actions Pipeline:
1. Build: Install dependencies; Build the Docker image.
2. Testing: Linting (Flake8), Unit tests (pytest, coverage ≥ 70%).
3. Security: SonarCloud scans.
4. Deploy: Automatic deploy on successful testing.