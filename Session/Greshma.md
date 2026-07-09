**Date: 28th April 2026**

Joined in a group and created the git account and connected it to the VS studio

**Date: 30 April 2026**

Disscussed on the team project
Created the branch

**Date: 5th May 2026**

Worked on different parts assigned to each one. 
Dealed with Part 4 : Feature Identification 

**Date: 7th May 2026**

Had a scrum meeting where the members of the team discussed about the parts they did.
Took feedback from the professor after he reviewed our project
Worked on tbe part-2 scenarios as advised by the professor
Had group discussions with the other group about each other projects and gave suggestions to the others and received suggestions that can be added to our project.

**Questions:**

**Which concept was more useful for your project and why?**

For me it will be the concept of PERSONAS because this is the main source which decides and defines the rest of our project WearItRight. The persona can help us build the scenarios, the user stories and also defines on what features are necessary and which are not.

**What is one assumption about your users that this workshop forced you to challenge?**

**Date:12 May 2026**
Installed VM virtualBox and installed the Linux operating system
Installed and enabled the OpenSSH server via SSH. Configured FTP services and SCP aswell

**Date: 19 May 2026**
Successfully installed and configured SSH, FTP, and SCP services for remote access and secure file transfer. Installed and configured the Nginx web server and deployed a static website, ensuring proper server setup, file permissions, and web accessibility.

**Date: 21 May 2026**
Successfully deployed an Nginx web server using Docker Compose with the lightweight nginx:alpine image. I configured a bind mount to enable live editing of HTML files from the host machine and exposed the service on port 8080. After deploying the container, I verified its status using docker compose ps and tested the website by accessing custom content through localhost:8080. During the setup process, I identified and resolved a YAML syntax error in the Docker Compose configuration. I also monitored the application using docker compose logs -f web, which confirmed the successful startup of Nginx worker processes and recorded HTTP GET requests from 192.168.65.1 returning 304 status codes, indicating proper browser caching behavior. Finally, I managed the container lifecycle by stopping the service using docker compose down. This project strengthened my skills in Docker, Docker Compose, Nginx configuration, web deployment, troubleshooting, and logg analysis.

**Date: 26 May 2026**
Presented the WearItRight project and explained its main features to the class and noted the feedback and suggestions provided by the lecturer and my classmates for future improvements. Also participated in reviewing other teams' projects and observed that some projects shared a similar architecture and API design with ours, which could be useful for future collaboration.

**Date:28 May 2026**
I completed the MVC project scaffold by setting up the frontend and backend folder structure. I implemented the FastAPI MVC architecture, created the React frontend, and configured Docker Compose so both services could run together successfully.

**Date:02 June 2026**
I tested the application after integrating the frontend and backend. I verified that all task operations, including Add, Edit, Save, Delete, and checkbox functionality, were working correctly through Docker Compose.

**Date:04 June 2026**
I improved the user interface by updating the styling to make it cleaner and more organized. After testing the application, I pushed the updated MVC project to GitHub.

**Date:09 June 2026**
I worked on setting up the new project stack. I encountered a PostgreSQL connection issue during startup and resolved it by checking the Docker configuration, verifying the database connection settings, and rebuilding the containers.

**Date:11 June 2026**
I converted the project to use SQLAlchemy ORM. While testing, I found that the required database tables were missing. I created the Task model, generated the database tables, and confirmed that CRUD operations worked correctly.

**Date:16 June 2026**
I implemented the User model and established the one-to-many relationship between users and tasks. I resolved foreign key issues by validating user IDs and ensuring that each task belonged to an existing user.

**Date:18 June 2026**
I replaced the automatic database table creation process with Alembic migrations. I initialized Alembic, generated migration files, and successfully updated the database schema after resolving migration errors.

**Date:23 June 2026**
I completed the required database migration by adding a new column through Alembic. I also resolved issues related to migration files and password hash formatting, ensuring that the migration completed successfully.

**Date:25 June 2026**
I implemented token validation and logout functionality. I fixed issues related to the frontend port configuration and outdated project files before confirming that the login system worked as expected.

**Date:30 June 2026**
I added authentication and authorization to protect application routes. I implemented JWT validation, restricted users to accessing only their own tasks, and added authorization checks to prevent unauthorized actions.

**Date:02 July 2026**
I set up the project's testing environment by configuring pytest with an in-memory SQLite database. After resolving configuration issues, I successfully ran the initial smoke tests and verified that the testing infrastructure was working correctly.

**Date:07 July 2026**
I continued improving the test suite by fixing issues in the service, API, and authorization tests. I updated the repository methods, resolved Pydantic compatibility problems, and implemented proper ownership validation until all authorization tests passed successfully.
