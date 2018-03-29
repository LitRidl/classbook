from collections import defaultdict, OrderedDict
from pprint import pprint
from moodle_parser import questions_from_files, order_dict, glossary_from_file
from transliterate import translit
import json
import sys


def defaultdict_to_dict(d):
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = defaultdict_to_dict(v)
        elif isinstance(v, set):
            d[k] = list(sorted(v))
    return dict(d)


def to_en(t):
    if t == 'all':
        return t
    return translit(t, reversed=True).replace(' ', '-').replace("'", '').strip().lower()


def gen_section(grade_name, grade):
    section_tpl = '''    <div class="nav-item u-category-{0}">
      <button type="button" id="button-{0}-all" data-section="{0}-all" class="nav-button anti-padding"><h5 class="nav-category">{1} классы</h5></button>
{2}
    </div>
'''
    button_tpl = '      <button type="button" id="button-{0}" data-section="{0}" class="nav-button">{1}</button>'

    buttons = []
    for t in grade['topics_informatics']:
        button = button_tpl.format(
            '{}-{}'.format(grade['grade_id'], to_en(t)), t)
        buttons.append(button)

    return section_tpl.format(grade['grade_id'], grade_name, '\n'.join(buttons))


def load_template(path):
    return open('templates/' + path).read()


def filter_questions(questions, filters):
    def check(q, k, v):
        if k == 'grade':
            return v in q[k]
        return q[k] == v
    return [q for q in questions if all(check(q, k, v) for k, v in filters.items())]


def question_to_html(q):
    task_tpl = '''        <div class="demo">
            <div class="demo-wrapper">
                <button id="new-window-hangs-demo-toggle" class="js-container-target demo-toggle-button">{}
                    <div class="demo-meta u-avoid-clicks"> Сложность: {}
                        <span class="demo-meta-divider">|</span> Тема: {}</div>
                </button>
                <div class="demo-box">{}</div>
            </div>
        </div>
'''
# <span class="demo-meta-divider">|</span> Тема: {}
    difficulty = {
        "Базовый уровень": 'базовая',
        "Повышенный уровень": 'повышенная',
        "Высокий уровень": 'высокая',
    }[q['difficulty']]
    return task_tpl.format(q['name'], difficulty, q['topic_finances'], q['text'])


def glossary_entry_to_html(e):
    entry_tpl = '''        <div class="demo glossary-entry">
            <div class="demo-wrapper">
                <h3 class="glossary-concept">{}</h3>
                <div class="glossary-definition">{}</div>
            </div>
        </div>
'''
    return entry_tpl.format(e['concept'], e['definition'])


if __name__ == '__main__':
    xml_files = sys.argv[1:] or ['moodle_data/moodle_export_1.xml']
    questions = questions_from_files(*xml_files)

    grades = defaultdict(lambda: defaultdict(set))
    for q in questions:
        for gr in q['grade']:
            grade = gr.replace(' класс', '').strip()
            grades[grade]['topics_finances'].add(q['topic_finances'])
            grades[grade]['topics_informatics'].add(q['topic_informatics'])
    grades = defaultdict_to_dict(grades)

    grades_ordered = OrderedDict()
    for i, k in enumerate(['5-6', '7-9', '10-11']):
        grades_ordered[k] = grades[k]
        grades_ordered[k]['grade_id'] = i + 1

    sections = []
    for grade_name, grade in grades_ordered.items():
        sections.append(gen_section(grade_name, grade))

    link_tpl = '  <link rel="import" href="sections/grade_{}/{}-{}.html">'
    includes = []
    for grade_name, g in grades_ordered.items():
        includes += [link_tpl.format(grade_name, g['grade_id'], to_en(t))
                     for t in ['all'] + g['topics_informatics']]

    index = load_template('index.html')
    index = (index.replace('<!-- GRADES DATA -->', '\n'.join(sections))
                  .replace('<!-- SECTIONS DATA -->', '\n'.join(includes)))

    with open('../index.html', 'w') as f:
        f.write(index)

    glossary_file = 'moodle_data/glossary_data_1.xml'
    glossary_entries = glossary_from_file(glossary_file)
    glossary_entries.sort(key=lambda k: k['concept'])
    glossary = load_template('glossary.html')
    with open('../sections/materials/glossary.html', 'w') as f:
        g = glossary.format('\n'.join(glossary_entry_to_html(e)
                                      for e in glossary_entries))
        f.write(g)

    textbook = load_template('textbook.html')
    with open('../sections/materials/textbook.html', 'w') as f:
        f.write(textbook)

    subsection_tpl = load_template('subsection.html')
    for grade_name, g in grades_ordered.items():
        for topic in ['all'] + g['topics_informatics']:
            filters = {'grade': '{} класс'.format(
                grade_name), 'topic_informatics': topic}
            if 'all' in topic:
                del filters['topic_informatics']
            qs = filter_questions(questions, filters)
            tasks = '\n'.join(question_to_html(q) for q in qs)
            topic_full = '{}-{}'.format(g['grade_id'], to_en(topic))
            head = '{} классы, &laquo;{}&raquo;'.format(grade_name, topic)
            if 'all' in topic:
                head = '{} классы, все задачи'.format(grade_name, topic)
            subsection = subsection_tpl.format(
                topic_full, g['grade_id'], head, tasks)
            with open('../sections/grade_{}/{}.html'.format(grade_name, topic_full), 'w') as f:
                f.write(subsection)
