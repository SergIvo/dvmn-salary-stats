# Salary Statistics From HeadHunter and SuperJob

## About

This application retrieves information about vacancies from public APIs of two major job search services: [HeadHUnter](https://hh.ru/) and [SuperJob](https://superjob.ru/). Application calculates avarage salaries for vacancies related to most popular programming languages and prints this statistics in the form of tables to the console. Tables contain total vacancies count, number of vacancies with specified salary and average salary for each of the languages.

This application created for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/)

## Running the application

1. Download application files from GitHub using `git clone` command:
```
git clone https://github.com/SergIvo/dvmn-salary-stats
```
2. Create virtual environment using python [venv](https://docs.python.org/3/library/venv.html) library to avoid conflicts with other versions of the same packages:
```
python -m venv venv
```
Install dependencies from "requirements.txt" in created virtual environment using `pip` package manager:
```
pip install -r requirements.txt
```
To run application, you have to set a few environment variables:
```
export USER_AGENT="some user agent"
export SJ_API_KEY="your SuperJob API key"
```
Both variables are necessary to run the application. If you are not sure what user agent to use, try `curl`.

If you don't want to set environment variables manually, you can create [.env](https://pypi.org/project/python-dotenv/#getting-started) file and store all variables in it. 

Run `main.py` to make application fetch data and print it to console:
```
python main.py
```
Retrieving data from APIs might take some time, so don't worry if nothing happens when application just started.
