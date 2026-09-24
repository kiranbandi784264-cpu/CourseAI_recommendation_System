import os
import math
import pandas as pd
import numpy as np

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).strip()
    return text

def preprocess_data(raw_dir='data/raw', cleaned_dir='data/cleaned'):
    os.makedirs(cleaned_dir, exist_ok=True)
    
    courses_file = os.path.join(raw_dir, 'Coursera_courses.csv')
    reviews_file = os.path.join(raw_dir, 'Coursera_reviews.csv')
    unclean_file = os.path.join(raw_dir, 'CourseraDataset-Unclean.csv')
    job_skills_file = os.path.join(raw_dir, 'job_skills.csv')
    linkedin_jobs_file = os.path.join(raw_dir, 'linkedin_job_postings.csv')
    
    if not all(os.path.exists(f) for f in [courses_file, reviews_file, unclean_file, job_skills_file, linkedin_jobs_file]):
        raise FileNotFoundError(f"One or more raw dataset files missing in {raw_dir}. Please run generate_synthetic_data.py first.")

    print("--- Step 1: Preprocessing & Data Cleaning ---")
    courses = pd.read_csv(courses_file)
    users = pd.read_csv(reviews_file)
    courses_metadata = pd.read_csv(unclean_file)
    job_skills = pd.read_csv(job_skills_file)
    job_metadata = pd.read_csv(linkedin_jobs_file)

    # 1. Clean course metadata
    courses_metadata.rename(columns={
        'Course Title': 'name',
        'Rating': 'Overall Ratings',
        'Review': 'Num of Reviews',
        'Offered By': 'institution'
    }, inplace=True)
    courses_metadata.drop_duplicates(subset=['name'], inplace=True)
    
    users.drop_duplicates(subset=['reviews', 'reviewers', 'course_id'], inplace=True)
    job_skills = job_skills.dropna(subset=['job_skills'])

    # Merge users and courses
    temp = pd.merge(users, courses, on="course_id", how="inner")

    # Combine description & skills columns
    desc_list = []
    skill_list = []
    for idx, row in courses_metadata.iterrows():
        wyl = str(row.get('What you will learn', '')) if pd.notna(row.get('What you will learn')) else ''
        cdx = str(row.get('course_description_x', '')) if pd.notna(row.get('course_description_x')) else ''
        cdy = str(row.get('course_description_y', '')) if pd.notna(row.get('course_description_y')) else ''
        desc = " ".join(set([d for d in [wyl, cdx, cdy] if d]))
        desc_list.append(desc if desc else "Course learning material")

        sg = str(row.get('Skill gain', '')) if pd.notna(row.get('Skill gain')) else ''
        sk = str(row.get('Skills', '')) if pd.notna(row.get('Skills')) else ''
        csk = str(row.get('course_skills', '')) if pd.notna(row.get('course_skills')) else ''
        all_sk = ", ".join(set([s for s in [sg, sk, csk] if s]))
        skill_list.append(all_sk if all_sk else "General Skills")

    courses_metadata['description'] = desc_list
    courses_metadata['skills'] = skill_list

    # Clean attributes
    courses_metadata['skills'] = courses_metadata['skills'].apply(clean_text)
    courses_metadata['institution'] = courses_metadata['institution'].apply(clean_text)
    courses_metadata['name'] = courses_metadata['name'].apply(clean_text)
    courses_metadata['Level'] = courses_metadata['Level'].fillna('None')
    courses_metadata['Duration'] = courses_metadata['Duration'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)

    # Merge courses with metadata
    courses_data = pd.merge(temp, courses_metadata, on=["name", "institution"], how="inner")

    # Extract final fields including Syllabus and Book Recommendations
    final_users_courses = courses_data[[
        'reviews', 'reviewers', 'rating', 'name', 'institution', 
        'Overall Ratings', 'Level', 'Duration', 'Num of Reviews', 
        'skills', 'description', 'Syllabus', 'Book Recommendations', 'date'
    ]].copy()

    # De-mean rating per reviewer
    reviewer_avg = final_users_courses.groupby('reviewers')['rating'].transform('mean')
    final_users_courses['Demeaned Rating'] = final_users_courses['rating'] - reviewer_avg

    # Popularity
    final_users_courses['Popularity'] = final_users_courses['Overall Ratings'] * final_users_courses['Num of Reviews']

    # Rename final columns
    final_users_courses = final_users_courses.rename(columns={
        'reviews': 'Review',
        'reviewers': 'Reviewer',
        'rating': 'Individual Rating',
        'name': 'Course Name',
        'institution': 'Institution',
        'skills': 'Course Skills',
        'description': 'Description',
        'date': 'Date'
    })

    # 2. Process jobs data
    jobs_data = pd.merge(job_skills, job_metadata, on="job_link", how="inner")
    final_jobs = jobs_data[['job_skills', 'job_title']].copy()
    final_jobs = final_jobs.rename(columns={'job_skills': 'Job Skills', 'job_title': 'Job Title'})
    final_jobs.drop_duplicates(inplace=True)

    # 3. Split train / eval / test (80% / 10% / 10%) per user
    train_list, eval_list, test_list = [], [], []
    grouped = final_users_courses.groupby('Reviewer')

    for name, group in grouped:
        sorted_group = group.sort_values(by='Date')
        n_total = len(sorted_group)
        if n_total < 3:
            train_list.append(sorted_group)
            continue
            
        n_eval = max(1, math.ceil(n_total * 0.1))
        n_test = max(1, math.ceil(n_total * 0.1))
        n_train = n_total - n_eval - n_test
        
        train_list.append(sorted_group.iloc[:n_train])
        eval_list.append(sorted_group.iloc[n_train:n_train+n_eval])
        test_list.append(sorted_group.iloc[n_train+n_eval:])

    train_df = pd.concat(train_list, ignore_index=True)
    eval_df = pd.concat(eval_list, ignore_index=True) if eval_list else train_df.head(10)
    test_df = pd.concat(test_list, ignore_index=True) if test_list else train_df.head(10)

    # Save to disk
    final_users_courses.to_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'), index=False)
    final_jobs.to_csv(os.path.join(cleaned_dir, 'final_jobs.csv'), index=False)
    train_df.to_csv(os.path.join(cleaned_dir, 'train.csv'), index=False)
    eval_df.to_csv(os.path.join(cleaned_dir, 'eval.csv'), index=False)
    test_df.to_csv(os.path.join(cleaned_dir, 'test.csv'), index=False)

    print(f"Data Preprocessing Complete!")
    print(f"  - Cleaned user-course interactions: {len(final_users_courses)}")
    print(f"  - Train records: {len(train_df)} | Eval records: {len(eval_df)} | Test records: {len(test_df)}")
    print(f"  - Jobs records: {len(final_jobs)}")

if __name__ == '__main__':
    preprocess_data()
