import pandas as pd
from pytrends.request import TrendReq
import json

pytrends = TrendReq(hl='en-US', tz=360)
kw_list = ['ChatGPT', 'Gemini', 'Claude', 'DeepSeek', 'Perplexity']
pytrends.build_payload(kw_list, cat=0, timeframe='2022-11-01 2026-04-30', geo='', gprop='')

data = pytrends.interest_over_time()
monthly = data.resample('ME').mean()

line_data = []
for index, row in monthly.iterrows():
    line_data.append({
        "month": index.strftime('%y.%m'),
        "ChatGPT": round(row['ChatGPT'], 1) if pd.notna(row['ChatGPT']) else 0,
        "Gemini": round(row['Gemini'], 1) if pd.notna(row['Gemini']) else 0,
        "Claude": round(row['Claude'], 1) if pd.notna(row['Claude']) else 0,
        "DeepSeek": round(row['DeepSeek'], 1) if pd.notna(row['DeepSeek']) else 0,
        "Perplexity": round(row['Perplexity'], 1) if pd.notna(row['Perplexity']) else 0,
    })

print("=== LINE DATA ===")
print(json.dumps(line_data, indent=2))

quarterly = data.resample('QE').mean()
bar_data = []
for index, row in quarterly.iterrows():
    quarter_str = f"{index.strftime('%y')}.Q{index.quarter}"
    if index.year >= 2023:
        bar_data.append({
            "quarter": quarter_str,
            "ChatGPT": round(row['ChatGPT'], 1) if pd.notna(row['ChatGPT']) else 0,
            "Gemini": round(row['Gemini'], 1) if pd.notna(row['Gemini']) else 0,
            "Claude": round(row['Claude'], 1) if pd.notna(row['Claude']) else 0,
            "DeepSeek": round(row['DeepSeek'], 1) if pd.notna(row['DeepSeek']) else 0,
            "Perplexity": round(row['Perplexity'], 1) if pd.notna(row['Perplexity']) else 0,
        })

print("=== BAR DATA ===")
print(json.dumps(bar_data, indent=2))
