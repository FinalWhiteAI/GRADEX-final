from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
import uuid
from pathlib import Path
import shutil

app = FastAPI(title="Python Compute Engine (RAW CODE MODE)")

# ---------------------------
# 🔥 ENABLE CORS HERE
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all frontends (React, ngrok, devtunnel)
    allow_credentials=True,
    allow_methods=["*"],          # allow POST
    allow_headers=["*"],          # allow all headers (Content-Type: text/plain)
)
# ---------------------------


@app.post("/execute")
async def execute_code(request: Request):
    # Read raw Python code directly
    code = await request.body()
    code = code.decode("utf-8")

    if not code.strip():
        raise HTTPException(status_code=400, detail="No code provided")

    run_id = str(uuid.uuid4())
    tmp_dir = Path(tempfile.mkdtemp(prefix="run-"))

    # Save user code
    code_file = tmp_dir / "code.py"
    code_file.write_text(code)

    # Windows safe runner
    runner_script = tmp_dir / "runner.py"
    runner_script.write_text(
        """
import sys, traceback

try:
    with open("code.py") as f:
        code = f.read()

    safe_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "dict": dict,
            "list": list,
            "set": set,
            "tuple": tuple,
            "enumerate": enumerate,
            "sum": sum
        }
    }

    exec(code, safe_globals, {})
except Exception:
    traceback.print_exc()
    sys.exit(1)
"""
    )

    try:
        proc = subprocess.run(
            ["python", str(runner_script)],
            capture_output=True,
            text=True,
            cwd=tmp_dir,
            timeout=6
        )
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=408, detail="Execution timed out")

    stdout = proc.stdout
    stderr = proc.stderr
    exit_code = proc.returncode

    shutil.rmtree(tmp_dir, ignore_errors=True)

    return JSONResponse({
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "run_id": run_id
    })
