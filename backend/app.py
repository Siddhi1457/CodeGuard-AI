from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


@app.get("/")
def home():
    return {
        "message": "CodeGuard AI backend is running!"
    }


@app.post("/analyze")
def analyze_code(request: CodeRequest):

    code = request.code
    lines = code.splitlines()

    critical_count = 0
    high_count = 0
    medium_count = 0

    issues = []
    fixes = []

    for index, line in enumerate(lines):

        line_number = index + 1
        trimmed = line.strip()

        if (
            "password =" in trimmed
            or "passwd =" in trimmed
            or "api_key =" in trimmed
        ):
            critical_count += 1

            issues.append(
                f"Line {line_number}: CRITICAL - Possible hardcoded password or API key"
            )

            fixes.append(
                "Use environment variables instead of storing passwords or API keys directly in code."
            )

        if "eval(" in trimmed:
            critical_count += 1

            issues.append(
                f"Line {line_number}: CRITICAL - Dangerous eval() function detected"
            )

            fixes.append(
                "Avoid eval(). Use safer alternatives such as explicit parsing or validation."
            )

        if trimmed == "except:":
            high_count += 1

            issues.append(
                f"Line {line_number}: HIGH - Possible silently ignored exception"
            )

            fixes.append(
                "Catch a specific exception such as ValueError or TypeError instead of using a bare except."
            )

    if_count = sum(
        1 for line in lines
        if line.strip().startswith("if ")
    )

    if if_count >= 4:
        high_count += 1

        issues.append(
            "HIGH - Multiple conditional statements detected"
        )

        fixes.append(
            "Consider simplifying complex conditions or splitting the logic into smaller functions."
        )

    if len(lines) > 50:
        medium_count += 1

        issues.append(
            "MEDIUM - Large code block detected"
        )

        fixes.append(
            "Consider breaking the code into smaller functions or modules."
        )

    score = 100

    if critical_count > 0:
        score -= 40

    if high_count > 0:
        score -= 25

    if medium_count > 0:
        score -= 10

    score = max(score, 0)

    if score >= 80:
        severity = "LOW"
    elif score >= 60:
        severity = "MEDIUM"
    elif score >= 40:
        severity = "HIGH"
    else:
        severity = "CRITICAL"

    return {
        "score": score,
        "severity": severity,
        "critical": critical_count,
        "high": high_count,
        "medium": medium_count,
        "issues": issues,
        "fixes": fixes,
       "lines": len(lines),
"corrected_code": code
    }
