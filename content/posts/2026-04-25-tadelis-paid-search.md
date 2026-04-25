---
title: "마케팅 예산 잔혹사: eBay는 어떻게 검색광고(SEM)의 오해를 벗겨냈는가?"
date: "2026-04-25"
excerpt: "Steve Tadelis의 유명한 eBay 대규모 실험 논문 리뷰. 브랜드 키워드 광고가 사실상 예산 낭비에 가깝다는 것을 증명한 전설적인 연구입니다."
category: "마케팅 논문 읽기"
---

지난 포스팅에서 Meta의 CMO Alex Schultz가 "브랜드 키워드 검색광고(SA)는 기본적으로 하지 마라"고 주장한 배경에는, 업계에 큰 파장을 일으켰던 전설적인 논문 한 편이 있습니다.

바로 Thomas Blake, Chris Nosko, 그리고 **Steven Tadelis**가 2015년에 발표한 논문, **[Consumer Heterogeneity and Paid Search Effectiveness: A Large Scale Field Experiment](/wooksai/papers/Tadelis.pdf)** 입니다. 

오늘의 '마케팅 논문 읽기'에서는 이 논문이 어떻게 퍼포먼스 마케팅 업계의 오랜 믿음을 산산조각 냈는지, 데이터와 그래프를 통해 살펴봅니다.

---

## 📉 'Brand Keyword' 광고를 껐더니 일어난 일

당시 eBay는 엄청난 금액의 예산을 검색엔진 마케팅(SEM)에 쏟아붓고 있었습니다. 그 중에서도 사용자가 구글 등에 'eBay' 혹은 'eBay shoes' 와 같이 브랜드 이름이 섞인 키워드를 검색했을 때 최상단에 뜨는 **브랜드 검색 광고**의 비중이 컸습니다. 

연구진은 아주 도발적인 실험을 기획합니다. **"특정 기간, 특정 지역에서 이 브랜드 광고를 완전히 꺼버리면 어떻게 될까?"**

아래 그래프는 이 실험의 충격적인 결과를 단적으로 보여줍니다.

![eBay Brand Search Experiment Results](/wooksai/images/tadelis_fig_7_1.jpeg)
<br/>
<caption class="text-sm text-neutral-500 text-center block mb-8">*그래프: 광고 노출이 중단된 기간, 유료 검색(Paid Search) 클릭은 소멸했지만 자연 검색(Organic Search) 클릭이 그 빈자리를 완벽하게 대체했습니다.*</caption>

### 완전한 대체 효과 (Perfect Substitution)
그래프에서 볼 수 있듯, 유료 광고(Paid)를 끄자 당연히 유료 클릭 트래픽은 0으로 떨어졌습니다. 하지만 **놀랍게도 자연 검색(Organic) 트래픽이 그만큼 정확하게 솟아오르며** 전체 트래픽 총량에는 전혀 변화가 없었습니다.

결론적으로, 브랜드 키워드 검색광고는 새로운 고객을 데려온 것(Incrementality)이 아니라, **"가만히 둬도 오가닉 검색으로 들어왔을 고객의 길목을 막고 서서 돈을 지불하게 만든 것"**에 불과했습니다.

---

## 👥 소비자 이질성 (Consumer Heterogeneity): 누가 광고를 누르는가?

논문의 두 번째 핵심은 Non-brand 키워드(예: '중고 기타', '여름 샌들' 등 eBay 브랜드가 포함되지 않은 일반 명사) 광고의 효율에 관한 것입니다. 

연구진은 소비자를 **'eBay를 얼마나 자주 이용하는가'**에 따라 그룹을 나누어 ROI(투자 대비 수익률)를 분석했습니다.

1. **신규 또는 비연속적 고객 (New / Infrequent Users)**
   - 이들에게는 검색 광고가 실제로 유의미한 효과를 발휘했습니다. 
   - 이들은 쇼핑몰이 어디인지 아직 확실히 마음을 정하지 않았기 때문에, 광고가 구매 결정에 긍정적인 정보(Informing)로 작용했습니다.

2. **충성 고객 (Frequent Users)**
   - 문제는 **가장 많은 광고 예산이 이 충성 고객들의 클릭에 소진되고 있었다**는 점입니다.
   - 이들은 광고가 없었더라도 어차피 접속해서 물건을 샀을 사람들입니다. 결국 마케팅 예산의 대부분이 구매 행동에 아무런 영향을 주지 못하는 '비-증분적(non-incremental)' 클릭에 낭비되고 있었습니다.
   - 논문에 따르면 충성 고객 대상으로 지출된 비용 때문에 평균적인 검색광고 ROI는 **'마이너스(Negative)'** 였습니다.

---

## 💡 Marketer's Takeaway

이 논문이 마케터들에게 던지는 묵직한 교훈은 명확합니다.

> **"로아스(ROAS)의 환상에서 벗어나, 증분(Incrementality)을 측정하라."**

우리가 매일 쳐다보는 광고 대시보드 위에는 전환당 비용(CPA)과 ROAS가 화려하게 찍힙니다. 브랜드 키워드 캠페인은 언제나 타 캠페인을 압도하는 최고의 효율을 보여줍니다. 하지만 Tadelis의 연구는 그 화려한 숫자가 사실 **'착시'**일 수 있음을 증명했습니다. 

1. **Brand와 Non-brand 예산의 분리**: 브랜드 검색광고의 예산과 성과를 전체 매체 믹스에 섞어버리면, 전체 마케팅 퍼포먼스가 부풀려지는 심각한 오류가 발생합니다.
2. **타겟팅의 중요성**: 모든 유저에게 일괄적으로 광고를 뿌리는 것이 아니라, 정말 리타겟팅과 광고 자극이 필요한 '신규/비활성 유저'를 걸러내어 예산을 집중해야 합니다.

*첨부: Tadelis 외 논문 원문 전체 보기 (클릭)* 
📄 [Consumer Heterogeneity and Paid Search Effectiveness](/wooksai/papers/Tadelis.pdf)
