"""AI 智能核查/评价模块。

- review(): 已实现 —— 基于 LangChain 调用大模型，对成果做结构化智能核查；
- parse_file() / check_code() / evaluate(): 预留封装入口，待后续实现。
"""
import json
import re
import time
from dataclasses import dataclass
from typing import Any

from app.ai.llm import get_llm
from app.ai.prompts import build_review_prompt
from app.core.config import settings
from app.schemas.ai_review import ReviewResult
from app.utils.logger import logger


@dataclass
class ReviewOutcome:
    """一次智能核查的结果与调用元数据（供上层落库到 llm_call_log）。"""

    result: ReviewResult
    model_name: str
    prompt_text: str
    response_text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0


def _extract_json(text: str) -> dict[str, Any]:
    """从模型输出中提取 JSON 对象，容忍 ```json 代码块包裹与前后噪声。"""
    if not isinstance(text, str):
        text = str(text)
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s).strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", s, re.S)  # 兜底：截取首个 {...} 块
        if match:
            return json.loads(match.group(0))
        raise


class AIEvaluator:
    """实训成果 AI 评价器。"""

    def __init__(self) -> None:
        self.llm = get_llm()

    def review(self, training_requirement: str, student_content: str) -> ReviewOutcome:
        """对成果做结构化智能核查（功能/逻辑/步骤/规范）。

        Args:
            training_requirement: 实训要求。
            student_content: 学生提交的代码/文档内容。

        Returns:
            ReviewOutcome：含结构化结果与调用元数据。

        Raises:
            RuntimeError: 大模型未配置。
            ValueError / json.JSONDecodeError: 模型输出无法解析为约定 JSON。
        """
        if self.llm is None:
            raise RuntimeError("大模型未配置，无法执行智能核查（请设置 LLM_API_KEY）")

        prompt = build_review_prompt(training_requirement, student_content)
        start = time.perf_counter()
        resp = self.llm.invoke(prompt)
        duration_ms = int((time.perf_counter() - start) * 1000)

        text = getattr(resp, "content", str(resp))
        text = text if isinstance(text, str) else str(text)
        result = ReviewResult.model_validate(_extract_json(text))

        usage = getattr(resp, "usage_metadata", None) or {}
        logger.info(f"AI 智能核查完成 tokens={usage.get('total_tokens', 0)} {duration_ms}ms")

        return ReviewOutcome(
            result=result,
            model_name=settings.llm_model,
            prompt_text=prompt,
            response_text=text,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            duration_ms=duration_ms,
        )

    def parse_file(self, file_path: str, **kwargs: Any) -> dict[str, Any]:
        """文件解析：抽取成果文件中的可评价文本。

        TODO: 使用 langchain_community 文档加载器与切分器实现。
        """
        raise NotImplementedError("文件解析功能待实现")

    def check_code(self, code: str, language: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """代码核查：单独对代码做规范/正确性/安全性核查。

        TODO: 构建代码审查提示词链 + 结构化输出。
        """
        raise NotImplementedError("代码核查功能待实现")

    def evaluate(
        self,
        content: str,
        indicators: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """指标加权智能评价：依据评价指标体系对成果打分。

        TODO: 基于指标动态生成提示词，链式调用 LLM 输出结构化评分。
        """
        raise NotImplementedError("指标加权评价功能待实现")


ai_evaluator = AIEvaluator()
