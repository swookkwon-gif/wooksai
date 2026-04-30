import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pytrends.request import TrendReq
import matplotlib.dates as mdates

# Create directory for images
output_dir = "/Users/wook/WookAi/Booklog/public/images/ai_trends"
os.makedirs(output_dir, exist_ok=True)

# Set matplotlib Korean font
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# Initialize pytrends
pytrend = TrendReq(hl='en-US', tz=360)

# Keywords to compare
# Pytrends allows max 5 keywords at a time.
# We will do Group 1: ChatGPT, Gemini, Claude, Perplexity, DeepSeek
kw_list = ['ChatGPT', 'Gemini', 'Claude', 'Perplexity', 'DeepSeek']

print(f"Fetching data for {kw_list}...")
pytrend.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')

# Get interest over time
df = pytrend.interest_over_time()

if not df.empty:
    if 'isPartial' in df.columns:
        df = df.drop(columns=['isPartial'])
        
    # We want data from 2022 to 2026
    df = df[df.index >= '2022-01-01']
    
    # 1. Monthly Trend Chart
    df_monthly = df.resample('ME').mean()
    
    plt.figure(figsize=(14, 7))
    sns.set_theme(style="darkgrid")
    sns.set_palette("husl")
    plt.rcParams['font.family'] = 'AppleGothic' # reset after sns theme
    
    for col in kw_list:
        plt.plot(df_monthly.index, df_monthly[col], label=col, linewidth=2.5)
        
    plt.title('Monthly Google Search Trends (2022-2026): Major AI Chatbots', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Search Interest', fontsize=12)
    plt.legend(title='AI Services', title_fontsize='13', fontsize='11')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'monthly_ai_trends.png'), dpi=300)
    plt.close()
    
    # 2. Quarterly Trend Chart (Bar Chart)
    df_quarterly = df.resample('QE').mean()
    # Filter to 2024-2026 for a better bar chart view
    df_quarterly = df_quarterly[df_quarterly.index >= '2024-01-01']
    
    df_quarterly.index = df_quarterly.index.strftime('%Y-Q%q')
    
    # Plot grouped bar chart
    ax = df_quarterly.plot(kind='bar', figsize=(14, 7), width=0.8, colormap='viridis')
    plt.title('Quarterly Search Interest Comparison (2024-2026)', fontsize=16, fontweight='bold')
    plt.xlabel('Quarter', fontsize=12)
    plt.ylabel('Average Search Interest', fontsize=12)
    plt.legend(title='AI Services')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'quarterly_ai_trends.png'), dpi=300)
    plt.close()
    
    print("Success! Charts saved to", output_dir)
else:
    print("Failed to fetch data or data is empty.")
