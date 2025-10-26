# Lenseshot

Lenseshot is a full-film production application that attempts to create a self-contained infrastructure for filmmakers to collaborate, create industry-standard screenplays, work on shotlists, schedules and an array of tools hoping to provide a richer pre-production experience.

#Disclaimer
The app is still in it's early developmental stages with many features still planning to come. 

---

## Features

1. The user can log in and create an account
2. The user can create projects that only the user can access, and then delete or update their listed projects
3. The user can write a screenplay in both English and Arabic formats, save it to the cloud, and delete it.

## Planned Features
 ### Screenplays
 1. Adding pagination logic
 2. Adding export functions to PDF
 3. adding scene-heading numbering

### Development

 1. Adding local environments like the database and storage for development
 2. adding tests

# Notes

The application is split into multiple Dockerized microservices orchestrated by a Docker Compose file. It uses Supabase for database and user auth and Cloudflare R3 for storage. The stack also consists of Flask REST API for the backend and React/Vite for the frontend. 
