import os

renames = {
    'Цвет и цена мобильного.xlsx': 'cvet_i_cena_mobilnogo.xlsx',
    'Цена поездки на такси.xlsx': 'cena_poezdki_na_taksi.xlsx',
    'Налог на имущество.xlsx': 'nalog_na_imushchestvo.xlsx',
    'Доход от инвестиций.xlsx': 'dohod_ot_investicii.xlsx',
    'Тесто для пиццы.xlsx': 'testo_dlya_piccy.xlsx',
    'Салон красоты.xlsx': 'salon_krasoty.xlsx',
    'Ставки по депозиту в рублях и долларах.xlsx': 'stavki_depozit_rub_usd.xlsx',
    'Кэшбэк по банковской карте.xlsx': 'keshbek_po_karte.xlsx',
    'Анализ бюджета семьи.xlsx': 'analiz_byudzheta_semi.xlsx',
    'Оценка возможностей семейного бюджета на 10 лет.xlsx': 'ocenka_budzhet_10_let.xlsx',
    'Оценка возможностей семейного бюджета на год.xlsx': 'ocenka_budzhet_god.xlsx',
    'Поездка в отпуск.xlsx': 'poezdka_v_otpusk.xlsx',
    'Поездка Москва-СПб.xlsx': 'poezdka_moskva_spb.xlsx',
    'Покупка гречки.txt': 'pokupka_grechki.txt',
    'Прогноз бюджета по отдельным данным.xlsx': 'prognoz_byudzheta.xlsx',
    'Покупка подержанного автомобиля.xlsx': 'pokupka_bu_avto.xlsx',
    'Условия микрокредита.xlsx': 'usloviya_mikrokredita.xlsx',
    'Вложения в акции.xlsx': 'vlozheniya_v_akcii.xlsx',
    'Динамика валютного курса.xlsx': 'dinamika_kursa.xlsx',
    'Проверяем по таблице.xlsx': 'proveryaem_po_tablice.xlsx',
    'Изменение цен на смартфон.xlsx': 'izmenenie_cen_smartfon.xlsx',
    'Стоимость БигМака.xlsx': 'stoimost_bigmaka.xlsx',
    'Инвестиции в валюту.xlsx': 'investicii_v_valyutu.xlsx',
    'Доходность по акциям.xlsx': 'dohodnost_po_akciyam.xlsx',
    'Устранение кассовых разрывов с использованием заемных средств.xlsx': 'kassovyi_razryv_s_zaymom.xlsx',
    'Устранение кассовых разрывов без использования заемных средств.xlsx': 'kassovyi_razryv_bez_zayma.xlsx',
    'Подоходный налог группы сотрудников.xlsx': 'ndfl_sotrudnikov.xlsx',
    'Коэффициент бонус-малус.xlsx': 'koeff_bonus_malus.xlsx',
    'Калькулятор ОСАГО.xlsx': 'kalkulyator_osago.xlsx',
    'Пользование кредитной картой.xlsx': 'polzovanie_kreditkoy.xlsx',
    'Накопительное страхование на дожитие.xlsx': 'nakopit_strahov_na_dozhitie.xlsx',
    'Энергопотребление бытовых приборов.xlsx': 'energopotreb_priborov.xlsx'
}

# for old_name, new_name in renames.items():
#     path = '../assets/finformatika.ru/attachments/{}'
#     os.rename(path.format(old_name), path.format(new_name))

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

for old_name, new_name in renames.items():
    for k in links_dict.keys():
        links_dict[k] = links_dict[k].replace(old_name, new_name)

print(links_dict)