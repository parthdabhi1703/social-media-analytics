-- ============================================================================
-- UNIFIED MULTI-PLATFORM SOCIAL MEDIA ANALYTICS SYSTEM
-- File: database_schema.sql
-- Description: MySQL Database Schema DDL for Social Media Analytics System
-- ============================================================================

CREATE DATABASE IF NOT EXISTS social_media_analytics;
USE social_media_analytics;

-- ----------------------------------------------------------------------------
-- 1. Table: Platforms
-- Description: Master dimension table storing social media platform details
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS Engagement;
DROP TABLE IF EXISTS Demographics;
DROP TABLE IF EXISTS Followers;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS Platforms;

CREATE TABLE Platforms (
    platform_id INT AUTO_INCREMENT PRIMARY KEY,
    platform_name VARCHAR(50) NOT NULL UNIQUE,
    platform_type VARCHAR(50) NOT NULL DEFAULT 'Social Network',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate Dim Platforms
INSERT INTO Platforms (platform_name, platform_type) VALUES
('Facebook', 'Social Network'),
('Instagram', 'Visual & Short Video'),
('LinkedIn', 'Professional Network'),
('Twitter', 'Microblogging & Real-time');

-- ----------------------------------------------------------------------------
-- 2. Table: Posts (Raw Staging & Main Storage)
-- Description: Fact table holding raw & cleaned post metrics across platforms
-- ----------------------------------------------------------------------------
CREATE TABLE Posts (
    post_id VARCHAR(50) PRIMARY KEY,
    platform_id INT NOT NULL,
    post_date DATE NOT NULL,
    post_time TIME NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    caption TEXT,
    hashtags VARCHAR(500),
    reach INT DEFAULT 0,
    impressions INT DEFAULT 0,
    likes INT DEFAULT 0,
    comments INT DEFAULT 0,
    shares INT DEFAULT 0,
    saves INT DEFAULT 0,
    video_views INT DEFAULT 0,
    clicks INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (platform_id) REFERENCES Platforms(platform_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Indexes for performance on analytical queries
CREATE INDEX idx_posts_date ON Posts(post_date);
CREATE INDEX idx_posts_platform ON Posts(platform_id);
CREATE INDEX idx_posts_content ON Posts(content_type);
CREATE INDEX idx_posts_platform_date ON Posts(platform_id, post_date);

-- ----------------------------------------------------------------------------
-- 3. Table: Followers
-- Description: Snapshot history table tracking daily follower & following counts
-- ----------------------------------------------------------------------------
CREATE TABLE Followers (
    follower_id INT AUTO_INCREMENT PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    platform_id INT NOT NULL,
    followers INT NOT NULL DEFAULT 0,
    following INT NOT NULL DEFAULT 0,
    FOREIGN KEY (platform_id) REFERENCES Platforms(platform_id) ON DELETE CASCADE,
    UNIQUE KEY uq_platform_date (platform_id, snapshot_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_followers_date ON Followers(snapshot_date);

-- ----------------------------------------------------------------------------
-- 4. Table: Demographics
-- Description: Demographic distribution of audience by age, gender, country
-- ----------------------------------------------------------------------------
CREATE TABLE Demographics (
    demo_id INT AUTO_INCREMENT PRIMARY KEY,
    platform_id INT NOT NULL,
    country VARCHAR(100) NOT NULL,
    age_group VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    followers INT NOT NULL DEFAULT 0,
    FOREIGN KEY (platform_id) REFERENCES Platforms(platform_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_demo_platform_country ON Demographics(platform_id, country);
CREATE INDEX idx_demo_age_gender ON Demographics(age_group, gender);

-- ----------------------------------------------------------------------------
-- 5. Table: Engagement Metrics (Calculated Fact Table)
-- Description: Derived performance metrics per post (Total Engagement, ER %, CTR)
-- ----------------------------------------------------------------------------
CREATE TABLE Engagement (
    engagement_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id VARCHAR(50) NOT NULL UNIQUE,
    total_engagement INT NOT NULL DEFAULT 0,
    engagement_rate DECIMAL(8, 4) DEFAULT 0.0000,
    click_through_rate DECIMAL(8, 4) DEFAULT 0.0000,
    virality_score DECIMAL(8, 4) DEFAULT 0.0000,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- Analytical Views
-- ----------------------------------------------------------------------------

-- View 1: Unified Post Performance Master View
CREATE OR REPLACE VIEW v_unified_post_performance AS
SELECT 
    p.post_id,
    pl.platform_name,
    p.post_date,
    p.post_time,
    DAYNAME(p.post_date) AS day_of_week,
    HOUR(p.post_time) AS posting_hour,
    p.content_type,
    p.caption,
    p.hashtags,
    p.reach,
    p.impressions,
    p.likes,
    p.comments,
    p.shares,
    p.saves,
    p.video_views,
    p.clicks,
    e.total_engagement,
    e.engagement_rate,
    e.click_through_rate,
    e.virality_score
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
LEFT JOIN Engagement e ON p.post_id = e.post_id;

-- View 2: Platform Monthly Summary View
CREATE OR REPLACE VIEW v_platform_monthly_summary AS
SELECT 
    pl.platform_name,
    DATE_FORMAT(p.post_date, '%Y-%m') AS month_year,
    COUNT(p.post_id) AS total_posts,
    SUM(p.reach) AS total_reach,
    SUM(p.impressions) AS total_impressions,
    SUM(e.total_engagement) AS total_engagement,
    AVG(e.engagement_rate) AS avg_engagement_rate
FROM Posts p
JOIN Platforms pl ON p.platform_id = pl.platform_id
LEFT JOIN Engagement e ON p.post_id = e.post_id
GROUP BY pl.platform_name, DATE_FORMAT(p.post_date, '%Y-%m');
