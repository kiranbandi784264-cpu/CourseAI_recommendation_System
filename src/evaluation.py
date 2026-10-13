import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def evaluate_single_model(score_df, test_df, train_df=None, k=10, mask_train=True):
    """
    Evaluates Top-K recommendation performance on held-out test data.
    Optionally masks items that were present in the training set for each user.
    """
    actuals = test_df.groupby('Reviewer')['Course Name'].agg(set).to_dict()
    train_taken = train_df.groupby('Reviewer')['Course Name'].agg(set).to_dict() if (train_df is not None and mask_train) else {}
    
    precisions = []
    norm_precisions = []
    recalls = []
    hit_rates = []
    ndcgs = []
    mrrs = []
    
    for user, actual_set in actuals.items():
        if user not in score_df.index or not actual_set:
            continue
            
        scores = score_df.loc[user].copy()
        if mask_train and user in train_taken:
            for c in train_taken[user]:
                if c in scores.index:
                    scores[c] = -1e9
                    
        recs = scores.sort_values(ascending=False).index[:k].tolist()
        hits = len(set(recs) & actual_set)
        
        precisions.append(hits / float(k))
        norm_precisions.append(hits / float(min(k, len(actual_set))))
        recalls.append(hits / float(len(actual_set)))
        hit_rates.append(1.0 if hits > 0 else 0.0)
        
        # DCG & IDCG
        dcg = sum(1.0 / np.log2(idx + 2) for idx, item in enumerate(recs) if item in actual_set)
        idcg = sum(1.0 / np.log2(idx + 2) for idx in range(min(k, len(actual_set))))
        ndcgs.append(dcg / (idcg + 1e-9) if idcg > 0 else 0.0)
        
        # MRR
        first_hit = next((idx + 1 for idx, item in enumerate(recs) if item in actual_set), None)
        mrrs.append(1.0 / first_hit if first_hit else 0.0)
        
    p = np.mean(precisions) if precisions else 0.0
    r = np.mean(recalls) if recalls else 0.0
    f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0
    
    return {
        'Precision@10': p,
        'Norm_Prec@10': np.mean(norm_precisions) if norm_precisions else 0.0,
        'Recall@10': r,
        'HitRate@10': np.mean(hit_rates) if hit_rates else 0.0,
        'NDCG@10': np.mean(ndcgs) if ndcgs else 0.0,
        'MRR': np.mean(mrrs) if mrrs else 0.0,
        'F1@10': f1
    }

def evaluate_all_models(cleaned_dir='data/cleaned', score_dir='data/score_matrices', output_fig='figures/model_accuracy_comparison.png', k=10):
    print("=" * 75)
    print("      COMPREHENSIVE MODEL EVALUATION & ACCURACY BENCHMARK      ")
    print("=" * 75)
    
    train_path = os.path.join(cleaned_dir, 'train.csv')
    test_path = os.path.join(cleaned_dir, 'test.csv')
    
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test dataset not found at {test_path}")
        
    train_df = pd.read_csv(train_path) if os.path.exists(train_path) else None
    test_df = pd.read_csv(test_path)
    
    models_config = [
        ('Hybrid (Ensemble)', 'scoring_matrix_hybrid.csv', 'Ensemble Fusion of all 7 base models'),
        ('LightGCN', 'scoring_matrix_lightgcn.csv', 'Graph Convolutional Neural Network'),
        ('NCF', 'scoring_matrix_ncf.csv', 'Neural Collaborative Filtering (NeuMF)'),
        ('Job-Skills', 'scoring_matrix_jobs.csv', 'Job-market skill gap vector matching'),
        ('User-Based CF', 'scoring_matrix_ubcf.csv', 'Neighborhood CF with VADER sentiment'),
        ('Content-Based', 'scoring_matrix_content_based.csv', 'TF-IDF semantic course descriptions'),
        ('Item-Based CF', 'scoring_matrix_item_based_cf.csv', 'Jaccard item co-enrollment patterns'),
        ('Implicit (LightFM)', 'scoring_matrix_implicit.csv', 'Implicit feedback matrix factorization')
    ]
    
    results = []
    for name, filename, desc in models_config:
        fpath = os.path.join(score_dir, filename)
        if not os.path.exists(fpath):
            print(f"  [Skipping] {name:18}: {filename} not found.")
            continue
            
        score_df = pd.read_csv(fpath, index_col=0)
        metrics = evaluate_single_model(score_df, test_df, train_df=train_df, k=k, mask_train=True)
        results.append({
            'Model': name,
            'File': filename,
            'Description': desc,
            'Precision@10': metrics['Precision@10'],
            'Recall@10': metrics['Recall@10'],
            'HitRate@10': metrics['HitRate@10'],
            'NDCG@10': metrics['NDCG@10'],
            'MRR': metrics['MRR'],
            'F1@10': metrics['F1@10']
        })
        
    df_results = pd.DataFrame(results)
    
    # Print formatted comparison table
    print(f"\n{'Model Architecture':22} | {'P@10':>7} | {'R@10':>7} | {'HitRate@10':>10} | {'NDCG@10':>8} | {'MRR':>7} | {'F1@10':>7}")
    print("-" * 80)
    for _, row in df_results.iterrows():
        print(f"{row['Model']:22} | {row['Precision@10']:7.4f} | {row['Recall@10']:7.4f} | {row['HitRate@10']*100:9.1f}% | {row['NDCG@10']:8.4f} | {row['MRR']:7.4f} | {row['F1@10']:7.4f}")
    print("-" * 80)
    
    # Save results to CSV & JSON
    out_csv = os.path.join('data', 'model_evaluation_results.csv')
    out_json = os.path.join('data', 'model_evaluation_results.json')
    df_results.to_csv(out_csv, index=False)
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[Saved] Metrics table saved to {out_csv} and {out_json}")
    
    # Generate visualization
    os.makedirs(os.path.dirname(output_fig), exist_ok=True)
    generate_accuracy_plot(df_results, output_fig)
    # Also save as fig6 for presentations
    fig6_path = 'figures/fig6_model_metrics_barchart.png'
    generate_accuracy_plot(df_results, fig6_path)
    print(f"[Saved] Accuracy comparison charts saved to {output_fig} and {fig6_path}\n")
    
    return df_results

def generate_accuracy_plot(df_results, output_path):
    plt.style.use('dark_background')
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.patch.set_facecolor('#060d1f')
    
    # Chart 1: Precision@10 & Recall@10
    ax1 = axes[0]
    ax1.set_facecolor('#0b1530')
    y_pos = np.arange(len(df_results))
    models = df_results['Model'].tolist()
    
    bar_width = 0.38
    bars1 = ax1.barh(y_pos - bar_width/2, df_results['Precision@10'], bar_width, label='Precision@10', color='#38bdf8', alpha=0.9)
    bars2 = ax1.barh(y_pos + bar_width/2, df_results['Recall@10'], bar_width, label='Recall@10', color='#818cf8', alpha=0.9)
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(models, fontsize=10, fontweight='bold', color='#f0f6ff')
    ax1.set_xlabel('Score Value', color='#94a3b8', fontweight='bold')
    ax1.set_title('Top-10 Precision & Recall by Model', color='#38bdf8', fontsize=12, fontweight='bold', pad=12)
    ax1.legend(loc='lower right', framealpha=0.3)
    ax1.grid(axis='x', color='#63a5ff', alpha=0.15, linestyle='--')
    ax1.invert_yaxis()
    
    # Add values at the end of bars
    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 0.0003, bar.get_y() + bar.get_height()/2, f'{w:.3f}', va='center', ha='left', fontsize=8, color='#38bdf8')
    for bar in bars2:
        w = bar.get_width()
        ax1.text(w + 0.0008, bar.get_y() + bar.get_height()/2, f'{w:.3f}', va='center', ha='left', fontsize=8, color='#818cf8')
        
    # Chart 2: Hit Rate@10 (%) & NDCG@10
    ax2 = axes[1]
    ax2.set_facecolor('#0b1530')
    hit_rates_pct = df_results['HitRate@10'] * 100.0
    
    bars3 = ax2.barh(y_pos - bar_width/2, hit_rates_pct, bar_width, label='Hit Rate@10 (%)', color='#34d399', alpha=0.9)
    bars4 = ax2.barh(y_pos + bar_width/2, df_results['NDCG@10'] * 100.0, bar_width, label='NDCG@10 (x100)', color='#fbbf24', alpha=0.9)
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(models, fontsize=10, fontweight='bold', color='#f0f6ff')
    ax2.set_xlabel('Percentage / Scaled Score (%)', color='#94a3b8', fontweight='bold')
    ax2.set_title('Hit Rate@10 (%) & Ranking NDCG@10', color='#34d399', fontsize=12, fontweight='bold', pad=12)
    ax2.legend(loc='lower right', framealpha=0.3)
    ax2.grid(axis='x', color='#63a5ff', alpha=0.15, linestyle='--')
    ax2.invert_yaxis()
    
    for bar in bars3:
        w = bar.get_width()
        ax2.text(w + 0.2, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', ha='left', fontsize=8, color='#34d399')
    for bar in bars4:
        w = bar.get_width()
        ax2.text(w + 0.2, bar.get_y() + bar.get_height()/2, f'{w:.1f}', va='center', ha='left', fontsize=8, color='#fbbf24')
        
    plt.suptitle('CourseAI Recommendation Models: Empirical Benchmark Evaluation', color='#ffffff', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

if __name__ == '__main__':
    evaluate_all_models()
