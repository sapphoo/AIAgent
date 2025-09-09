import sqlite3
import re # 导入正则表达式库，用于更复杂的文本匹配
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DB_FILE = "school.db"

def get_db_connection():
    """创建数据库连接，并设置行工厂以返回类似字典的对象"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- 核心数据获取函数 (内部使用) ---

def get_scores_data(student_id):
    """根据学号查询该生所有课程的成绩数据 (内部函数)"""
    conn = get_db_connection()
    query = """
        SELECT c.course_name, c.credits, e.semester, e.score
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.student_id = ?
        ORDER BY e.semester DESC
    """
    scores_cursor = conn.execute(query, (student_id,))
    scores = [dict(row) for row in scores_cursor.fetchall()]
    conn.close()
    return scores

# --- 新增的AI分析函数 ---

def score_to_gpa_point(score):
    """将百分制分数转换为4.0制绩点"""
    if score is None:
        return 0
    if score >= 90:
        return 4.0
    if score >= 85:
        return 3.7
    if score >= 82:
        return 3.3
    if score >= 78:
        return 3.0
    if score >= 75:
        return 2.7
    if score >= 72:
        return 2.3
    if score >= 68:
        return 2.0
    if score >= 64:
        return 1.5
    if score >= 60:
        return 1.0
    return 0.0

# --- 新的API Endpoints ---

@app.route('/api/login', methods=['POST'])
def login():
    # ... (此部分代码保持不变) ...
    data = request.get_json()
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({"error": "需要提供学号"}), 400
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE student_id = ?', (student_id,)).fetchone()
    conn.close()
    if student:
        return jsonify(dict(student))
    else:
        return jsonify({"error": "学号不存在"}), 404

@app.route('/api/students/<student_id>/academic_summary', methods=['GET'])
def get_academic_summary(student_id):
    """【新功能】生成学业总结，包括GPA、总学分、挂科数"""
    scores_data = get_scores_data(student_id)
    
    if not scores_data:
        return jsonify({
            "summary_text": "你还没有任何成绩记录，无法生成学业总结。",
            "gpa": 0,
            "total_credits": 0,
            "failed_courses": 0
        })

    total_credit_points = 0
    total_credits_attempted = 0
    completed_credits = 0
    failed_courses_count = 0

    for course in scores_data:
        if course['score'] is not None:
            gpa_point = score_to_gpa_point(course['score'])
            credits = course['credits']
            
            total_credit_points += gpa_point * credits
            total_credits_attempted += credits
            
            if course['score'] >= 60:
                completed_credits += credits
            else:
                failed_courses_count += 1
    
    # 计算GPA，避免除以零的错误
    gpa = total_credit_points / total_credits_attempted if total_credits_attempted > 0 else 0.0
    
    # 构建一个自然语言的总结
    summary_text = (
        f"根据你的记录，我为你生成了学业总结：\n"
        f" - **平均绩点 (GPA)**: {gpa:.2f}\n"
        f" - **已获得学分**: {completed_credits} 分\n"
        f" - **挂科课程数**: {failed_courses_count} 门\n"
    )
    if gpa > 3.5:
        summary_text += "\n表现非常出色，请继续保持！"
    elif failed_courses_count > 0:
        summary_text += "\n注意到你有未通过的课程，请关注补考或重修安排。"

    return jsonify({
        "summary_text": summary_text,
        "gpa": round(gpa, 2),
        "completed_credits": completed_credits,
        "failed_courses_count": failed_courses_count
    })

@app.route('/api/ai/process_query', methods=['POST'])
def process_query():
    """【AI大脑核心】接收自然语言，解析意图并返回答案"""
    data = request.get_json()
    query_text = data.get('text', '').lower()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({"answer": "错误：请求中缺少用户信息。"}), 400

    # --- 意图识别与实体提取 ---
    
    # 意图：查询特定课程的成绩
    # 使用正则表达式提取课程名称，例如 "我的高等数学成绩"
    match = re.search(r'(我的|查询|查一下)(.+)(的成绩|多少分|怎么样)', query_text)
    if match:
        course_name = match.group(2).strip()
        scores = get_scores_data(student_id)
        found_score = None
        for score in scores:
            if course_name in score['course_name'].lower():
                found_score = score
                break
        if found_score:
            answer = f"你《{found_score['course_name']}》这门课的成绩是 {found_score['score']} 分。"
        else:
            answer = f"抱歉，没有找到你关于《{course_name}》的成绩记录。"
        return jsonify({"answer": answer})

    # 意图：查询全部成绩
    if any(keyword in query_text for keyword in ['成绩', '分数', '成绩单']):
        scores = get_scores_data(student_id)
        if not scores:
            return jsonify({"answer": "你还没有任何成绩记录。"})
        
        table = '这是你的成绩单：<table><tr><th>课程</th><th>学期</th><th>学分</th><th>成绩</th></tr>'
        for s in scores:
            table += f"<tr><td>{s['course_name']}</td><td>{s['semester']}</td><td>{s['credits']}</td><td>{s['score']}</td></tr>"
        table += '</table>'
        return jsonify({"answer": table})

    # 意图：查询学业总结或GPA
    if any(keyword in query_text for keyword in ['gpa', '绩点', '总结', '学业情况']):
        summary_data = get_academic_summary(student_id).get_json()
        return jsonify({"answer": summary_data['summary_text']})
    
    # 意图：查询学分
    if '学分' in query_text:
        summary_data = get_academic_summary(student_id).get_json()
        answer = f"你目前已获得 **{summary_data['completed_credits']}** 个学分。"
        return jsonify({"answer": answer})

    # 如果所有意图都未匹配
    return jsonify({"answer": '抱歉，我暂时无法理解你的问题。你可以试试问我：<br>- "我的成绩怎么样？"<br>- "我的绩点是多少？"<br>- "我高等数学的成绩是多少？"'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)