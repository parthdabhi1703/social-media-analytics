-- ============================================================================
-- UNIFIED MULTI-PLATFORM SOCIAL MEDIA ANALYTICS SYSTEM
-- File: data_cleaning.sql
-- Description: SQL Queries for Data Cleansing, Normalization & Feature Population
-- ============================================================================

USE social_media_analytics;

-- Disable Safe Updates for this session to allow batch updates and deletes
SET SQL_SAFE_UPDATES = 0;

-- ----------------------------------------------------------------------------
-- STEP 1: Identify & Remove Duplicate Posts
-- Uses CTE and Window Function ROW_NUMBER() to target duplicates
-- ----------------------------------------------------------------------------

-- Check duplicate count
SELECT post_id, COUNT(*) AS dup_count
FROM Posts
GROUP BY post_id
HAVING COUNT(*) > 1;

-- SQL Procedure / Query to Delete Duplicate Rows keeping only the first record
WITH DuplicatedPosts AS (
    SELECT 
        post_id,
        ROW_NUMBER() OVER (
            PARTITION BY post_id 
            ORDER BY post_date DESC, post_time DESC
        ) AS row_num
    FROM Posts
)
DELETE FROM Posts
WHERE post_id IN (
    SELECT post_id FROM DuplicatedPosts WHERE row_num > 1
);

-- ----------------------------------------------------------------------------
-- STEP 2: Handle Missing & NULL Values
-- Impute missing text fields and zero-fill missing numeric metrics
-- ----------------------------------------------------------------------------

-- Update NULL Captions to default placeholder
UPDATE Posts
SET caption = 'No Caption Provided'
WHERE caption IS NULL OR TRIM(caption) = '';

-- Update NULL Hashtags
UPDATE Posts
SET hashtags = '#General'
WHERE hashtags IS NULL OR TRIM(hashtags) = '';

-- Impute NULL Likes with median / mean by platform & content_type
UPDATE Posts p
JOIN (
    SELECT platform_id, content_type, AVG(COALESCE(likes, 0)) as avg_likes
    FROM Posts
    WHERE likes IS NOT NULL
    GROUP BY platform_id, content_type
) avg_table ON p.platform_id = avg_table.platform_id AND p.content_type = avg_table.content_type
SET p.likes = ROUND(avg_table.avg_likes)
WHERE p.likes IS NULL;

-- ----------------------------------------------------------------------------
-- STEP 3: Standardize Inconsistent Date Formats
-- Convert heterogeneous date strings (e.g., '15/04/2025', '04-15-2025') into standard 'YYYY-MM-DD'
-- ----------------------------------------------------------------------------

-- Example procedure for staging raw date standardization:
-- UPDATE staging_posts
-- SET clean_post_date = CASE 
--     WHEN post_date LIKE '%/%/%' THEN STR_TO_DATE(post_date, '%d/%m/%Y')
--     WHEN post_date LIKE '%-%-%' AND CHAR_LENGTH(SUBSTRING_INDEX(post_date, '-', 1)) = 2 THEN STR_TO_DATE(post_date, '%m-%d-%Y')
--     ELSE STR_TO_DATE(post_date, '%Y-%m-%d')
-- END;

-- ----------------------------------------------------------------------------
-- STEP 4: Populate & Recalculate Derived Engagement Table
-- Compute Total Engagement, Engagement Rate (%), CTR (%), and Virality Score
-- ----------------------------------------------------------------------------

-- Clear existing derived rows
TRUNCATE TABLE Engagement;

-- Insert fresh clean calculations
INSERT INTO Engagement (post_id, total_engagement, engagement_rate, click_through_rate, virality_score)
SELECT 
    post_id,
    (likes + comments + shares + saves) AS total_engagement,
    CASE 
        WHEN reach > 0 THEN ROUND(((likes + comments + shares + saves) / reach) * 100, 4)
        ELSE 0.0000
    END AS engagement_rate,
    CASE 
        WHEN impressions > 0 THEN ROUND((clicks / impressions) * 100, 4)
        ELSE 0.0000
    END AS click_through_rate,
    CASE 
        WHEN reach > 0 THEN ROUND((shares / reach) * 100, 4)
        ELSE 0.0000
    END AS virality_score
FROM Posts;

-- Verify data integrity post-cleaning
SELECT 
    (SELECT COUNT(*) FROM Posts) AS total_posts,
    (SELECT COUNT(*) FROM Engagement) AS total_engagement_records,
    (SELECT COUNT(*) FROM Posts WHERE likes IS NULL) AS null_likes_count,
    (SELECT COUNT(*) FROM Posts WHERE caption IS NULL) AS null_captions_count;

-- Re-enable Safe Updates for this session
SET SQL_SAFE_UPDATES = 1;
