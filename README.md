# SpellChecking

Использование:
1) Обучение языковой модели
2) Генерация кандидатов:
Использование:
"Использование: candidateProcessor.py source_file candidate_file\n"
                 "source_file: исходный файл c предложениями\n"
                 "candidate_file: выходной файл с кандидатами\n"
3) Переранжирование кандидатов:
Использование: evaluate.py language_model source_candidate_file source_correct_file test_candidate_file test_correct_file
language_model: языковая модель
source_candidate_file: файл c исправлениями-кандидатами для обучающей выборки
source_correct_file: файл с эталонными исправлениями для обучающей выборки
test_candidate_file: файл с исправлениями-кандидатами для тестовой выборки
test_correct_file: файл с эталонными исправлениями для тестовой выборки
