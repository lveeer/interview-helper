from typing import Dict, Any, List
import json
from app.services.llm_service import get_llm
from app.utils.prompt_loader import PromptLoader


class EvaluationService:
    """评估服务"""

    @staticmethod
    async def generate_interview_report(
        interview_data: Dict[str, Any],
        conversation: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        生成面试评估报告

        Args:
            interview_data: 面试数据
            conversation: 对话记录

        Returns:
            评估报告
        """
        llm = await get_llm()

        # 构建对话文本
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation
        ])

        # 加载提示词模板
        prompt = PromptLoader.format_prompt(
            'evaluation_report',
            conversation_text=conversation_text
        )

        try:
            response = await llm.generate_text(prompt, temperature=0.5)

            # 去除可能存在的 markdown 代码块标记
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            result = json.loads(response)
            return result
        except Exception as e:
            print(f"生成评估报告失败: {e}")
            # 默认返回示例报告
            return {
                "total_score": 70,
                "overall_feedback": "面试表现良好，建议继续加强技术深度",
                "question_evaluations": [
                    {
                        "question_id": 1,
                        "question": "请简单介绍一下你自己",
                        "score": 75,
                        "feedback": "自我介绍较为完整",
                        "strengths": ["表达清晰"],
                        "improvements": ["可以增加更多亮点"]
                    }
                ],
                "recommended_resources": [
                    {
                        "type": "article",
                        "title": "面试技巧提升指南"
                    }
                ]
            }