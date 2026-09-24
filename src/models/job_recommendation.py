import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def train_job_recommendation(cleaned_dir='data/cleaned', out_dir='data/score_matrices'):
    os.makedirs(out_dir, exist_ok=True)
    print("--- Step 7: Training Job-Skills Gap Recommendation Model ---")
    
    train_df = pd.read_csv(os.path.join(cleaned_dir, 'train.csv'))
    full_df = pd.read_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'))
    jobs_df = pd.read_csv(os.path.join(cleaned_dir, 'final_jobs.csv'))
    
    all_users = full_df['Reviewer'].unique().tolist()
    
    courses_info = full_df[['Course Name', 'Course Skills', 'Description']].drop_duplicates(subset=['Course Name'])
    courses_info['Text'] = courses_info['Course Skills'].fillna('') + ' ' + courses_info['Description'].fillna('')
    all_courses = courses_info['Course Name'].tolist()
    
    # Combined jobs skill string
    job_skills_combined = " ".join(jobs_df['Job Skills'].dropna().tolist())
    
    # TF-IDF on course text vs job skill requirements
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf.fit(courses_info['Text'].tolist() + [job_skills_combined])
    
    course_vectors = tfidf.transform(courses_info['Text'])
    job_vector = tfidf.transform([job_skills_combined])
    
    # Base course-job alignment
    course_job_sim = cosine_similarity(course_vectors, job_vector).flatten()
    
    # Compute user skill gap score matrix
    user_job_matrix = np.zeros((len(all_users), len(all_courses)))
    
    for u_idx, user in enumerate(all_users):
        user_history = train_df[train_df['Reviewer'] == user]
        completed_courses = user_history['Course Name'].values
        
        # User current skills vector
        if len(completed_courses) > 0:
            comp_indices = [all_courses.index(c) for c in completed_courses if c in all_courses]
            if comp_indices:
                user_skill_vec = np.mean(course_vectors[comp_indices].toarray(), axis=0, keepdims=True)
                # Skill gap = Job required skills - User current skills
                gap_vec = np.maximum(0, job_vector.toarray() - user_skill_vec)
            else:
                gap_vec = job_vector.toarray()
        else:
            gap_vec = job_vector.toarray()
            
        # Score remaining courses against skill gap
        user_job_matrix[u_idx] = cosine_similarity(course_vectors, gap_vec).flatten()
        
    score_df = pd.DataFrame(user_job_matrix, index=all_users, columns=all_courses)
    out_path = os.path.join(out_dir, 'scoring_matrix_jobs.csv')
    score_df.to_csv(out_path)
    print(f"Job-Skill Gap scoring matrix saved to {out_path} (Shape: {score_df.shape})")
    return score_df

if __name__ == '__main__':
    train_job_recommendation()
