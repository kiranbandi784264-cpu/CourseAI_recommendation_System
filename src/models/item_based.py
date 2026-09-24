import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def train_item_based(cleaned_dir='data/cleaned', out_dir='data/score_matrices'):
    os.makedirs(out_dir, exist_ok=True)
    print("--- Step 6: Training Item-Based Collaborative Filtering ---")
    
    train_df = pd.read_csv(os.path.join(cleaned_dir, 'train.csv'))
    full_df = pd.read_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'))
    
    all_users = full_df['Reviewer'].unique().tolist()
    all_courses = full_df['Course Name'].unique().tolist()
    
    # User-Item interaction matrix
    user_course = train_df.pivot_table(
        index='Reviewer', 
        columns='Course Name', 
        values='Individual Rating',
        aggfunc='mean'
    ).fillna(0)
    
    user_course = user_course.reindex(index=all_users, columns=all_courses, fill_value=0)
    
    # Transpose for Item-Item matrix
    item_user_matrix = user_course.values.T
    
    # Cosine / Jaccard similarity between items
    item_sim = cosine_similarity(item_user_matrix)
    
    # Predict user scores
    sim_sum = np.abs(item_sim).sum(axis=1, keepdims=True).T + 1e-9
    pred_scores = np.dot(user_course.values, item_sim) / sim_sum
    
    score_df = pd.DataFrame(pred_scores, index=all_users, columns=all_courses)
    out_path = os.path.join(out_dir, 'scoring_matrix_item_based_cf.csv')
    score_df.to_csv(out_path)
    print(f"Item-Based CF scoring matrix saved to {out_path} (Shape: {score_df.shape})")
    return score_df

if __name__ == '__main__':
    train_item_based()
