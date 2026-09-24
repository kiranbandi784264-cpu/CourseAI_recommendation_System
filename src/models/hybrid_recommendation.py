import os
import pandas as pd
import numpy as np

def min_max_normalize(df):
    val = df.values
    min_v = val.min()
    max_v = val.max()
    if max_v - min_v == 0:
        return df
    norm_val = (val - min_v) / (max_v - min_v)
    return pd.DataFrame(norm_val, index=df.index, columns=df.columns)

def evaluate_top_k(hybrid_df, test_df, k=10):
    precisions, recalls, ndcgs = [], [], []
    
    test_grouped = test_df.groupby('Reviewer')
    for user, group in test_grouped:
        if user not in hybrid_df.index:
            continue
        actual_courses = set(group['Course Name'].tolist())
        if not actual_courses:
            continue
            
        user_scores = hybrid_df.loc[user].sort_values(ascending=False)
        recommended_courses = user_scores.index[:k].tolist()
        
        hits = len(set(recommended_courses).intersection(actual_courses))
        precision = hits / k
        recall = hits / len(actual_courses)
        
        # DCG & IDCG for NDCG@k
        dcg = 0.0
        for idx, item in enumerate(recommended_courses):
            if item in actual_courses:
                dcg += 1.0 / np.log2(idx + 2)
        idcg = sum(1.0 / np.log2(idx + 2) for idx in range(min(k, len(actual_courses))))
        ndcg = dcg / (idcg + 1e-9)
        
        precisions.append(precision)
        recalls.append(recall)
        ndcgs.append(ndcg)
        
    return {
        'Precision@10': np.mean(precisions) if precisions else 0.0,
        'Recall@10': np.mean(recalls) if recalls else 0.0,
        'NDCG@10': np.mean(ndcgs) if ndcgs else 0.0
    }

def train_hybrid_recommendation(cleaned_dir='data/cleaned', score_dir='data/score_matrices'):
    print("--- Step 9: Training & Evaluating Hybrid Recommendation Model ---")
    
    test_df = pd.read_csv(os.path.join(cleaned_dir, 'test.csv'))
    
    model_files = {
        'ubcf': ('scoring_matrix_ubcf.csv', 0.15),
        'content': ('scoring_matrix_content_based.csv', 0.15),
        'lightgcn': ('scoring_matrix_lightgcn.csv', 0.15),
        'ncf': ('scoring_matrix_ncf.csv', 0.15),
        'item': ('scoring_matrix_item_based_cf.csv', 0.10),
        'jobs': ('scoring_matrix_jobs.csv', 0.15),
        'implicit': ('scoring_matrix_implicit.csv', 0.15)
    }
    
    hybrid_matrix = None
    loaded_models = []
    
    for key, (filename, weight) in model_files.items():
        filepath = os.path.join(score_dir, filename)
        if not os.path.exists(filepath):
            print(f"  Warning: {filename} missing. Skipping model {key}.")
            continue
            
        df = pd.read_csv(filepath, index_col=0)
        df_norm = min_max_normalize(df)
        
        if hybrid_matrix is None:
            hybrid_matrix = df_norm * weight
        else:
            # Reindex to ensure index alignment
            df_norm = df_norm.reindex(index=hybrid_matrix.index, columns=hybrid_matrix.columns).fillna(0)
            hybrid_matrix += df_norm * weight
            
        loaded_models.append(key)
        
    if hybrid_matrix is None:
        raise RuntimeError("No scoring matrices found to construct hybrid model!")
        
    out_path = os.path.join(score_dir, 'scoring_matrix_hybrid.csv')
    hybrid_matrix.to_csv(out_path)
    print(f"Hybrid Recommendation Matrix saved to {out_path} (Ensembled {len(loaded_models)} models)")
    
    metrics = evaluate_top_k(hybrid_matrix, test_df, k=10)
    print("\nHybrid Recommendation Performance Metrics:")
    for metric_name, val in metrics.items():
        print(f"  - {metric_name}: {val:.4f}")
        
    return hybrid_matrix, metrics

if __name__ == '__main__':
    train_hybrid_recommendation()
