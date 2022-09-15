import os
import requests
from dotenv import load_dotenv


def get_vacancies(user_agent, params):
    url = 'https://api.hh.ru/vacancies'
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_language_stats(languages):
    language_statistics = {}
    for language in languages:
        params = {'text': language, 'area': 1, 'period': 15}
        vacancies = get_vacancies(user_agent, params)
        language_statistics.update({language: vacancies['found']})
    return language_statistics


def predict_rub_salary(vacancy):
    try:
        salary = vacancy['salary']
    except Exception as ex:
        print(vacancy, ex, sep='\n')
    if not salary or salary['currency'] != 'RUR':
        return None
    if salary.get('from') and salary.get('to'):
        return (float(salary.get('from')) + float(salary.get('to'))) / 2
    elif salary.get('from'):
        return float(salary.get('from')) * 1.2
    elif salary.get('to'):
        return float(salary.get('to')) * 0.8


if __name__ == '__main__':
    load_dotenv()
    user_agent = os.getenv('USER_AGENT')

    params = {'text': 'Python', 'area': 1, 'period': 30}
    vacancies = get_vacancies(user_agent, params)
    print(vacancies['found'])

    for vacancy in vacancies['items']:
        print(vacancy['name'], vacancy['salary'], f'estimated: {predict_rub_salary(vacancy)}', sep=': ')

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

    languages_statistics = dict()
    for language in languages:
        params = {'text': language, 'area': 1, 'period': 30, 'per_page': 100}
        vacancies = get_vacancies(user_agent, params)
        all_vacancies = vacancies['items']
        page = vacancies['page'] + 1

        while page < vacancies['pages']:
            params = {'text': language, 'area': 1, 'period': 30, 'per_page': 100, 'page': page}
            vacancies = get_vacancies(user_agent, params)
            all_vacancies.extend(vacancies['items'])
            print(f'Page {page} from {vacancies["pages"]} for {language} language processed.')
            page += 1

        salaries = [predict_rub_salary(vacancy) for vacancy in all_vacancies if predict_rub_salary(vacancy)]
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

    print(languages_statistics)
