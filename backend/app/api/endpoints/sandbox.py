import os
import shutil
import subprocess
import tempfile
import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models.user import User
from app.schemas.sandbox import SandboxRequest, SandboxResponse

router = APIRouter()


async def run_command(command: list, timeout: int = 5, input_data: str = None) -> tuple[str, str, int]:
    """
    运行命令（同步包装为异步），解决 Windows 下 asyncio.create_subprocess_exec 可能的不兼容问题。
    """
    def _sync_run():
        try:
            # 确保命令参数都是字符串
            cmd_args = [str(arg) for arg in command]
            
            # 使用同步 subprocess.run
            result = subprocess.run(
                cmd_args,
                input=input_data.encode() if input_data else None,
                capture_output=True, # 需要 Python 3.7+
                timeout=timeout,
                check=False
            )
            return result.stdout.decode(errors='replace'), result.stderr.decode(errors='replace'), result.returncode
        except subprocess.TimeoutExpired:
            return "", "Execution Timeout (runs longer than timeout)", -1
        except Exception as e:
            return "", f"System Error: {repr(e)}", -1

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_run)


@router.post("/execute", response_model=SandboxResponse)
async def execute_code(
    request: SandboxRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    执行 C++ 代码（临时演示版：直接在本机编译运行）。
    注意：这极其不安全，生产环境必须换成 Docker 隔离执行。
    """
    # 检查是否有 g++
    gpp_path = shutil.which("g++")
    if not gpp_path:
        # 再次尝试常见路径，以防 PATH 未设置
        possible_paths = [
            r"C:\msys64\ucrt64\bin\g++.exe",
            r"C:\MinGW\bin\g++.exe",
            r"C:\Program Files\MinGW-w64\x86_64-8.1.0-posix-seh-rt_v6-rev0\mingw64\bin\g++.exe",
        ]
        for p in possible_paths:
            if os.path.exists(p):
                gpp_path = p
                break
    
    if not gpp_path:
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: g++ compiler not found. Please install MinGW-w64 or g++."
        )

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        source_file = os.path.join(temp_dir, "main.cpp")
        exe_file = os.path.join(temp_dir, "main.exe" if os.name == 'nt' else "main")


        # 写入源码
        with open(source_file, "w", encoding="utf-8") as f:
            f.write(request.code)

        # 1. 编译
        # 使用绝对路径，避免依赖 PATH
        compile_cmd = [gpp_path, source_file, "-o", exe_file]
        stdout, stderr, returncode = await run_command(compile_cmd, timeout=10)

        if returncode != 0:
            return SandboxResponse(
                output="",
                error=f"Compile Error:\n{stderr}",
                status="compile_error"
            )

        # 2. 运行
        run_cmd = [exe_file]
        stdout, stderr, returncode = await run_command(run_cmd, timeout=5, input_data=request.input_data)

        if returncode == -1 and "Timeout" in stderr:
            return SandboxResponse(output=stdout, error=stderr, status="runtime_error")
        
        if returncode != 0:
            return SandboxResponse(
                output=stdout,
                error=f"Runtime Error (Exit Code {returncode}):\n{stderr}",
                status="runtime_error"
            )

        return SandboxResponse(output=stdout, error=stderr, status="success")
