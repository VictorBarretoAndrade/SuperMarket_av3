"""Executa Bandit, pip-audit e Safety e salva as saídas como evidência.

Uso (na raiz do repositório, com o venv ativo):
    python scripts/security_audit.py antes
    python scripts/security_audit.py depois

Saída: docs/evidencias/seguranca/<etapa>/
  ambiente.txt          versões do Python, SO e das ferramentas
  bandit.txt/.json      análise estática de src/
  pip-audit.txt         vulnerabilidades conhecidas em requirements.txt
  safety.txt            tentativa com Safety (pode exigir login/conta)

Falhas das ferramentas NÃO interrompem o script: o código de saída e a
mensagem de erro também são evidência (ex.: limitação de autenticação).
"""
import argparse
import datetime
import os
import platform
import subprocess  # nosec B404 - comandos fixos, sem shell e sem entrada externa
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(cmd):
    """Roda um comando fixo e devolve (código de saída, saída combinada)."""
    try:
        result = subprocess.run(  # nosec B603 - lista fixa de argumentos, shell=False
            cmd, cwd=ROOT, capture_output=True, text=True, timeout=900,
            stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace",
            env={**os.environ, "NO_COLOR": "1", "TERM": "dumb"})
        return result.returncode, result.stdout + result.stderr
    except (OSError, subprocess.TimeoutExpired) as error:
        return -1, f"Falha ao executar: {error}"


def save(out_dir, name, cmd):
    code, output = run(cmd)
    header = f"$ {' '.join(cmd)}\n# exit code: {code}\n\n"
    (out_dir / name).write_text(header + output, encoding="utf-8")
    print(f"  {name:<14} exit={code}")
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("etapa", choices=["antes", "depois"])
    parser.add_argument("--out", type=Path, default=None,
                        help="diretório de saída (padrão: docs/evidencias/seguranca/<etapa>)")
    args = parser.parse_args()

    out_dir = args.out or ROOT / "docs" / "evidencias" / "seguranca" / args.etapa
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Salvando em {out_dir}")

    commit = run(["git", "rev-parse", "--short", "HEAD"])[1].strip()
    env_lines = [
        f"data: {datetime.datetime.now().isoformat(timespec='seconds')}",
        f"etapa: {args.etapa}",
        f"commit: {commit}",
        f"python: {sys.version.split()[0]}",
        f"so: {platform.platform()}",
        f"bandit: {run([PY, '-m', 'bandit', '--version'])[1].strip()}",
        f"pip-audit: {run([PY, '-m', 'pip_audit', '--version'])[1].strip()}",
        f"safety: {run([PY, '-m', 'safety', '--version'])[1].strip()}",
    ]
    (out_dir / "ambiente.txt").write_text("\n".join(env_lines) + "\n", encoding="utf-8")

    save(out_dir, "bandit.txt", [PY, "-m", "bandit", "-r", "src"])
    bandit_json = out_dir / "bandit.json"
    code, _ = run([PY, "-m", "bandit", "-r", "src", "-f", "json", "-o", str(bandit_json)])
    print(f"  {'bandit.json':<14} exit={code}")
    save(out_dir, "pip-audit.txt",
         [PY, "-m", "pip_audit", "-r", "requirements.txt", "--desc"])

    # Safety 3.x usa "scan" (exige login); "check" é o modo legado/depreciado.
    code = save(out_dir, "safety.txt", [PY, "-m", "safety", "scan"])
    if code != 0:
        save(out_dir, "safety-check.txt",
             [PY, "-m", "safety", "check", "-r", "requirements.txt"])


if __name__ == "__main__":
    main()
