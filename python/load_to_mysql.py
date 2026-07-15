import os
import pandas as pd
import pymysql
import getpass

def load_data():
    print("--- Social Media Analytics: MySQL Database Loader ---")
    host = input("MySQL Host [localhost]: ") or "localhost"
    user = input("MySQL User [root]: ") or "root"
    password = getpass.getpass("MySQL Password: ")
    database = input("MySQL Database [social_media_analytics]: ") or "social_media_analytics"
    
    try:
        conn = pymysql.connect(host=host, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        print("\n[+] Connected to MySQL successfully!")
    except Exception as e:
        print(f"\n[-] Error connecting to database: {e}")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datasets_dir = os.path.join(base_dir, 'datasets')
    
    # 1. Load Demographics
    try:
        print("Loading demographics.csv...")
        demo_df = pd.read_csv(os.path.join(datasets_dir, 'demographics.csv'))
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE Demographics;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        for _, row in demo_df.iterrows():
            cursor.execute(
                "INSERT INTO Demographics (platform_id, country, age_group, gender, followers) VALUES (%s, %s, %s, %s, %s)",
                (int(row['platform_id']), row['country'], row['age_group'], row['gender'], int(row['followers']))
            )
        print("[+] Demographics table loaded successfully.")
    except Exception as e:
        print(f"[-] Error loading demographics: {e}")
        
    # 2. Load Followers
    try:
        print("Loading followers_history.csv...")
        followers_df = pd.read_csv(os.path.join(datasets_dir, 'followers_history.csv'))
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE Followers;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        for _, row in followers_df.iterrows():
            cursor.execute(
                "INSERT INTO Followers (snapshot_date, platform_id, followers, following) VALUES (%s, %s, %s, %s)",
                (row['snapshot_date'], int(row['platform_id']), int(row['followers']), int(row['following']))
            )
        print("[+] Followers table loaded successfully.")
    except Exception as e:
        print(f"[-] Error loading followers: {e}")
        
    # 3. Load Posts
    try:
        print("Loading cleaned_social_media_posts.csv...")
        posts_df = pd.read_csv(os.path.join(datasets_dir, 'cleaned_social_media_posts.csv'))
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE Posts;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        # Replace NaN with None for nullable columns
        posts_df = posts_df.where(pd.notnull(posts_df), None)
        
        for _, row in posts_df.iterrows():
            cursor.execute(
                """INSERT INTO Posts 
                   (post_id, platform_id, post_date, post_time, content_type, caption, hashtags, reach, impressions, likes, comments, shares, saves, video_views, clicks) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    row['post_id'], int(row['platform_id']), row['post_date'], row['post_time'], row['content_type'],
                    row['caption'], row['hashtags'], int(row['reach']), int(row['impressions']), int(row['likes']),
                    int(row['comments']), int(row['shares']), int(row['saves']), int(row['video_views']), int(row['clicks'])
                )
            )
        print("[+] Posts table loaded successfully.")
    except Exception as e:
        print(f"[-] Error loading posts: {e}")
        
    cursor.close()
    conn.close()
    print("\n[+] Database loading complete.")

if __name__ == '__main__':
    load_data()
