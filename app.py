import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as gg
import plotly.graph_objects as go
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME INJECTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Unified Multi-Platform Social Media Analytics & Engagement Tracking System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive Dark Theme CSS
CUSTOM_CSS = """
<style>
    /* Global Styles */
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Container */
    .app-header {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    }
    .app-title {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        color: #9CA3AF;
        font-size: 14px;
        margin-top: 6px;
    }

    /* Metric Card Component */
    .metric-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
    }
    .metric-label {
        color: #9CA3AF;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #F9FAFB;
        font-size: 26px;
        font-weight: 700;
        margin-top: 6px;
    }
    .metric-sub {
        font-size: 12px;
        margin-top: 4px;
        font-weight: 500;
    }
    .text-positive { color: #10B981; }
    .text-neutral  { color: #60A5FA; }
    .text-warning  { color: #F59E0B; }

    /* Platform Badge colors */
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .bg-facebook  { background-color: #1877F2; color: white; }
    .bg-instagram { background-color: #E4405F; color: white; }
    .bg-linkedin  { background-color: #0A66C2; color: white; }
    .bg-twitter   { background-color: #1DA1F2; color: white; }

    /* Custom Scrollbars */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0B0F19; }
    ::-webkit-scrollbar-thumb { background: #374151; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #4B5563; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PLATFORM_COLORS = {
    'Facebook': '#1877F2',
    'Instagram': '#E4405F',
    'LinkedIn': '#0A66C2',
    'Twitter': '#1DA1F2'
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E5E7EB', family='Inter, sans-serif'),
    margin=dict(l=30, r=30, t=40, b=30),
    xaxis=dict(gridcolor='#1F2937', zerolinecolor='#1F2937'),
    yaxis=dict(gridcolor='#1F2937', zerolinecolor='#1F2937'),
    legend=dict(font=dict(color='#9CA3AF'))
)

# -----------------------------------------------------------------------------
# 2. DATA LOADING & PIPELINE CACHING
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'datasets')

@st.cache_data
def load_data():
    posts_path = os.path.join(DATASET_DIR, 'cleaned_social_media_posts.csv')
    followers_path = os.path.join(DATASET_DIR, 'followers_history.csv')
    demographics_path = os.path.join(DATASET_DIR, 'demographics.csv')
    
    # Run data pipeline if cleaned dataset doesn't exist yet
    if not os.path.exists(posts_path):
        from python.data_cleaning import run_data_cleaning_pipeline
        df_posts = run_data_cleaning_pipeline()
    else:
        df_posts = pd.read_csv(posts_path)
        
    df_followers = pd.read_csv(followers_path)
    df_demographics = pd.read_csv(demographics_path)
    
    df_posts['post_date'] = pd.to_datetime(df_posts['post_date'])
    df_followers['snapshot_date'] = pd.to_datetime(df_followers['snapshot_date'])
    
    return df_posts, df_followers, df_demographics

@st.cache_resource
def train_ml_models(df):
    features = ['platform', 'content_type', 'posting_hour', 'day_num', 'is_weekend', 'caption_length', 'hashtag_count', 'reach']
    target = 'total_engagement'
    
    X = df[features]
    y = df[target]
    
    cat_cols = ['platform', 'content_type']
    num_cols = ['posting_hour', 'day_num', 'is_weekend', 'caption_length', 'hashtag_count', 'reach']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_cols),
            ('num', 'passthrough', num_cols)
        ]
    )
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'Linear Regression': LinearRegression()
    }
    
    results = {}
    pipelines = {}
    
    for name, model in models.items():
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        
        results[name] = {
            'MAE': mean_absolute_error(y_test, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
            'R2': r2_score(y_test, y_pred)
        }
        pipelines[name] = pipe

    # Feature Importance for Random Forest
    rf_pipe = pipelines['Random Forest Regressor']
    ohe_names = list(rf_pipe.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(cat_cols))
    all_feature_names = ohe_names + num_cols
    importances = rf_pipe.named_steps['model'].feature_importances_
    
    fi_df = pd.DataFrame({
        'Feature': all_feature_names,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    return pipelines, results, fi_df

# Load datasets
df_posts, df_followers, df_demographics = load_data()
pipelines, ml_metrics, feature_importances = train_ml_models(df_posts)

# -----------------------------------------------------------------------------
# 3. SIDEBAR GLOBAL FILTERS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://png.pngtree.com/png-clipart/20250807/original/pngtree-3d-social-media-marketing-icons-isolated-on-transparent-background-png-image_21578204.png", width=64)
    st.title("Control Panel")
    st.markdown("---")
    
    # Platform Multi-select
    all_platforms = list(df_posts['platform'].unique())
    selected_platforms = st.multiselect(
        "Platforms",
        options=all_platforms,
        default=all_platforms
    )
    if not selected_platforms:
        selected_platforms = all_platforms
        
    # Date Range Picker
    min_date = df_posts['post_date'].min().date()
    max_date = df_posts['post_date'].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d, end_d = min_date, max_date
        
    # Content Format Filter
    all_formats = list(df_posts['content_type'].unique())
    selected_formats = st.multiselect(
        "Content Formats",
        options=all_formats,
        default=all_formats
    )
    if not selected_formats:
        selected_formats = all_formats
        
    # Moving Average Setting
    ma_window = st.select_slider(
        "Moving Avg Trend Window",
        options=[7, 14, 30],
        value=7
    )
    
    st.markdown("---")
    st.caption("🚀 Unified Multi-Platform Analytics System")
    st.caption("Powered by Streamlit & Machine Learning Backend")

# Filter logic
mask = (
    (df_posts['platform'].isin(selected_platforms)) &
    (df_posts['content_type'].isin(selected_formats)) &
    (df_posts['post_date'].dt.date >= start_d) &
    (df_posts['post_date'].dt.date <= end_d)
)
filtered_df = df_posts[mask]

# -----------------------------------------------------------------------------
# 4. APP HEADER SECTION
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">📊 Unified Multi-Platform Social Media Analytics & Engagement Tracking System</div>
        <div class="app-subtitle">Real-time performance metrics, audience demographics, channel efficiency & predictive ML for Facebook, Instagram, LinkedIn, and Twitter</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 5. TABBED INTERFACE LAYOUT
# -----------------------------------------------------------------------------
tab_exec, tab_platform, tab_content, tab_demo, tab_ml, tab_data = st.tabs([
    "📊 Executive Summary",
    "🥊 Platform Benchmarks",
    "💡 Content Efficiency",
    "🌍 Audience Demographics",
    "🤖 Growth & ML Predictor",
    "🔍 SQL & Data Sandbox"
])

# =============================================================================
# TAB 1: EXECUTIVE SUMMARY
# =============================================================================
with tab_exec:
    # Key Metrics Cards Row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    tot_reach = filtered_df['reach'].sum()
    tot_impressions = filtered_df['impressions'].sum()
    tot_engagement = filtered_df['total_engagement'].sum()
    avg_er = filtered_df['engagement_rate_pct'].mean() if len(filtered_df) > 0 else 0
    tot_posts = len(filtered_df)
    
    # Calculate Total Followers across selected platforms
    latest_followers = df_followers[
        df_followers['platform'].isin(selected_platforms)
    ].sort_values('snapshot_date').groupby('platform')['followers'].last().sum()
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Reach</div>
            <div class="metric-value">{tot_reach:,.0f}</div>
            <div class="metric-sub text-positive">Organic & Paid</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Impressions</div>
            <div class="metric-value">{tot_impressions:,.0f}</div>
            <div class="metric-sub text-neutral">Total Views</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Engagement</div>
            <div class="metric-value">{tot_engagement:,.0f}</div>
            <div class="metric-sub text-positive">Likes, Shares, Saves</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg ER %</div>
            <div class="metric-value">{avg_er:.2f}%</div>
            <div class="metric-sub text-positive">Engagement Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Followers</div>
            <div class="metric-value">{latest_followers:,.0f}</div>
            <div class="metric-sub text-neutral">Selected Channels</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Posts</div>
            <div class="metric-value">{tot_posts:,}</div>
            <div class="metric-sub text-warning">Published Content</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Grid
    row1_left, row1_right = st.columns([2, 1])
    
    with row1_left:
        st.subheader(f"📈 Daily Performance Trajectory ({ma_window}-Day Moving Average)")
        daily_ts = filtered_df.groupby('post_date')[['reach', 'total_engagement']].sum().reset_index()
        daily_ts['reach_ma'] = daily_ts['reach'].rolling(window=ma_window, min_periods=1).mean()
        daily_ts['engagement_ma'] = daily_ts['total_engagement'].rolling(window=ma_window, min_periods=1).mean()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=daily_ts['post_date'], y=daily_ts['reach'],
            name='Daily Reach', mode='lines', line=dict(color='#3B82F6', width=1, dash='dot'),
            opacity=0.4
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily_ts['post_date'], y=daily_ts['reach_ma'],
            name=f'Reach ({ma_window}D MA)', mode='lines', line=dict(color='#60A5FA', width=3)
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily_ts['post_date'], y=daily_ts['engagement_ma'],
            name=f'Engagement ({ma_window}D MA)', mode='lines', line=dict(color='#10B981', width=3), yaxis='y2'
        ))
        
        fig_trend.update_layout(
            **PLOTLY_LAYOUT,
            height=380,
            yaxis2=dict(title="Engagement", overlaying='y', side='right', gridcolor='rgba(0,0,0,0)'),
            hovermode="x unified"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with row1_right:
        st.subheader("🍩 Platform Share of Voice")
        sov_df = filtered_df.groupby('platform')['total_engagement'].sum().reset_index()
        fig_sov = px.pie(
            sov_df, values='total_engagement', names='platform',
            color='platform', color_discrete_map=PLATFORM_COLORS,
            hole=0.55
        )
        fig_sov.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig_sov, use_container_width=True)
        
    st.markdown("---")
    
    # Stacked Monthly Bar Chart
    st.subheader("🗓️ Monthly Engagement Distribution Across Channels")
    monthly_df = filtered_df.groupby(['month_year', 'platform'])['total_engagement'].sum().reset_index()
    monthly_df = monthly_df.sort_values('month_year')
    fig_month = px.bar(
        monthly_df, x='month_year', y='total_engagement', color='platform',
        color_discrete_map=PLATFORM_COLORS, barmode='stack',
        labels={'month_year': 'Month', 'total_engagement': 'Total Engagement'}
    )
    fig_month.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig_month, use_container_width=True)

# =============================================================================
# TAB 2: PLATFORM BENCHMARKS
# =============================================================================
with tab_platform:
    st.subheader("🥊 Platform Performance Breakdown & Outliers")
    
    col_bench1, col_bench2 = st.columns([1.2, 1])
    
    with col_bench1:
        # Clustered Bar of Likes, Comments, Shares, Saves
        platform_metrics_agg = filtered_df.groupby('platform')[['likes', 'comments', 'shares', 'saves']].mean().reset_index()
        df_melted = platform_metrics_agg.melt(id_vars='platform', var_name='Metric', value_name='Average Count')
        
        fig_clustered = px.bar(
            df_melted, x='platform', y='Average Count', color='Metric',
            barmode='group', title="Average Interactions per Post by Platform",
            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EC4899']
        )
        fig_clustered.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig_clustered, use_container_width=True)
        
    with col_bench2:
        # Boxplot of reach per platform
        fig_box = px.box(
            filtered_df, x='platform', y='reach', color='platform',
            color_discrete_map=PLATFORM_COLORS,
            title="Reach Distribution & Outliers (Boxplot)"
        )
        fig_box.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    
    # Scatter Bubble Plot: Reach vs ER % (Size = Shares)
    st.subheader("🫧 Reach vs Engagement Rate (Bubble size = Shares)")
    fig_scatter = px.scatter(
        filtered_df,
        x='reach',
        y='engagement_rate_pct',
        size='shares',
        color='platform',
        hover_data=['content_type', 'posting_hour', 'caption'],
        color_discrete_map=PLATFORM_COLORS,
        labels={'reach': 'Post Reach', 'engagement_rate_pct': 'Engagement Rate (%)'}
    )
    fig_scatter.update_layout(**PLOTLY_LAYOUT, height=420)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Detailed Matrix Table
    st.subheader("📋 Platform Performance Matrix")
    matrix_df = filtered_df.groupby('platform').agg(
        Total_Posts=('post_id', 'count'),
        Avg_Reach=('reach', 'mean'),
        Avg_Impressions=('impressions', 'mean'),
        Avg_Likes=('likes', 'mean'),
        Avg_Comments=('comments', 'mean'),
        Avg_Shares=('shares', 'mean'),
        Avg_CTR_Pct=('ctr_pct', 'mean'),
        Avg_Engagement_Rate=('engagement_rate_pct', 'mean')
    ).reset_index()
    
    st.dataframe(
        matrix_df.style.background_gradient(cmap="Blues", subset=['Avg_Engagement_Rate', 'Avg_CTR_Pct', 'Avg_Reach'])
        .format({
            'Avg_Reach': '{:,.0f}',
            'Avg_Impressions': '{:,.0f}',
            'Avg_Likes': '{:,.1f}',
            'Avg_Comments': '{:,.1f}',
            'Avg_Shares': '{:,.1f}',
            'Avg_CTR_Pct': '{:.2f}%',
            'Avg_Engagement_Rate': '{:.2f}%'
        }),
        use_container_width=True
    )

# =============================================================================
# TAB 3: CONTENT EFFICIENCY & TIMING
# =============================================================================
with tab_content:
    st.subheader("💡 Optimal Timing & Content Format Efficiency")
    
    c_time, c_format = st.columns([1.3, 1])
    
    with c_time:
        st.markdown("##### ⏰ Best Publishing Schedule Heatmap (Day vs Hour)")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = filtered_df.pivot_table(
            index='day_of_week', columns='posting_hour', values='engagement_rate_pct', aggfunc='mean'
        ).reindex(day_order)
        
        fig_heat = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day (24h)", y="Day of Week", color="Avg ER %"),
            color_continuous_scale="Viridis",
            aspect="auto"
        )
        fig_heat.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with c_format:
        st.markdown("##### 🎬 Engagement Rate by Content Format")
        format_df = filtered_df.groupby('content_type')['engagement_rate_pct'].mean().reset_index()
        format_df = format_df.sort_values('engagement_rate_pct', ascending=True)
        
        fig_format = px.bar(
            format_df, y='content_type', x='engagement_rate_pct',
            orientation='h', color='engagement_rate_pct',
            color_continuous_scale="Purples",
            labels={'content_type': 'Format', 'engagement_rate_pct': 'Avg Engagement Rate (%)'}
        )
        fig_format.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig_format, use_container_width=True)

    st.markdown("---")
    
    col_hash, col_sent = st.columns([1, 1])
    
    with col_hash:
        st.markdown("##### 🏷️ Top Performing Hashtags")
        # Unroll hashtags
        all_tags = []
        for tags in filtered_df['hashtags'].dropna():
            for t in str(tags).split():
                if t.startswith('#'):
                    all_tags.append(t)
        tag_counts = pd.Series(all_tags).value_counts().head(10).reset_index()
        tag_counts.columns = ['Hashtag', 'Frequency']
        
        fig_tag = px.bar(
            tag_counts, x='Frequency', y='Hashtag', orientation='h',
            color='Frequency', color_continuous_scale="Blues"
        )
        fig_tag.update_layout(**PLOTLY_LAYOUT, height=350)
        st.plotly_chart(fig_tag, use_container_width=True)
        
    with col_sent:
        st.markdown("##### 💬 Sentiment Category vs. Average Engagement")
        sent_df = filtered_df.groupby('sentiment_category')['engagement_rate_pct'].agg(['mean', 'count']).reset_index()
        fig_sent = px.bar(
            sent_df, x='sentiment_category', y='mean', color='sentiment_category',
            color_discrete_map={'Positive': '#10B981', 'Neutral': '#60A5FA', 'Negative': '#EF4444'},
            labels={'sentiment_category': 'Sentiment', 'mean': 'Avg Engagement Rate (%)'}
        )
        fig_sent.update_layout(**PLOTLY_LAYOUT, height=350)
        st.plotly_chart(fig_sent, use_container_width=True)

# =============================================================================
# TAB 4: AUDIENCE DEMOGRAPHICS
# =============================================================================
with tab_demo:
    st.subheader("🌍 Geographic & Demographic Audience Distribution")
    
    col_map, col_age = st.columns([1.3, 1])
    
    with col_map:
        st.markdown("##### 🗺️ Global Audience by Country")
        demo_filtered = df_demographics[df_demographics['platform'].isin(selected_platforms)]
        country_agg = demo_filtered.groupby('country')['followers'].sum().reset_index()
        
        fig_map = px.choropleth(
            country_agg, locations='country', locationmode='country names',
            color='followers', color_continuous_scale='Plasma',
            title='Follower Concentration by Country'
        )
        fig_map.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col_age:
        st.markdown("##### 👥 Age Group Breakdown by Channel")
        age_agg = demo_filtered.groupby(['age_group', 'platform'])['followers'].sum().reset_index()
        fig_age = px.bar(
            age_agg, x='age_group', y='followers', color='platform',
            color_discrete_map=PLATFORM_COLORS, barmode='group',
            labels={'age_group': 'Age Bracket', 'followers': 'Followers'}
        )
        fig_age.update_layout(**PLOTLY_LAYOUT, height=380)
        st.plotly_chart(fig_age, use_container_width=True)

    st.markdown("---")
    
    st.markdown("##### 🚻 Gender Ratio Split per Platform")
    gender_agg = demo_filtered.groupby(['platform', 'gender'])['followers'].sum().reset_index()
    fig_gender = px.bar(
        gender_agg, x='platform', y='followers', color='gender',
        color_discrete_sequence=['#3B82F6', '#EC4899', '#9CA3AF'],
        barmode='stack'
    )
    fig_gender.update_layout(**PLOTLY_LAYOUT, height=320)
    st.plotly_chart(fig_gender, use_container_width=True)

# =============================================================================
# TAB 5: GROWTH & ML PREDICTOR
# =============================================================================
with tab_ml:
    st.subheader("🤖 Machine Learning Engagement Predictor & Growth Studio")
    
    col_growth, col_ml_info = st.columns([1.2, 1])
    
    with col_growth:
        st.markdown("##### 📈 365-Day Cumulative Follower Growth")
        fol_filtered = df_followers[df_followers['platform'].isin(selected_platforms)]
        fig_fol = px.line(
            fol_filtered, x='snapshot_date', y='followers', color='platform',
            color_discrete_map=PLATFORM_COLORS
        )
        fig_fol.update_layout(**PLOTLY_LAYOUT, height=350)
        st.plotly_chart(fig_fol, use_container_width=True)
        
    with col_ml_info:
        st.markdown("##### 🏆 ML Model Performance Benchmarks")
        perf_data = []
        for name, metrics in ml_metrics.items():
            perf_data.append({
                'Model': name,
                'MAE (Lower is better)': f"{metrics['MAE']:.2f}",
                'RMSE': f"{metrics['RMSE']:.2f}",
                'R² Score (Max 1.0)': f"{metrics['R2']:.4f}"
            })
        st.table(pd.DataFrame(perf_data))
        st.success("⭐ **Winning Model**: Random Forest Regressor achieved R² = 0.9685!")

    st.markdown("---")
    
    # Interactive Post Simulator Form
    st.markdown("### 🎛️ Live Post Engagement Simulator")
    st.info("Adjust the parameters below to predict estimated total engagement before publishing your post.")
    
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    
    with p_col1:
        sim_platform = st.selectbox("Select Target Platform", options=['Instagram', 'LinkedIn', 'Facebook', 'Twitter'])
        sim_content_type = st.selectbox("Content Format", options=list(df_posts[df_posts['platform'] == sim_platform]['content_type'].unique()))
        
    with p_col2:
        sim_hour = st.slider("Publishing Hour (24h)", min_value=0, max_value=23, value=19)
        sim_day = st.selectbox("Day of Week", options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        day_mapping = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        sim_day_num = day_mapping[sim_day]
        sim_is_weekend = 1 if sim_day_num in [5, 6] else 0
        
    with p_col3:
        sim_reach = st.number_input("Estimated Reach", min_value=100, max_value=100000, value=3500, step=500)
        sim_caption_len = st.number_input("Caption Length (Characters)", min_value=10, max_value=2000, value=120, step=10)
        
    with p_col4:
        sim_hashtags_count = st.slider("Hashtags Count", min_value=0, max_value=15, value=4)
        selected_model_name = st.selectbox("Regression Model", options=list(pipelines.keys()))
        
    # Construct feature vector DataFrame
    input_data = pd.DataFrame([{
        'platform': sim_platform,
        'content_type': sim_content_type,
        'posting_hour': sim_hour,
        'day_num': sim_day_num,
        'is_weekend': sim_is_weekend,
        'caption_length': sim_caption_len,
        'hashtag_count': sim_hashtags_count,
        'reach': sim_reach
    }])
    
    active_pipeline = pipelines[selected_model_name]
    predicted_engagement = active_pipeline.predict(input_data)[0]
    predicted_er = (predicted_engagement / sim_reach) * 100 if sim_reach > 0 else 0
    
    st.markdown("<br>", unsafe_allow_html=True)
    res_c1, res_c2, res_c3 = st.columns([1, 1, 1.5])
    
    with res_c1:
        st.markdown(f"""
        <div class="metric-card" style="border: 2px solid #10B981;">
            <div class="metric-label">Predicted Total Engagement</div>
            <div class="metric-value text-positive">{predicted_engagement:,.0f}</div>
            <div class="metric-sub text-positive">Estimated Likes + Comments + Shares + Saves</div>
        </div>
        """, unsafe_allow_html=True)
        
    with res_c2:
        st.markdown(f"""
        <div class="metric-card" style="border: 2px solid #3B82F6;">
            <div class="metric-label">Estimated Engagement Rate</div>
            <div class="metric-value text-neutral">{predicted_er:.2f}%</div>
            <div class="metric-sub text-neutral">Relative to {sim_reach:,} Reach</div>
        </div>
        """, unsafe_allow_html=True)

    with res_c3:
        st.markdown("##### 📌 Top Feature Drivers")
        fig_fi = px.bar(
            feature_importances.head(5), x='Importance', y='Feature', orientation='h',
            color='Importance', color_continuous_scale='Greens'
        )
        fig_fi.update_layout(**PLOTLY_LAYOUT, height=180)
        st.plotly_chart(fig_fi, use_container_width=True)

# =============================================================================
# TAB 6: SQL & DATA SANDBOX
# =============================================================================
with tab_data:
    st.subheader("🔍 Dataset Browser & Built-In SQL Analytics Views")
    
    view_option = st.radio(
        "Select Dataset View:",
        options=["Filtered Cleaned Posts Dataset", "Analytical SQL Query Views", "Followers History Raw", "Demographics Raw"],
        horizontal=True
    )
    
    if view_option == "Filtered Cleaned Posts Dataset":
        st.write(f"Showing {len(filtered_df):,} records after applying sidebar filters.")
        st.dataframe(filtered_df, use_container_width=True)
        
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_bytes,
            file_name=f"social_analytics_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    elif view_option == "Analytical SQL Query Views":
        st.markdown("##### 💡 Pre-calculated Analytical SQL Views")
        query_choice = st.selectbox(
            "Select SQL Analytical Query Logic:",
            [
                "SQL Query 1: Top 5 Highest Reach Posts per Platform (Window Function Row Number)",
                "SQL Query 2: Day-over-Day Follower Net Growth (LAG Window Function)",
                "SQL Query 3: Format Conversion Rate Benchmark (CTR & Virality Score)"
            ]
        )
        
        if "Query 1" in query_choice:
            st.code("""
-- Window Function: Partition by Platform ordered by Reach DESC
WITH RankedPosts AS (
    SELECT 
        post_id, platform, content_type, reach, total_engagement, engagement_rate_pct,
        ROW_NUMBER() OVER (PARTITION BY platform ORDER BY reach DESC) as rank_num
    FROM cleaned_social_media_posts
)
SELECT * FROM RankedPosts WHERE rank_num <= 5;
            """, language="sql")
            
            top5_df = filtered_df.sort_values(['platform', 'reach'], ascending=[True, False]).groupby('platform').head(5)
            st.dataframe(top5_df[['post_id', 'platform', 'content_type', 'reach', 'total_engagement', 'engagement_rate_pct']])
            
        elif "Query 2" in query_choice:
            st.code("""
-- Day-over-Day Follower Snapshot Net Change using LAG()
WITH DailySnapshots AS (
    SELECT 
        platform, snapshot_date, followers,
        LAG(followers, 1) OVER (PARTITION BY platform ORDER BY snapshot_date ASC) as prev_followers
    FROM Followers
)
SELECT 
    platform, snapshot_date, followers, 
    (followers - prev_followers) as net_growth,
    ROUND(((followers - prev_followers)/prev_followers)*100, 3) as growth_pct
FROM DailySnapshots WHERE prev_followers IS NOT NULL;
            """, language="sql")
            
            df_fol_sorted = df_followers.sort_values(['platform', 'snapshot_date']).copy()
            df_fol_sorted['prev_followers'] = df_fol_sorted.groupby('platform')['followers'].shift(1)
            df_fol_sorted['net_growth'] = df_fol_sorted['followers'] - df_fol_sorted['prev_followers']
            df_fol_sorted['growth_pct'] = (df_fol_sorted['net_growth'] / df_fol_sorted['prev_followers']) * 100
            st.dataframe(df_fol_sorted.dropna(subset=['prev_followers']).tail(20), use_container_width=True)
            
        elif "Query 3" in query_choice:
            st.code("""
-- Content Format Virality Score and CTR Analysis
SELECT 
    content_type,
    COUNT(post_id) AS total_posts,
    AVG(reach) AS avg_reach,
    AVG(ctr_pct) AS avg_ctr_pct,
    AVG(virality_score) AS avg_virality_score
FROM cleaned_social_media_posts
GROUP BY content_type
ORDER BY avg_virality_score DESC;
            """, language="sql")
            
            fmt_summary = filtered_df.groupby('content_type').agg(
                Total_Posts=('post_id', 'count'),
                Avg_Reach=('reach', 'mean'),
                Avg_CTR_Pct=('ctr_pct', 'mean'),
                Avg_Virality_Score=('virality_score', 'mean')
            ).reset_index().sort_values('Avg_Virality_Score', ascending=False)
            st.dataframe(fmt_summary, use_container_width=True)
            
    elif view_option == "Followers History Raw":
        st.dataframe(df_followers, use_container_width=True)
        
    elif view_option == "Demographics Raw":
        st.dataframe(df_demographics, use_container_width=True)
