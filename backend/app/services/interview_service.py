from typing import Dict, Any, List
import json
from app.services.llm_service import get_llm


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

        prompt = f"""
        我需要你作为一个专业的面试官，根据以下求职者的简历和目标岗位描述，生成 {num_questions} 道针对性的面试问题。

        求职者简历：
        {resume_text}

        目标岗位描述：
        {job_description}

        请按照以下要求生成问题：
        1. 问题应该涵盖自我介绍、项目经验、技术能力、问题解决等多个维度
        2. 问题难度应该适中，既有基础问题也有挑战性问题
        3. 每个问题应该包含：问题内容、问题类型、难度级别
        4. 问题应该能够深入挖掘求职者的真实能力

        请以 JSON 数组格式返回，每个问题包含以下字段：
        - id: 问题序号（从1开始）
        - question: 问题内容
        - category: 问题类型（如：自我介绍、项目经验、技术能力、问题解决、团队协作等）
        - difficulty: 难度级别（简单、中等、困难）

        示例格式：
        [
            {{
                "id": 1,
                "question": "请简单介绍一下你自己",
                "category": "自我介绍",
                "difficulty": "简单"
            }}
        ]
        """

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

        prompt = f"""
        你是一个专业的面试官。请根据以下信息决定是否需要追问，或者进入下一个问题。

        当前问题：{current_question}
        求职者回答：{user_answer}

        最近的对话历史：
        {context}

        求职者简历（部分信息）：
        {json.dumps(resume_data.get('experience', [])[:2], ensure_ascii=False)}

        请分析求职者的回答：
        1. 如果回答不够深入或存在模糊之处，请生成一个追问，帮助求职者展开说明
        2. 如果回答已经比较完整，请生成下一个相关问题
        3. 追问应该具有针对性，能够挖掘更多细节
        4. 下一个问题应该与之前的问题有一定的关联性

        请以 JSON 格式返回，包含以下字段：
        - type: "followup"（追问）或 "next"（下一个问题）
        - question: 问题内容
        - reason: 为什么需要这个问题（可选）

        示例：
        {{
            "type": "followup",
            "question": "你提到了使用了 Redis 缓存，能具体说说缓存策略是如何设计的吗？",
            "reason": "求职者提到了 Redis 但没有详细说明实现细节"
        }}
        """

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

        expected = "\n".join([f"- {point}" for point in (expected_points or [])])

        prompt = f"""
        请评估求职者的面试回答质量。

        问题：{question}
        求职者回答：{answer}

        期望的回答要点：
        {expected or "无特定要求"}

        请从以下维度进行评估：
        1. 逻辑性：回答是否有条理，逻辑清晰
        2. 完整性：是否全面回答了问题
        3. 深度：是否有深入的分析和见解
        4. 表达能力：表达是否清晰流畅

        请以 JSON 格式返回，包含以下字段：
        - score: 总分（0-100）
        - feedback: 总体评价（1-2句话）
        - strengths: 优点列表（2-3条）
        - improvements: 需要改进的地方（2-3条）

        示例：
        {{
            "score": 75,
            "feedback": "整体回答较为完整，但可以更深入地分析技术细节",
            "strengths": ["逻辑清晰", "举例恰当"],
            "improvements": ["可以补充更多技术细节", "可以增加数据支撑"]
        }}
        """

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