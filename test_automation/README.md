Current Capabilities
====================
 - Runs Test Cases (which are collectively formed into Use Cases) for Search, Batch Jobs, Build Server and   Reports Tabs 
 - Runs on browsers (Firefox, Chrome)
 - Each Use Case launches a new browser and executes the steps. Methods in a Use Case denote a “Test Case”.
 - Results are logged in report output with Green indicating 'Pass' and Red as 'Failed'.
 - Tests run on Windows as well as Linux (RHEL)
 - Use Cases can be run as a Test Suite 

Front End Testing -
 - Automation covers tests for all the Functionalities of AutoPort tool from the GUI perspective. 

Back End Testing -
 - Server Side Testing i.e. testing for responses, or API testing is not covered as part of Automation.


Dependencies
============
1. Java (1.7)
-  Install Java (JDK + JRE). Java will be used as a programming language to write tests in Selenium.
2. Eclipse (Luna 4.x)
- Configure build path in Eclipse to include jars for Selenium. Eclipse is used as an IDE to automate and run test cases.
3. Selenium WebDriver (2.47)
-  Extract the contents from the zip folder for Selenium 2.47.0. Selenium is used as an automation tool.
4. TestNG (6.8)
-  Testing Framework is used to automate tests in Selenium. TestNG is available as a plugin in Eclipse.


Setup 
=====
To run Automation -

1. Using IDE :
- Import project ‘test_automation’ to the IDE workspace.
- Reload Library Files : Right click ‘test_automation’ project, Build Path -> Configure Build Path -> Add External Jars.
- Navigate to the ‘library_files’ folder and select all files.
- On Package Explorer, edit ‘test_automation’-> ‘testng.xml’ file to configure for browsers and test cases to run.
- Right click ‘testng.xml’, select 'Run As' -> ‘TestNG Suite’.
- Test cases listed in the Testng.xml will run for the browser selected.

2. Using command prompt:
<TBD>

To view Results –

1. Using IDE :
- Automation test results are stored in a result file. 
- On the Package Explorer, open  'Test Output' -> ‘index.html’ in (Web Browser)	 format
- Test Case wise results are available. Green indicates 'PASS' and Red indicates 'FAIL'.

2. Using Command prompt:
<TBD>
