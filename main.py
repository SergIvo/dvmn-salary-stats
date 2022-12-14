import os
import requests
from terminaltables import DoubleTable
from dotenv import load_dotenv


def get_vacancies_hh(user_agent, params):
    url = 'https://api.hh.ru/vacancies'
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_vacancies_sj(api_key, params):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': api_key}
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
    moscow_area_id = 1
    period_in_days = 30
    for language in languages:
        params = {'text': language, 'area': moscow_area_id, 'period': period_in_days, 'per_page': 100}
        vacancies = get_vacancies_hh(user_agent, params)
        all_vacancies = vacancies['items']
        page = vacancies['page'] + 1

        while page < vacancies['pages']:
            params = {
                'text': language,
                'area': moscow_area_id,
                'period': period_in_days,
                'per_page': 100,
                'page': page
            }
            vacancies = get_vacancies_hh(user_agent, params)
            all_vacancies.extend(vacancies['items'])
            page += 1

        unfiltered_salaries = [predict_rub_salary_hh(vacancy) for vacancy in all_vacancies]
        salaries = list(filter(None, unfiltered_salaries))
        if not salaries:
            average_salary = None
        else:
            average_salary = int(sum(salaries) / len(salaries))
        language_stats = {
            "vacancies_found": vacancies['found'],
            "vacancies_processed": len(salaries),
            "average_salary": average_salary
        }
        languages_statistics[language] = language_stats
    return languages_statistics


def get_language_stats_sj(sj_api_key, languages):
    languages_statistics = dict()
    for language in languages:
        all_vacancies = []
        moscow_town_id = 4
        programmers_catalogue_id = 48
        params = {
            'keyword': language,
            'town': moscow_town_id,
            'catalogues': programmers_catalogue_id,
            'page': 0
        }
        vacancies = get_vacancies_sj(sj_api_key, params)
        all_vacancies.extend(vacancies['objects'])
        number_of_vacancies = vacancies['total']
        page = 1

        while len(all_vacancies) < number_of_vacancies and len(all_vacancies) < 500:
            params = {
                'keyword': language,
                'town': moscow_town_id,
                'catalogues': programmers_catalogue_id,
                'page': page
            }
            vacancies = get_vacancies_sj(sj_api_key, params)
            all_vacancies.extend(vacancies['objects'])
            page += 1

        unfiltered_salaries = [predict_rub_salary_sj(vacancy) for vacancy in all_vacancies]
        salaries = list(filter(None, unfiltered_salaries))
        if not salaries:
            average_salary = None
        else:
            average_salary = int(sum(salaries) / len(salaries))
        language_stats = {
            "vacancies_found": number_of_vacancies,
            "vacancies_processed": len(salaries),
            "average_salary": average_salary
        }
        languages_statistics[language] = language_stats

    return languages_statistics


def make_table(title, languages_stats):
    header = ['???????? ????????????????????????????????', '???????????????? ??????????????', '???????????????? ????????????????????', '?????????????? ????????????????']
    rows = [header]
    for language, stats in languages_stats.items():
        row = [language]
        row.extend(stats.values())
        rows.append(row)
    table = DoubleTable(rows, title)
    return table.table


if __name__ == '__main__':
    load_dotenv()
    user_agent = os.getenv('USER_AGENT')
    sj_api_key = os.getenv('SJ_API_KEY')

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

    hh_statistics = get_language_stats_hh(user_agent, languages)
    sj_statistics = get_language_stats_sj(sj_api_key, languages)

    hh_stats_table = make_table('HeadHunter Moscow', hh_statistics)
    sj_stats_table = make_table('SuperJob Moscow', sj_statistics)

    print(hh_stats_table, sj_stats_table, sep='\n')
