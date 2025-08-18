import hashlib
import json
import re
from pathlib import Path

from modules.codex_guardian import run_guardian
from modules.codex_supreme import self_diagnostic

MANIFEST = "codex_manifest.json"
BANNED_KEYWORDS = ["TODO", "WIP", "temp_var", "placeholder"]


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_metadata(path: Path) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    legal = "unknown"
    m = re.search(r"Legal Function:\s*(.+)", text)
    if m:
        legal = m.group(1).strip()
    imports = set()
    for mod in re.findall(r"^import\s+([\w\.]+)", text, re.MULTILINE):
        imports.add(mod)
    for mod in re.findall(r"^from\s+([\w\.]+)\s+import", text, re.MULTILINE):
        imports.add(mod)
    return legal, sorted(imports)


def scan_for_banned_keywords(paths: list[Path]) -> None:
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for word in BANNED_KEYWORDS:
            pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
            for line in text.splitlines():
                if "BANNED_KEYWORDS" in line:
                    continue
                if re.search(rf"\b(no|without|recovered)[-\s]+{word}\b", line, re.IGNORECASE):
                    continue
                if pattern.search(line):
                    raise ValueError(f"Banned keyword '{word}' found in {p}")


def parse_required_folders() -> list[str]:
    cfg_path = Path(".codex_config.yaml")
    folders: list[str] = []
    if not cfg_path.exists():
        return folders
    capture = False
    for line in cfg_path.read_text().splitlines():
        if line.strip().startswith("required_folders:"):
            capture = True
            continue
        if capture:
            if line.startswith("  -"):
                folders.append(line.strip()[2:])
            elif line and not line.startswith(" "):
                break
    return folders


def verify_required_folders() -> None:
    missing = [f for f in parse_required_folders() if not Path(f).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required folders: {', '.join(missing)}")


def update_manifest() -> None:
    files = [p for p in Path(".").rglob("*.py") if not p.parts[0].startswith(".")]
    scan_for_banned_keywords(files)
    manifest = []
    for p in files:
        legal, deps = extract_metadata(p)
        manifest.append(
            {
                "module": p.stem,
                "path": str(p),
                "hash": hash_file(p),
                "legal_function": legal,
                "dependencies": deps,
            }
        )
    Path(MANIFEST).write_text(json.dumps(manifest, indent=2))


def main() -> None:
    run_guardian()
    verify_required_folders()
    update_manifest()
    self_diagnostic()
    print("codex manifest updated")


if __name__ == "__main__":
    main()
