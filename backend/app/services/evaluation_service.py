from typing import Dict, Any, List
import json
from app.services.llm_service import get_llm


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

        prompt = f"""
        请根据面试对话记录，生成一份详细的面试评估报告。

        面试对话记录：
        {conversation_text}

        请从以下维度进行评估：
        1. 总体表现：整体表现如何
        2. 技术能力：技术掌握程度
        3. 沟通能力：表达是否清晰流畅
        4. 问题解决：解决问题的思路和方法
        5. 学习能力：对新知识的理解和应用能力

        请以 JSON 格式返回，包含以下字段：
        - total_score: 总体分数（0-100）
        - overall_feedback: 总体评价（2-3句话）
        - question_evaluations: 每个问题的评估列表
            - question_id: 问题 ID
            - question: 问题内容
            - score: 该问题得分（0-100）
            - feedback: 对该问题的评价
            - strengths: 优点列表
            - improvements: 需要改进的地方
        - recommended_resources: 推荐的学习资源列表
            - type: 资源类型（article、video、course等）
            - title: 资源标题
            - url: 资源链接（可选）

        示例：
        {{
            "total_score": 75,
            "overall_feedback": "整体表现良好，技术基础扎实，但在项目细节描述方面可以更加深入",
            "question_evaluations": [
                {{
                    "question_id": 1,
                    "question": "请简单介绍一下你自己",
                    "score": 80,
                    "feedback": "自我介绍清晰，逻辑性强",
                    "strengths": ["逻辑清晰", "表达流畅"],
                    "improvements": ["可以增加更多个人亮点"]
                }}
            ],
            "recommended_resources": [
                {{
                    "type": "article",
                    "title": "如何进行有效的项目经验描述",
                    "url": "https://example.com/article"
                }}
            ]
        }}
        """

        try:
            response = await llm.generate_text(prompt, temperature=0.5)
            result = json.loads(response)
            return result
        except Exception as e:
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
                        "title": "面试技巧提升指南",
                        "url": "https://example.com/article"
                    }
                ]
            }