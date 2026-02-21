# Synopsis to Screenplay Workflow Engine

시놉시스를 장편 영화 시나리오로 전환하는 멀티 에이전트 워크플로우 엔진.

1\~3페이지 분량의 시놉시스를 입력받아, 사전 분석(비평) → 막 구조 → 비트시트 → 트리트먼트(15\~25페이지) → 초고(55\~70페이지)까지, 한국어 장편 영화 시나리오(90분, 70\~85씬)를 단계적으로 산출합니다. Claude Code에 최적화되어 있으나, Cursor, Windsurf 등 AI 코딩 도구나 ChatGPT, Claude 웹/앱에서 프롬프트를 직접 실행해도 사용할 수 있습니다.

2편의 상업 영화를 제작했고, 10년간 영화 투자 업계에 종사했던 20년차 영화인(비개발자)이 바이브 코딩으로 만든 프로그램입니다.

## Architecture

```
[입력] 시놉시스 + 레퍼런스
         │
         ▼
┌─────────────────────────────┐
│     Orchestrator Agent      │
│  워크플로우 제어 · 체크포인트 │
└──────────┬──────────────────┘
    ┌──────┼──────────┐
    ▼      ▼          ▼
 Analyst  Writer    Critic
```

| Agent | Role | Steps |
|-------|------|-------|
| **Orchestrator** | 워크플로우 제어, 데이터 전달, 체크포인트 관리, 피드백 라우팅 | All |
| **Analyst** | 스토리 아키텍트 — 시놉시스 분석, 막 구조, 비트시트 | 0, 1, 2 |
| **Writer** | 시나리오 작가 — 이미지 시스템, 인물, 트리트먼트, 씬 리스트, 초고 | 3, 4, 5, 6, 7 |
| **Critic** | 스크립트 닥터 — 구조 진단, 서브텍스트, 이미지 일관성, 비주얼 리비전 | Checkpoints, 8 |

**설계 원칙**: Writer는 자기 산출물을 스스로 평가하지 않습니다 (자기확인 편향 방지). Critic이 먼저 리뷰하고, 사람이 최종 판단합니다.

## Workflow Pipeline

```
STEP 0  [Analyst]  시놉시스 사전분석 (비평)
STEP 1  [Analyst]  막 구조 & 러닝타임 설계
STEP 2  [Analyst]  비트시트 (15비트, Snyder 기반)
        ──── Checkpoint A: 구조 확정 ────
STEP 3  [Writer]   이미지 시스템 설계
STEP 4  [Writer]   인물 재설계
        ──── Checkpoint B: 비주얼 전략 & 인물 확정 ────
STEP 5  [Writer]   트리트먼트 (15\~20페이지)
STEP 6  [Writer]   씬 리스트 (70\~85씬)
        ──── Checkpoint C: 초고 전 최종 리뷰 ────
STEP 7  [Writer]   초고 (55\~70페이지, 막별 분할 집필)
STEP 8  [Critic]   비주얼 리비전 (Linda Seger 프로세스)
```

각 체크포인트에서 Critic 리뷰 → 사람 승인/수정/재작업 결정.

## Project Structure

```
prompts/
├── orchestrator.md                  # 전체 실행 흐름
├── config_schema.yaml               # 프로젝트 설정 스키마
├── state_schema.json                # 진행 상태 스키마
├── analyst/
│   ├── system.md                    # Analyst 페르소나
│   ├── step_00_critique.md
│   ├── step_01_act_structure.md
│   └── step_02_beat_sheet.md
├── writer/
│   ├── system.md                    # Writer 페르소나
│   ├── step_03_image_system.md
│   ├── step_04_characters.md
│   ├── step_05_treatment.md
│   ├── step_06_scene_list.md
│   ├── step_07_first_draft.md
│   └── step_07_examples.md
└── critic/
    ├── system.md                    # Critic 페르소나
    ├── checkpoint_a.md
    ├── checkpoint_b.md
    ├── checkpoint_c.md
    └── step_08_visual_revision.md
scripts/
├── init_project.py                  # 프로젝트 초기화
└── md_to_docx.py                    # Markdown → .docx 변환
projects/                            # 프로젝트별 작업 디렉토리 (.gitignore)
└── {name}/
    ├── config.yaml
    ├── state.json
    ├── input/                       # 시놉시스 원본
    └── output/                      # 단계별 산출물
```

## Quick Start

### 1. 프로젝트 초기화

```bash
python scripts/init_project.py my-project
```

### 2. 설정

`projects/my-project/config.yaml`을 편집하여 제목, 장르, 톤 등을 설정하고, `projects/my-project/input/`에 시놉시스 파일을 배치합니다.

### 3. 워크플로우 실행

Claude Code 세션에서:

```
이 프로젝트의 워크플로우를 시작해 주세요.
```

이전 세션에서 이어서 작업하려면:

```
워크플로우 이어서 진행해 주세요.
```

### 4. 최종 산출물 변환

```bash
pip install python-docx
python scripts/md_to_docx.py projects/my-project/output/final_screenplay.md
```

## Theoretical Foundations

| Theorist | Key Concept | Applied In |
|----------|-------------|------------|
| Syd Field | 3막 구조 | STEP 1 |
| Blake Snyder | 비트시트, 비주얼 북엔드 | STEP 2, 3 |
| Robert McKee | 이미지 시스템, 상징적 상승 | STEP 3, 8 |
| David Trottier | 화면에 보이는 것만 쓴다 | STEP 7, 8 |
| Michael Hauge | 비주얼 디테일 인물 소개 | STEP 4 |
| Linda Seger | 비주얼 리비전 프로세스 | STEP 8 |
| Tony Tost | 가상 샷 리스트 (문장=샷) | STEP 7 |
| Bong Joon-ho | 건축적 공간 메타포, 전(轉) | STEP 3, 4, 5 |
| David Mamet | "무성영화 테스트" | STEP 8 |

## Korean Screenplay Conventions

- **기본 단위**: 씬 수 (페이지 수가 아님 — 한국 시나리오는 표준화된 폰트/레이아웃이 없음)
- **90분 영화**: 70\~85씬, 55\~70페이지
- **페이지:분 비율**: 1.3\~1.5 (할리우드 Courier 12pt의 1:1이 아님)
- **용어**: 대지문, 소지문, 씬 헤딩, 대사
- **미학**: 여백의 미학 — 감독의 해석 여지를 남긴다

## Requirements

- LLM 환경 — [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://cursor.com), [Windsurf](https://windsurf.com) 등 AI 코딩 도구 또는 Claude/ChatGPT 등 LLM 대화 환경
- Python 3.8+ (유틸리티 스크립트)
- `python-docx` (최종 .docx 변환 시)

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

- **BY** — 출처 표시 필수
- **NC** — 상업적 사용 금지 (상업적 이용은 별도 협의)
- **SA** — 동일 조건 변경 허락 (파생물도 같은 라이선스 적용)

본 라이선스는 워크플로우 엔진(프롬프트, 스크립트, 설계 문서)에 적용됩니다. 이 도구를 사용하여 생성된 시나리오의 저작권은 사용자에게 귀속됩니다.
