# RPA Homework
The robot is used to automate the process of Semantic Scholar literature collection for the user-defined topic. Result of the process is an excel with info about each found article.



#### Algorithm 

1. User defines a topic, number of pages, receiver and password of the resulting email
2. Robot creates links for each search results page
3. Robot collects links to the articles from each page
4. Robot scraps article's info and downloads source docs if available
5. Robot writes all info to excel

#### Contents

Write the robot for https://www.semanticscholar.org/ website.

Robot functionality:
* Search articles by specific topic on N pages
* Get title, author, number of citations, article file (if available)

The final git repo should contain the following files:
* readme.md with robot description
* requiremnts.txt
* robot's python script named "main.py"
* folder with downloaded articles
* summary excel with articles info
* link to the video of the running robot (feel free to use [loom](https://www.loom.com/) for recording)
