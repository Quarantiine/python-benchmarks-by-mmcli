"""
Symbolic Calculus Engine & Interactive Terminal User Interface (TUI).

Unified entry point supporting all calculus project implementations under all-projects/calculus:
1. mmcli-flash-calculus         (Minovative Mind CLI - Gemini 3.6 Flash CAS Engine)
2. mmcli-flash-lite-calculus    (Minovative Mind CLI - Flash Lite Engine)
3. antigravity-flash-calculus   (Antigravity IDE - Gemini 3.6 Flash Engine TUI)
4. antigravity-opus-calculus    (Antigravity IDE - Claude Opus 4.6 Engine TUI)
5. antigravity-gemini-pro-calculus (Antigravity IDE - Gemini 3.1 Pro Engine TUI)

Examples:
  python3 main.py                          # Run active/saved default calculus engine
  python3 main.py -p flash                 # Run mmcli-flash-calculus (Gemini 3.6 Flash CAS)
  python3 main.py -p lite                  # Run mmcli-flash-lite-calculus (Flash Lite)
  python3 main.py -p opus                  # Run antigravity-opus-calculus (Claude Opus 4.6)
  python3 main.py -p ag-flash              # Run antigravity-flash-calculus (Antigravity Flash)
  python3 main.py --select                 # Interactively select/switch calculus engine
  python3 main.py --list-projects          # List all available projects & aliases
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "all-projects" / "calculus"
CONFIG_FILE = BASE_DIR / ".calculus_project"

PROJECTS: Dict[str, Dict[str, Any]] = {
    "mmcli-flash-calculus": {
        "dir_name": "mmcli-flash-calculus",
        "aliases": ["mmcli-flash", "flash", "mmcli", "cas", "1"],
        "title": "Minovative Mind CLI - Gemini 3.6 Flash (Full CAS Engine)",
        "type": "calculus_package",
    },
    "mmcli-flash-lite-calculus": {
        "dir_name": "mmcli-flash-lite-calculus",
        "aliases": ["mmcli-flash-lite", "flash-lite", "lite", "2"],
        "title": "Minovative Mind CLI - Flash Lite Engine",
        "type": "calculus_package",
    },
    "antigravity-flash-calculus": {
        "dir_name": "antigravity-flash-calculus",
        "aliases": ["antigravity-flash", "ag-flash", "3"],
        "title": "Antigravity IDE - Gemini 3.6 Flash Engine (TUI & AST Visualizer)",
        "type": "ag_flash",
    },
    "antigravity-opus-calculus": {
        "dir_name": "antigravity-opus-calculus",
        "aliases": ["antigravity-opus", "opus", "ag-opus", "4"],
        "title": "Antigravity IDE - Claude Opus 4.6 Engine (3-Pane Curses TUI)",
        "type": "ag_opus",
    },
    "antigravity-gemini-pro-calculus": {
        "dir_name": "antigravity-gemini-pro-calculus",
        "aliases": ["antigravity-gemini-pro", "pro", "ag-pro", "gemini-pro", "5"],
        "title": "Antigravity IDE - Gemini 3.1 Pro Engine (Textual TUI)",
        "type": "ag_pro",
    },
}


def resolve_project(key: str) -> Optional[Dict[str, Any]]:
    """Match a project key or alias to its registry entry."""
    key_lower = key.strip().lower()
    for proj_key, info in PROJECTS.items():
        if key_lower == proj_key.lower() or key_lower in info["aliases"]:
            return info
    return None


def get_saved_default() -> str:
    """Retrieve saved project from config file or env var."""
    env_val = os.environ.get("CALCULUS_PROJECT") or os.environ.get("CALCULUS_ENGINE")
    if env_val:
        res = resolve_project(env_val)
        if res:
            return res["dir_name"]

    if CONFIG_FILE.exists():
        try:
            val = CONFIG_FILE.read_text().strip()
            res = resolve_project(val)
            if res:
                return res["dir_name"]
        except Exception:
            pass
    return "mmcli-flash-lite-calculus"


def save_default(proj_dir_name: str):
    """Save active project to .calculus_project config file."""
    try:
        CONFIG_FILE.write_text(proj_dir_name.strip() + "\n")
    except Exception:
        pass


def print_projects_list():
    """Print all available calculus projects and aliases."""
    saved_key = get_saved_default()
    print("\nAvailable Calculus Projects:")
    print("=" * 72)
    for idx, (proj_key, info) in enumerate(PROJECTS.items(), start=1):
        active_marker = " * [ACTIVE DEFAULT]" if proj_key == saved_key else ""
        aliases_str = ", ".join(info["aliases"])
        print(f" [{idx}] {info['title']}{active_marker}")
        print(f"     Directory: {info['dir_name']}")
        print(f"     Aliases  : {aliases_str}\n")
    print("=" * 72)
    print("Switch engines via:")
    print("  python3 main.py --project <alias> [subcommand...]")
    print("  python3 main.py --select")
    print()


def interactive_select_project() -> Dict[str, Any]:
    """Interactively select active project engine."""
    saved_key = get_saved_default()
    print("\n" + "=" * 72)
    print("  SELECT CALCULUS ENGINE / PROJECT")
    print("=" * 72)
    for idx, (proj_key, info) in enumerate(PROJECTS.items(), start=1):
        active_marker = " * [ACTIVE]" if proj_key == saved_key else ""
        print(f"  {idx}) {info['title']}{active_marker}")
    print("=" * 72)

    while True:
        try:
            choice = input(f"Select engine (1-{len(PROJECTS)}) [Enter keeps current]: ").strip()
            if not choice:
                return PROJECTS[saved_key]
            res = resolve_project(choice)
            if res:
                save_default(res["dir_name"])
                print(f"Switched active calculus engine to: {res['title']}\n")
                return res
            print("Invalid selection. Please enter a valid number or alias.")
        except (KeyboardInterrupt, EOFError):
            print("\nSelection cancelled.")
            sys.exit(0)


def run_project(info: Dict[str, Any]):
    """Launch the chosen calculus project."""
    calculus_dir = PROJECTS_DIR / info["dir_name"]
    if not calculus_dir.exists():
        print(f"Error: Project directory '{calculus_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    proj_type = info["type"]

    if proj_type == "calculus_package":
        if str(calculus_dir) in sys.path:
            sys.path.remove(str(calculus_dir))

        if "calculus" in sys.modules:
            del sys.modules["calculus"]
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("calculus."):
                del sys.modules[mod_name]

        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "calculus",
            calculus_dir / "__init__.py",
            submodule_search_locations=[str(calculus_dir)]
        )
        calculus_mod = importlib.util.module_from_spec(spec)
        sys.modules["calculus"] = calculus_mod
        spec.loader.exec_module(calculus_mod)

        from calculus.cli import main as cli_main
        cli_main()

    elif proj_type == "ag_flash":
        if str(calculus_dir) not in sys.path:
            sys.path.insert(0, str(calculus_dir))

        for mod in ["core", "tui"]:
            if mod in sys.modules:
                del sys.modules[mod]
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("core.") or mod_name.startswith("tui."):
                del sys.modules[mod_name]

        from tui.app import CalculusTUIApp
        demo_mode = "--demo" in sys.argv or not sys.stdin.isatty()
        app = CalculusTUIApp()
        app.run(demo_mode=demo_mode)

    elif proj_type == "ag_opus":
        if str(calculus_dir) not in sys.path:
            sys.path.insert(0, str(calculus_dir))

        for mod in ["nodes", "parser", "tui"]:
            if mod in sys.modules:
                del sys.modules[mod]

        import tui
        tui.run_tui()

    elif proj_type == "ag_pro":
        if str(calculus_dir) not in sys.path:
            sys.path.insert(0, str(calculus_dir))

        for mod in ["parser", "math_ast"]:
            if mod in sys.modules:
                del sys.modules[mod]

        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "__main__",
            calculus_dir / "__main__.py"
        )
        main_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_mod)


def main():
    args = sys.argv[1:]
    target_project: Optional[Dict[str, Any]] = None

    i = 0
    clean_args = [sys.argv[0]]
    while i < len(args):
        arg = args[i]
        if arg in ("--project", "-p", "--engine", "-e"):
            if i + 1 < len(args):
                target_key = args[i + 1]
                res = resolve_project(target_key)
                if not res:
                    print(f"Error: Unknown project/engine alias '{target_key}'.", file=sys.stderr)
                    print_projects_list()
                    sys.exit(1)
                target_project = res
                i += 2
                continue
            else:
                print("Error: Missing argument for --project / -p.", file=sys.stderr)
                sys.exit(1)
        elif arg.startswith("--project=") or arg.startswith("-p=") or arg.startswith("--engine=") or arg.startswith("-e="):
            target_key = arg.split("=", 1)[1]
            res = resolve_project(target_key)
            if not res:
                print(f"Error: Unknown project/engine alias '{target_key}'.", file=sys.stderr)
                print_projects_list()
                sys.exit(1)
            target_project = res
            i += 1
            continue
        elif arg in ("--select", "--switch", "-s"):
            target_project = interactive_select_project()
            i += 1
            continue
        elif arg in ("--list-projects", "--projects", "-l"):
            print_projects_list()
            sys.exit(0)
        elif arg in ("--benchmark", "-b", "--bench"):
            import subprocess
            runner_path = BASE_DIR / "all-projects" / "calculus" / "calculus_engine_benchmark_runner.py"
            res = subprocess.run([sys.executable, str(runner_path)])
            sys.exit(res.returncode)
        else:
            clean_args.append(arg)
            i += 1

    sys.argv = clean_args

    if not target_project:
        default_dir = get_saved_default()
        target_project = PROJECTS.get(default_dir, PROJECTS["mmcli-flash-lite-calculus"])

    run_project(target_project)


if __name__ == "__main__":
    main()
