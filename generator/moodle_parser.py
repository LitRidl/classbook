import html
from bs4 import BeautifulSoup, Comment
import random
import json
from collections import OrderedDict
import sys


def fmt(tag):
    if 'Кл: ' in tag:
        tag += ' класс'
    if 'Ур: ' in tag:
        tag += ' уровень'
    return (tag
            .replace('Кл: ', '')
            .replace('Ур: ', '')
            .replace('Фин: ', '')
            .replace('Инф: ', ''))


def tags_classifier(question, fake_attributes=False):
    tags = question['_tags']
    grades = [
        'Кл: 5-6',
        'Кл: 7-9',
        'Кл: 10-11',
    ]
    difficulties = [
        'Ур: Базовый',
        'Ур: Повышенный',
        'Ур: Высокий',
    ]
    topics_finances = [
        'Фин: Доходы',
        'Фин: Кредиты и займы',
        'Фин: Налоги',
        'Фин: Платежи и расчёты',
        'Фин: Потребности и расходы',
        'Фин: Расходы',
        'Фин: Риски и финансовая безопасность',
        'Фин: Сбережения и инвестиции',
        'Фин: Семейный бюджет',
        'Фин: Страхование',
    ]
    topics_informatics = [
        'Инф: Измерение количества информации',
        'Инф: Информационная безопасность',
        'Инф: Информационный поиск и анализ информации',
        'Инф: Моделирование',
        'Инф: Мультимедиа',
        'Инф: Программирование',
        'Инф: Программные и информационные системы',
        'Инф: Электронные таблицы',
    ]

    attributes = {
        'grade':             fmt(random.choice(grades)) if fake_attributes else None,
        'difficulty':        fmt(random.choice(difficulties)) if fake_attributes else None,
        'topic_finances':    fmt(random.choice(topics_finances)) if fake_attributes else None,
        'topic_informatics': fmt(random.choice(topics_informatics)) if fake_attributes else None,
        '_fake_attributes':  ['grade', 'difficulty', 'topic_finances', 'topic_informatics']
    }

    for tag in tags:
        if tag in grades:
            attributes['grade'] = fmt(tag)
            attributes['_fake_attributes'].remove('grade')
        elif tag in difficulties:
            attributes['difficulty'] = fmt(tag)
            attributes['_fake_attributes'].remove('difficulty')
        elif tag in topics_finances:
            attributes['topic_finances'] = fmt(tag)
            attributes['_fake_attributes'].remove('topic_finances')
        elif tag in topics_informatics:
            attributes['topic_informatics'] = fmt(tag)
            attributes['_fake_attributes'].remove('topic_informatics')

    if not fake_attributes:
        if len(attributes['_fake_attributes']) > 0:
            raise Exception(
                "Incomplete tags for attributes: {}".format(question))
        del attributes['_fake_attributes']

    return attributes


def parse_question(q, _id=None):
    question = {
        'name': q.find('name').text.strip()[7:].strip(),
        'text': html.unescape(q.find('questiontext').find('text')
                              .prettify(formatter='xml').strip()
                              .lstrip('<text>').rstrip('</text>').strip()),
        '_tags': [t.find('text').text.strip() for t in q.find('tags').find_all('tag')]
    }
    if _id:
        question['_id'] = _id
    question.update(tags_classifier(question))
    return question


links_dict = {
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3LqyPZ0Z2BQmju9': 'Энергопотребление бытовых приборов.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3MeyO-YKsZ5iUrC': 'Тесто для пиццы.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3QlRj2rMgZ2HEp1': 'Изменение цен на смартфон.xlsx',
    'https://1drv.ms/t/s!AkwppQEzBB-Yi3U-vbgkBZSwW0qX': 'Покупка гречки.txt',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3Zn97c2fOh1R9Vv': 'Цвет и цена мобильного.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3fD_QnLtW0sOwPP': 'Кэшбэк по банковской карте.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3gmwz48_DiT1f20': 'Поездка Москва-СПб.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3lwM9b5IziSabwb': 'Поездка в отпуск.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3rVrqN0UkDTKCM4': 'Покупка подержанного автомобиля.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3veWX7YSmm-AsPn': 'Цена поездки на такси.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi3ww8Z4VhRLLo2vx': 'Салон красоты.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi37qmEITegev1co6': 'Налог на имущество.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi31STRw4W97_Vw16': 'Подоходный налог группы сотрудников.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-Yi38DvKbGd-_1j1X6': 'Анализ бюджета семьи.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAAQSlWGOZzWx98G': 'Оценка возможностей семейного бюджета на год.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAHnJSTqRHKmvTi5': 'Оценка возможностей семейного бюджета на 10 лет.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAToanPYNUGTJYxj': 'Прогноз бюджета по отдельным данным.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAKi1W_bjwbH_St1': 'Устранение кассовых разрывов без использования заемных средств.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjANfNHRSB5fmY0Bh': 'Устранение кассовых разрывов с использованием заемных средств.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAXyvOcm0bTIHynH': 'Ставки по депозиту в рублях и долларах.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAZrWqIKDrFDR2nu': 'Вложения в акции.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAlPE6bX2pcu4ur8': 'Доходность по акциям.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAcByU2MRGrR2ZXv': 'Доход от инвестиций.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAig3acx222V2pJf': 'Инвестиции в валюту.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAuJrBNeaZVROkyi': 'Стоимость БигМака.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAqX7mhze_7OjFqp': 'Динамика валютного курса.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjAzekhJpNMX0HP32': 'Условия микрокредита.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjA2oYKsitj8wWRCj': 'Пользование кредитной картой.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjBE0ijXL6iNj0Byt': 'Накопительное страхование на дожитие.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjA5-9k4hrYGM5ycZ': 'Калькулятор ОСАГО.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjBIMAxHCHMY_oAI9': 'Коэффициент бонус-малус.xlsx',
    'https://1drv.ms/x/s!AkwppQEzBB-YjA9RiTz8ylRbyO_e': 'Проверяем по таблице.xlsx'
}


def parse_questions(xml):
    for link, fname in links_dict.items():
        new_link = 'assets/finformatika.ru/attachments/{}'.format(fname)
        xml = xml.replace(link, new_link)
    xml = xml.replace('src="http://finformatika.ru/images/', 'src="/images/')
    xml = xml.replace('src="/images/', 'src="assets/finformatika.ru/images/')
    soup = BeautifulSoup(xml, 'xml')

    soup_comments = [c.strip()for c in soup.findAll(text=lambda text: isinstance(text, Comment))
                     if 'question' in c]
    question_ids = [int(c.replace('question: ', ''))
                    for c in soup_comments if 'question: 0' not in c]

    soup_questions = soup.find_all('question', attrs={'type': 'essay'})
    questions = [parse_question(q, _id=i)
                 for i, q in enumerate(soup_questions)]
    questions = [dict(q, question_id=q_id)
                 for q_id, q in zip(question_ids, questions)]

    return questions


def order_dict(d, order):
    return [OrderedDict(sorted(el.items(), key=lambda el: order.index(el[0]))) for el in d]


def questions_from_files(*xml_files):
    questions = sum([parse_questions(open(f).read()) for f in xml_files], [])
    order = ['_id', 'question_id', 'grade', 'difficulty', 'topic_finances',
             'topic_informatics', 'name', 'text', '_tags', '_fake_attributes']

    return order_dict(questions, order)


def parse_glossary_entry(e):
    return {
        'concept': e.find('CONCEPT').text.strip(),
        'definition': html.unescape(e.find('DEFINITION').prettify(formatter='xml').strip()
                                     .lstrip('<DEFINITION>').rstrip('</DEFINITION>').strip()),
    }


def glossary_from_file(xml_file):
    soup = BeautifulSoup(open(xml_file).read(), 'xml')
    return [parse_glossary_entry(e) for e in soup.find_all('ENTRY')]


def json_to_file(data, fname):
    with open(fname, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    xml_files = sys.argv[1:] or ['moodle_data/moodle_export_1.xml']
    fname = 'moodle_data.json'

    print('Outputting questions to {}'.format(fname))

    qs = questions_from_files(*xml_files)
    json_to_file(qs, fname)

    print('Outputting glossary to {}'.format('glossary.json'))

    glossary_file = 'moodle_data/glossary_data_1.xml'
    glossary = glossary_from_file(glossary_file)
    json_to_file(glossary, 'glossary.json')
