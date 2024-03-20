import psycopg2


DB_NAME = 'Students'
HOST = 'localhost'
USER = 'postgres'
PASSWORD = 'root'
PORT = '5432'


MENU = {
    1: "Вывести всех студентов и их средний балл;",
    2: "Добавить нового студента;",
    3: "Удалить студента по его ID;",
    4: "Вывести всех студентов со средним баллом больше 4.5;",
    5: "Выход из программы"
}


def create_table(db):
    with db.cursor() as curs:
        curs.execute('''
                        CREATE TABLE Students
                        (id SERIAL PRIMARY KEY,
                        name VARCHAR(50),
                        avg_score REAL)
                        ''')
    return True


def draw_console(menu_items_dict):
    print('-' * 50)
    for num, text in menu_items_dict.items():
        print(num, '. ', text, sep='')
    print('-' * 50)


def is_valid_menu_item(item):
    if item.isdigit():
        return True
    return False


def is_valid_value(answer, col_name):
    if col_name == 'avg_score':
        try:
            answer = float(answer)
            if not 2 <= answer <= 5:
                return False
        except ValueError:
            return False
    elif col_name == 'id' and not answer.isdigit():
        return False
    return True


def draw_table(field_name, data):
    print(f'|{"id":^5}|{field_name[0]:^20}|{field_name[1]:^20}|')
    print('=' * 49)
    for row in data:
        print(f'|{row[0]:^5}|{row[1]:^20}|{row[2]:^20}|')
        print('-' * 49)


def get_students(db, field_name):
    with db.cursor() as curs:
        curs.execute('SELECT * FROM Students')
        data = curs.fetchall()
    draw_table(field_name, data)
    input('Нажмите ENTER чтобы продолжить...')


def add_student(db, field_name):
    data_dict = {}
    for i in range(len(field_name)):
        while True:
            answer = input(f'Введите значение столбца {field_name[i]}: >>> ')
            if is_valid_value(answer, field_name[i]):
                data_dict[field_name[i]] = answer
                break
            else:
                print('Ошибка типа данных или значения для данного столбца! Повторите попытку...')
    with db.cursor() as curs:
        curs.execute(f'''
                        INSERT INTO Students ({field_name[0]}, {field_name[1]})
                        VALUES ('{data_dict[field_name[0]]}', {data_dict[field_name[1]]})
                        ''')
    print('-------------')
    print('Запись добавлена в базу данных!')
    input('Нажмите ENTER чтобы продолжить...')


def del_student_by_id(db, *args):
    with db.cursor() as curs:
        curs.execute('SELECT id FROM Students')
        all_id = [i[0] for i in curs.fetchall()]
    while True:
        answer = input('Введите ID студента, которого необходимо удалить из базы: >>> ')
        if is_valid_value(answer, 'id') and (answer in all_id):
            break
        else:
            print('Ошибка типа данных или значения для данного столбца! Повторите попытку...')
    with db.cursor() as curs:
        curs.execute(f'''
                        DELETE FROM Students
                        WHERE id = {answer}  
        ''')
    print('-------------')
    print(f'Студент с ID = {answer} удален из базы данных.')
    input('Нажмите ENTER чтобы продолжить...')


def get_score_more_4_5(db, field_name):
    with db.cursor() as curs:
        curs.execute('SELECT * FROM Students WHERE avg_score >= 4.5')
        data = curs.fetchall()
    draw_table(field_name, data)
    input('Нажмите ENTER чтобы продолжить...')


try:
    conn = psycopg2.connect(dbname=DB_NAME, host=HOST, user=USER, password=PASSWORD, port=PORT)
except:
    raise Exception('Ошибка подключения к базе данных...')

conn.autocommit = True
with conn.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='students'")
    count_tables = cursor.fetchone()[0]
    if count_tables == 0:
        create_table(conn)
        print('Таблица Students создана!')
    elif count_tables == 1:
        print('Таблица Students уже существует!')
    else:
        raise Exception('Ошибка! Таблиц Students больше чем одна!')
    cursor.execute("SELECT * FROM Students LIMIT 0")
    column_names = ([desc[0] for desc in cursor.description][1:])

MENU_BACK = {
    1: get_students,
    2: add_student,
    3: del_student_by_id,
    4: get_score_more_4_5
}

exit_flag = False
while not exit_flag:
    draw_console(MENU)
    choice = input('>>> ').strip()
    while not is_valid_menu_item(choice):
        print('Ошибка ввода номера пункта! Повторите ввод...')
        choice = input('>>> ')
    choice = int(choice)
    if choice in MENU_BACK.keys():
        MENU_BACK[choice](conn, column_names)
    elif choice == 5:
        exit_flag = True
    else:
        print('Такого пункта меню нет! Повторите ввод...')

conn.close()
