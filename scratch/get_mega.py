import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pytrends.request import TrendReq

output_dir = "/Users/wook/WookAi/Booklog/public/images/ai_trends"
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

pytrend = TrendReq(hl='en-US', tz=360, timeout=(10,25))

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
    print("Success mega_trends.png")
except Exception as e:
    print(f"Error fetching Mega trends: {e}")
