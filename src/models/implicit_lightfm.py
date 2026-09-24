import os
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD

def train_implicit_lightfm(cleaned_dir='data/cleaned', out_dir='data/score_matrices', n_components=32):
    os.makedirs(out_dir, exist_ok=True)
    print("--- Step 8: Training Implicit Feedback Matrix Factorization ---")
    
    train_df = pd.read_csv(os.path.join(cleaned_dir, 'train.csv'))
    full_df = pd.read_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'))
    
    all_users = full_df['Reviewer'].unique().tolist()
    all_courses = full_df['Course Name'].unique().tolist()
    
    # Binary implicit matrix (1 if interacted, 0 otherwise)
    binary_matrix = train_df.pivot_table(
        index='Reviewer', 
        columns='Course Name', 
        values='Individual Rating',
        aggfunc=lambda x: 1.0
    ).fillna(0)
    
    binary_matrix = binary_matrix.reindex(index=all_users, columns=all_courses, fill_value=0)
    
    # Truncated SVD Matrix Factorization
    n_comp = min(n_components, len(all_courses) - 1, len(all_users) - 1)
    svd = TruncatedSVD(n_components=n_comp, random_state=42)
    user_factors = svd.fit_transform(binary_matrix.values)
    item_factors = svd.components_
    
    # Reconstructed scoring matrix
    pred_scores = np.dot(user_factors, item_factors)
    
    score_df = pd.DataFrame(pred_scores, index=all_users, columns=all_courses)
    out_path = os.path.join(out_dir, 'scoring_matrix_implicit.csv')
    score_df.to_csv(out_path)
    print(f"Implicit Matrix Factorization scoring matrix saved to {out_path} (Shape: {score_df.shape})")
    return score_df

if __name__ == '__main__':
    train_implicit_lightfm()
