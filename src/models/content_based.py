import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack

def train_content_based(cleaned_dir='data/cleaned', out_dir='data/score_matrices'):
    os.makedirs(out_dir, exist_ok=True)
    print("--- Step 3: Training Content-Based Recommendation Model ---")
    
    train_df = pd.read_csv(os.path.join(cleaned_dir, 'train.csv'))
    full_df = pd.read_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'))
    
    # Drop duplicate course info to build unique course features
    courses_info = full_df[['Course Name', 'Institution', 'Overall Ratings', 'Num of Reviews', 'Duration', 'Course Skills', 'Description']].drop_duplicates(subset=['Course Name'])
    courses_info['Text_Features'] = courses_info['Course Skills'].fillna('') + ' ' + courses_info['Description'].fillna('')
    
    all_courses = courses_info['Course Name'].tolist()
    all_users = full_df['Reviewer'].unique().tolist()
    
    # 1. TF-IDF on text
    tfidf = TfidfVectorizer(stop_words='english', max_features=500)
    text_matrix = tfidf.fit_transform(courses_info['Text_Features'])
    
    # 2. Scale numeric features
    scaler = MinMaxScaler()
    num_features = scaler.fit_transform(courses_info[['Overall Ratings', 'Num of Reviews', 'Duration']].fillna(0))
    
    # Combine text and numeric features
    course_features = hstack([text_matrix, num_features]).tocsr()
    course_features_df = pd.DataFrame(course_features.toarray(), index=all_courses)
    
    # 3. Construct user profile vectors
    user_profiles = []
    for user in all_users:
        user_interactions = train_df[train_df['Reviewer'] == user]
        if len(user_interactions) == 0:
            user_profiles.append(np.zeros(course_features.shape[1]))
            continue
            
        weights = user_interactions['Individual Rating'].values
        interacted_courses = user_interactions['Course Name'].values
        
        # Get indices of interacted courses
        course_indices = [all_courses.index(c) for c in interacted_courses if c in all_courses]
        if not course_indices:
            user_profiles.append(np.zeros(course_features.shape[1]))
            continue
            
        feat_sub = course_features.toarray()[course_indices]
        w = weights[:len(course_indices)].reshape(-1, 1)
        profile = np.sum(feat_sub * w, axis=0) / (np.sum(w) + 1e-9)
        user_profiles.append(profile)
        
    user_profiles_matrix = np.array(user_profiles)
    
    # Compute similarity matrix (User Profile vs Course Features)
    score_matrix = cosine_similarity(user_profiles_matrix, course_features.toarray())
    
    score_df = pd.DataFrame(score_matrix, index=all_users, columns=all_courses)
    out_path = os.path.join(out_dir, 'scoring_matrix_content_based.csv')
    score_df.to_csv(out_path)
    print(f"Content-Based scoring matrix saved to {out_path} (Shape: {score_df.shape})")
    return score_df

if __name__ == '__main__':
    train_content_based()
