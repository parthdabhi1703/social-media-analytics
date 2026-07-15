import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset_dir = os.path.join(base_dir, 'datasets')
images_dir = os.path.join(base_dir, 'images')
os.makedirs(images_dir, exist_ok=True)

print("--- Phase 3: Social Media Analysis & Visualization Generator ---")

# Load Cleaned Data
df_posts = pd.read_csv(os.path.join(dataset_dir, 'cleaned_social_media_posts.csv'))
df_followers = pd.read_csv(os.path.join(dataset_dir, 'followers_history.csv'))
df_demo = pd.read_csv(os.path.join(dataset_dir, 'demographics.csv'))

colors = {'Facebook': '#1877F2', 'Instagram': '#E4405F', 'LinkedIn': '#0A66C2', 'Twitter': '#1DA1F2'}

# 1. Platform Engagement Comparison
plt.figure(figsize=(9, 5))
platform_metrics = df_posts.groupby('platform')['engagement_rate_pct'].mean()
bars = plt.bar(platform_metrics.index, platform_metrics.values, color=[colors[p] for p in platform_metrics.index])
plt.title('Average Engagement Rate (%) by Platform', fontweight='bold', fontsize=14)
plt.xlabel('Platform', fontsize=12)
plt.ylabel('Avg Engagement Rate (%)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(images_dir, '01_platform_engagement_comparison.png'), dpi=300)
plt.close()
print("Saved 01_platform_engagement_comparison.png")

# 2. Content Type Performance
plt.figure(figsize=(10, 5))
content_df = df_posts.groupby('content_type')['engagement_rate_pct'].mean().sort_values(ascending=False)
bars = plt.bar(content_df.index, content_df.values, color='#4F46E5')
plt.title('Average Engagement Rate (%) by Content Format', fontweight='bold', fontsize=14)
plt.xlabel('Content Format', fontsize=12)
plt.ylabel('Avg Engagement Rate (%)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(images_dir, '02_content_type_performance.png'), dpi=300)
plt.close()
print("Saved 02_content_type_performance.png")

# 3. Posting Time Heatmap
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
pivot_time = df_posts.pivot_table(index='day_of_week', columns='posting_hour', values='engagement_rate_pct', aggfunc='mean').reindex(day_order)

plt.figure(figsize=(12, 6))
im = plt.imshow(pivot_time.values, cmap='YlGnBu', aspect='auto')
plt.colorbar(im, label='Avg Engagement Rate (%)')
plt.xticks(ticks=range(len(pivot_time.columns)), labels=pivot_time.columns)
plt.yticks(ticks=range(len(pivot_time.index)), labels=pivot_time.index)
plt.title('Best Posting Times: Engagement Rate Heatmap (Day vs Hour)', fontweight='bold', fontsize=14)
plt.xlabel('Hour of Day (24-hour)', fontsize=12)
plt.ylabel('Day of Week', fontsize=12)

plt.tight_layout()
plt.savefig(os.path.join(images_dir, '03_posting_time_heatmap.png'), dpi=300)
plt.close()
print("Saved 03_posting_time_heatmap.png")

# 4. Follower Growth Trajectory
plt.figure(figsize=(11, 5))
df_followers['snapshot_date'] = pd.to_datetime(df_followers['snapshot_date'])
for p in ['Facebook', 'Instagram', 'LinkedIn', 'Twitter']:
    sub = df_followers[df_followers['platform'] == p]
    plt.plot(sub['snapshot_date'], sub['followers'], label=p, color=colors[p], linewidth=2)

plt.title('365-Day Follower Growth Trajectory by Platform', fontweight='bold', fontsize=14)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Total Followers', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(images_dir, '04_monthly_follower_growth.png'), dpi=300)
plt.close()
print("Saved 04_monthly_follower_growth.png")

# 5. Country Demographics Distribution
plt.figure(figsize=(7, 7))
country_df = df_demo.groupby('country')['followers'].sum()
plt.pie(country_df.values, labels=country_df.index, autopct='%1.1f%%', startangle=140, 
        wedgeprops=dict(width=0.4, edgecolor='w'))
plt.title('Audience Demographic Distribution by Top Countries', fontweight='bold', fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(images_dir, '05_demographics_country_distribution.png'), dpi=300)
plt.close()
print("Saved 05_demographics_country_distribution.png")

# 6. Correlation Matrix Heatmap
plt.figure(figsize=(9, 7))
num_cols = ['reach', 'impressions', 'likes', 'comments', 'shares', 'saves', 'clicks', 'caption_length', 'hashtag_count', 'engagement_rate_pct']
corr = df_posts[num_cols].corr()

im = plt.imshow(corr.values, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar(im, label='Pearson Correlation')
plt.xticks(ticks=range(len(num_cols)), labels=num_cols, rotation=45, ha='right')
plt.yticks(ticks=range(len(num_cols)), labels=num_cols)
plt.title('Social Media Metrics Correlation Matrix', fontweight='bold', fontsize=14)

plt.tight_layout()
plt.savefig(os.path.join(images_dir, '06_correlation_matrix.png'), dpi=300)
plt.close()
print("Saved 06_correlation_matrix.png")

# 7. Platform Reach Outliers Boxplot
plt.figure(figsize=(9, 5))
data_by_platform = [df_posts[df_posts['platform'] == p]['reach'].values for p in ['Facebook', 'Instagram', 'LinkedIn', 'Twitter']]
plt.boxplot(data_by_platform, tick_labels=['Facebook', 'Instagram', 'LinkedIn', 'Twitter'], patch_artist=True)
plt.title('Platform Reach Distribution & Outliers', fontweight='bold', fontsize=14)
plt.xlabel('Platform', fontsize=12)
plt.ylabel('Reach per Post', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig(os.path.join(images_dir, '08_platform_reach_boxplot.png'), dpi=300)
plt.close()
print("Saved 08_platform_reach_boxplot.png")

print("All static visualizations generated successfully!")
