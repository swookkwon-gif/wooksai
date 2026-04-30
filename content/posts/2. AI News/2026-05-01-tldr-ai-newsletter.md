---
title: '[TLDR AI] AI 시장의 핵심 동향: TPU 경쟁, 오픈소스 LLM의 약진, 그리고 평가의 중요성'
date: '2026-05-01'
excerpt: 'AI 인프라 및 모델 경쟁 동향 Google, TPU 칩 외부 판매로 Nvidia에 도전장 Alphabet은 자체 개발한 Tensor Processing UnitTPU을 일부 고객에게 판매하여 데이터 센터에 설치할 ...'
category: 'AI News'
---

### AI 인프라 및 모델 경쟁 동향

*   **Google, TPU 칩 외부 판매로 Nvidia에 도전장**
    *   Alphabet은 자체 개발한 Tensor Processing Unit(TPU)을 일부 고객에게 판매하여 데이터 센터에 설치할 수 있도록 할 계획입니다. 최근 훈련 및 추론을 위한 두 가지 새로운 TPU를 발표했으며, 이미 Anthropic 및 Meta와 칩 공급 계약을 체결했습니다. 이러한 Google의 움직임은 Nvidia와의 경쟁을 더욱 심화시킬 것입니다.
    *   [원문 보기](https://finance.yahoo.com/markets/stocks/article/google-to-sell-tpu-chips-to-select-customers-in-latest-shot-at-nvidia-214900221.html?utm_source=tldrai)

*   **Mistral Medium 3.5, 원격 Vibe 에이전트 구동**
    *   128B 밀집 모델인 Mistral Medium 3.5가 Vibe 원격 에이전트를 구동하여 CLI 또는 Le Chat에서 시작하는 클라우드 기반의 장기 비동기 코딩 작업을 실행합니다. 이 모델은 명령어 수행, 추론, 코딩 기능을 결합하며, 4개의 GPU에서 효율적으로 작동하고 SWE-Bench Verified에서 높은 점수를 기록했습니다. Le Chat의 새로운 Work 모드는 이 모델을 사용하여 다양한 도구와 기능을 아우르는 복잡하고 다단계 작업을 실행합니다.
    *   [원문 보기](https://mistral.ai/news/vibe-remote-agents-mistral-medium-3-5?utm_source=tldrai)

*   **OpenAI, Stargate 데이터센터 계획 철회 및 유연한 계약 선호**
    *   OpenAI는 Stargate 데이터센터 프로젝트의 초기 목표였던 20개 데이터센터 구축 계획을 사실상 포기했습니다. 프로젝트 파트너들이 데이터센터의 최종 통제권에 합의하지 못했기 때문으로 알려졌습니다. OpenAI는 대신 컴퓨팅 자원을 임대하는 방식으로 전환했습니다.
    *   [원문 보기](https://www.tomshardware.com/tech-industry/artificial-intelligence/openai-has-effectively-abandoned-first-party-stargate-data-centers-in-favor-of-more-flexible-deals-company-now-prefers-to-lease-compute-and-says-stargate-is-an-umbrella-term?utm_source=tldrai)

*   **AI 추론 시장의 다윈적 전문화**
    *   AI 추론 시장은 워크로드의 다양성으로 인해 세분화되고 있습니다. 모델 생태계는 지연 시간 계층, 멀티모달 모델, 엣지 모델 등으로 파편화되었으며, 각 모델 유형은 다른 서비스 요구사항을 가지므로 인프라 또한 세분화됩니다. 이러한 파편화는 여러 승자가 나올 수 있는 여지를 만듭니다.
    *   [원문 보기](https://tomtunguz.com/inference-market-segmentation/?utm_source=tldrai)

### LLM 개발 및 평가의 새로운 도전과 기술

*   **AI 평가, 새로운 컴퓨팅 병목 현상으로 부상**
    *   AI 평가 비용이 급증하여 훈련 비용과 맞먹거나 이를 초과하는 심각한 컴퓨팅 병목 현상이 되고 있으며, 일부 실행에는 수만 달러가 소요됩니다. 이 분야는 모델과 작업 전반에 걸쳐 불균등한 비용 분포에 직면해 있으며, 표준화된 문서화 및 데이터 재사용과 같은 비용 효율적인 접근 방식의 필요성을 강조합니다. 이러한 문제를 해결하지 않으면 평가 프로세스는 여전히 비싸고, 동등한 접근을 어렵게 하며, AI 연구의 외부 검증을 방해할 것입니다.
    *   [원문 보기](https://huggingface.co/blog/evaleval/eval-costs-bottleneck?utm_source=tldrai)

*   **AutoSP: 긴 컨텍스트 LLM 훈련을 위한 시퀀스 병렬 코드 자동화**
    *   AutoSP는 표준 트랜스포머 훈련 코드를 긴 컨텍스트 LLM 훈련을 위한 시퀀스 병렬 코드로 자동 변환하며, DeepSpeed와 통합됩니다. 이는 복잡한 수동 코드 변경 없이 여러 GPU에서 더 긴 시퀀스 훈련을 가능하게 하고, 상당한 런타임 오버헤드 없이 작동합니다. AutoSP는 또한 더 나은 메모리 관리를 위한 고급 활성화 체크포인팅 전략을 제공하여 최소한의 비용으로 성능을 향상시킵니다.
    *   [원문 보기](https://pytorch.org/blog/introducing-autosp/?utm_source=tldrai)

*   **Granite 4.1 LLM: 구축 방식 심층 분석**
    *   Granite 4.1 LLM은 3B, 8B, 30B 파라미터의 밀집 디코더 전용 아키텍처를 활용하며, 15조 토큰으로 훈련되고 5단계 사전 훈련 접근 방식을 사용합니다. 8B 모델은 데이터 품질에 중점을 둔 다단계 강화 학습 파이프라인을 통해 이전 32B Mixture-of-Experts 모델과 동등한 성능을 달성합니다. 효율적이고 신뢰할 수 있는 엔터프라이즈 사용을 위해 설계된 이 모델들은 경쟁력 있는 명령어 수행 및 도구 성능을 보여주면서 비용 효율성과 안정적인 사용을 유지합니다.
    *   [원문 보기](https://huggingface.co/blog/ibm-granite/granite-4-1?utm_source=tldrai)

*   **LaDiR: 잠재 확산으로 LLM 텍스트 추론 능력 향상**
    *   LaDiR(Latent Diffusion Reasoner)은 연속 잠재 표현의 표현력과 잠재 확산 모델의 반복적인 개선 기능을 기존 LLM과 통합하는 새로운 추론 프레임워크입니다. 이 설계는 다양한 추론 궤적의 효율적인 병렬 생성을 가능하게 하여 모델이 추론 프로세스를 전체적으로 계획하고 수정할 수 있도록 합니다. LaDiR는 기존의 자기회귀, 확산 기반 및 잠재 추론 방법보다 정확도, 다양성 및 해석 가능성을 일관되게 향상시킵니다. 이는 잠재 확산을 이용한 텍스트 추론의 새로운 패러다임입니다.
    *   [원문 보기](https://machinelearning.apple.com/research/ladir?utm_source=tldrai)

*   **DeepMind ProEval: 생성형 AI 평가 비용 절감 및 실패 모드 식별**
    *   ProEval은 대체 모델 및 벤치마크 간 전이 학습을 사용하여 생성형 AI 평가 비용을 절감하고 실패 모드를 식별하는 프레임워크입니다.
    *   [원문 보기](https://github.com/google-deepmind/proeval?utm_source=tldrai)

### AI 에이전트의 발전과 실제 적용

*   **MCP 서버 구축 교훈: 에이전트의 효율적인 도구 사용**
    *   이 게시물은 MCP 서버가 대부분의 작업을 수행하고 모델은 '빵 부스러기'를 따라가는 프레임워크를 사용하여 MCP 툴체인을 작동시키는 방법을 논의합니다. 모델은 계획하지 않고 대화를 보고 도구 목록을 스캔하여 가장 가능성이 높은 것을 선택합니다. 효과적인 체인을 만들려면 서버가 모든 단계에서 다음 호출을 명확하게 만들도록 해야 합니다.
    *   [원문 보기](https://taoofmac.com/space/blog/2026/04/29/2341?utm_source=tldrai)

*   **Microsoft World-R1: 3D 일관성 비디오 생성 개선**
    *   World-R1은 기본 아키텍처를 수정하지 않고 3D 및 비전-언어 모델의 피드백을 활용하여 비디오 생성의 3D 일관성을 향상시키는 강화 학습 프레임워크입니다.
    *   [원문 보기](https://microsoft.github.io/World-R1/?utm_source=tldrai)

*   **DataPRM: 신뢰할 수 있는 데이터 분석 에이전트**
    *   DataPRM은 환경 인식 프로세스 보상 모델로, 무음 오류를 감지하고 데이터 분석 에이전트를 더 잘 감독하여 벤치마크 전반에 걸쳐 다운스트림 성능과 일반화 능력을 향상시킵니다.
    *   [원문 보기](https://arxiv.org/abs/2604.24198?utm_source=tldrai)

*   **스스로 코드를 작성하고 수정하는 AI 에이전트 등장**
    *   CrewAI는 Slack 기반의 사내 AI 직원인 Iris를 구축했습니다. Iris는 CrewAI 엔지니어링 조직 전반에서 코드를 작성하고, PR을 제출하고, 팀원의 작업을 검토하며, 자체 코드베이스를 수정합니다.
    *   [원문 보기](https://links.tldrnewsletter.com/8r8rai)

