import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'datasets')
os.makedirs(output_dir, exist_ok=True)

print(f"Generating datasets in: {output_dir}")

# Shared parameters
num_posts = 550  # Slightly more than 500 to allow for duplicates
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)

hashtags_pool = [
    "#TechTrends", "#AI", "#MarketingStrategy", "#DataAnalytics", "#DigitalMarketing",
    "#GrowthHacking", "#BusinessTips", "#Leadership", "#SocialMedia2025", "#Innovation",
    "#StartupLife", "#MachineLearning", "#DesignThinking", "#Productivity", "#Coding"
]

content_types_map = {
    'Facebook': ['Image', 'Video', 'Link', 'Text', 'Carousel'],
    'Instagram': ['Image', 'Reel', 'Carousel', 'Story Promotion'],
    'LinkedIn': ['Image', 'Video', 'Article/Link', 'Text', 'Document/Carousel'],
    'Twitter': ['Text', 'Image', 'Video', 'Link']
}

caption_templates = [
    "Discover how {topic} is transforming the industry! What are your thoughts? {hashtags}",
    "Top 5 actionable strategies for {topic} in 2025. Save this post for later! {hashtags}",
    "We are excited to announce our newest breakthrough in {topic}. Check out the link below! {hashtags}",
    "Unpopular opinion about {topic}: Most teams are doing it wrong. Here is why... {hashtags}",
    "Behind the scenes at our team workshop on {topic}. Innovation starts here! {hashtags}",
    "Quick question for our community: How do you handle {topic} in your daily workflow? {hashtags}",
    "Mastering {topic} in under 10 minutes. Read our full step-by-step guide now! {hashtags}",
    "Why {topic} matters more than ever for modern business growth. {hashtags}",
    "Case study alert: How we boosted results by 350% using {topic}. {hashtags}",
    "Sunday motivation: Start your week with a fresh mindset on {topic}. {hashtags}"
]

topics = [
    "Data Analytics", "AI Workflow", "Social Media ROI", "Content Marketing",
    "Customer Engagement", "Brand Strategy", "Python Automation", "Executive Leadership",
    "Cloud Scale", "User Experience"
]

def generate_random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)
    return start + timedelta(days=random_days, seconds=random_seconds)

def generate_posts_for_platform(platform_name):
    posts = []
    types = content_types_map[platform_name]
    
    for i in range(1, num_posts + 1):
        post_dt = generate_random_date(start_date, end_date)
        # Dates formatting: inject inconsistent formats intentionally
        date_fmt_choice = random.random()
        if date_fmt_choice < 0.85:
            date_str = post_dt.strftime("%Y-%m-%d")
        elif date_fmt_choice < 0.93:
            date_str = post_dt.strftime("%d/%m/%Y")
        else:
            date_str = post_dt.strftime("%m-%d-%Y")
            
        time_str = post_dt.strftime("%H:%M:%S")
        
        c_type = random.choice(types)
        topic = random.choice(topics)
        sample_tags = random.sample(hashtags_pool, k=random.randint(1, 4))
        hashtags_str = " ".join(sample_tags)
        caption = random.choice(caption_templates).format(topic=topic, hashtags=hashtags_str)
        
        # Base multiplier per platform and content type
        platform_mult = {'Instagram': 1.8, 'LinkedIn': 1.2, 'Facebook': 1.0, 'Twitter': 0.7}[platform_name]
        type_mult = {'Video': 2.0, 'Reel': 2.5, 'Carousel': 1.6, 'Document/Carousel': 1.7, 'Image': 1.2, 'Text': 0.8, 'Link': 0.6, 'Article/Link': 0.7, 'Story Promotion': 0.5}[c_type]
        
        # Time seasonality: Evening posts (18:00 - 21:00) perform 40% better
        hour = post_dt.hour
        time_mult = 1.4 if 18 <= hour <= 21 or 12 <= hour <= 14 else 0.9
        
        # Viral outlier chance (1.5% chance)
        is_viral = random.random() < 0.015
        viral_mult = random.uniform(8.0, 15.0) if is_viral else 1.0
        
        base_reach = int(random.uniform(500, 5000) * platform_mult * type_mult * time_mult * viral_mult)
        base_impressions = int(base_reach * random.uniform(1.1, 1.8))
        
        base_likes = int(base_reach * random.uniform(0.02, 0.08))
        base_comments = int(base_likes * random.uniform(0.05, 0.25))
        base_shares = int(base_likes * random.uniform(0.02, 0.15))
        base_saves = int(base_likes * random.uniform(0.01, 0.30)) if platform_name in ['Instagram', 'LinkedIn'] else 0
        base_video_views = int(base_reach * random.uniform(0.4, 0.9)) if c_type in ['Video', 'Reel'] else 0
        base_clicks = int(base_reach * random.uniform(0.01, 0.06))
        
        # Introduce anomalies: NULLs
        if random.random() < 0.03:
            caption = np.nan
        if random.random() < 0.02:
            hashtags_str = np.nan
        if random.random() < 0.01:
            base_likes = np.nan

        platform_id = {'Facebook': 1, 'Instagram': 2, 'LinkedIn': 3, 'Twitter': 4}[platform_name]
        post_row = {
            'post_id': f"{platform_name[:2].upper()}_{i:04d}",
            'platform_id': platform_id,
            'platform': platform_name,
            'post_date': date_str,
            'post_time': time_str,
            'content_type': c_type,
            'caption': caption,
            'hashtags': hashtags_str,
            'reach': base_reach,
            'impressions': base_impressions,
            'likes': base_likes,
            'comments': base_comments,
            'shares': base_shares,
            'saves': base_saves,
            'video_views': base_video_views,
            'clicks': base_clicks
        }
        posts.append(post_row)

    df = pd.DataFrame(posts)
    
    # Inject intentional duplicates (15 rows)
    duplicate_rows = df.sample(n=15, random_state=42)
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    return df

# Generate post files
for p in ['Facebook', 'Instagram', 'LinkedIn', 'Twitter']:
    df_p = generate_posts_for_platform(p)
    filename = f"{p.lower()}_posts.csv"
    filepath = os.path.join(output_dir, filename)
    df_p.to_csv(filepath, index=False)
    print(f"Created {filename} with {len(df_p)} rows.")

# 5. Followers History CSV (365 days)
def generate_followers_history():
    records = []
    base_followers = {
        'Facebook': 45000,
        'Instagram': 85000,
        'LinkedIn': 32000,
        'Twitter': 28000
    }
    base_following = {
        'Facebook': 120,
        'Instagram': 450,
        'LinkedIn': 890,
        'Twitter': 350
    }
    
    curr_followers = base_followers.copy()
    
    for day_offset in range(365):
        curr_date = start_date + timedelta(days=day_offset)
        date_str = curr_date.strftime("%Y-%m-%d")
        
        for platform in ['Facebook', 'Instagram', 'LinkedIn', 'Twitter']:
            # Growth rates differ
            growth_mean = {'Instagram': 80, 'LinkedIn': 45, 'Facebook': 20, 'Twitter': 15}[platform]
            daily_growth = int(np.random.normal(growth_mean, growth_mean * 0.3))
            curr_followers[platform] += max(-5, daily_growth)
            
            platform_id = {'Facebook': 1, 'Instagram': 2, 'LinkedIn': 3, 'Twitter': 4}[platform]
            records.append({
                'snapshot_date': date_str,
                'platform_id': platform_id,
                'platform': platform,
                'followers': curr_followers[platform],
                'following': base_following[platform] + random.randint(-2, 3)
            })
            
    df_fol = pd.DataFrame(records)
    filepath = os.path.join(output_dir, 'followers_history.csv')
    df_fol.to_csv(filepath, index=False)
    print(f"Created followers_history.csv with {len(df_fol)} rows.")

# 6. Demographics CSV
def generate_demographics():
    platforms = ['Facebook', 'Instagram', 'LinkedIn', 'Twitter']
    age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
    genders = ['Male', 'Female', 'Other']
    countries = ['United States', 'India', 'United Kingdom', 'Canada', 'Germany', 'Australia', 'Brazil']
    
    records = []
    for platform in platforms:
        for country in countries:
            for age in age_groups:
                for gender in genders:
                    # Realistic distribution
                    if platform == 'Instagram' and age in ['18-24', '25-34']:
                        weight = 2.5
                    elif platform == 'LinkedIn' and age in ['25-34', '35-44']:
                        weight = 2.8
                    elif platform == 'Facebook' and age in ['35-44', '45-54']:
                        weight = 2.0
                    else:
                        weight = 1.0
                        
                    followers_count = int(random.randint(200, 2500) * weight)
                    platform_id = {'Facebook': 1, 'Instagram': 2, 'LinkedIn': 3, 'Twitter': 4}[platform]
                    records.append({
                        'platform_id': platform_id,
                        'platform': platform,
                        'country': country,
                        'age_group': age,
                        'gender': gender,
                        'followers': followers_count
                    })
                    
    df_demo = pd.DataFrame(records)
    filepath = os.path.join(output_dir, 'demographics.csv')
    df_demo.to_csv(filepath, index=False)
    print(f"Created demographics.csv with {len(df_demo)} rows.")

if __name__ == '__main__':
    generate_followers_history()
    generate_demographics()
    print("All datasets generated successfully!")
