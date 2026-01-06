from typing import Dict, Any, List
import json
from app.services.llm_service import get_llm
from app.utils.prompt_loader import PromptLoader


class InterviewService:
    """面试服务"""

    @staticmethod
    async def generate_interview_questions(
        resume_data: Dict[str, Any],
        job_description: str,
        num_questions: int = 10
    ) -> List[Dict[str, Any]]:
        """
        基于简历和 JD 生成面试问题

        Args:
            resume_data: 简历数据
            job_description: 岗位描述
            num_questions: 问题数量

        Returns:
            面试问题列表
        """
        llm = await get_llm()

        # 构建提示词
        resume_text = json.dumps(resume_data, ensure_ascii=False, indent=2)

        # 加载提示词模板
        prompt = PromptLoader.format_prompt(
            'interview_questions',
            num_questions=num_questions,
            resume_text=resume_text,
            job_description=job_description
        )

        try:
            response = await llm.generate_text(prompt, temperature=0.8)
            # 解析 JSON 响应
            questions = json.loads(response)
            # 验证返回的问题格式
            if not isinstance(questions, list) or len(questions) == 0:
                raise ValueError("LLM 返回的问题格式不正确")
            return questions
        except json.JSONDecodeError as e:
            # JSON 解析失败，返回默认问题
            print(f"警告: LLM 返回的 JSON 解析失败: {e}")
            print(f"LLM 原始响应: {response[:500]}")
            return [
                {
                    "id": 1,
                    "question": "请简单介绍一下你自己",
                    "category": "自我介绍",
                    "difficulty": "简单"
                },
                {
                    "id": 2,
                    "question": "请详细介绍一下你最引以为豪的项目",
                    "category": "项目经验",
                    "difficulty": "中等"
                },
                {
                    "id": 3,
                    "question": "你在项目中遇到的最大挑战是什么？如何解决的？",
                    "category": "问题解决",
                    "difficulty": "中等"
                }
            ]
        except Exception as e:
            # 其他错误，返回默认问题并记录日志
            print(f"警告: 生成面试问题失败: {e}")
            return [
                {
                    "id": 1,
                    "question": "请简单介绍一下你自己",
                    "category": "自我介绍",
                    "difficulty": "简单"
                },
                {
                    "id": 2,
                    "question": "请详细介绍一下你最引以为豪的项目",
                    "category": "项目经验",
                    "difficulty": "中等"
                },
                {
                    "id": 3,
                    "question": "你在项目中遇到的最大挑战是什么？如何解决的？",
                    "category": "问题解决",
                    "difficulty": "中等"
                }
            ]

    @staticmethod
    async def generate_followup_question(
        current_question: str,
        user_answer: str,
        conversation_history: List[Dict[str, str]],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        根据用户回答生成追问

        Args:
            current_question: 当前问题
            user_answer: 用户回答
            conversation_history: 对话历史
            resume_data: 简历数据

        Returns:
            追问或下一个问题
        """
        llm = await get_llm()

        # 构建对话上下文
        context = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-5:]  # 只取最近5轮对话
        ])

        resume_info = json.dumps(resume_data.get('experience', [])[:2], ensure_ascii=False)

        # 加载提示词模板
        prompt = PromptLoader.format_prompt(
            'followup_question',
            current_question=current_question,
            user_answer=user_answer,
            context=context,
            resume_info=resume_info
        )

        try:
            response = await llm.generate_text(prompt, temperature=0.7)
            result = json.loads(response)
            # 验证返回的格式
            if not isinstance(result, dict) or "type" not in result:
                raise ValueError("LLM 返回的格式不正确")
            return result
        except json.JSONDecodeError as e:
            print(f"警告: 追问生成 JSON 解析失败: {e}")
            print(f"LLM 原始响应: {response[:500]}")
            return {
                "type": "next",
                "question": "感谢你的回答。让我们继续下一个问题。",
                "reason": "继续面试流程"
            }
        except Exception as e:
            print(f"警告: 生成追问失败: {e}")
            return {
                "type": "next",
                "question": "感谢你的回答。让我们继续下一个问题。",
                "reason": "继续面试流程"
            }

    @staticmethod
    async def evaluate_answer(
        question: str,
        answer: str,
        expected_points: List[str] = None
    ) -> Dict[str, Any]:
        """
        评估求职者的回答

        Args:
            question: 问题
            answer: 回答
            expected_points: 期望的回答要点

        Returns:
            评估结果
        """
        llm = await get_llm()

        expected = "\n".join([f"- {point}" for point in (expected_points or [])]) or "无特定要求"

        # 加载提示词模板
        prompt = PromptLoader.format_prompt(
            'answer_evaluation',
            question=question,
            answer=answer,
            expected_points=expected
        )

        try:
            response = await llm.generate_text(prompt, temperature=0.5)
            result = json.loads(response)
            # 验证返回的格式
            if not isinstance(result, dict) or "score" not in result:
                raise ValueError("LLM 返回的评估格式不正确")
            return result
        except json.JSONDecodeError as e:
            print(f"警告: 答案评估 JSON 解析失败: {e}")
            print(f"LLM 原始响应: {response[:500]}")
            return {
                "score": 70,
                "feedback": "回答基本符合要求",
                "strengths": ["回答了问题"],
                "improvements": ["可以更详细", "可以增加实例"]
            }
        except Exception as e:
            print(f"警告: 评估答案失败: {e}")
            return {
                "score": 70,
                "feedback": "回答基本符合要求",
                "strengths": ["回答了问题"],
                "improvements": ["可以更详细", "可以增加实例"]
            }