from pydantic import BaseModel


class SandboxRequest(BaseModel):
    code: str
    input_data: str = ""  # 标准输入


class SandboxResponse(BaseModel):
    output: str
    error: str
    status: str  # "success", "compile_error", "runtime_error"
