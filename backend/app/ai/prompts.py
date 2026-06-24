"""大模型提示词模板。"""

# 实训成果智能核查提示词。
# 占位符使用 {{...}} 双花括号，避免与 JSON 示例中的花括号冲突，
# 通过 build_review_prompt() 以字符串替换方式注入，故不走 str.format/f-string。
REVIEW_PROMPT_TEMPLATE = """你是专业的软件实训评审专家，请严格根据实训要求，对学生提交的成果进行智能核查，输出结构化结果。

【实训要求】
{{training_requirement}}

【学生提交的代码/文档内容】
{{student_content}}

【核查维度】
1. 功能实现校验：判断是否完成所有要求功能，列出未完成的功能点
2. 逻辑漏洞识别：检查代码中的逻辑错误、异常处理缺失、潜在bug
3. 步骤完整性：核对实训要求的开发步骤是否全部完成，列出缺失项
4. 代码/文档规范：命名规范、注释完整度、格式规范性

请严格按照以下JSON格式输出，不要输出额外解释文字：
{
  "function_check": {
    "is_complete": true/false,
    "problem_list": ["问题1", "问题2"]
  },
  "logic_check": {
    "has_risk": true/false,
    "risk_list": ["风险点1", "风险点2"]
  },
  "step_check": {
    "is_complete": true/false,
    "missing_steps": ["缺失步骤1", "缺失步骤2"]
  },
  "standard_score": 0-100整数,
  "standard_suggestion": "规范优化建议",
  "summary": "整体核查总结"
}"""


def build_review_prompt(training_requirement: str, student_content: str) -> str:
    """填充智能核查提示词。"""
    return (
        REVIEW_PROMPT_TEMPLATE
        .replace("{{training_requirement}}", training_requirement or "")
        .replace("{{student_content}}", student_content or "")
    )
