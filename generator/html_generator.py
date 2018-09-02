from collections import defaultdict, OrderedDict
from pprint import pprint
from moodle_parser import questions_from_file, order_dict, gen_index, glossary_from_file, json_to_file
from transliterate import translit
import json
import sys
import os
from os.path import join
import htmlmin

def minify(html):
    return htmlmin.minify(html, remove_comments=True, remove_empty_space=False, 
                          remove_all_empty_space=False, pre_tags=(u'pre', u'textarea'))

DATA_VERSION = '00.00.11'

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
                        <a download href="assets/files/excel/{filename}.xlsx" class="demo-button excel-button">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 475.078 475.077"><path d="M467.083,318.627c-5.324-5.328-11.8-7.994-19.41-7.994H315.195l-38.828,38.827c-11.04,10.657-23.982,15.988-38.828,15.988 c-14.843,0-27.789-5.324-38.828-15.988l-38.543-38.827H27.408c-7.612,0-14.083,2.669-19.414,7.994 C2.664,323.955,0,330.427,0,338.044v91.358c0,7.614,2.664,14.085,7.994,19.414c5.33,5.328,11.801,7.99,19.414,7.99h420.266 c7.61,0,14.086-2.662,19.41-7.99c5.332-5.329,7.994-11.8,7.994-19.414v-91.358C475.078,330.427,472.416,323.955,467.083,318.627z  M360.025,414.841c-3.621,3.617-7.905,5.424-12.854,5.424s-9.227-1.807-12.847-5.424c-3.614-3.617-5.421-7.898-5.421-12.844 c0-4.948,1.807-9.236,5.421-12.847c3.62-3.62,7.898-5.431,12.847-5.431s9.232,1.811,12.854,5.431 c3.613,3.61,5.421,7.898,5.421,12.847C365.446,406.942,363.638,411.224,360.025,414.841z M433.109,414.841 c-3.614,3.617-7.898,5.424-12.848,5.424c-4.948,0-9.229-1.807-12.847-5.424c-3.613-3.617-5.42-7.898-5.42-12.844 c0-4.948,1.807-9.236,5.42-12.847c3.617-3.62,7.898-5.431,12.847-5.431c4.949,0,9.233,1.811,12.848,5.431 c3.617,3.61,5.427,7.898,5.427,12.847C438.536,406.942,436.729,411.224,433.109,414.841z"/><path d="M224.692,323.479c3.428,3.613,7.71,5.421,12.847,5.421c5.141,0,9.418-1.808,12.847-5.421l127.907-127.908 c5.899-5.519,7.234-12.182,3.997-19.986c-3.23-7.421-8.847-11.132-16.844-11.136h-73.091V36.543c0-4.948-1.811-9.231-5.421-12.847 c-3.62-3.617-7.901-5.426-12.847-5.426h-73.096c-4.946,0-9.229,1.809-12.847,5.426c-3.615,3.616-5.424,7.898-5.424,12.847V164.45 h-73.089c-7.998,0-13.61,3.715-16.846,11.136c-3.234,7.801-1.903,14.467,3.999,19.986L224.692,323.479z"/></svg>
                            Скачать условие
                        </a>
                        <input id="file-input-{filename}" type="file" accept=".xlsx" class="demo-input checker-input checker-input-file" id="check-input-{question_id}" placeholder="Загрузите файл" data-question-id="{question_id}" data-question-type="{q_type}" data-answer="null" data-tolerance="null" />
                        <!-- <button class="demo-button" id="check-button-{question_id}" data-question-id="{question_id}" data-question-type="{q_type}" data-answer="null" data-tolerance="null"></button> -->
                            <label for="file-input-{filename}" class="demo-button excel-button">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 475.078 475.077"><path d="M467.081,327.767c-5.321-5.331-11.797-7.994-19.411-7.994h-121.91c-3.994,10.657-10.705,19.411-20.126,26.262 c-9.425,6.852-19.938,10.28-31.546,10.28h-73.096c-11.609,0-22.126-3.429-31.545-10.28c-9.423-6.851-16.13-15.604-20.127-26.262 H27.408c-7.612,0-14.083,2.663-19.414,7.994C2.664,333.092,0,339.563,0,347.178v91.361c0,7.61,2.664,14.089,7.994,19.41 c5.33,5.329,11.801,7.991,19.414,7.991h420.266c7.61,0,14.086-2.662,19.41-7.991c5.332-5.328,7.994-11.8,7.994-19.41v-91.361 C475.078,339.563,472.416,333.099,467.081,327.767z M360.025,423.978c-3.621,3.617-7.905,5.428-12.854,5.428 s-9.227-1.811-12.847-5.428c-3.614-3.613-5.421-7.898-5.421-12.847s1.807-9.236,5.421-12.847c3.62-3.613,7.898-5.428,12.847-5.428 s9.232,1.814,12.854,5.428c3.613,3.61,5.421,7.898,5.421,12.847S363.638,420.364,360.025,423.978z M433.109,423.978 c-3.614,3.617-7.898,5.428-12.848,5.428c-4.948,0-9.229-1.811-12.847-5.428c-3.613-3.613-5.42-7.898-5.42-12.847 s1.807-9.236,5.42-12.847c3.617-3.613,7.898-5.428,12.847-5.428c4.949,0,9.233,1.814,12.848,5.428 c3.617,3.61,5.427,7.898,5.427,12.847S436.729,420.364,433.109,423.978z"/><path d="M109.632,173.59h73.089v127.909c0,4.948,1.809,9.232,5.424,12.847c3.617,3.613,7.9,5.427,12.847,5.427h73.096 c4.948,0,9.227-1.813,12.847-5.427c3.614-3.614,5.421-7.898,5.421-12.847V173.59h73.091c7.997,0,13.613-3.809,16.844-11.42 c3.237-7.422,1.902-13.99-3.997-19.701L250.385,14.562c-3.429-3.617-7.706-5.426-12.847-5.426c-5.136,0-9.419,1.809-12.847,5.426 L96.786,142.469c-5.902,5.711-7.233,12.275-3.999,19.701C96.026,169.785,101.64,173.59,109.632,173.59z"/></svg>
                                Проверить решение
                            </label>
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
        idx_rev_str = json.dumps(questions_idx_rev, ensure_ascii=False, separators=(',',':'))
        filters = filters_to_html(questions_idx_rev)
        tasks = ''.join(question_to_html(q) for q in questions)
        res = questions_tpl.format(questions_index=idx_rev_str, filters=filters, questions=tasks, questions_qty=len(questions), data_version=DATA_VERSION)
        f.write(minify(res))
        print('dataVersion = {}'.format(DATA_VERSION))

    with open('../sections/questions_data.js', 'w') as f:
        question_idx = {q['question_id']: q for q in questions}
        question_idx_str = json.dumps(question_idx, ensure_ascii=False, indent=None, separators=(',',':'))
        f.write('window.questionsData={}\n'.format(question_idx_str))
    
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
