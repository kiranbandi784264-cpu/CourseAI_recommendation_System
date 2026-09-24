import os
import sys
import time

from src.generate_synthetic_data import generate_datasets
from src.data_preprocessing import preprocess_data
from src.models.user_based import train_user_based
from src.models.content_based import train_content_based
from src.models.lightgcn import train_lightgcn
from src.models.ncf import train_ncf
from src.models.item_based import train_item_based
from src.models.job_recommendation import train_job_recommendation
from src.models.implicit_lightfm import train_implicit_lightfm
from src.models.hybrid_recommendation import train_hybrid_recommendation

def run_full_pipeline():
    start_time = time.time()
    print("=" * 70)
    print("      COURSE RECOMMENDATION SYSTEM - FULL PIPELINE RUNNER      ")
    print("=" * 70)
    
    # 1. Dataset generation
    generate_datasets(raw_dir='data/raw')
    
    # 2. Preprocessing
    preprocess_data(raw_dir='data/raw', cleaned_dir='data/cleaned')
    
    # 3. Model training & Scoring matrix generation
    train_user_based(cleaned_dir='data/cleaned', out_dir='data/score_matrices')
    train_content_based(cleaned_dir='data/cleaned', out_dir='data/score_matrices')
    train_lightgcn(cleaned_dir='data/cleaned', out_dir='data/score_matrices', epochs=10)
    train_ncf(cleaned_dir='data/cleaned', out_dir='data/score_matrices', epochs=10)
    train_item_based(cleaned_dir='data/cleaned', out_dir='data/score_matrices')
    train_job_recommendation(cleaned_dir='data/cleaned', out_dir='data/score_matrices')
    train_implicit_lightfm(cleaned_dir='data/cleaned', out_dir='data/score_matrices')
    
    # 4. Hybrid ensemble & Evaluation
    hybrid_mat, metrics = train_hybrid_recommendation(cleaned_dir='data/cleaned', score_dir='data/score_matrices')
    
    elapsed = time.time() - start_time
    print("=" * 70)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS!")
    print("=" * 70)
    return metrics

if __name__ == '__main__':
    run_full_pipeline()
