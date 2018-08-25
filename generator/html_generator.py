from collections import defaultdict, OrderedDict
from pprint import pprint
from moodle_parser import questions_from_file, order_dict, gen_index, glossary_from_file, json_to_file
from transliterate import translit
import json
import sys
import os
from os.path import join


DATA_VERSION = '00.00.06'

difficulty_icons = {
    "Базовый уровень":    '<span title="Базовая"    class="difficulty-icon"><i class="fas fa-star"></i><i class="far fa-star"></i><i class="far fa-star"></i></span>',
    "Повышенный уровень": '<span title="Повышенная" class="difficulty-icon"><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="far fa-star"></i></span>',
    "Высокий уровень":    '<span title="Высокая"    class="difficulty-icon"><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i></span>'
}


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


# def gen_section(grade_name, grade):
#     section_tpl = '''    <div class="nav-item u-category-{0}">
#       <button type="button" id="button-{0}-all" data-section="{0}-all" class="nav-button anti-padding"><h5 class="nav-category">{1} классы</h5></button>
# {2}
#     </div>
# '''
#     button_tpl = '      <button type="button" id="button-{0}" data-section="{0}" class="nav-button">{1}</button>'

#     buttons = []
#     for t in grade['topics_informatics']:
#         button = button_tpl.format(
#             '{}-{}'.format(grade['grade_id'], to_en(t)), t)
#         buttons.append(button)

#     return section_tpl.format(grade['grade_id'], grade_name, '\n'.join(buttons))


def load_template(path):
    return open('templates/' + path).read()


# def filter_questions(questions, filters, combiner=all):
#     def check(q, k, v):
#         if k in ('grade', 'topics_finances', 'topics_informatics'):
#             return v in q[k]
#         return q[k] == v
#     return [q for q in questions if combiner(check(q, k, v) for k, v in filters.items())]


def question_to_html(q):
    task_tpl = '''
        <div class="question demo" id="question-{q[question_id]}" data-question-id="{q[question_id]}" data-code="{q[code]}" data-question-type="{qtype}">
            <div class="demo-wrapper">
                <button id="new-window-hangs-demo-toggle" class="js-container-target demo-toggle-button">{q[code]} {q[name]}
                    <div class="demo-meta u-avoid-clicks"> 
                        {difficulty}
                        <span class="demo-meta-divider">|</span> {grade} классы
                        <span class="demo-meta-divider">|</span> {sections}
                        <span class="demo-meta-divider">|</span> {topics}
                    </div>
                    <div class="demo-meta u-avoid-clicks"> 
                        {interact}
                    </div>
                </button>
                <div class="demo-box">
                    {q[text]}
                    {checker}
                </div>
            </div>
        </div>
'''
    checker_tpl = '''
                    <div class="demo-controls checker-controls checker-interactive">
                        <input class="demo-input checker-input" id="check-input-{question_id}" placeholder="Введите ответ"></input>
                        <button class="demo-button checker-button" id="check-button-{question_id}" data-question-id="{question_id}" data-question-type="{q_type}" data-answer="{answer}" data-tolerance="{tolerance}">Проверить</button>
                    </div>
                    <p id="checker-result-{question_id}" class="checker-result"></p>
'''
    checker_excel_tpl = '''
                    <div class="demo-controls checker-controls checker-excel">
                        <div><a download href="assets/files/excel/{filename}.xlsx">Скачайте условие</a> а затем загрузите файл.</div>
                        <input id="file-input-{filename}" type="file" accept=".xlsx" class="demo-input checker-input checker-input-file" id="check-input-{question_id}" placeholder="Загрузите файл" onchange="handleFiles(this.files)" />
                        <button class="demo-button" id="check-button-{question_id}" data-question-id="{question_id}" data-question-type="{q_type}" data-answer="null" onclick="return false;" data-tolerance="null"><label for="file-input-{filename}">Проверить</label></button>
                        
                    </div>
                    <p id="checker-result-{question_id}" class="checker-result"></p>
'''
    interact_tpl = '''
                            {task_type} 
                            <span class="demo-meta-divider">|</span> <span id="solution-{question_id}" class="solution-history"><i class="fas fa-edit"></i> Нет попыток решения</span>
'''
    qtype = 'Текст' if q['type'] == 'essay' else 'Интерактив'
    qtype = 'Excel' if q['type'] == 'excel' else qtype
    ans = q['answer'] or 'null'
    tol = q['answer_tolerance'] or 'null'
    fin = ', '.join(q['topics_finances']) if len(q['topics_finances']) > 0 else 'Отсутствует'
    tword = 'Тема' if len(q['topics_finances']) <= 1 else 'Темы'
    inf = ', '.join(q['topics_informatics']) if len(q['topics_informatics']) > 0 else 'Отсутствует'
    iword = 'Раздел' if len(q['topics_informatics']) <= 1 else 'Разделы'
    k = lambda v: ['5-6 класс', '7-9 класс', '10-11 класс'].index(v)
    grade = ', '.join(v.replace(' класс', '') for v in sorted(q['grade'], key=k)) if len(q['grade']) > 0 else 'не назначен'
    gword = 'Класс' if len(q['grade']) <= 1 else 'Классы'
    
    if q['type'] == 'essay':
        interact = 'Текстовая задача' 
        checker = ''
    elif q['type'] == 'excel':
        interact = interact_tpl.format(question_id=q['question_id'], task_type='Excel-задача')
        checker = checker_excel_tpl.format(question_id=q['question_id'], filename=code_to_filename(q['code']), q_type=q['type'])
    else:
        interact = interact_tpl.format(question_id=q['question_id'], task_type='Интерактивная задача')
        checker = checker_tpl.format(question_id=q['question_id'], answer=ans, tolerance=tol, q_type=q['type'])
    
    return task_tpl.format(q=q, qtype=qtype, difficulty=difficulty_icons[q['difficulty']], interact=interact, checker=checker,
                           topic_word=tword, topics=fin, section_word=iword, sections=inf, grade=grade, grade_word=gword)


def glossary_entry_to_html(e):
    entry_tpl = '''
        <div class="demo glossary-entry">
            <div class="demo-wrapper">
                <h3 class="glossary-concept">{0[concept]}</h3>
                <div class="glossary-definition">{0[definition]}</div>
            </div>
        </div>
'''
    return entry_tpl.format(e)


def filters_to_html(qs_index):
    topics_finances_order = ['Расходы', 'Доходы', 'Семейный бюджет', 'Сбережения и инвестиции', 'Платежи и расчёты', 'Кредиты и займы', 'Страхование', 'Риски и финансовая безопасность']
    topics_informatics_order = ['Информация и информационные процессы', 'Алгоритмизация и программирование', 'Моделирование и формализация', 'Обработка числовых данных в электр. таблицах', 'Измерение количества информации', 'Информационная безопасность']
    type_order = ['Интерактив', 'Excel', 'Текст']
    filter_tpl = '''
                            <div class="filter-group-item">
                                <input type="checkbox" id="{id}" class="filter-item-input" name="{group}" value="{value}">
                                <label for="{id}">{label}</label>
                            </div>
'''
    
    filters = defaultdict(str)
    for field in qs_index.keys():
        keys = qs_index[field].keys()
        if field == 'topics_finances':
            keys = [topic for topic in topics_finances_order if topic in keys]
        elif field == 'topics_informatics':
            keys = [topic for topic in topics_informatics_order if topic in keys]
        elif field == 'type':
            keys = [task_type for task_type in type_order if task_type in keys]
        for i, v in enumerate(keys):
            raw_v = v
            if field == 'difficulty':
                v = difficulty_icons[v]
            # elif field == 'type':
            #     v = 'Интерактив' if v == 'Интерактивная' else 'Текст' # TODO автоматизированная vs ручная
            filters[field] += filter_tpl.format(id="filter-{}-{}".format(field, i + 1), group=field, label=v, value=raw_v)

    return filters


def grade_order(grades):
    if '5-6 класс' in grades:
        return 1
    elif '6-7 класс' in grades:
        return 2
    return 3


def difficulty_order(d):
    if 'Базовый' in d:
        return 1
    elif 'Повышенный' in d:
        return 2
    return 3


def code_to_filename(code):
    return ''.join(code.split('.')[:4])


if __name__ == '__main__':
    questions = questions_from_file('moodle_data/moodle_export_1.xml')
    order = lambda q: (grade_order(q['grade']), len(q['grade']), difficulty_order(q['difficulty']), q['topics_informatics'], q['topics_finances'], q['name'], q['task_type'])
    questions.sort(key=lambda q: q['name'])
    questions.sort(key=order)

    # old1()

    questions_idx_rev = gen_index(questions)

    questions_tpl = load_template('questions.html')
    with open('../sections/questions.html', 'w') as f:
        idx_rev_str = json.dumps(questions_idx_rev, ensure_ascii=False)
        filters = filters_to_html(questions_idx_rev)
        tasks = '\n'.join(question_to_html(q) for q in questions)
        f.write(questions_tpl.format(questions_index=idx_rev_str, filters=filters, questions=tasks, questions_qty=len(questions), data_version=DATA_VERSION))
        print('dataVersion = {}'.format(DATA_VERSION))

    with open('../sections/questions_data.js', 'w') as f:
        question_idx = {q['question_id']: q for q in questions}
        question_idx_str = json.dumps(question_idx, ensure_ascii=False, indent=None)
        f.write('window.questionsData = {}\n'.format(question_idx_str))
    
    # old2()




##### OLD DEFUNCT SECTIONS OF MAIN #####

# def old1():
#     gradeCounts = defaultdict(lambda: {
#         'Информация и информационные процессы': 0, 'Алгоритмизация и программирование': 0, 'Моделирование и формализация': 0, 'Обработка числовых данных в электр. таблицах': 0, 'Измерение количества информации': 0, 'Информационная безопасность': 0
#     })
#     for q in questions:
#         if 'ручная' in q['task_type'].lower():
#             continue
#         grade = q['grade'][0]
#         for topic in q['topics_informatics']:
#             gradeCounts[grade][topic] += 1
#     print(gradeCounts)

#     grades = defaultdict(lambda: defaultdict(set))
#     for q in questions:
#         for gr in q['grade']:
#             grade = gr.replace(' класс', '').strip()
#             grades[grade]['topics_finances'].add(q['topics_finances'])
#             grades[grade]['topics_informatics'].add(q['topics_informatics'])
#     grades = defaultdict_to_dict(grades)

#     grades_ordered = OrderedDict()
#     for i, k in enumerate(['5-6', '7-9', '10-11']):
#         grades_ordered[k] = grades[k]
#         grades_ordered[k]['grade_id'] = i + 1

#     sections = []
#     for grade_name, grade in grades_ordered.items():
#         sections.append(gen_section(grade_name, grade))

#     link_tpl = '  <link rel="import" href="sections/grade_{}/{}-{}.html">'
#     includes = []
#     for grade_name, g in grades_ordered.items():
#         includes += [link_tpl.format(grade_name, g['grade_id'], to_en(t))
#                      for t in ['all'] + g['topics_informatics']]

#     index = load_template('index.html')
#     index = (index.replace('<!-- GRADES DATA -->', '\n'.join(sections))
#                   .replace('<!-- SECTIONS DATA -->', '\n'.join(includes)))

#     with open('../index.html', 'w') as f:
#         f.write(index)

#     glossary_file = 'moodle_data/glossary_data_1.xml'
#     glossary_entries = glossary_from_file(glossary_file)
#     glossary_entries.sort(key=lambda k: k['concept'])
#     glossary = load_template('glossary.html')
#     with open('../sections/materials/glossary.html', 'w') as f:
#         g = glossary.format('\n'.join(glossary_entry_to_html(e)
#                                       for e in glossary_entries))
#         f.write(g)

#     textbook = load_template('textbook.html')
#     with open('../sections/materials/textbook.html', 'w') as f:
#         f.write(textbook)


# def old2():
#     for grade_name, g in grades_ordered.items():
#         for topic in ['all'] + g['topics_informatics']:
#             filters = {'grade': '{} класс'.format(
#                 grade_name), 'topics_informatics': topic}
#             if 'all' in topic:
#                 del filters['topics_informatics']
#             qs = filter_questions(questions, filters)
#             tasks = '\n'.join(question_to_html(q) for q in qs)
#             topics_full = '{}-{}'.format(g['grade_id'], to_en(topic))
#             head = '{} классы, &laquo;{}&raquo;'.format(grade_name, topic)
#             if 'all' in topic:
#                 head = '{} классы, все задачи'.format(grade_name, topic)
#             subsection = subsection_tpl.format(
#                 topics_full, g['grade_id'], head, tasks)
#             with open('../sections/grade_{}/{}.html'.format(grade_name, topics_full), 'w') as f:
#                 f.write(subsection)
