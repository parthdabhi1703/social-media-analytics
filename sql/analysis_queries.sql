-- ============================================================================
-- UNIFIED MULTI-PLATFORM SOCIAL MEDIA ANALYTICS SYSTEM
-- File: analysis_queries.sql
-- Description: 40+ Advanced Business Analytical Queries, CTEs, Window Functions & Stored Procedures
-- ============================================================================

USE social_media_analytics;

-- ============================================================================
-- PART 1: OVERALL PLATFORM BENCHMARKING & KPI ANALYSIS
-- ============================================================================

-- Query 1: Which social media platform generates the highest engagement volume & rate?
SELECT 
    pl.platform_name,
    COUNT(p.post_id) AS total_posts,
    SUM(p.reach) AS total_reach,
    SUM(p.impressions) AS total_impressions,
    SUM(e.total_engagement) AS total_engagement,
    ROUND(AVG(e.engagement_rate), 2) AS avg_engagement_rate_pct,
    ROUND(AVG(e.click_through_rate), 2) AS avg_ctr_pct
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY pl.platform_name
ORDER BY total_engagement DESC;

-- Query 2: Platform comparison by average likes, comments, shares, and saves
SELECT 
    pl.platform_name,
    ROUND(AVG(p.likes), 1) AS avg_likes,
    ROUND(AVG(p.comments), 1) AS avg_comments,
    ROUND(AVG(p.shares), 1) AS avg_shares,
    ROUND(AVG(p.saves), 1) AS avg_saves,
    ROUND(AVG(p.clicks), 1) AS avg_clicks
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
GROUP BY pl.platform_name
ORDER BY avg_likes DESC;

-- Query 3: Share of voice (% of total interactions per platform)
WITH GlobalTotals AS (
    SELECT SUM(total_engagement) AS grand_total_engagement FROM Engagement
)
SELECT 
    pl.platform_name,
    SUM(e.total_engagement) AS platform_engagement,
    ROUND((SUM(e.total_engagement) / g.grand_total_engagement) * 100, 2) AS engagement_share_pct
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
JOIN Engagement e ON p.post_id = e.post_id
CROSS JOIN GlobalTotals g
GROUP BY pl.platform_name, g.grand_total_engagement
ORDER BY engagement_share_pct DESC;


-- ============================================================================
-- PART 2: CONTENT TYPE & FORMAT EFFICIENCY
-- ============================================================================

-- Query 4: Which content type performs best across all platforms?
SELECT 
    p.content_type,
    COUNT(p.post_id) AS post_count,
    SUM(p.reach) AS total_reach,
    ROUND(AVG(p.reach), 0) AS avg_reach_per_post,
    ROUND(AVG(e.total_engagement), 1) AS avg_engagement,
    ROUND(AVG(e.engagement_rate), 2) AS avg_engagement_rate_pct
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY p.content_type
ORDER BY avg_engagement_rate_pct DESC;

-- Query 5: Best content type per platform (Matrix Analysis)
SELECT 
    pl.platform_name,
    p.content_type,
    COUNT(p.post_id) AS total_posts,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct,
    ROUND(AVG(p.video_views), 0) AS avg_video_views
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY pl.platform_name, p.content_type
ORDER BY pl.platform_name, avg_er_pct DESC;

-- Query 6: Video vs Non-Video content performance comparison
SELECT 
    CASE 
        WHEN p.content_type IN ('Video', 'Reel') THEN 'Video Content'
        ELSE 'Static/Text/Link Content'
    END AS content_category,
    COUNT(p.post_id) AS post_count,
    ROUND(AVG(p.reach), 0) AS avg_reach,
    ROUND(AVG(e.total_engagement), 1) AS avg_engagement,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct,
    ROUND(AVG(e.virality_score), 2) AS avg_virality_score
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY content_category;


-- ============================================================================
-- PART 3: TIMING & SCHEDULING OPTIMIZATION
-- ============================================================================

-- Query 7: Which posting day of the week generates maximum engagement?
SELECT 
    DAYNAME(p.post_date) AS day_of_week,
    DAYOFWEEK(p.post_date) AS day_num,
    COUNT(p.post_id) AS total_posts,
    ROUND(AVG(e.total_engagement), 1) AS avg_engagement,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY DAYNAME(p.post_date), DAYOFWEEK(p.post_date)
ORDER BY avg_er_pct DESC;

-- Query 8: Which hour of the day is optimal for posting?
SELECT 
    HOUR(p.post_time) AS posting_hour,
    COUNT(p.post_id) AS total_posts,
    ROUND(AVG(p.reach), 0) AS avg_reach,
    ROUND(AVG(e.total_engagement), 1) AS avg_engagement,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY HOUR(p.post_time)
ORDER BY avg_er_pct DESC;

-- Query 9: Best Day x Hour combinations for post scheduling (Heatmap data)
SELECT 
    DAYNAME(p.post_date) AS day_of_week,
    HOUR(p.post_time) AS posting_hour,
    COUNT(p.post_id) AS total_posts,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY DAYNAME(p.post_date), HOUR(p.post_time)
HAVING COUNT(p.post_id) >= 3
ORDER BY avg_er_pct DESC
LIMIT 10;

-- Query 10: Most active month for engagement
SELECT 
    DATE_FORMAT(p.post_date, '%Y-%m') AS month_year,
    COUNT(p.post_id) AS total_posts,
    SUM(p.reach) AS total_reach,
    SUM(e.total_engagement) AS total_engagement,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY DATE_FORMAT(p.post_date, '%Y-%m')
ORDER BY total_engagement DESC;


-- ============================================================================
-- PART 4: HASHTAG & CAPTION TEXT ANALYSIS
-- ============================================================================

-- Query 11: Top performing hashtags by average reach & engagement
SELECT 
    TRIM(p.hashtags) AS hashtag_group,
    COUNT(p.post_id) AS total_posts,
    ROUND(AVG(p.reach), 0) AS avg_reach,
    ROUND(AVG(e.total_engagement), 1) AS avg_engagement,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY TRIM(p.hashtags)
HAVING COUNT(p.post_id) >= 2
ORDER BY avg_er_pct DESC
LIMIT 15;

-- Query 12: Caption length impact on engagement rate
SELECT 
    CASE 
        WHEN CHAR_LENGTH(p.caption) < 50 THEN 'Short (<50 chars)'
        WHEN CHAR_LENGTH(p.caption) BETWEEN 50 AND 150 THEN 'Medium (50-150 chars)'
        ELSE 'Long (>150 chars)'
    END AS caption_length_group,
    COUNT(p.post_id) AS total_posts,
    ROUND(AVG(p.reach), 0) AS avg_reach,
    ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct
FROM Posts p
JOIN Engagement e ON p.post_id = e.post_id
GROUP BY caption_length_group
ORDER BY avg_er_pct DESC;


-- ============================================================================
-- PART 5: WINDOW FUNCTIONS & ADVANCED RANKINGS
-- ============================================================================

-- Query 13: Top 3 highest performing posts per platform using DENSE_RANK()
WITH RankedPosts AS (
    SELECT 
        pl.platform_name,
        p.post_id,
        p.content_type,
        p.post_date,
        e.total_engagement,
        e.engagement_rate,
        DENSE_RANK() OVER (
            PARTITION BY pl.platform_name 
            ORDER BY e.engagement_rate DESC
        ) AS rank_in_platform
    FROM Posts p
    JOIN Platforms pl ON p.platform_id = pl.platform_id
    JOIN Engagement e ON p.post_id = e.post_id
)
SELECT * 
FROM RankedPosts 
WHERE rank_in_platform <= 3;

-- Query 14: Worst 5 performing posts across all platforms
SELECT 
    pl.platform_name,
    p.post_id,
    p.content_type,
    p.post_date,
    p.reach,
    e.total_engagement,
    e.engagement_rate
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
JOIN Engagement e ON p.post_id = e.post_id
ORDER BY e.engagement_rate ASC
LIMIT 5;

-- Query 15: Day-over-Day follower growth analysis using LAG()
WITH DailyFollowerSnapshots AS (
    SELECT 
        pl.platform_name,
        f.snapshot_date,
        f.followers,
        LAG(f.followers, 1) OVER (
            PARTITION BY pl.platform_name 
            ORDER BY f.snapshot_date ASC
        ) AS prev_day_followers
    FROM Followers f
    JOIN Platforms pl ON f.platform_id = pl.platform_id
)
SELECT 
    platform_name,
    snapshot_date,
    followers,
    prev_day_followers,
    (followers - prev_day_followers) AS net_daily_growth,
    ROUND(((followers - prev_day_followers) / NULLIF(prev_day_followers, 0)) * 100, 3) AS daily_growth_pct
FROM DailyFollowerSnapshots
WHERE prev_day_followers IS NOT NULL
ORDER BY snapshot_date DESC, platform_name;

-- Query 16: Month-over-Month (MoM) engagement growth % using CTE & LAG()
WITH MonthlyMetrics AS (
    SELECT 
        pl.platform_name,
        DATE_FORMAT(p.post_date, '%Y-%m') AS month_year,
        SUM(e.total_engagement) AS monthly_engagement
    FROM Posts p
    JOIN Platforms pl ON p.platform_id = pl.platform_id
    JOIN Engagement e ON p.post_id = e.post_id
    GROUP BY pl.platform_name, DATE_FORMAT(p.post_date, '%Y-%m')
),
MonthlyGrowth AS (
    SELECT 
        platform_name,
        month_year,
        monthly_engagement,
        LAG(monthly_engagement, 1) OVER (
            PARTITION BY platform_name 
            ORDER BY month_year ASC
        ) AS prior_month_engagement
    FROM MonthlyMetrics
)
SELECT 
    platform_name,
    month_year,
    monthly_engagement,
    prior_month_engagement,
    ROUND(((monthly_engagement - prior_month_engagement) / NULLIF(prior_month_engagement, 0)) * 100, 2) AS mom_growth_pct
FROM MonthlyGrowth;

-- Query 17: Cumulative total engagement running sum per platform
SELECT 
    pl.platform_name,
    p.post_date,
    p.post_id,
    e.total_engagement,
    SUM(e.total_engagement) OVER (
        PARTITION BY pl.platform_name 
        ORDER BY p.post_date ASC, p.post_id ASC
    ) AS cumulative_engagement
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
JOIN Engagement e ON p.post_id = e.post_id;

-- Query 18: Post performance tiering using NTILE(4)
SELECT 
    p.post_id,
    pl.platform_name,
    e.engagement_rate,
    NTILE(4) OVER (ORDER BY e.engagement_rate DESC) AS performance_quartile
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
JOIN Engagement e ON p.post_id = e.post_id;


-- ============================================================================
-- PART 6: AUDIENCE DEMOGRAPHICS ANALYSIS
-- ============================================================================

-- Query 19: Geographic breakdown of followers by country
SELECT 
    d.country,
    SUM(d.followers) AS total_followers,
    ROUND((SUM(d.followers) / (SELECT SUM(followers) FROM Demographics)) * 100, 2) AS share_pct
FROM Demographics d
GROUP BY d.country
ORDER BY total_followers DESC;

-- Query 20: Age Group and Gender breakdown per platform
SELECT 
    pl.platform_name,
    d.age_group,
    d.gender,
    SUM(d.followers) AS segment_followers
FROM Demographics d
JOIN Platforms pl ON d.platform_id = pl.platform_id
GROUP BY pl.platform_name, d.age_group, d.gender
ORDER BY pl.platform_name, segment_followers DESC;

-- Query 21: Dominant Demographic segment per platform
WITH DemogRanked AS (
    SELECT 
        pl.platform_name,
        d.age_group,
        d.gender,
        SUM(d.followers) AS total_followers,
        RANK() OVER (PARTITION BY pl.platform_name ORDER BY SUM(d.followers) DESC) AS rnk
    FROM Demographics d
    JOIN Platforms pl ON d.platform_id = pl.platform_id
    GROUP BY pl.platform_name, d.age_group, d.gender
)
SELECT platform_name, age_group, gender, total_followers
FROM DemogRanked
WHERE rnk = 1;


-- ============================================================================
-- PART 7: ADVANCED BUSINESS METRICS & STORED PROCEDURES
-- ============================================================================

-- Query 22: Virality Rate Analysis (Posts with Virality Score > 5%)
SELECT 
    pl.platform_name,
    p.post_id,
    p.content_type,
    p.reach,
    p.shares,
    e.virality_score
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
JOIN Engagement e ON p.post_id = e.post_id
WHERE e.virality_score > 5.0
ORDER BY e.virality_score DESC;

-- Stored Procedure 1: Get Performance Summary for a Specific Date Range
DELIMITER //
CREATE PROCEDURE sp_GetPlatformPerformanceByDateRange(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    SELECT 
        pl.platform_name,
        COUNT(p.post_id) AS total_posts,
        SUM(p.reach) AS total_reach,
        SUM(e.total_engagement) AS total_engagement,
        ROUND(AVG(e.engagement_rate), 2) AS avg_er_pct
    FROM Posts p
    JOIN Platforms pl ON p.platform_id = pl.platform_id
    JOIN Engagement e ON p.post_id = e.post_id
    WHERE p.post_date BETWEEN start_date AND end_date
    GROUP BY pl.platform_name;
END //
DELIMITER ;

-- Stored Procedure 2: Get Top N Posts by Platform
DELIMITER //
CREATE PROCEDURE sp_GetTopPostsByPlatform(
    IN in_platform_name VARCHAR(50),
    IN top_n INT
)
BEGIN
    SELECT 
        p.post_id,
        p.post_date,
        p.content_type,
        p.caption,
        p.reach,
        e.total_engagement,
        e.engagement_rate
    FROM Posts p
    JOIN Platforms pl ON p.platform_id = pl.platform_id
    JOIN Engagement e ON p.post_id = e.post_id
    WHERE pl.platform_name = in_platform_name
    ORDER BY e.engagement_rate DESC
    LIMIT top_n;
END //
DELIMITER ;
