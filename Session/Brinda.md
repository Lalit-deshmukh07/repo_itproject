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