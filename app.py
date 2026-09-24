import os
import json
import re
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from run_pipeline import run_full_pipeline

app = Flask(__name__, template_folder='templates', static_folder='static')

CLEANED_DIR = 'data/cleaned'
SCORE_DIR = 'data/score_matrices'

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/presentation')
def presentation():
    return send_from_directory('static', 'presentation.html')

@app.route('/download-presentation')
def download_presentation():
    return send_from_directory('static', 'presentation.html', as_attachment=True, download_name='CourseAI_Interactive_Presentation.html')

@app.route('/figures/<path:filename>')
def serve_figure(filename):
    return send_from_directory('figures', filename)

@app.route('/api/stats')
def get_stats():
    courses_file = os.path.join(CLEANED_DIR, 'final_users_courses.csv')
    jobs_file = os.path.join(CLEANED_DIR, 'final_jobs.csv')
    
    total_courses = 0
    total_users = 0
    total_jobs = 0
    users_list = []
    jobs_list = []
    
    if os.path.exists(courses_file):
        df = pd.read_csv(courses_file)
        total_courses = df['Course Name'].nunique()
        users_list = sorted(df['Reviewer'].unique().tolist())
        total_users = len(users_list)
        
    if os.path.exists(jobs_file):
        jobs_df = pd.read_csv(jobs_file)
        jobs_list = sorted(jobs_df['Job Title'].unique().tolist())
        total_jobs = len(jobs_list)
        
    return jsonify({
        'total_courses': total_courses,
        'total_users': total_users,
        'total_jobs': total_jobs,
        'users': users_list[:50],
        'jobs': jobs_list
    })

@app.route('/api/recommend')
def recommend():
    user = request.args.get('user', 'user_001')
    job = request.args.get('job', 'Senior Data Scientist')
    model_name = request.args.get('model', 'hybrid')
    
    file_map = {
        'hybrid': 'scoring_matrix_hybrid.csv',
        'ubcf': 'scoring_matrix_ubcf.csv',
        'content': 'scoring_matrix_content_based.csv',
        'lightgcn': 'scoring_matrix_lightgcn.csv',
        'ncf': 'scoring_matrix_ncf.csv',
        'item': 'scoring_matrix_item_based_cf.csv',
        'jobs': 'scoring_matrix_jobs.csv',
        'implicit': 'scoring_matrix_implicit.csv'
    }
    
    matrix_file = os.path.join(SCORE_DIR, file_map.get(model_name, 'scoring_matrix_hybrid.csv'))
    
    if not os.path.exists(matrix_file):
        return jsonify({'error': f'Scoring matrix for model {model_name} not found. Run pipeline first.', 'recommendations': []})
        
    score_df = pd.read_csv(matrix_file, index_col=0)
    
    if user not in score_df.index:
        user = score_df.index[0]
        
    user_scores = score_df.loc[user].sort_values(ascending=False).head(10)
    
    courses_file = os.path.join(CLEANED_DIR, 'final_users_courses.csv')
    if os.path.exists(courses_file):
        courses_df = pd.read_csv(courses_file).drop_duplicates(subset=['Course Name'])
        course_meta = courses_df.set_index('Course Name').to_dict('index')
    else:
        course_meta = {}
        
    recommendations = []
    max_score = user_scores.max() if user_scores.max() > 0 else 1.0
    
    for c_name, score in user_scores.items():
        meta = course_meta.get(c_name, {})
        norm_score = float(score / max_score)
        
        syllabus_raw = meta.get('Syllabus', '[]')
        books_raw = meta.get('Book Recommendations', '[]')
        
        try:
            syllabus = json.loads(syllabus_raw) if isinstance(syllabus_raw, str) else []
        except:
            syllabus = []
            
        try:
            books = json.loads(books_raw) if isinstance(books_raw, str) else []
        except:
            books = []
            
        recommendations.append({
            'course_name': str(c_name),
            'institution': str(meta.get('Institution', 'Coursera')),
            'level': str(meta.get('Level', 'Intermediate')),
            'duration': f"{meta.get('Duration', 4)} Weeks",
            'rating': meta.get('Overall Ratings', 4.8),
            'num_reviews': meta.get('Num of Reviews', 1200),
            'skills': str(meta.get('Course Skills', 'Python, Data Analytics')),
            'description': str(meta.get('Description', 'Master skills with expert-led courses.')),
            'syllabus': syllabus,
            'books': books,
            'score': round(norm_score, 4)
        })
        
    return jsonify({
        'user': user,
        'job': job,
        'model': model_name,
        'recommendations': recommendations
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_prompt = data.get('prompt', '').strip()
    selected_job = data.get('job', 'AI / LLM Research Engineer')
    
    if not user_prompt:
        return jsonify({'response': "Hi! I am your AI Study Assistant. Ask me anything about course syllabi, prerequisites, or learning roadmaps!"})
        
    courses_file = os.path.join(CLEANED_DIR, 'final_users_courses.csv')
    if not os.path.exists(courses_file):
        return jsonify({'response': "Dataset loading... Please click 'Run Pipeline Training' to initialize course metadata."})
        
    courses_df = pd.read_csv(courses_file).drop_duplicates(subset=['Course Name'])
    
    # Combined search text for TF-IDF RAG search
    search_texts = (
        courses_df['Course Name'].fillna('') + " " +
        courses_df['Course Skills'].fillna('') + " " +
        courses_df['Description'].fillna('')
    ).tolist()
    
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(search_texts)
    prompt_vec = tfidf.transform([user_prompt])
    
    sims = cosine_similarity(prompt_vec, matrix).flatten()
    top_indices = sims.argsort()[::-1][:3]
    
    matched_courses = []
    for idx in top_indices:
        if sims[idx] > 0.05:
            row = courses_df.iloc[idx]
            syl_raw = row.get('Syllabus', '[]')
            try:
                syl = json.loads(syl_raw) if isinstance(syl_raw, str) else []
            except:
                syl = []
                
            matched_courses.append({
                'name': row['Course Name'],
                'institution': row['Institution'],
                'level': row['Level'],
                'skills': row['Course Skills'],
                'desc': row['Description'],
                'syllabus': syl
            })
            
    # Formulate intelligent answer
    low_prompt = user_prompt.lower()
    
    if 'prerequisite' in low_prompt or 'before' in low_prompt or 'start' in low_prompt:
        if matched_courses:
            top_c = matched_courses[0]
            answer = f"**Prerequisites for {top_c['name']}**:\n\n"
            answer += f"• **Recommended Skill Level**: {top_c['level']}\n"
            answer += f"• **Key Foundational Skills**: {top_c['skills']}\n"
            answer += f"• **Overview**: {top_c['desc']}\n\n"
            answer += "💡 **Study Tip**: Make sure you have a solid grasp of basic Python and linear algebra before diving into advanced modules."
        else:
            answer = "For foundational courses in Data Science & AI, we recommend starting with **Python for Data Science** and basic linear algebra before taking advanced tracks."
            
    elif 'week' in low_prompt or 'syllabus' in low_prompt or 'module' in low_prompt or 'topic' in low_prompt:
        if matched_courses:
            top_c = matched_courses[0]
            answer = f"📖 **Syllabus Breakdown for {top_c['name']}**:\n\n"
            if top_c['syllabus']:
                for mod in top_c['syllabus']:
                    answer += f"• **{mod.get('week', 'Module')} - {mod.get('title', '')}**: {mod.get('topics', '')}\n"
            else:
                answer += f"Covers {top_c['skills']} across 4 comprehensive modules."
        else:
            answer = "You can view the week-by-week syllabus for any course by clicking directly on its card in the recommendation list!"
            
    elif 'job' in low_prompt or 'career' in low_prompt or 'role' in low_prompt:
        answer = f"🎯 **Career Learning Pathway for {selected_job}**:\n\n"
        if matched_courses:
            answer += "Here are the top recommended courses to master the required skills:\n\n"
            for idx, c in enumerate(matched_courses, 1):
                answer += f"{idx}. **{c['name']}** ({c['institution']}) - Skills: *{c['skills']}*\n"
        else:
            answer += "To succeed as a " + selected_job + ", build core proficiency in Python, Machine Learning models, and Cloud/DevOps infrastructure."
            
    else:
        if matched_courses:
            top_c = matched_courses[0]
            answer = f"Here is what I found for **{top_c['name']}**:\n\n"
            answer += f"• **Offered by**: {top_c['institution']} ({top_c['level']} Level)\n"
            answer += f"• **Skills Covered**: {top_c['skills']}\n"
            answer += f"• **Description**: {top_c['desc']}\n"
        else:
            answer = f"I explored all 250+ courses! Try asking about specific topics like *'What is covered in Generative AI?'* or *'What are the prerequisites for PyTorch?'*"

    return jsonify({
        'response': answer,
        'matched_courses': matched_courses
    })

@app.route('/api/run_pipeline', methods=['POST'])
def api_run_pipeline():
    try:
        metrics = run_full_pipeline()
        return jsonify({'status': 'success', 'metrics': metrics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("Starting Course Recommendation Web Server at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=True)
