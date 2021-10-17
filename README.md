# RPA
The robot is used to automate the process of Semantic Scholar literature collection for the user-defined topic. Result of the process is an email with attached excel with info about each found article.

Used libraries
selenium - web-browser automation
pandas - work with datatables
smtplib - email creating and sending
re - Regular expression operations
Algorithm
User defines a topic, number of pages, receiver and password of the resulting email
Robot creates links for each search results page
Robot collects links to the articles from each page
Robot scraps article's info and downloads source docs if available
Robot writes all info to excel and sends email
