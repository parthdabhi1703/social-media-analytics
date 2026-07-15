import os
import glob
import pandas as pd
import numpy as np

def run_data_cleaning_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, 'datasets')
    
    print("--- Phase 3: Data Cleaning & Feature Engineering Pipeline ---")
    
    # 1. Load Platform Post Files
    post_files = glob.glob(os.path.join(dataset_dir, '*_posts.csv'))
    raw_df_list = []
    
    for f in post_files:
        if 'cleaned' in f:
            continue
        df_temp = pd.read_csv(f)
        print(f"Loaded {os.path.basename(f)}: {len(df_temp)} rows")
        raw_df_list.append(df_temp)
        
    combined_df = pd.concat(raw_df_list, ignore_index=True)
    initial_count = len(combined_df)
    print(f"Total raw posts combined: {initial_count}")
    
    # 2. Deduplication
    combined_df = combined_df.drop_duplicates(subset=['post_id'], keep='first')
    dedup_count = len(combined_df)
    print(f"Removed {initial_count - dedup_count} duplicate records. Current rows: {dedup_count}")
    
    # 3. Standardize Dates
    # Format parsing for mixed date strings (%Y-%m-%d, %d/%m/%Y, %m-%d-%Y)
    combined_df['post_date'] = pd.to_datetime(combined_df['post_date'], format='mixed').dt.strftime('%Y-%m-%d')
    combined_df['post_date'] = pd.to_datetime(combined_df['post_date'])
    
    # 4. Handle Missing Values / Imputation
    combined_df['caption'] = combined_df['caption'].fillna('No Caption Provided')
    combined_df['hashtags'] = combined_df['hashtags'].fillna('#General')
    
    # Impute missing likes with group median by platform and content_type
    combined_df['likes'] = combined_df.groupby(['platform', 'content_type'])['likes'].transform(lambda x: x.fillna(x.median()))
    
    # Fill remaining metric NaNs with 0
    metric_cols = ['reach', 'impressions', 'likes', 'comments', 'shares', 'saves', 'video_views', 'clicks']
    combined_df[metric_cols] = combined_df[metric_cols].fillna(0).astype(int)
    
    # 5. Feature Engineering
    combined_df['posting_hour'] = pd.to_datetime(combined_df['post_time'], format='%H:%M:%S').dt.hour
    combined_df['day_of_week'] = combined_df['post_date'].dt.day_name()
    combined_df['day_num'] = combined_df['post_date'].dt.dayofweek
    combined_df['is_weekend'] = combined_df['day_num'].isin([5, 6]).astype(int)
    combined_df['month_year'] = combined_df['post_date'].dt.strftime('%Y-%m')
    combined_df['month_name'] = combined_df['post_date'].dt.month_name()
    
    # Derived Performance Metrics
    combined_df['total_engagement'] = (
        combined_df['likes'] + combined_df['comments'] + 
        combined_df['shares'] + combined_df['saves']
    )
    
    combined_df['engagement_rate_pct'] = np.where(
        combined_df['reach'] > 0,
        (combined_df['total_engagement'] / combined_df['reach']) * 100,
        0.0
    )
    
    combined_df['ctr_pct'] = np.where(
        combined_df['impressions'] > 0,
        (combined_df['clicks'] / combined_df['impressions']) * 100,
        0.0
    )
    
    combined_df['virality_score'] = np.where(
        combined_df['reach'] > 0,
        (combined_df['shares'] / combined_df['reach']) * 100,
        0.0
    )
    
    # Text Features
    combined_df['caption_length'] = combined_df['caption'].apply(lambda x: len(str(x)))
    combined_df['hashtag_count'] = combined_df['hashtags'].apply(lambda x: len(str(x).split()))
    
    # Simple Rule-Based Sentiment Scoring for Demo Portfolio
    positive_words = ['transforming', 'strategies', 'excited', 'breakthrough', 'innovation', 'motivation', 'boosted', 'mastering', 'growth']
    negative_words = ['wrong', 'unpopular', 'struggle', 'fail', 'problem']
    
    def calculate_sentiment(text):
        text_lower = str(text).lower()
        pos = sum(1 for w in positive_words if w in text_lower)
        neg = sum(1 for w in negative_words if w in text_lower)
        if pos > neg:
            return 'Positive'
        elif neg > pos:
            return 'Negative'
        else:
            return 'Neutral'
            
    combined_df['sentiment_category'] = combined_df['caption'].apply(calculate_sentiment)
    
    # 6. Save Cleaned Dataset
    cleaned_filepath = os.path.join(dataset_dir, 'cleaned_social_media_posts.csv')
    combined_df.to_csv(cleaned_filepath, index=False)
    print(f"Cleaned dataset saved successfully to {cleaned_filepath} ({len(combined_df)} records).")
    return combined_df

if __name__ == '__main__':
    run_data_cleaning_pipeline()
