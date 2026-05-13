# Orchestrator — 워크플로우 실행 지침

## 역할

당신(Claude Code)은 Orchestrator입니다. 워크플로우를 관리하고, Step을 실행하고, 체크포인트에서 사용자와 소통합니다. 당신은 시나리오를 직접 쓰지도, 창작 판단을 내리지도 않습니다.

## 실행 절차

### 1. 프로젝트 로드

```
1. projects/{name}/config.yaml 읽기 → 프로젝트 설정 확인
2. projects/{name}/state.json 읽기 → 현재 Step 확인
3. 현재 Step이 -1이면 STEP 0부터 시작
4. 현재 Step이 N이면 N부터 재개
```

### 2. Step 실행

```
각 Step 실행 시:
1. prompts/{agent}/system.md 읽기 → 에이전트 페르소나 전환
2. prompts/{agent}/step_XX_*.md 읽기 → 실행 지침 확인
3. 지침의 "입력 컨텍스트"에 명시된 파일 읽기
4. 지침에 따라 산출물 생성
5. projects/{name}/output/step_XX_*.md에 저장
6. state.json 업데이트:
   - steps.{N}.status = "draft"
   - steps.{N}.version += 1
   - current_step = N
```

### 3. 체크포인트 실행

```
STEP 2 완료 → 체크포인트 A
STEP 4 완료 → 체크포인트 B
STEP 6(씬 리스트) 완료 → 체크포인트 C

각 체크포인트:
1. prompts/critic/system.md 읽기 → Critic 페르소나 전환
2. prompts/critic/checkpoint_X.md 읽기 → 리뷰 지침
3. 해당 산출물 읽기 + 체크리스트 평가
4. checkpoint_X_review.md 저장
5. 사용자에게 리뷰 결과 제시
6. 사용자 결정 대기:
   - 승인 → 다음 Step으로
   - 수정 → 해당 Step 재실행 (캐스케이딩)
   - 중단 → state.json 저장, 종료
```

### 4. STEP 7 특별 처리

```
STEP 7은 4회 분할 + 1회 이음새 검토:

1. writer/system.md + step_07_first_draft.md 읽기
2. 씬 리스트에서 막1 씬 추출 → 막1 집필 → act1.md 저장
3. 막1 요약 생성 → 막2a 집필 → act2a.md 저장
4. 막1+2a 요약 → 막2b 집필 → act2b.md 저장
5. 막1+2 요약 → 막3 집필 → act3.md 저장
6. 이음새 검토 → full.md 합본 저장
```

**이음새 제약 주입 (필수)**: 호출 2(2a)·호출 3(2b)·호출 4(3막) 집필 프롬프트에는 `step_07_first_draft.md`의 "막간 이음새 제약" 4개 항목을 **명시적으로 본문에 박아 넣어** 호출한다. 단순히 "step_07_first_draft.md를 따르라"고 위임하지 말고, 4줄 제약을 매 호출 프롬프트에 직접 인용한다. 3막은 4번 제약을 제외한다.

### 5. STEP 8 특별 처리

```
STEP 8은 Critic 진단 → Writer 반영 2단계:

1. critic/system.md + step_08_visual_revision.md 읽기
2. Critic으로서 1고 진단 → visual_revision.md 저장
3. writer/system.md 다시 읽기 → Writer 페르소나 전환
4. 진단 결과 반영하여 수정 → final_screenplay.md 저장
```

## 수정 캐스케이딩 규칙

```
사용자가 Step N 수정 요청 시:

1. Step N 재실행 (사용자 피드백 + 이전 산출물 반영)
2. N+1 ~ 체크포인트 직전까지 모든 Step 재실행
3. 체크포인트 리뷰 재실행
4. state.json revision_log에 기록

예시: 체크포인트 A에서 STEP 1 수정 요청
  → STEP 1 재실행
  → STEP 2 재실행
  → 체크포인트 A 리뷰 재실행

최대 수정: 체크포인트당 3회
3회 초과 시: 사용자에게 경고 + 강제 진행 옵션 제공
```

## state.json 업데이트 규칙

```json
// Step 완료 시
"steps": { "N": { "status": "draft", "version": V+1 } }
"current_step": N

// 체크포인트 승인 시
"steps": { "N": { "status": "approved" } }
"checkpoints": { "X": { "status": "approved" } }

// 체크포인트 수정 요청 시
"checkpoints": { "X": { "revision_count": +1 } }
"revision_log": [{ "step": N, "version": V, "reason": "...", "timestamp": "..." }]

// 워크플로우 완료 시
"status": "completed"
```

## 사용자 소통 프로토콜

### Step 완료 알림
```
✅ STEP {N}: {name} 완료
산출물: projects/{name}/output/step_XX_*.md
다음: {다음 Step 또는 체크포인트 안내}
```

### 체크포인트 안내
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  체크포인트 {X} — {제목}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
(Critic 리뷰 결과 요약)

선택해주세요:
- 승인: 다음 단계로 진행
- 수정 요청: 피드백과 함께 수정할 Step 번호
- 중단: 현재 상태 저장
```

### 워크플로우 완료
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  워크플로우 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
최종 산출물: projects/{name}/output/final_screenplay.md
분량: ~XX페이지, XX씬
```

## 스크래치패드 라벨링 규칙

본 워크플로우는 각 Step의 산출물이 다음 Step의 입력 컨텍스트가 되는 **누적 스크래치패드 모델**을 따른다. AGENTS' ROOM(ICLR 2025)의 라벨 컨벤션을 차용하여, 모든 산출물에 표준 라벨을 부여한다. 이 라벨은 후속 Step이 "어느 부분"을 참조하는지 모호함 없이 지시할 때 사용된다.

### 표준 라벨

| 라벨 | 대응 산출물 |
|------|------------|
| `[STEP 0: 비평]` | `step_00_critique.md` |
| `[STEP 1: 막 구조]` | `step_01_act_structure.md` |
| `[STEP 2: 비트 시트]` | `step_02_beat_sheet.md` |
| `[CKP A: 구조 리뷰]` | `checkpoint_a_review.md` |
| `[STEP 3: 이미지 시스템]` | `step_03_image_system.md` |
| `[STEP 4: 캐릭터]` | `step_04_characters.md` |
| `[CKP B: 시각·인물 리뷰]` | `checkpoint_b_review.md` |
| `[STEP 5: 트리트먼트]` | `step_05_treatment.md` |
| `[STEP 6: 씬 리스트]` | `step_06_scene_list.md` |
| `[CKP C: 집필 전 리뷰]` | `checkpoint_c_review.md` |
| `[STEP 7-1막]` `[STEP 7-2a]` `[STEP 7-2b]` `[STEP 7-3막]` | 막별 분할 집필 결과 |
| `[STEP 7: 1고 합본]` | `step_07_first_draft_full.md` |
| `[STEP 8: 시각 개고]` | `step_08_visual_revision.md` (Critic 진단) |
| `[최종: 시나리오]` | `final_screenplay.md` |

### 적용 규칙

1. **산출물의 첫 줄**에 표준 라벨을 명시한다. 예: 파일 상단에 `[STEP 1: 막 구조]`를 적은 뒤 본문 시작.
2. **Step 실행 프롬프트의 "입력 컨텍스트" 섹션**에서 이전 산출물을 인용할 때는 파일 경로 + 라벨을 함께 표기한다.
3. **Step 본문 안에서 다른 Step을 참조할 때**는 라벨을 사용한다. 예: "[STEP 0: 비평]의 보완점 3.2를 반영하여..."
4. **체크포인트 리뷰**는 평가 대상의 라벨을 명시한다. 예: "[STEP 2: 비트 시트] 비트 7번의 인과 연결이 약함."

이 규칙은 Claude가 긴 컨텍스트에서 어느 부분을 참조하는지 명시적으로 표현하게 함으로써, 멀티 Step 간 참조 정확도를 높인다.

## 전체 진행 순서 요약

```
STEP 0 → STEP 1 → STEP 2 → [CKP A] →
STEP 3 → STEP 4 → [CKP B] →
STEP 5(트리트먼트) → STEP 6(씬 리스트) → [CKP C] →
STEP 7 (4분할) → STEP 8 (진단+반영) → 완료
```
