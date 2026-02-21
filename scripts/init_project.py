"""
프로젝트 초기화 스크립트
사용법: python scripts/init_project.py <project_name>

projects/{project_name}/ 디렉토리를 생성하고
config.yaml과 state.json 초기 파일을 배치합니다.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent


def init_project(project_name: str) -> None:
    project_dir = ROOT_DIR / "projects" / project_name

    if project_dir.exists():
        print(f"[!] 프로젝트 '{project_name}'이 이미 존재합니다: {project_dir}")
        sys.exit(1)

    # 디렉토리 생성
    (project_dir / "input" / "references").mkdir(parents=True)
    (project_dir / "output").mkdir(parents=True)

    # config.yaml 복사
    config_schema = ROOT_DIR / "prompts" / "config_schema.yaml"
    config_dest = project_dir / "config.yaml"
    shutil.copy(config_schema, config_dest)
    print(f"[+] config.yaml 생성: {config_dest}")

    # state.json 생성
    state_schema_path = ROOT_DIR / "prompts" / "state_schema.json"
    with open(state_schema_path, encoding="utf-8") as f:
        state = json.load(f)

    state["project_name"] = project_name
    state["created_at"] = datetime.now().isoformat()

    state_dest = project_dir / "state.json"
    with open(state_dest, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"[+] state.json 생성: {state_dest}")

    print(f"""
[완료] 프로젝트 '{project_name}' 초기화 완료!

다음 단계:
  1. {config_dest} 편집 → 프로젝트 설정 입력
  2. {project_dir / 'input'}/에 시놉시스 파일 배치
  3. Claude Code 세션에서 워크플로우 시작
""")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python scripts/init_project.py <project_name>")
        sys.exit(1)

    init_project(sys.argv[1])
