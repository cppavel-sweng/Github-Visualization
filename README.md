# Github-Visualization

### Running on your local machine

1. Clone the project
2. Rename [.env_example](https://github.com/cppavel-sweng/Github-Visualization/blob/main/.env_example) to .env and put your Github token in it. 
3. Execute [./run.cmd](https://github.com/cppavel-sweng/Github-Visualization/blob/main/run.cmd). The website will be hosted on localhost:5000. 
4. Execute [./exit.cmd](https://github.com/cppavel-sweng/Github-Visualization/blob/main/exit.cmd), if you would like to stop all containers.

### What it does

I decided to measure the overall metrics for a particular developer. My main idea was to focus not only on code contributions (commits), but also on creating/assigning/closing issues and creating/reviewing pull requests.

The project fetches data from github API for a prompted user handle and visualizes the data in the form of report.

I decided to call such report "type of developer" as it contains metrics that determine the things that developer normally works on.

For example, a developer may have a lot of contributions in C++ and a lot of pull requests and issues they were involved with, so we can deduce they are an Open Source C++ developer.

### Example report and Video Demo

The histograms show the distribution of the data. On the horizontal axis there are labeled columns, each label is an interval for the metric, for example average change size per commit. The height of the column represents how many of all the values observed fall into that interval.

In the below screenshots, some of the diagrams are empty because my main account [cppavel](https://github.com/cppavel) does not have any issues assigned, PRs created and PRs assigned.

![Example top section of the report - data based on commits](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_top_section.png).

![Example diagram: "Histogram of time between consequtive commits"](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_diagram_one.png).

![Example diagram: "Histogram of change size per commit"](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_diagram_two.png).

![Example bottom section of the report - data based on collaboration and Histogram of time between consequtive issues created in hours](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_bottom_section.png).

![Example diagram: "Histogram of time between consequtive issues assigned in hours"](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_diagram_three.png).

![Example diagram: "Histogram of time between consequtive PRs created in hours](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_diagram_four.png).

![Example diagram: "Histogram of time between consequtive PRs assigned in hours](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_diagram_five.png). 

### Metrics explanation 

Both commits and issues data is gathered in most recent order using Github Search API to ensure relevancy of the results.

* I decided to analyze what languages the developer has used recently, because it can show their areas of experties or the languages they are starting to use. This data could be used to recommend users as mentors or as mentees, if paired with some simple AI engine.
* Median and average time between consequtive commits can tell us how active the developer is.
* Median and average change per commit tell us how well the developer can break down the changes into smaller pieces.
* It is also interesting to look at the distributions of time between consequtive commits and change per commit. However, due to breaks in development and configuration commits these distributions tend to have a lot of outliers, so they are cut at 90 percentile to be more readable.
* A few other metrics examine how many issues/PRs user has created/was assigned to. These are important for examining how well the developer can collaborate.
* We can see how many issues they user has closed out of all issues that were assigned to them, this tell us how the developer handles feature requests and tickets.
* Average time to close the issue can help us understand how quick the developer responds to feature requests and tickets.
* Average time to review PR tell us how quickly the user reviews code assigned to them. 
* Average number of comments in issues and PRs created help us understand how influential are users contributions to the discussions. Moreover, they user could be a new hire or an intern, not very familliar with style guides, hence they are getting loads of comments on their PRs.
* Again, it is interesting to have a look at the distributions.

To sum up, we can see that the metrics provided can be used to infer lots of different things about the developer. 

### Testing Strategy

* I used Docker to ensure that the testing and running environments remain the same regardless the machine I am working on. This increases the reproducibility of bugs.
* I used parameterized testing to make my tests more readable and less repetitive. 
* I mocked the pygithub.Github class to ensure my tests are hermetic (not dependent on external APIs or services). 

Here is the result of my unit tests:

![Test results](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/tests.png).

Next steps could be testing the API, i.e. integration tests, but this is outside of the scope of this project.

To run tests, please navigate to [backend/](https://github.com/cppavel-sweng/Github-Visualization/tree/main/backend) and execute [./run_tests.cmd](https://github.com/cppavel-sweng/Github-Visualization/blob/main/backend/run_tests.cmd).

### Technologies used

* MongoDB (pymongo) - database

* Pygithub - accessing github api

* Flask - backend

* HTML, JQuery, Bootstrap - frontend
