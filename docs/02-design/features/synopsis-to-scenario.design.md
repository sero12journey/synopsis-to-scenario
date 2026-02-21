# Design: Synopsis to Screenplay Workflow Engine

> **Feature**: synopsis-to-scenario
> **Created**: 2026-02-14
> **Updated**: 2026-02-14
> **Status**: Draft
> **PDCA Phase**: Design
> **Plan Reference**: `docs/01-plan/features/synopsis-to-scenario.plan.md`

---

## 1. 기술 결정 사항 (Technical Decisions)

| 항목 | 결정 | 근거 |
|------|------|------|
| 구현 전략 | **A-1: Claude Code 직접 실행** | MAX 구독으로 추가 비용 없음, 코드 개발 불필요 |
| 실행 환경 | Claude Code 세션 | 프롬프트 파일 읽기 → 실행 → 산출물 파일 저장 |
| 상태 저장 | JSON 파일 기반 | 프로젝트 디렉토리 내 state.json |
| 산출물 | Markdown 파일 | 각 Step별 .md 파일로 저장 |
| API 비용 | 없음 | Claude MAX 구독 범위 내 |

### Python의 역할 (보조)

Python은 LLM 호출이 아닌 **후처리 유틸리티**로만 사용:
- Markdown → .docx 변환 스크립트
- state.json 초기화/검증 스크립트
- (선택) 시놉시스 PDF → 텍스트 추출

---

## 2. 시스템 아키텍처

### 2.1 실행 모델

```
사용자
  │
  ▼
Claude Code 세션 (Orchestrator)
  │  CLAUDE.md 읽음 → 워크플로우 규칙 인지
  │
  │  Step 실행 루프:
  │    1. state.json 읽기 → 현재 Step 확인
  │    2. prompts/step_XX.md 읽기 → 에이전트 프롬프트 로드
  │    3. 이전 산출물 읽기 → 컨텍스트 구성
  │    4. 프롬프트 + 컨텍스트로 산출물 생성
  │    5. output/step_XX_*.md에 저장
  │    6. state.json 업데이트
  │    7. 체크포인트면 → 사용자에게 리뷰 요청
  │
  ▼
프로젝트 파일 시스템 (산출물)
```

### 2.2 전체 디렉토리 구조

```
synopsis-to-scenario/
├── CLAUDE.md                           # Claude Code 프로젝트 지침
├── synopsis_to_screenplay_workflow.md  # 원본 명세서 (이론/규칙)
│
├── prompts/                            # 에이전트별 프롬프트 파일
│   ├── orchestrator.md                 # 워크플로우 실행 지침
│   ├── analyst/
│   │   ├── system.md                   # Analyst 페르소나 + 이론 기반
│   │   ├── step_00_critique.md         # STEP 0 실행 프롬프트
│   │   ├── step_01_act_structure.md    # STEP 1 실행 프롬프트
│   │   └── step_02_beat_sheet.md       # STEP 2 실행 프롬프트
│   ├── writer/
│   │   ├── system.md                   # Writer 페르소나 + 작법 원칙
│   │   ├── step_03_image_system.md
│   │   ├── step_04_characters.md
│   │   ├── step_05_treatment.md
│   │   ├── step_06_scene_list.md
│   │   └── step_07_first_draft.md      # 막별 분할 집필 지침 포함
│   └── critic/
│       ├── system.md                   # Critic 페르소나 + 평가 기준
│       ├── checkpoint_a.md             # 체크포인트 A 리뷰 프롬프트
│       ├── checkpoint_b.md
│       ├── checkpoint_c.md
│       └── step_08_visual_revision.md
│
├── projects/                           # 프로젝트별 작업 디렉토리
│   └── {project_name}/
│       ├── config.yaml                 # 프로젝트 설정
│       ├── state.json                  # 워크플로우 상태
│       ├── input/                      # 원작 시놉시스, 레퍼런스
│       │   ├── synopsis.md (or .pdf)
│       │   └── references/
│       └── output/                     # Step별 산출물
│           ├── step_00_critique.md
│           ├── step_01_act_structure.md
│           ├── step_02_beat_sheet.md
│           ├── checkpoint_a_review.md
│           ├── step_03_image_system.md
│           ├── step_04_characters.md
│           ├── checkpoint_b_review.md
│           ├── step_05_treatment.md
│           ├── step_06_scene_list.md
│           ├── checkpoint_c_review.md
│           ├── step_07_first_draft_act1.md
│           ├── step_07_first_draft_act2a.md
│           ├── step_07_first_draft_act2b.md
│           ├── step_07_first_draft_act3.md
│           ├── step_07_first_draft_full.md
│           ├── step_08_visual_revision.md
│           └── final_screenplay.md
│
├── scripts/                            # 보조 Python 스크립트
│   ├── md_to_docx.py                  # Markdown → .docx 변환
│   └── init_project.py                # 프로젝트 디렉토리 초기화
│
└── docs/                               # PDCA 문서
    ├── 01-plan/
    └── 02-design/
```

---

## 3. 프롬프트 설계

### 3.1 프롬프트 구조 원칙

각 Step의 프롬프트 파일은 다음 구조를 따른다:

```markdown
# [Agent명] — STEP N: [Step명]

## 페르소나
(이 Step에서의 역할과 전문성)

## 입력 컨텍스트
(이전 Step 산출물 참조 지시 — 파일 경로로 명시)

## 작업 지시
(구체적 수행 내용, 체크리스트)

## 출력 형식
(Markdown 구조, 섹션 헤딩, 필수 포함 항목)

## 품질 기준
(자체 점검 체크리스트)

## 주의사항
(금지 사항, 흔한 실수 방지)
```

### 3.2 에이전트별 시스템 프롬프트 핵심

#### Analyst (`prompts/analyst/system.md`)

```
페르소나: 구조 분석가 / 스토리 아키텍트
이론 기반:
  - Syd Field 3막 구조론
  - Blake Snyder 15비트 시트
  - 한국 시나리오 분량 기준 (1p ≈ 1.3~1.5분)
  - 봉준호 기승전결 '전(轉)' 개념
출력 스타일: 구조화된 분석 (표, 리스트, YAML 블록)
금지: 창작하지 않음. 구조만 설계함.
```

#### Writer (`prompts/writer/system.md`)

```
페르소나: 시나리오 작가
작법 원칙:
  - McKee 이미지 시스템 (잠재의식적 상징)
  - Tony Tost "모든 문장이 하나의 숏, 마침표마다 컷"
  - Trottier "보이고 들리는 것만 쓰라"
  - 봉준호 건축적 공간 메타포
  - 한국 시나리오 여백의 미학
출력 스타일: 창작 산문 (시나리오 형식)
금지: 자기 글을 평가하지 않음. 쓰기만 함.
```

#### Critic (`prompts/critic/system.md`)

```
페르소나: 시나리오 닥터 / 스크립트 컨설턴트
평가 기반:
  - 체크포인트별 체크리스트 (섹션 9 참조)
  - STEP 0 보완점 목록 대조
  - 작법 레퍼런스 기반 진단
출력 스타일: 구조화된 리뷰 (평가/우려/권고/질문)
금지: 직접 수정하지 않음. 진단만 함. (STEP 8 제외)
```

### 3.3 컨텍스트 전달 전략

Claude Code 세션에서의 컨텍스트 관리:

```
Step 실행 시 Claude Code가 읽어야 할 파일:

STEP 0: synopsis.md + references/*
STEP 1: step_00_critique.md
STEP 2: step_00 + step_01
CKP A:  step_00 + step_01 + step_02
STEP 3: step_00 ~ step_02
STEP 4: step_00 ~ step_03
CKP B:  step_03 + step_04
STEP 5: step_00 ~ step_04 (전체)
STEP 6: step_05 + step_03 + step_04
CKP C:  step_05 + step_06
STEP 7: 막별 분할 (아래 섹션 참조)
STEP 8: step_07_full + step_03 + step_00
```

**원칙**: 모든 산출물을 매번 읽지 않는다. 각 Step 프롬프트에 필요한 파일 목록을 명시하고, 해당 파일만 읽는다.

---

## 4. STEP 7 막별 분할 집필 설계

### 4.1 분할 전략

55~70페이지 시나리오를 한 번에 생성하면 품질이 떨어지고 컨텍스트가 흐려진다.
**4회 분할 집필** + **1회 이음새 검토**로 진행:

```
호출 1: 막 1 집필
  입력: writer/system.md + step_05(씬 리스트 중 막1) + step_03 + step_04
  출력: step_07_first_draft_act1.md (~15-18페이지)

호출 2: 막 2a 집필
  입력: writer/system.md + act1 요약(3페이지) + step_05(막2a) + step_03 + step_04
  출력: step_07_first_draft_act2a.md (~15-18페이지)

호출 3: 막 2b 집필
  입력: writer/system.md + act1-2a 요약(3페이지) + step_05(막2b) + step_03 + step_04
  출력: step_07_first_draft_act2b.md (~15-18페이지)

호출 4: 막 3 집필
  입력: writer/system.md + act1-2 요약(4페이지) + step_05(막3) + step_03 + step_04
  출력: step_07_first_draft_act3.md (~15-18페이지)

호출 5: 이음새 검토
  입력: 각 막의 마지막 2씬 + 다음 막의 첫 2씬 (3개 이음새)
  출력: 연결 부분 수정 → step_07_first_draft_full.md (합본)
```

### 4.2 막간 요약 형식

이전 막을 다음 막에 전달할 때 사용하는 요약 형식:

```markdown
## 이전 막 요약 (막 1)
- **마지막 씬 상황**: [현재 상태 서술]
- **캐릭터 감정 상태**: [주인공/주요 인물의 심리적 위치]
- **미해결 복선**: [이 막에서 심어졌지만 아직 회수되지 않은 것]
- **이미지 모티프 상태**: [현재까지 모티프가 어떻게 변화했는지]
- **마지막 대사/이미지**: [직전 씬의 마지막 문장 — 톤 연결용]
```

---

## 5. 상태 관리 설계

### 5.1 state.json 구조

```json
{
  "project_name": "kanta",
  "created_at": "2026-02-14T10:00:00",
  "current_step": 2,
  "status": "in_progress",
  "steps": {
    "0": {"name": "critique", "status": "approved", "version": 1},
    "1": {"name": "act_structure", "status": "approved", "version": 1},
    "2": {"name": "beat_sheet", "status": "draft", "version": 1}
  },
  "checkpoints": {
    "A": {"status": "pending", "revision_count": 0},
    "B": {"status": "pending", "revision_count": 0},
    "C": {"status": "pending", "revision_count": 0}
  },
  "revision_log": []
}
```

### 5.2 상태 전이 규칙

```
Step 상태: pending → draft → reviewed → approved
                              ↑          │
                              └──────────┘ (수정 시)

체크포인트 상태: pending → in_review → approved
                              ↑          │
                              └──────────┘ (수정 시, 최대 3회)
```

### 5.3 세션 간 재개 방법

Claude Code 새 세션에서 워크플로우를 재개하는 방법:

```
사용자: "KANTA 프로젝트 워크플로우를 이어서 진행해줘"

Claude Code:
  1. CLAUDE.md 읽기 → 프로젝트 규칙 인지
  2. projects/kanta/state.json 읽기 → current_step 확인
  3. 해당 Step의 프롬프트 파일 읽기
  4. 필요한 이전 산출물 파일 읽기
  5. 다음 Step 실행
```

---

## 6. 체크포인트 대화 프로토콜

### 6.1 Critic 리뷰 → 사용자 승인 흐름

```
[체크포인트 진입]
  │
  ▼
Claude Code가 Critic 프롬프트로 전환
  → critic/checkpoint_X.md 읽기
  → 해당 Step 산출물 + 체크리스트로 리뷰 생성
  → output/checkpoint_X_review.md 저장
  │
  ▼
사용자에게 리뷰 결과 제시
  → 평가 (pass / conditional_pass / rework_needed)
  → 우려 사항 목록
  → 개선 권고
  → 사용자에게 질문
  │
  ▼
사용자 결정 대기
  → 승인: 다음 Step으로 진행
  → 수정 요청: 피드백 수렴 → 해당 Step 재실행
  → 중단: state.json 저장 후 종료
```

### 6.2 수정 캐스케이딩 규칙

```
수정 대상 Step이 N일 때:
  1. Step N 재실행 (사용자 피드백 반영)
  2. N 이후 ~ 체크포인트 직전까지의 Step은 "invalidated"
  3. invalidated Step을 순차 재실행
  4. 체크포인트 리뷰 재실행

예시: 체크포인트 A에서 STEP 1 수정 요청
  → STEP 1 재실행
  → STEP 2 재실행 (STEP 1에 의존하므로)
  → 체크포인트 A 리뷰 재실행

최대 수정 횟수: 체크포인트당 3회
```

---

## 7. Critic 평가 기준 정량화

### 체크포인트별 체크리스트 (pass 기준)

**체크포인트 A (구조 확정)**:
- [ ] 각 막의 씬 수가 목표 범위 내 (±3)
- [ ] 미드포인트가 전체 러닝타임의 47~53% 위치
- [ ] 주인공 능동적 선택 지점 최소 3곳
- [ ] 비트 15개 모두 배치됨
- [ ] STEP 0 보완점 중 구조 관련 항목 반영됨

**체크포인트 B (시각/인물 확정)**:
- [ ] 이미지 모티프 3개 이상 정의됨
- [ ] 시각적 북엔드(Opening↔Final Image) 대응 설계됨
- [ ] 모든 주요 인물에 시각적 식별자 부여됨
- [ ] 악역/조연 최소 1명 입체화 설계됨
- [ ] 복선(Plant) 3개 이상 배치됨

**체크포인트 C (집필 전 최종)**:
- [ ] 씬 수 70~85 범위 내
- [ ] 모든 Plant에 대응 Payoff 존재
- [ ] 트리트먼트에서 대사 비율 10% 이하
- [ ] breathing room 씬 최소 3곳
- [ ] 이미지 모티프가 3개 막에 고르게 분포

**평가 로직**:
- 모든 항목 충족 → `pass`
- 1~2개 미충족 → `conditional_pass` (권고 후 진행 가능)
- 3개 이상 미충족 → `rework_needed` (수정 필수)

---

## 8. 구현 순서 (Implementation Order)

```
Phase 1: 프로젝트 기반
  1. 디렉토리 구조 생성
  2. config.yaml 스키마 정의
  3. state.json 초기 구조 정의
  4. CLAUDE.md 업데이트 (워크플로우 실행 지침 추가)

Phase 2: 프롬프트 작성 — 분석 파이프라인
  5. prompts/analyst/system.md
  6. prompts/analyst/step_00_critique.md
  7. prompts/analyst/step_01_act_structure.md
  8. prompts/analyst/step_02_beat_sheet.md
  9. prompts/critic/checkpoint_a.md

Phase 3: 프롬프트 작성 — 시각 설계
  10. prompts/writer/system.md
  11. prompts/writer/step_03_image_system.md
  12. prompts/writer/step_04_characters.md
  13. prompts/critic/checkpoint_b.md

Phase 4: 프롬프트 작성 — 트리트먼트 & 씬 구축
  14. prompts/writer/step_05_treatment.md
  15. prompts/writer/step_06_scene_list.md
  16. prompts/critic/checkpoint_c.md

Phase 5: 프롬프트 작성 — 집필
  17. prompts/writer/step_07_first_draft.md (막별 분할 지침 포함)
  18. prompts/critic/step_08_visual_revision.md
  19. prompts/orchestrator.md (전체 실행 지침)

Phase 6: 보조 스크립트
  20. scripts/init_project.py (프로젝트 디렉토리 + config + state 초기화)
  21. scripts/md_to_docx.py (최종 변환)
```

---

## 9. 비기능 요구사항

| 항목 | 기준 |
|------|------|
| API 비용 | 없음 (MAX 구독 범위) |
| Step당 실행 시간 | Claude Code 응답 시간에 의존 (~1-3분) |
| 전체 워크플로우 시간 | ~1-2시간 (피드백 시간 제외) |
| 세션 간 재개 | state.json 기반, 새 세션에서 이어서 진행 가능 |
| 최대 수정 루프 | 체크포인트당 3회 |
| 산출물 보존 | 모든 중간 산출물 .md 파일로 보존 |
