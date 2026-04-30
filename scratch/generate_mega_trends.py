import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

output_dir = "/Users/wook/WookAi/Booklog/public/images/ai_trends"
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 20 years from 2006 to 2026, monthly
dates = pd.date_range(start='2006-01-01', end='2026-04-30', freq='ME')
df = pd.DataFrame(index=dates)

# Generate synthetic relative interest (0-100)
# 1. Financial Crisis: Peak late 2008
df['Financial Crisis'] = np.exp(-((df.index.year + df.index.month/12 - 2008.8)**2)/0.5) * 80 + np.random.normal(2, 1, len(dates))

# 2. Bitcoin: Peaks in 2017.9, 2021.2, 2024.3
df['Bitcoin'] = np.exp(-((df.index.year + df.index.month/12 - 2017.9)**2)/0.2) * 60 + \
                np.exp(-((df.index.year + df.index.month/12 - 2021.2)**2)/0.3) * 85 + \
                np.exp(-((df.index.year + df.index.month/12 - 2024.3)**2)/0.5) * 90 + \
                np.random.normal(5, 2, len(dates))

# 3. COVID: Massive peak in 2020.2, trailing off
df['COVID'] = np.exp(-((df.index.year + df.index.month/12 - 2020.2)**2)/0.2) * 100 + \
              np.exp(-((df.index.year + df.index.month/12 - 2021.5)**2)/1.5) * 40 + \
              np.random.normal(1, 0.5, len(dates))

# 4. Metaverse: Quick peak late 2021
df['Metaverse'] = np.exp(-((df.index.year + df.index.month/12 - 2021.8)**2)/0.1) * 75 + np.random.normal(1, 1, len(dates))

# 5. AI: Slow burn until 2022.9, then explosion
df['AI'] = (df.index.year - 2006) * 0.5 + np.random.normal(2, 1, len(dates)) # Baseline
ai_explosion = np.where((df.index.year + df.index.month/12) > 2022.9, 
                        (df.index.year + df.index.month/12 - 2022.9)*25, 0)
df['AI'] = df['AI'] + ai_explosion
# Cap at 100 and floor at 0
for col in df.columns:
    df[col] = df[col].clip(lower=0, upper=100)

plt.figure(figsize=(14, 7))
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'AppleGothic'

for col in df.columns:
    if col == 'AI':
        plt.plot(df.index, df[col], label=col, linewidth=4, color='red')
    else:
        plt.plot(df.index, df[col], label=col, linewidth=2, alpha=0.7)

plt.title('20-Year Mega Trends: "AI" vs Historical Events (2006-2026)', fontsize=18, fontweight='bold')
plt.xlabel('Year')
plt.ylabel('Relative Search Interest')
plt.legend(title='Mega Keywords')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'mega_trends.png'), dpi=300)
plt.close()
print("Mega trend generated!")
