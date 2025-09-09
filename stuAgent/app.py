import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS  # 1. 导入CORS

app = Flask(__name__)
CORS(app)  # 2. 在创建app实例后，用CORS包装它

DB_FILE = "school.db"

def get_db_connection():
    """创建数据库连接，并设置行工厂以返回类似字典的对象"""
    conn = sqlite3.connect(DB_FILE)
    # 这行代码让查询结果可以通过列名访问，非常方便
    conn.row_factory = sqlite3.Row
    return conn

# --- API Endpoints ---

@app.route('/api/login', methods=['POST'])
def login():
    """模拟登录。在真实项目中，这里必须进行加密密码比对！"""
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password') # 暂时未使用

    if not student_id:
        return jsonify({"error": "需要提供学号"}), 400

    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE student_id = ?', (student_id,)).fetchone()
    conn.close()

    if student:
        # 登录成功，返回学生信息
        return jsonify(dict(student))
    else:
        return jsonify({"error": "学号不存在"}), 404


@app.route('/api/students/<student_id>/scores', methods=['GET'])
def get_scores(student_id):
    """根据学号查询该生所有课程的成绩"""
    conn = get_db_connection()
    query = """
        SELECT c.course_name, c.credits, e.semester, e.score
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
        ORDER BY e.semester DESC
    """
    scores_cursor = conn.execute(query, (student_id,))
    # 将查询结果转换为字典列表
    scores = [dict(row) for row in scores_cursor.fetchall()]
    conn.close()
    return jsonify(scores)


@app.route('/api/students/<student_id>/credits_summary', methods=['GET'])
def get_credits_summary(student_id):
    """查询已修学分总和（只计算及格课程）"""
    conn = get_db_connection()
    # 假设60分及格
    query = """
        SELECT SUM(c.credits)
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = ? AND e.score >= 60
    """
    cursor = conn.execute(query, (student_id,))
    # fetchone()[0] 获取查询结果的第一行第一列
    total_credits = cursor.fetchone()[0]
    conn.close()
    
    return jsonify({
        "student_id": student_id,
        "completed_credits": float(total_credits or 0) # 如果没有及格课程，返回0
    })

# 更多API可以按此模式添加...

if __name__ == '__main__':
    # host='0.0.0.0' 允许局域网访问, debug=True 开启调试模式
    app.run(host='0.0.0.0', port=5000, debug=True)