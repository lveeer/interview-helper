from typing import Dict, Any, List
import json
from app.services.llm_service import get_llm


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

        prompt = f"""
        请分析求职者简历与目标岗位的匹配度。

        求职者简历：
        {resume_text}

        目标岗位描述：
        {job_description}

        请从以下三个维度进行分析：
        1. 关键词匹配：简历中的关键词与 JD 中的关键词匹配程度
        2. 技能等级：求职者掌握的技能与岗位要求的匹配程度
        3. 项目相关性：求职者的项目经验与岗位的相关性

        请以 JSON 格式返回，包含以下字段：
        - match_score: 总体匹配分数（0-100）
        - keyword_match: 关键词匹配分数（0-100）
        - skill_match: 技能匹配分数（0-100）
        - project_relevance: 项目相关性分数（0-100）
        - suggestions: 优化建议列表（3-5条）
        - missing_skills: 缺失的技能列表
        - strengths: 优势列表（3-5条）

        示例：
        {{
            "match_score": 75,
            "keyword_match": 80,
            "skill_match": 70,
            "project_relevance": 75,
            "suggestions": [
                "建议在简历中突出与岗位相关的项目经验",
                "可以补充更多关于技术栈的详细描述"
            ],
            "missing_skills": ["Docker", "Kubernetes"],
            "strengths": ["项目经验丰富", "技术栈覆盖面广"]
        }}
        """

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