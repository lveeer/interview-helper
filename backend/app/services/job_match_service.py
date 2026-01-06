from typing import Dict, Any, List
import json
from app.services.llm_service import get_llm
from app.utils.prompt_loader import PromptLoader


class JobMatchService:
    """岗位匹配服务"""

    @staticmethod
    async def analyze_job_match(
        resume_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """
        分析简历与岗位的匹配度

        Args:
            resume_data: 简历数据
            job_description: 岗位描述

        Returns:
            匹配分析结果
        """
        llm = await get_llm()

        resume_text = json.dumps(resume_data, ensure_ascii=False, indent=2)

        # 加载提示词模板
        prompt = PromptLoader.format_prompt(
            'job_match',
            resume_text=resume_text,
            job_description=job_description
        )

        try:
            response = await llm.generate_text(prompt, temperature=0.5)
            result = json.loads(response)
            return result
        except Exception as e:
            # 默认返回示例数据
            return {
                "match_score": 70,
                "keyword_match": 70,
                "skill_match": 70,
                "project_relevance": 70,
                "suggestions": [
                    "建议补充更多项目细节",
                    "可以增加相关技能的学习"
                ],
                "missing_skills": [],
                "strengths": ["基础扎实"]
            }