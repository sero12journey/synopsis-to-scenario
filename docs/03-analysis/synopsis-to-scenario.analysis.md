# Gap Analysis: synopsis-to-scenario

> **Date**: 2026-02-14
> **Phase**: PDCA Check
> **Match Rate**: 97%
> **Status**: PASS

---

## Overall Scores

| Category | Score | Status |
|----------|:-----:|:------:|
| File Existence (21 items) | 100% | PASS |
| Directory Structure (Section 2.2) | 95% | PASS |
| Prompt Structure (Section 3.1) | 100% | PASS |
| Agent System Prompts (Section 3.2) | 100% | PASS |
| Context Passing (Section 3.3) | 100% | PASS |
| STEP 7 Split Strategy (Section 4) | 100% | PASS |
| State Management (Section 5) | 97% | PASS |
| Checkpoint Protocol (Section 6) | 100% | PASS |
| Critic Evaluation Criteria (Section 7) | 100% | PASS |
| Implementation Order (Section 8) | 100% | PASS |
| Non-functional Requirements (Section 9) | 100% | PASS |
| **Overall** | **97%** | **PASS** |

## Gaps Found (3%, Minor)

### 1. Config 필드명 불일치 (Low)

| 위치 | CLAUDE.md | config_schema.yaml |
|------|-----------|-------------------|
| 시놉시스 필드 | `synopsis_doc` | `synopsis_file` |
| 레퍼런스 필드 | `reference_docs` | `reference_files` |
| 타겟 포맷 | `target_format: feature_film` | (누락) |

### 2. state.json version 초기값 (Low)

- Design 예시: `"version": 1` (실행 완료 상태)
- 구현: `"version": 0` (미실행 초기 상태)
- 영향: 없음 (구현이 더 논리적)

### 3. state.json 추가 필드 (Enhancement)

구현에서 Design보다 추가된 유용한 필드:
- `steps[N].agent` — 담당 에이전트 명시
- `checkpoints[X].after_step` — 트리거 Step 명시
- `checkpoints[X].max_revisions` — 최대 수정 횟수 명시

## Matched Items (97%)

- 21/21 파일 존재
- 12/12 프롬프트 템플릿 구조 준수
- 3/3 에이전트 시스템 프롬프트 (페르소나, 이론, 금지사항)
- 12/12 컨텍스트 전달 맵 일치
- 5/5 STEP 7 분할 전략 요소
- 15/15 체크포인트 체크리스트 항목 + 평가 로직
- 4/4 비기능 요구사항

## 권장 조치

1. CLAUDE.md의 ProjectConfig Schema 필드명을 config_schema.yaml과 일치시키기
2. Design 문서의 state.json 예시를 구현과 동기화
