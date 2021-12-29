# Github-Visualization

### Running on your local machine

1. Clone the project
2. Rename .env_example to .env and put your Github token in it. 
3. Execute ./run.cmd. The website will be hosted on localhost:5000. 
4. Execute ./exit.cmd, if you would like to stop all containers.

### What it does

I decided to measure the overall metrics for a particular developer. My main idea was to focus not only on code contributions (commits), but also on creating/assigning/closing issues and creating/reviewing pull requests.

The project fetches data from github API for a prompted user handle and visualizes the data in the form of report.

I decided to call such report "type of developer" as it contains metrics that determine the things that developer normally works on.

For example, a developer may have a lot of contributions in C++ and a lot of pull requests and issues they were involved with, so we can deduce they are an Open Source C++ developer.

### Example report and Video Demo

![Example top section of the report](https://github.com/cppavel-sweng/Github-Visualization/blob/main/images/example_top_section.png).

### Metrics explanation 

### Testing Strategy

### Technologies used
