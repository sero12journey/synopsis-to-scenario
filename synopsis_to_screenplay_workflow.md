# Synopsis to Screenplay Workflow Engine
## 시놉시스 → 장편 영화 시나리오 전환 워크플로우 시스템

> **목적**: 다양한 형식의 원작(숏폼, 웹드라마, 소설, 웹툰, 실화 등)을 장편 영화 시나리오로 전환하는 범용 워크플로우 엔진
> **최종 산출물**: 완성된 한국어 장편 영화 시나리오 (.docx / .pdf)

---

## 1. 시스템 아키텍처

### 1.1 전체 구조

```
[입력] 시놉시스 문서 + 작법 레퍼런스
         │
         ▼
┌─────────────────────────────────────────────┐
│              Orchestrator Agent              │
│   (워크플로우 관리, Step 간 데이터 전달,       │
│    체크포인트 관리, Human 피드백 라우팅)        │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────────┐
    ▼          ▼              ▼
┌────────┐ ┌────────┐ ┌────────────┐
│Analyst │ │Writer  │ │  Critic    │
│Agent   │ │Agent   │ │  Agent     │
└────────┘ └────────┘ └────────────┘
               │
               ▼
[출력] 완성 시나리오 (.docx / .pdf)
```

### 1.2 에이전트 정의

#### Orchestrator Agent (오케스트레이터)

```yaml
role: "워크플로우 관리자"
responsibilities:
  - Step 실행 순서 제어
  - 이전 Step 산출물을 다음 Step에 컨텍스트로 전달
  - 체크포인트에서 Human 피드백 수렴
  - 수정 요청 시 해당 Agent에 재작업 지시
  - 전체 진행 상태 추적
  - ProjectConfig 관리
does_not:
  - 시나리오를 직접 쓰지 않음
  - 창작 판단을 내리지 않음
```

#### Analyst Agent (분석 에이전트)

```yaml
role: "구조 분석가 / 스토리 아키텍트"
expertise:
  - 시놉시스 분석 (강점/약점 도출)
  - 막 구조 설계
  - 비트 설계 (Beat Sheet)
  - 씬 수/분량 산출
reference_knowledge:
  - Syd Field 3막 구조론
  - Blake Snyder 비트 시트 (15 비트)
  - 한국 시나리오 분량 기준 (1p ≈ 1.3~1.5분)
  - 기승전결 구조 (봉준호식 '전(轉)' 개념)
담당_step: [0, 1, 2]
```

#### Writer Agent (작가 에이전트)

```yaml
role: "시나리오 작가"
expertise:
  - 이미지 시스템 설계
  - 캐릭터 시각적 식별자 설계
  - 씬 리스트 작성
  - 트리트먼트 서술
  - 시나리오 집필 (지문/대사)
reference_knowledge:
  - McKee 이미지 시스템 및 상징적 상승
  - Tony Tost "모든 문장이 하나의 숏, 마침표마다 컷"
  - 봉준호 건축적 공간 메타포
  - Trottier "보이고 들리는 것만 쓰라"
  - Michael Hauge 시각적 디테일을 통한 캐릭터 소개
  - 한국 시나리오 지문 형식 (대지문/소지문)
  - 한국 시나리오 여백의 미학 (협업적 해석 공간)
담당_step: [3, 4, 5, 6, 7]
```

#### Critic Agent (비평 에이전트)

```yaml
role: "시나리오 닥터 / 스크립트 컨설턴트"
expertise:
  - 구조적 결함 진단
  - 서브텍스트 부재 탐지
  - 이미지 시스템 일관성 검증
  - "설명이 묘사를 압도하는" 장면 탐지
  - 복선-회수(Plant-Payoff) 매핑 검증
  - 대사 과다 장면 식별
  - 캐릭터 능동성/수동성 균형 점검
evaluation_criteria:
  - 작법 레퍼런스 기반 체크리스트
  - 프로젝트별 보완점(Critique) 목록 대조
담당: [체크포인트 A/B/C 사전 리뷰, STEP 8 시각적 개고]
design_rationale: >
  Writer가 자기 글을 평가하면 자기 확증 편향이 작동한다.
  실제 영화 산업에서 시나리오 닥터가 별도로 존재하는 이유와 동일.
  Critic이 먼저 리뷰한 뒤 Human에게 넘기면,
  사용자는 "어디를 봐야 하는지" 가이드가 있는 상태에서 판단할 수 있다.
```

---

## 2. 프로젝트 설정

### 2.1 ProjectConfig

```yaml
ProjectConfig:
  title: string              # 작품 제목
  source_format: enum        # 원작 형식
    # options: shortform | webdrama | novel | webtoon | real_story | original
  target_format: "feature_film"  # 고정값: 장편 영화 시나리오
  target_duration: 90        # 목표 러닝타임 (분), 기본값 90
  genre: string[]            # 장르 태그 (ex: ["실화 범죄", "심리 스릴러", "로맨스"])
  tone: string               # 톤 (ex: "로맨스→스릴러 전환")
  theme_direction: string    # 테마적 방향성
  reference_docs: file[]     # 작법 레퍼런스 문서
  synopsis_doc: file         # 원작 시놉시스
```

### 2.2 분량 설계 기준 (DurationEstimate)

> **핵심 원칙**: 한국 시나리오는 할리우드와 달리 표준화된 형식이 없다. 작가마다 폰트(9~14pt), 레이아웃, 지문/대사 배치가 다르므로, 페이지 수가 아닌 **씬 수를 1차 지표**로 사용한다.

```yaml
DurationEstimate:
  primary_metric: scene_count      # 씬 수 (가장 신뢰할 수 있는 지표)
  secondary_metric: page_count     # 페이지 수 (참고용)

  feature_film_90min:
    target_minutes: 90
    scene_count: 70~85             # 90분 기준 비례 산출
    page_count: 55~70              # 한국 시나리오 기준
    page_to_minute_ratio: 1.3~1.5  # 한국어 시나리오 특성 반영
                                   # (할리우드 Courier 12pt = 1:1과 구분)

  act_structure:                   # 3막 구조 배분 (90분 기준)
    act_1:
      percentage: 25%
      duration: ~22분
      scene_count: ~18~21
      function: "주인공 일상 + 촉매 사건 + 첫 전환점"
    act_2a:
      percentage: 25%
      duration: ~22분
      scene_count: ~18~21
      function: "갈등 에스컬레이션 + 조력자 등장"
    act_2b:
      percentage: 25%
      duration: ~22분
      scene_count: ~18~21
      function: "미드포인트 반전 + 장르 전환 + 수사/추적"
    act_3:
      percentage: 25%
      duration: ~24분
      scene_count: ~16~22
      function: "클라이맥스 + 해결 + 에필로그"
```

### 2.3 Step 공통 산출물 구조

```yaml
StepOutput:
  step_number: number
  step_name: string
  agent: string                # 담당 에이전트
  analysis: string             # 분석/작업 결과
  deliverable: file            # 산출물 (문서)
  critique_points: string[]    # 자체 보완점 지적
  questions_for_human: string[] # 사용자에게 확인할 질문
  status: enum                 # draft | reviewed | approved
```

### 2.4 체크포인트 구조

```yaml
Checkpoint:
  checkpoint_id: "A" | "B" | "C"
  critic_review: CriticReview       # Critic Agent 사전 리뷰
  review_criteria: string[]         # 검토 기준
  previous_steps_summary: string    # 이전 Step 요약
  human_feedback: string            # 사용자 피드백
  revision_needed: boolean
  revision_targets: number[]        # 수정 필요한 Step 번호

CriticReview:
  overall_assessment: enum          # pass | conditional_pass | rework_needed
  structural_check: object          # 구조 점검 결과
  concerns: string[]                # 우려 사항
  recommendations: string[]        # 개선 권고
  questions_for_human: string[]    # 사용자에게 확인할 질문
```

---

## 3. 워크플로우 상세

### 전체 흐름도

```
STEP 0  [Analyst]  시놉시스 사전 분석 (Critique)
STEP 1  [Analyst]  막 구조 및 분량 설계
STEP 2  [Analyst]  비트 설계 (Beat Sheet)

        [Critic]   체크포인트 A 사전 리뷰
        [Human]    체크포인트 A 최종 승인 → 승인 시 STEP 3으로
                                         → 수정 시 해당 Step 재실행

STEP 3  [Writer]   이미지 시스템 설계
STEP 4  [Writer]   캐릭터 재설계

        [Critic]   체크포인트 B 사전 리뷰
        [Human]    체크포인트 B 최종 승인 → 승인 시 STEP 5로
                                         → 수정 시 해당 Step 재실행

STEP 5  [Writer]   트리트먼트 (Treatment)
STEP 6  [Writer]   씬 리스트 (Scene List)

        [Critic]   체크포인트 C 사전 리뷰
        [Human]    체크포인트 C 최종 승인 → 승인 시 STEP 7로
                                         → 수정 시 해당 Step 재실행

STEP 7  [Writer]   시나리오 1고 (First Draft)
STEP 8  [Critic]   시각적 개고 (Visual Revision) → [Writer] 반영
```

### Step 간 데이터 의존성

```
STEP 0 (사전 분석) ──→ 모든 Step에 보완점 목록 전달
         │
STEP 1 (막 구조) ──→ STEP 2 (비트)
                         │
              ┌──────────┘
              ▼
         STEP 3 (이미지) ←──→ STEP 4 (캐릭터)  [상호 참조, 병렬 가능]
              │                    │
              └────────┬───────────┘
                       ▼
                  STEP 5 (트리트먼트)  ← STEP 1~4 모든 산출물 입력
                       │
                       ▼
                  STEP 6 (씬 리스트)  ← 트리트먼트 기반 씬 분해
                       │
                       ▼
                  STEP 7 (1고)
                       │
                       ▼
                  STEP 8 (개고)
```

---

## 4. 각 Step 상세 명세

### STEP 0. 시놉시스 사전 분석 (Critique)

```yaml
agent: Analyst
input:
  - synopsis_doc
  - reference_docs
output:
  - 원작 형식 분석 결과 (source_format 특성)
  - 강점 목록 (장편 전환 시 유지할 요소)
  - 보완점 목록 (Critique)
  - 사용자 추가 보완점 수렴 결과
```

**분석 프레임워크:**

| 분석 항목 | 검토 내용 |
|-----------|-----------|
| 구조적 완성도 | 3막 구조 명확성, 전환점 유무, 클라이맥스 위치 |
| 영상적 묘사 수준 | "설명" vs "묘사" 비율, 카메라 불가능 서술 빈도 |
| 서브텍스트 | 대사/행동의 이중 레이어 존재 여부 |
| 이미지 시스템 | 시각적 모티프 설계 유무 |
| 캐릭터 입체성 | 시각적 식별자, 행동적 소개, 변화 호(arc) |
| 공간 활용 | 공간이 서사 도구로 기능하는지 |
| 주인공 능동성 | 수동적 인물인 경우 능동적 선택 지점 부족 여부 |
| 복선 설계 | Plant-Payoff 구조 존재 여부 |
| 원작→장편 전환 이슈 | 숏폼 클리프행어 구조 → 장편 호흡 전환 필요성 등 |

**핵심 보완점 프레임워크 (KANTA 사례 기반 일반화):**

1. **심리적 여정(유니티 아크) 심화** — 외적 갈등만 있고 내면 변형이 부족한 경우
2. **미드포인트 장르 전복 극대화** — 영화의 정확한 허리에서 톤/장르 전환
3. **보이지 않는 복선(Invisible Plants) 설계** — 결말 반전의 역소급적 필연성
4. **단면적 인물(Monolithic Evil) 탈피** — 악역/조연의 입체화
5. **게으른 정보 전달자(Exposition Dump) 지양** — 대사 설명 → 시각적 발견으로 전환
6. **원작 형식 특성 → 장편 호흡 전환** — breathing room 추가, 감정적 투자 시간 확보

### STEP 1. 막 구조 및 분량 설계

```yaml
agent: Analyst
input:
  - STEP 0 산출물 (보완점 목록 포함)
  - ProjectConfig (target_duration: 90)
  - DurationEstimate 기준
output:
  - 3막 구조 (막별 시작점/끝점/핵심 기능)
  - 씬 수 배분 (1차 지표)
  - 페이지 수 배분 (2차 지표, 참고용)
  - 원작 사건 재배치 맵 (원작 사건 → 어느 막에 배치되는지)
```

### STEP 2. 비트 설계 (Beat Sheet)

```yaml
agent: Analyst
input:
  - STEP 1 산출물 (막 구조)
  - STEP 0 보완점 중 구조 관련 항목
output:
  - 15개 비트 포인트 배치 (Snyder 비트 시트 기반)
  - 각 비트의 예상 러닝타임 및 씬 수
  - 주인공 능동적 선택 지점 표시
  - 긴장/이완 리듬 곡선
```

**비트 시트 템플릿 (90분 기준):**

| # | 비트 | 시간대 | 씬 수 | 내용 |
|---|------|--------|--------|------|
| 1 | Opening Image | 0~1분 | 1 | 시각적 북엔드 시작점 |
| 2 | Theme Stated | 3~5분 | 1 | 테마 암시 (대사 or 시각적) |
| 3 | Set-Up | 1~10분 | 5~8 | 주인공 일상, 결핍 상태 |
| 4 | Catalyst | 10~12분 | 1~2 | 촉매 사건 |
| 5 | Debate | 12~20분 | 4~6 | 갈등, 첫 선택 |
| 6 | Break into Two | 20~22분 | 1~2 | 1막→2막 전환점 |
| 7 | B Story | 22~25분 | 2~3 | 서브플롯 도입 |
| 8 | Fun & Games | 25~40분 | 8~12 | 장르의 약속 이행 |
| 9 | Midpoint | 43~47분 | 2~3 | 가짜 승리 or 가짜 패배, 장르 전복 |
| 10 | Bad Guys Close In | 47~58분 | 6~8 | 외적/내적 압박 증가 |
| 11 | All Is Lost | 58~62분 | 2~3 | 최저점 |
| 12 | Dark Night of the Soul | 62~67분 | 2~4 | 내면 대면 |
| 13 | Break into Three | 67~68분 | 1 | 해결책 발견 |
| 14 | Finale | 68~85분 | 8~12 | 클라이맥스 + 해결 |
| 15 | Final Image | 88~90분 | 1 | 시각적 북엔드 종결점 |

### 🔵 체크포인트 A — 구조 확정 리뷰

```yaml
agent: Critic → Human
timing: STEP 2 완료 후
review_criteria:
  - 막 구조 균형 (각 막의 러닝타임/씬 수 편차)
  - 미드포인트 위치 및 장르 전복 효과
  - 주인공 능동적 선택 지점 최소 3곳 이상 존재
  - 비트 간 긴장/이완 리듬 적절성
  - 결말의 테마적 방향성 확정
  - 심리적 여정(유니티 아크) 설계 충분성
significance: >
  이 체크포인트 이후로는 구조를 크게 바꾸기 어렵다.
  비트가 확정되면 이후 모든 Step이 이 뼈대 위에 구축된다.
```

**Critic 리뷰 출력 템플릿:**

```yaml
checkpoint_a_review:
  overall_assessment: "pass | conditional_pass | rework_needed"
  structure_check:
    act_balance: "각 막의 러닝타임/씬 수 분석"
    midpoint_placement: "미드포인트 위치 및 효과 평가"
    protagonist_agency: "주인공 능동적 선택 지점 N곳 확인"
    rhythm: "긴장/이완 곡선 평가"
  concerns: ["구체적 우려 사항 목록"]
  recommendations: ["개선 권고 목록"]
  questions_for_human: ["사용자에게 확인할 질문"]
```

### STEP 3. 이미지 시스템 설계

```yaml
agent: Writer
input:
  - STEP 0~2 전체 산출물
  - 작법 레퍼런스 (McKee 이미지 시스템)
output:
  - 핵심 시각 모티프 3개 내외 확정
  - 비트별 모티프 매핑 (어떤 비트에 어떤 모티프를 심을지)
  - 시각적 북엔드 설계 (Opening Image ↔ Final Image)
  - 상징적 상승(Symbolic Ascension) 계획
    (모티프가 영화 진행에 따라 어떻게 무게가 변하는지)
```

**설계 원칙:**
- 이미지 시스템은 반드시 **잠재의식적(subliminal)**이어야 한다 (McKee)
- 관객이 의식적으로 알아차리면 상징이 아니라 설교가 된다
- 특수에서 보편으로, 구체에서 원형적인 것으로 상징적 무게가 점진적으로 상승

### STEP 4. 캐릭터 재설계

```yaml
agent: Writer
input:
  - STEP 0~3 전체 산출물
  - 작법 레퍼런스 (Hauge, Arndt 캐릭터 소개 기법)
output:
  - 각 인물별:
    - 시각적 식별자 (즉각 인식 가능한 외적 표지)
    - 행동적 서브텍스트 (말과 행동의 불일치 설계)
    - 첫 등장 방식 (즉각 공개 vs 점진적 공개)
    - 변화 호(arc)와 시각 요소 연동 계획
  - 인물 관계 역학의 시각적 표현 전략
```

**설계 원칙:**
- 인물은 "설명"이 아닌 "관찰"로 소개되어야 한다 (Hauge)
- 두세 가지 선명하고 구체적인 시각적 디테일로 본질을 드러내기
- 악역/조연의 입체화: 직접 보여주기보다 **암시**로 깊이 만들기
- 수동적 주인공의 경우, STEP 2의 능동적 선택 지점과 연동

### 🔵 체크포인트 B — 시각 전략 및 인물 확정 리뷰

```yaml
agent: Critic → Human
timing: STEP 4 완료 후
review_criteria:
  - 이미지 시스템의 일관성 및 잠재의식적 수준 유지
  - 캐릭터 입체성 (특히 악역/조연)
  - 복선(Plant) 배치 계획의 "보이지 않음(Invisible)" 수준
  - 원작 추가 요청 사항 반영 여부 (ex: Her적 로맨스 깊이)
  - 시각적 식별자의 명확성과 서사적 기능성
significance: >
  씬 리스트에 들어가면 세부 조정은 가능해도
  캐릭터의 근본 설계를 바꾸긴 힘들다.
```

### STEP 5. 트리트먼트 (Treatment)

```yaml
agent: Writer
input:
  - STEP 1~4 전체 산출물
output:
  - 15~20페이지 분량 산문 (한국 시나리오 기준)
  - 시각적 묘사 중심, 대사 최소한
  - 핵심 장면은 상세 전개
  - 감정 곡선(emotional arc) 시각화
```

### STEP 6. 씬 리스트 (Scene List)

```yaml
agent: Writer
input:
  - STEP 5 산출물 (트리트먼트) — 핵심 입력
  - STEP 1~4 산출물 (구조적 참조)
output:
  - 70~85개 씬 나열 (90분 기준, 트리트먼트 기반 분해)
  - 각 씬별:
    - 씬 번호
    - 장소/시간
    - 등장인물
    - 핵심 이미지 1개 ("이 씬에서 카메라가 반드시 잡아야 할 것")
    - 해당 비트 번호
    - 이미지 시스템 모티프 해당 여부
    - 복선(Plant) 또는 회수(Payoff) 해당 여부
  - 씬 간 전환 방식 구상 (컷, 디졸브, 매치컷 등)
```

**작성 원칙:**
- 대사는 트리트먼트에서 10% 이하로 제한
- "카메라가 보는 것"만 서술
- 각 문단이 하나의 시퀀스에 대응

### 🔵 체크포인트 C — 집필 전 최종 리뷰

```yaml
agent: Critic → Human
timing: STEP 6 완료 후
review_criteria:
  - 전체 흐름과 감정 곡선의 자연스러움
  - 누락된 장면 또는 불필요한 장면 존재 여부
  - 복선-회수(Plant-Payoff) 매핑 완전성
  - 이미지 시스템 모티프의 분포 균형
  - 긴장/이완 리듬이 트리트먼트에서 체감되는지
  - breathing room(숨 쉬는 장면) 충분성
significance: >
  트리트먼트는 시나리오의 "설계도 최종본"이다.
  1고 집필에 들어가면 55~70페이지를 쓰게 되니,
  그 전에 전체를 최종 점검한다.
```

### STEP 7. 시나리오 1고 (First Draft)

```yaml
agent: Writer
input:
  - STEP 5 산출물 (트리트먼트)
  - STEP 3~4 산출물 (이미지 시스템, 캐릭터)
  - STEP 6 산출물 (씬 리스트)
  - 대사 전략 가이드 (STEP 0에서 도출)
output:
  - 완성된 시나리오 1고 (.docx)
  - 55~70페이지 (한국 시나리오 형식, 90분 기준)
  - 한국 시나리오 형식: 씬 헤딩, 대지문, 소지문, 대사
```

**집필 원칙:**
- Tony Tost: "모든 문장이 하나의 숏, 마침표마다 컷"
- Trottier: "스크린에 나타날 수 없는 것은 쓰지 마라"
- 액션 라인 최대 3~4줄 (업계 표준)
- 현재 시제, 능동태, 강력한 동사
- McKee: "큰 못(big nail)" 대신 "대못(spike)" — 구체적 단어 선택
- 한국 시나리오 여백의 미학: 감독이 해석할 공간 남기기

### STEP 8. 시각적 개고 (Visual Revision)

```yaml
agent: Critic (진단) → Writer (반영)
input:
  - STEP 7 산출물 (1고)
  - STEP 0 보완점 목록 (최종 대조)
  - STEP 3 이미지 시스템 설계
output:
  - 시각적 개고 완료된 최종 시나리오 (.docx / .pdf)
```

**Linda Seger 시각적 개고 프로세스:**

1. **대사 과다 장면 식별** → 시각적 행동으로 대체
2. **반복되는 시각 요소 식별** → 이미지 시스템 일관성 확인
3. **설명적 지문 탐지** → 영상적 지문으로 전환
   - "그는 외롭다" → "편의점 도시락을 혼자 먹는다" (행동으로 번역)
   - "그녀는 분노했다" → "유리잔을 움켜쥔 손가락이 하얗게 변한다"
4. **카메라 불가능 서술 제거**
   - "그는 오래 앉아 있었다" → "열 번째 담배를 비벼 끈다" (McKee)
5. **복선-회수 최종 점검** → 모든 Plant에 Payoff가 있는지, 그 역도 확인
6. **이미지 시스템 상징적 상승 확인** → 초반의 구체적 모티프가 결말에서 보편적 공명으로 변환되는지

---

## 5. 프로그램 동작 흐름 (Pseudocode)

```python
def run_workflow(project_config, synopsis_doc, reference_docs):
    
    # ──────────────────────────────────
    # Phase 1: 분석 (Analyst Agent)
    # ──────────────────────────────────
    
    step0_output = analyst.analyze_synopsis(
        synopsis=synopsis_doc,
        references=reference_docs,
        config=project_config
    )
    # → 사용자에게 보완점 목록 제시, 추가 보완점 수렴
    step0_output = orchestrator.collect_human_critique(step0_output)
    
    step1_output = analyst.design_act_structure(
        critique=step0_output,
        duration_estimate=project_config.duration_estimate
    )
    
    step2_output = analyst.design_beat_sheet(
        act_structure=step1_output,
        critique=step0_output
    )
    
    # ──────────────────────────────────
    # Checkpoint A: 구조 확정 리뷰
    # ──────────────────────────────────
    
    checkpoint_a_review = critic.review_structure(
        steps=[step0_output, step1_output, step2_output],
        criteria=CHECKPOINT_A_CRITERIA
    )
    
    human_decision_a = orchestrator.present_to_human(
        deliverables=[step1_output, step2_output],
        critic_review=checkpoint_a_review
    )
    
    if human_decision_a.revision_needed:
        # 수정 대상 Step으로 라우팅
        goto_step(human_decision_a.revision_targets)
    
    # ──────────────────────────────────
    # Phase 2: 시각 설계 (Writer Agent)
    # ──────────────────────────────────
    
    step3_output = writer.design_image_system(
        all_previous=[step0_output, step1_output, step2_output],
        references=reference_docs
    )
    
    step4_output = writer.redesign_characters(
        all_previous=[step0_output, step1_output, step2_output, step3_output],
        references=reference_docs
    )
    
    # ──────────────────────────────────
    # Checkpoint B: 시각 전략/인물 확정 리뷰
    # ──────────────────────────────────
    
    checkpoint_b_review = critic.review_visual_strategy(
        steps=[step3_output, step4_output],
        context=[step0_output, step1_output, step2_output],
        criteria=CHECKPOINT_B_CRITERIA
    )
    
    human_decision_b = orchestrator.present_to_human(
        deliverables=[step3_output, step4_output],
        critic_review=checkpoint_b_review
    )
    
    if human_decision_b.revision_needed:
        goto_step(human_decision_b.revision_targets)
    
    # ──────────────────────────────────
    # Phase 3: 씬 구축 (Writer Agent)
    # ──────────────────────────────────
    
    step5_output = writer.create_scene_list(
        all_previous=[step0..step4_outputs]
    )
    
    step6_output = writer.write_treatment(
        scene_list=step5_output,
        all_previous=[step0..step4_outputs]
    )
    
    # ──────────────────────────────────
    # Checkpoint C: 집필 전 최종 리뷰
    # ──────────────────────────────────
    
    checkpoint_c_review = critic.review_pre_draft(
        steps=[step5_output, step6_output],
        context=[step0..step4_outputs],
        criteria=CHECKPOINT_C_CRITERIA
    )
    
    human_decision_c = orchestrator.present_to_human(
        deliverables=[step5_output, step6_output],
        critic_review=checkpoint_c_review
    )
    
    if human_decision_c.revision_needed:
        goto_step(human_decision_c.revision_targets)
    
    # ──────────────────────────────────
    # Phase 4: 집필 & 개고
    # ──────────────────────────────────
    
    step7_output = writer.write_first_draft(
        treatment=step6_output,
        all_previous=[step0..step6_outputs]
    )
    
    step8_diagnosis = critic.visual_revision_diagnosis(
        first_draft=step7_output,
        image_system=step3_output,
        critique=step0_output
    )
    
    final_output = writer.apply_visual_revision(
        first_draft=step7_output,
        diagnosis=step8_diagnosis
    )
    
    return final_output  # 완성 시나리오 (.docx / .pdf)
```

---

## 6. 이론적 기반 요약

본 워크플로우에서 참조하는 핵심 이론과 적용 지점:

| 이론가/원칙 | 핵심 개념 | 적용 Step |
|------------|-----------|-----------|
| Syd Field | "시나리오는 그림으로 이야기하는 것", 3막 구조 | STEP 1 |
| Blake Snyder | 비트 시트, 시각적 북엔드 (Opening/Final Image) | STEP 2, 3 |
| Robert McKee | 이미지 시스템, 상징적 상승, "언어적 표현의 90%는 영화적 등가물 없음" | STEP 3, 8 |
| David Trottier | "스크린에 나타날 수 없는 것은 쓸 수 없다" | STEP 7, 8 |
| Tony Tost | "모든 문장이 하나의 숏, 마침표마다 컷" | STEP 7 |
| Michael Hauge | 시각적 디테일을 통한 캐릭터 소개 | STEP 4 |
| Linda Seger | 시각적 개고 프로세스 | STEP 8 |
| 봉준호 | 건축적 공간 메타포, 기승전결 '전(轉)' | STEP 3, 4, 5 |
| 한국 시나리오 전통 | 대지문/소지문, 여백의 미학, 협업적 해석 공간 | STEP 7 |
| 숏폼→장편 전환 | 극단적 시각적 경제성 → breathing room 추가 | STEP 0, 2, 6 |

---

## 7. 한국 시나리오 분량 기준 참고

| 항목 | 할리우드 | 한국 |
|------|---------|------|
| 표준 폰트 | Courier 12pt (고정) | 비표준 (9~14pt, 작가별 상이) |
| 1페이지 = 러닝타임 | ≈ 1분 | ≈ 1.3~1.5분 |
| 90분 영화 페이지 수 | ~90페이지 | ~55~70페이지 |
| 90분 영화 씬 수 | ~70~85 | ~70~85 (씬 수는 유사) |
| 1차 분량 지표 | 페이지 수 | **씬 수** (페이지는 참고용) |
| 형식 | INT./EXT., 엄격한 들여쓰기 | 작가별 자유 형식, 씬 넘버 표기 다양 |
| 지문 용어 | Action Line | 대지문(大指文) / 소지문(小指文) |

---

## 부록: KANTA 프로젝트 적용 예시

> 본 워크플로우 엔진의 첫 적용 사례로서, 「KANTA_로맨스스캠사건」 프로젝트의 설정값을 기록한다.

```yaml
KANTA_ProjectConfig:
  title: "KANTA (가제)"
  source_format: shortform         # 90초 × 50화 (총 75분)
  target_format: feature_film
  target_duration: 90
  genre: ["실화 범죄", "심리 스릴러", "로맨스"]
  tone: "로맨스 → 심리 스릴러 장르 전환"
  theme_direction: >
    "그럼에도 불구하고 연결을 갈망하는 인간의 본질"
    — 타락도 아니고 영원한 굴레도 아닌, 
    가짜 위에 세워진 진짜 감정의 모호한 비극
  reference_docs: 
    - 영화시나리오연구_영화적묘사_markdown.md
    - Senses_Touch_한국어시나리오.docx (촉각 시각화 기법 참고)
  synopsis_doc: KANTA_로맨스스캠사건.pdf
```

**KANTA 프로젝트 고유 보완점:**

1. 심리적 여정(유니티 아크) 심화 — 민준의 내면 변형 필요
2. 미드포인트(카페 장면)에서 스릴러적 전복 극대화 — 서윤 스토킹 피해 이력 활용
3. 보이지 않는 복선 설계 — "엄마 병원비" = 성형수술 단계, "울어서 부었다" = 수술 붓기
4. 단면적 인물 탈피 — 지우의 입체화는 암시로 처리 (미스터리 유지)
5. 게으른 정보 전달자 지양 — 박수범 형사 역할 전환 (정보 제공자 → 반응/해석자)
6. 《Her》적 로맨스 깊이 추가 — 화면/음성만으로 구축되는 깊은 친밀감, 관객도 함께 빠져들게

**KANTA 이미지 시스템 (안):**

| 모티프 | 의미 | 변화 |
|--------|------|------|
| 스크린/프레임 | 모든 관계가 화면 매개 | 핸드폰 → SNS → CCTV → 취조실 유리창 |
| 거울/반영 | 정체성의 복제와 가면 | 서윤 사진 → 유리창 반영 → 일방경 |
| 하강의 공간 | 내면 추락의 물리적 시각화 | 오피스텔(높은 층) → 모텔(지상) → 찜질방(지하) |
