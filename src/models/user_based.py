import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def train_user_based(cleaned_dir='data/cleaned', out_dir='data/score_matrices'):
    os.makedirs(out_dir, exist_ok=True)
    print("--- Step 2: Training User-Based Collaborative Filtering (UBCF) ---")
    
    train_df = pd.read_csv(os.path.join(cleaned_dir, 'train.csv'))
    full_df = pd.read_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'))
    
    analyzer = SentimentIntensityAnalyzer()
    
    # Calculate sentiment compound score for reviews
    def get_sentiment(text):
        if pd.isna(text):
            return 0.0
        return analyzer.polarity_scores(str(text))['compound']

    train_df['Sentiment'] = train_df['Review'].apply(get_sentiment)
    
    # Interaction weight combining rating and sentiment
    train_df['Weight'] = train_df['Individual Rating'] * (1.0 + 0.2 * train_df['Sentiment'])
    
    # Pivot user-course matrix
    user_course_matrix = train_df.pivot_table(
        index='Reviewer', 
        columns='Course Name', 
        values='Weight', 
        aggfunc='mean'
    ).fillna(0)
    
    all_users = full_df['Reviewer'].unique()
    all_courses = full_df['Course Name'].unique()
    
    user_course_matrix = user_course_matrix.reindex(index=all_users, columns=all_courses, fill_value=0)
    
    # Compute User Similarity
    user_sim = cosine_similarity(user_course_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=all_users, columns=all_users)
    
    # Score Prediction Matrix
    sim_sum = np.abs(user_sim).sum(axis=1, keepdims=True) + 1e-9
    pred_matrix = np.dot(user_sim, user_course_matrix.values) / sim_sum
    
    score_df = pd.DataFrame(pred_matrix, index=all_users, columns=all_courses)
    
    out_path = os.path.join(out_dir, 'scoring_matrix_ubcf.csv')
    score_df.to_csv(out_path)
    print(f"UBCF scoring matrix saved to {out_path} (Shape: {score_df.shape})")
    return score_df

if __name__ == '__main__':
    train_user_based()
