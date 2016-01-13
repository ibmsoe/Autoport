Current Capabilities
====================
 - Runs Test Cases (which are collectively formed into Use Cases) for Search, Batch Jobs, Build Server and Reports Tabs.
 - Runs on browsers (Firefox, Chrome).
 - Each Tab can launch a new browser and execute the steps. Methods in a Use Case denote a “Test Case”.
 - Results are logged in report output with Green indicating 'Pass' and Red as 'Failed'.
 - Tests run on Windows as well as Linux (RHEL).
 - Use Cases can be run as a Test Suite.

Front End Testing -
 - Automation covers tests for all the Functionalities of AutoPort tool from the GUI perspective. 

Back End Testing -
 - Server Side Testing i.e. testing for responses, or API testing is not covered as part of Automation.


Dependencies
============
1. Java (1.7)
 - Install Java (JDK + JRE). Java will be used as a programming language to write tests in Selenium.
2. Eclipse (Luna 4.x) (in case you are using an IDE to run automation)
 - Configure build path in Eclipse to include jars for Selenium. Eclipse is used as an IDE to automate and run test cases.
3. Selenium WebDriver (2.47) 
 - Download latest Selenium driver from the link http://www.seleniumhq.org/download/. This readme document is created with Selenium driver version 2.47.0.
 - Extract the contents from the zip folder for Selenium 2.47.0. Selenium is used as an automation tool.
4. TestNG (6.8)
 - Testing Framework is used to automate tests in Selenium. TestNG is available as a plugin in Eclipse.


Setup 
=====
To run Automation -

1. Using IDE :
 - Import project 'test_automation' to the IDE workspace.
 - Copy folowing library files or jars into test_automation/library_files directory:
 1. all files from selenium2.47/libs directory
 2. selenium-java-2.47.1*.jar (2)files from selenium2.47 directory
 3. opencsv-3.6.jar is available on internet
 - Reload Library Files : Right click 'test_automation' project, Build Path -> Configure Build Path -> Add External Jars.
 - Navigate to the 'library_files' folder and select all files.
 - On Package Explorer, edit 'test_automation'-> '<tab name>.xml' file or 'AllSuites.xml' to run test cases.
 - Right click above xml, select 'Run As' -> 'TestNG Suite'.
 - Edit 'test_automation'-> 'config.properties' to configure data.
 - Test cases listed in the selected xml will run for the browser selected.

2. Using command prompt:
 -Ensure that folowing library files or jars are copied into test_automation/library_files directory.
 1. all files from selenium2.47/libs directory
 2. selenium-java-2.47.1*.jar (2)files from selenium2.47 directory
 3. opencsv-3.6.jar is available on internet
 - Set CLASSPATH variable :
 export CLASSPATH= $CLASSPATH:<path to automation project>/test_automation/bin/:<path to automation project>/test_automation/library_files/*
 - Run the relevant/combined TestNG suite file:
 java org.testng.TestNG batchJobs.xml (OR AllSuites.xml)

To view Results –

1. Using IDE :
 - Automation test results are stored in a result file. 
 - On the Package Explorer, open  'test-output' -> 'index.html' in Web Browser format
 OR 
 - On the console, click on the option 'Open TestNG Report'.
 - Test Case wise results are available. Green indicates 'PASS' and Red indicates 'FAIL'.

2. Using Command prompt:
 - Navigate to test automation folder.
 <path to automation project>/test_automation/test-output
 - Open 'index.html' in Web Browser format.
