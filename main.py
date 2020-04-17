import psycopg2
import datetime

students_j = [
    ('Первенцев Илларион Михайлович', 0, '1990-11-07'),
    ('Секондов Васисуалий Евлампиевич', 0, '1994-07-09'),
]
students_p = [
    ('Четвертак Микола Бандэрович', 0, '2000-09-03'),
    ('Третьяков Иммануил Кантович', 0, '1988-12-17')
]
students_c = [
    ('Шестёркин Промокашка Шныревич', 0, '1990-10-02'),
    ('Пятюнин Иван Степанович', 0, '1979-05-01')
]

courses = ('JavaScript', 'Python', 'C++')


def create_db():  # создает таблицы
    with psycopg2.connect(database="test_db", user="test", password="1234") as conn:
        with conn.cursor() as curs:
            curs.execute("""
                        CREATE TABLE student (
                        id serial PRIMARY KEY NOT NULL, 
                        name varchar(100) NOT NULL, 
                        gpa numeric(10, 2), 
                        birth timestamp with time zone);
                        """)
            curs.execute("""
                        CREATE TABLE course (
                        id serial PRIMARY KEY NOT NULL,
                        name varchar(100) NOT NULL);
                        """)
            for item in courses:
                curs.execute("""
                            INSERT INTO course (name)
                            values (%s)                        
                            """, (item,))

            curs.execute("""
                        CREATE TABLE student_course (
                        id serial PRIMARY KEY,
						student_id INTEGER REFERENCES student(id),
						course_id INTEGER REFERENCES course(id));
                        """)
    print('Таблицы созданы, курсы добавлены')


def get_students(course_id):  # возвращает студентов определенного курса
    with psycopg2.connect(database="test_db", user="test", password="1234") as conn:
        with conn.cursor() as curs:
            curs.execute("""select s.id, s.name, c.name 
                        from student_course sc 
                        join student s on s.id = sc.student_id 
                        join course c on c.id = sc.course_id
                        where sc.course_id = %s;
                        """, (course_id,))
            rows = curs.fetchall()
            print(f'на курсе <{rows[0][2]}> учатся:')
            for item in rows:
                print(f'id={item[0]} name={item[1]}')


def add_students(course_id, students):  # создает студентов и записывает их на курс
    with psycopg2.connect(database="test_db", user="test", password="1234") as conn:
        with conn.cursor() as curs:
            for item in students:
                curs.execute("""
                            INSERT INTO student (name, gpa, birth)
                            values (%s, %s, %s)                        
                            """, item)
                conn.commit()
                curs.execute("""
                            SELECT id FROM student
                            WHERE name = %s;
                            """, (item[0],))
                student_id = curs.fetchall()[0][0]
                curs.execute("""
                            INSERT INTO student_course (course_id, student_id)
                            values (%s, %s)                        
                            """, (course_id, student_id,))
    print('Студенты добавлены в базу и записаны на курс')


def add_student(student: tuple):  # просто создает студента
    with psycopg2.connect(database="test_db", user="test", password="1234") as conn:
        with conn.cursor() as curs:
            curs.execute("""
                        INSERT INTO student (name, gpa, birth)
                        values (%s, %s, %s)                        
                        """, student)
    print(f'студент {student[0]} добавлен в базу')


def get_student(student_id):
    with psycopg2.connect(database="test_db", user="test", password="1234") as conn:
        with conn.cursor() as curs:
            curs.execute("""
                        SELECT * FROM student
                        WHERE id = %s;
                        """, (student_id,))
            rows_s = curs.fetchall()
            curs.execute("""
                        select c.name 
                        from student_course sc  
                        join course c on c.id = sc.course_id
                        where sc.student_id = %s;
                        """, (student_id,))
            rows_c = curs.fetchall()
            print(f'Информация по студенту id <{rows_s[0][0]}>:')
            print(
                f'\tФ.И.О.: {rows_s[0][1]}\n\tдата рождения: {datetime.datetime.date(rows_s[0][3])}\n\tgpa: {rows_s[0][2]}')
            if len(rows_c) != 0:
                print('записан на курсы:')
                for item in rows_c:
                    print(f'- {item[0]}')
            else:
                print('В настоящий момент на курсы не записан.')


if __name__ == '__main__':
    create_db()
    add_students(1, students_j)
    add_students(2, students_p)
    add_students(3, students_c)
    add_student(('Ульянов Владимир Ильич', 1, '1870-04-22'))
    get_students(2)
    get_student(3)
