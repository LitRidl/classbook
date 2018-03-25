import html
from bs4 import BeautifulSoup, Comment
import random
import json
from collections import OrderedDict
import sys


def tags_classifier(question, fake_attributes=False):
    tags = question['_tags']
    grades = [
        '5-6 класс',
        '7-9 класс',
        '10-11 класс',
    ]
    difficulties = [
        'Базовый уровень',
        'Повышенный уровень',
        'Высокий уровень',
    ]
    topics_finances = [
        'Бюджет',
        'Доходы',
        'Игры с денежными ставками',
        'Кредиты и займы',
        'Платежи и расчёты',
        'Потребности и расходы',
        'Расходы',
        'Расчёты',
        'Риски и финансовая безопасность',
        'Сбережения и инвестиции',
        'Семейный бюджет',
        'Страхование',
    ]
    topics_informatics = [
        'Измерение количества информации',
        'Информационная безопасность',
        'Информационный поиск и анализ информации',
        'Использование программных систем и информационных сервисов',
        'Моделирование',
        'Мультимедиа',
        'Программирование',
        'Электронные таблицы',
    ]

    attributes = {
        'grade':             random.choice(grades) if fake_attributes else None,
        'difficulty':        random.choice(difficulties) if fake_attributes else None,
        'topic_finances':    random.choice(topics_finances) if fake_attributes else None,
        'topic_informatics': random.choice(topics_informatics) if fake_attributes else None,
        '_fake_attributes':  ['grade', 'difficulty', 'topic_finances', 'topic_informatics']
    }

    for tag in tags:
        if tag in grades:
            attributes['grade'] = tag
            attributes['_fake_attributes'].remove('grade')
        elif tag in difficulties:
            attributes['difficulty'] = tag
            attributes['_fake_attributes'].remove('difficulty')
        elif tag in topics_finances:
            attributes['topic_finances'] = tag
            attributes['_fake_attributes'].remove('topic_finances')
        elif tag in topics_informatics:
            attributes['topic_informatics'] = tag
            attributes['_fake_attributes'].remove('topic_informatics')

    if not fake_attributes:
        if len(attributes['_fake_attributes']) > 0:
            raise Exception(
                "Incomplete tags for attributes: {}".format(question))
        del attributes['_fake_attributes']

    return attributes


def parse_question(q, _id=None):
    question = {
        'name': q.find('name').text.strip(),
        'text': html.unescape(q.find('questiontext').find('text')
                              .prettify(formatter='xml').strip()
                              .lstrip('<text>').rstrip('</text>').strip()),
        '_tags': [t.find('text').text.strip() for t in q.find('tags').find_all('tag')]
    }
    if _id:
        question['_id'] = _id
    question.update(tags_classifier(question))
    return question


def parse_questions(xml):
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
