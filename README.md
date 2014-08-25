Dependencies
========
Install [pip](https://pip.pypa.io/en/latest/installing.html) and then run these commands to install dependencies:

    pip install Flask
    pip install PyGithub
    pip install requests

Running
========
After installing dependencies, simply clone the repo and run:

    python main.py

Navigate to http://127.0.0.1:5000/ to access the app.

Design Overview
========
Stack
------
The backend runs on python using the Flask microframework. On the front end, bootstrap, rivets.js, jQuery, and a few other libraries are used to acquire and render content.

Data Flow
------
When the client first loads the web app, the backend sends templates/main.html to the client as a response. This file represents the entire clientside of the application and utilizes several CSS and JavaScript files. When the client performs an action such as searching for a new project or clicking the "Add to Jenkins" button, an asynchronous request is made to the backend. The backend responds with JSON data, which is then interpreted and displayed on the clientside.

Backend
------
The backend consists of main.py, which defines endpoints such as /, /search, /detail/<id>, and /createJob. It uses PyGithub to make GitHub api requests. The / route returns main.html, all others return only JSON. Other files such as buildAnalyzer.py and classifiers.py are called upon to perform analysis of repositories.

Frontend
------
main.html defines the structure for the entire application. main.js defines a few state variables that contain data about the various views of the application (loading panel, search results, detail page). Rivets.js is used to bind data from these state variables to HTML. Bootstrap is heavily relied on for styling, icons, and other front end components.

Next Steps
=========
- Provide numeric estimates for project interest (how useful is this package?) and ease of porting (how hard is it to port?)
- Add an option to fork the repository to IBMSOE before creating a Jenkins job
- Make build step inference more modular and robust
- Set up test reporting for well known test suites such as JUnit