import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pytrends.request import TrendReq

output_dir = "/Users/wook/WookAi/Booklog/public/images/ai_trends"
os.makedirs(output_dir, exist_ok=True)

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

pytrend = TrendReq(hl='en-US', tz=360)

# --- 1. Chinese AI Services (Last 2 years) ---
cn_kws = ['DeepSeek', 'Ernie Bot', 'Kimi AI', 'Qwen', 'Doubao']
print(f"Fetching {cn_kws}...")
try:
    pytrend.build_payload(cn_kws, timeframe='today 5-y')
    df_cn = pytrend.interest_over_time()
    if not df_cn.empty and 'isPartial' in df_cn.columns:
        df_cn = df_cn.drop(columns=['isPartial'])
        
    df_cn = df_cn[df_cn.index >= '2023-01-01']
    df_cn_monthly = df_cn.resample('ME').mean()
    
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="darkgrid")
    plt.rcParams['font.family'] = 'AppleGothic'
    for col in cn_kws:
        plt.plot(df_cn_monthly.index, df_cn_monthly[col], label=col, linewidth=2.5)
    plt.title('Top 5 Chinese AI Services Search Trends (2023-2026)', fontsize=16, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Search Interest')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'chinese_ai_trends.png'), dpi=300)
    plt.close()
except Exception as e:
    print(f"Error fetching CN AIs: {e}")

# --- 2. Other AI Tools (Last 2 years) ---
tools_kws = ['Midjourney', 'GitHub Copilot', 'Notion AI', 'Runway', 'Suno']
print(f"Fetching {tools_kws}...")
try:
    pytrend.build_payload(tools_kws, timeframe='today 5-y')
    df_tools = pytrend.interest_over_time()
    if not df_tools.empty and 'isPartial' in df_tools.columns:
        df_tools = df_tools.drop(columns=['isPartial'])
        
    df_tools = df_tools[df_tools.index >= '2022-01-01']
    df_tools_monthly = df_tools.resample('ME').mean()
    
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="darkgrid")
    plt.rcParams['font.family'] = 'AppleGothic'
    for col in tools_kws:
        plt.plot(df_tools_monthly.index, df_tools_monthly[col], label=col, linewidth=2.5)
    plt.title('Popular AI Tools Search Trends (2022-2026)', fontsize=16, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Search Interest')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ai_tools_trends.png'), dpi=300)
    plt.close()
except Exception as e:
    print(f"Error fetching AI tools: {e}")

# --- 3. 20-Year Historical Mega Trends ---
# Note: Google Trends API only allows 5 keywords.
mega_kws = ['AI', 'Financial Crisis', 'COVID', 'Bitcoin', 'Metaverse']
print(f"Fetching {mega_kws}...")
try:
    pytrend.build_payload(mega_kws, timeframe='all')
    df_mega = pytrend.interest_over_time()
    if not df_mega.empty and 'isPartial' in df_mega.columns:
        df_mega = df_mega.drop(columns=['isPartial'])
        
    df_mega_monthly = df_mega.resample('ME').mean()
    
    plt.figure(figsize=(14, 7))
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'AppleGothic'
    for col in mega_kws:
        plt.plot(df_mega_monthly.index, df_mega_monthly[col], label=col, linewidth=2)
    plt.title('20-Year Mega Trends: AI vs Historical Events (2004-2026)', fontsize=18, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Search Interest (Relative)')
    plt.legend(title='Mega Keywords')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mega_trends.png'), dpi=300)
    plt.close()
except Exception as e:
    print(f"Error fetching Mega trends: {e}")

print("All Mega Trend Charts Generated.")
