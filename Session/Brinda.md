28/04/26
changed the leadership after one of our team member left
cloned the repo to the vision code

30/04/26
setup the README.md 
created a branch
comitted and push
opened pull request
decided on the topic for team project which is creating a website which can help find the restaurants around the Uni for students and staff called WearItRight.

05/05/26
Today we worked on creating personas and identifying target users for the project.

07/05/26
Had a scrum meeting discussed and cleared all the conflicts
Had discussion with the other team members regarding their topics and our topic aswell 
Took suggestions and gave suggestions 
Talked to Rohan regarding their project No ghost job it was a goog idead for project had a suggestion that if they get rejected in the job selection they can adda feature suggesting a job more desirable to their background
Talked to Nithin their project was Fake house detector gave them the suggestion regarding the house if it gets detected fake we can always give suggestions regarding another house which would not be fake.

Q: Which concept (personas / scenarios / user stories / features) was most useful for your project, and why?
For our WearItRight project, personas were the most useful concept because they helped us understand different types of users and their fashion needs. Creating personas like beginners and fashion enthusiasts helped us design features that are practical, user-friendly, and suitable for different levels of fashion knowledge.

Q: What is one assumption about your users that this workshop forced you to challenge?
This workshop made us realize that not all users are highly confident in choosing outfits or using fashion apps. We initially assumed users would already know current fashion trends, but we learned that many users need simple guidance and personalized recommendations rather than complex styling options.

12/05/26
Installed VM virtualBox and installed the Linux operating system
Installed and enabled the OpenSSH server via SSH. Configured FTP services and SCP aswell 

19/05/26
Installed the Nginx web server using sudo apt install nginx -y, started and enabled the service with systemctl so it launches on boot, and verified the installation by accessing the default web page through the VM's IP address.
Created a simple HTML page with "Hello from my Linux Server" in the Nginx document root and confirmed the site loaded successfully in the browser.
I researched major cloud providers with data centers in Germany including AWS eu-central-1 Frankfurt, Microsoft Azure Germany West Central, Google Cloud europe-west3 Frankfurt, and German providers IONOS and Hetzner, noting that blocking parts for adoption include GDPR data residency requirements, Schrems II compliance for US providers, high energy costs, and complex vendor lock-in risks.

21/05/26
I deployed Nginx using Docker Compose with nginx:alpine, configured a bind mount for live HTML editing on port 8080, verified the container with docker compose ps, tested custom content at localhost:8080, fixed a YAML syntax error, and stopped the service with docker compose down.
Checked live Nginx logs using docker compose logs -f web, which showed worker processes starting and HTTP GET requests from 192.168.65.1 returning 304 status codes when accessing localhost.

26/05/26
Presented the WearItRight PPT and walked through key slides/features . Listened to feedback and took suggestions for improvements on our project. Asked questions and gave suggestions to the other team/project.
Noted that the architecture and API models for some other projects were the same as ours — possible areas for reuse/collaboration.
Document common architecture + API models to identify shared components. Follow up on suggestions received for WearItRight v2. Sync with other team on overlapping tech stack.

28/05/26
complete Part 0-1 MVC scaffold
Built  folder structure with backend/frontend split. Implemented FastAPI MVC: main, schemas, controller, service layers. Added React View with API service + task list component. Configured docker-compose + Dockerfiles for both services

02/06/26
Frontend React + Backend FastAPI both running via Docker compose. UI renders correctly at localhost:3000 with input field and Add button. Edit, Save, Delete buttons display and respond to clicks. Clicking an item toggles Edit mode and applies strikethrough/cross-off effect. Clicking the checkbox also triggers cross-off, confirming frontend-backend data flow works.

04/06/26
Updated the UI styling for a cleaner look and pushed the full MVC repo to GitHub. Frontend and backend both run via Docker, and the interface now renders with Add, Edit, Save, Delete buttons plus checkbox cross-off working end-to-end.

09/06/26
Stand up the new stack: Error is backend failed to connect to PostgreSQL on startup.sqlalchemy.exc.OperationalError: connection refused in backend logs. I fixed it by Ensuring Postgres container was healthy and DATABASE_URL matched docker-compose.yml config.docker compose up --build runs, /db-ping returns Postgres version.

11/06/26
Convert to SQLAlchemy: The error was AttributeError or Table 'tasks' doesn't exist when running CRUD operations. sqlalchemy.exc.ProgrammingError: relation "tasks" does not exist after implementing models. I Fixed by creating SQLAlchemy Task model inheriting from Base, ran Base.metadata.create_all(bind=engine) to generate tables.

16/06/26
User and a one-to-many relationship: The error was Task creation failed with ForeignKeyViolation because owner_id referenced non-existent users. psycopg2.errors.ForeignKeyViolation: Key (owner_id)=(99) is not present in table "users" appeared in docker-compose logs backend. This was fixed by adding User model with relationship to Task, seeded a default user, and validated owner_id exists before inserting tasks.

18/06/26
Replace create_all with Alembic: Error was Schema changes failed to apply after model updates because Base.metadata.create_all() was removed and migrations were not initialized. alembic.util.exc.CommandError: Can't locate revision identified by 'head' and sqlalchemy.exc.ProgrammingError: column "created_at" does not exist appeared after adding the new field. Initialized Alembic with alembic init, generated migrations via alembic revision --autogenerate -m "initial", and applied schema changes using alembic upgrade head instead of create_all().

23/06/26
I completed the data migration by manually creating Alembic revision to add a column using the 3-step pattern: add nullable, backfill existing users with, then alter to NOT NULL. The main errors were the migration file being created inside Docker where VSCode couldn't see it, and the hashes initially saving as 61 chars due to a hidden character that we fixed with . The migration now runs successfully with  and all users have valid 60-character bcrypt hashes, completing Exercise 1.

25/06/26
Built, updated to check token in, added logout. Tested with  / . I had multiple issues after writing code. Frontend ran on port 3000 not 5173. Deleted old code before rewriting new . Used port 3000 and verified login works.

30/06/26
Protected Routes + Authorization: Unauthenticated requests could access /tasks and any logged-in user could view/delete tasks belonging to other users due to missing JWT enforcement and ownership checks. GET /tasks returned 200 OK without a token, and DELETE /tasks/5 returned 204 No Content for a task where owner_id != current_user.id. I Added get_current_user dependency to all routes to enforce JWT auth, moved ownership logic to TaskService to filter by current_user.id, and raised HTTPException(403) when users accessed tasks they didn’t own.

02/07/26
Test Infrastructure: Initial test runs failed with ModuleNotFoundError: No module named 'app' and database connection errors because no isolated test environment existed. pytest -v showed FAILED tests/test_smoke.py::test_client_fixture_wires_alice_as_current_user - sqlite3.OperationalError: no such table: users before fixtures were configured. I Added pytest, httpx to requirements.txt, created in-memory SQLite fixtures db_session, alice, and client with dependency overrides for get_db and get_current_user, then verified with a passing smoke test. Testing infrastructure was started in class and a quiz on authentication was given.