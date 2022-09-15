import os
import requests
from dotenv import load_dotenv


def get_vacancies_hh(user_agent, params):
    url = 'https://api.hh.ru/vacancies'
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (float(salary_from) + float(salary_to)) / 2
    elif salary_from:
        return float(salary_from) * 1.2
    elif salary_to:
        return float(salary_to) * 0.8


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    if not salary or salary['currency'] != 'RUR':
        return None
    return predict_salary(salary['from'], salary['to'])


def predict_rub_salary_sj(vacancy):
    if not vacancy['currency'] or vacancy['currency'] != 'rub':
        return None
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def get_language_stats_hh(user_agent, languages):
    languages_statistics = dict()
    for language in languages:
        params = {'text': language, 'area': 1, 'period': 30, 'per_page': 100}
        vacancies = get_vacancies_hh(user_agent, params)
        all_vacancies = vacancies['items']
        page = vacancies['page'] + 1

        while page < vacancies['pages']:
            params = {'text': language, 'area': 1, 'period': 30, 'per_page': 100, 'page': page}
            vacancies = get_vacancies_hh(user_agent, params)
            all_vacancies.extend(vacancies['items'])
            page += 1

        salaries = [predict_rub_salary_hh(vacancy) for vacancy in all_vacancies if predict_rub_salary_hh(vacancy)]
        if not salaries:
            average_salary = None
        else:
            average_salary = int(sum(salaries) / len(salaries))
        language_stats = {
            "vacancies_found": vacancies['found'],
            "vacancies_processed": len(salaries),
            "average_salary": average_salary
        }
        languages_statistics.update({language: language_stats})
    return languages_statistics


if __name__ == '__main__':
    load_dotenv()
    user_agent = os.getenv('USER_AGENT')
    languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
        'Shell',
        'Objective-C',
        'Scala',
        'Swift',
        'TypeScript'
    ]

    headers = {'X-Api-App-Id': os.getenv('SJ_API_KEY')}
    url = 'https://api.superjob.ru/2.0/vacancies/'
    params = {'keyword': 'Python', 'town': 4, 'catalogues': 48}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    vacancies = response.json()['objects']
    for vacancy in vacancies:
        print(vacancy['profession'], vacancy['town']['title'], predict_rub_salary_sj(vacancy), sep=', ')
