import sqlite3
import os

DB_FILE = "school.db"

# 如果数据库文件已存在，先删除，以便重新创建
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# 连接到数据库（如果文件不存在，会自动创建）
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 1. 创建学生表 (students)
cursor.execute('''
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    student_name TEXT NOT NULL,
    program TEXT NOT NULL,
    password_hash TEXT NOT NULL
);
''')

# 2. 创建课程表 (courses)
cursor.execute('''
CREATE TABLE courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    credits REAL NOT NULL
);
''')

# 3. 创建成绩/选课表 (enrollments)
cursor.execute('''
CREATE TABLE enrollments (
    enroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    semester TEXT NOT NULL,
    score REAL,
    FOREIGN KEY (student_id) REFERENCES students (student_id),
    FOREIGN KEY (course_id) REFERENCES courses (course_id)
);
''')

# --- 填充模拟数据 ---

# 插入学生数据
students_data = [
    ('2021001', '张三', '计算机科学', 'hashed_password_1'),
    ('2021002', '李四', '软件工程', 'hashed_password_2')
]
cursor.executemany('INSERT INTO students VALUES (?, ?, ?, ?)', students_data)

# 插入课程数据
courses_data = [
    ('CS101', '计算机科学导论', 3.0),
    ('MA101', '高等数学 I', 4.0),
    ('PH101', '大学物理', 4.0),
    ('CS202', '数据结构', 3.5)
]
cursor.executemany('INSERT INTO courses VALUES (?, ?, ?)', courses_data)

# 插入选课和成绩数据
enrollments_data = [
    # 张三的成绩
    ('2021001', 'CS101', '2023-Fall', 92.0),
    ('2021001', 'MA101', '2023-Fall', 85.0),
    ('2021001', 'PH101', '2024-Spring', 55.0), # 一门挂科
    ('2021001', 'CS202', '2024-Spring', 95.0),
    # 李四的成绩
    ('2021002', 'CS101', '2023-Fall', 88.0),
    ('2021002', 'MA101', '2023-Fall', 76.0)
]
cursor.executemany('INSERT INTO enrollments (student_id, course_id, semester, score) VALUES (?, ?, ?, ?)', enrollments_data)

# 提交更改并关闭连接
conn.commit()
conn.close()

print(f"数据库 '{DB_FILE}' 创建并填充数据成功！")