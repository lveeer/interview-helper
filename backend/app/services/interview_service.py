from typing import Dict, Any, List
import json
import asyncio
from sqlalchemy.orm import Session
from app.services.llm_service import get_llm
from app.utils.prompt_loader import PromptLoader
from app.models.interview import Interview, InterviewStatus


class InterviewService:
    """面试服务"""

    @staticmethod
    async def retrieve_knowledge_context(
        resume_data: Dict[str, Any],
        job_description: str,
        user_id: int,
        knowledge_doc_ids: List[int] = None,
        db: Session = None
    ) -> str:
        """
        从知识库中检索与JD和简历相关的知识点

        Args:
            resume_data: 简历数据
            job_description: 岗位描述
            user_id: 用户ID
            knowledge_doc_ids: 指定的知识库文档ID列表（可选）
            db: 数据库会话

        Returns:
            格式化的知识库上下文文本
        """
        try:
            from app.services.rag_service import RAGService

            # 提取简历中的技术栈和关键词
            tech_stack = []
            if resume_data.get('skills'):
                skills_text = json.dumps(resume_data['skills'], ensure_ascii=False)
                tech_stack.extend([skill.get('name', '') for skill in resume_data['skills'] if skill.get('name')])

            if resume_data.get('experience'):
                for exp in resume_data['experience']:
                    tech_stack.append(exp.get('title', ''))
                    tech_stack.append(exp.get('company', ''))

            # 构建查询，结合JD和技术栈
            tech_keywords = ', '.join([kw for kw in tech_stack if kw][:5])  # 最多取5个关键词
            query = f"{job_description} {tech_keywords}"

            print(f"[知识库检索] 查询: {query}")

            # 从知识库中检索相关内容
            results = await RAGService.search_knowledge(
                query=query,
                user_id=user_id,
                top_k=5,
                use_query_expansion=True,
                use_hybrid_search=True,
                use_reranking=True,
                db=db
            )

            # 如果指定了文档ID列表，过滤结果
            if knowledge_doc_ids:
                results = [r for r in results if r.get('document_id') in knowledge_doc_ids]

            if not results:
                print(f"[知识库检索] 未找到相关内容")
                return ""

            # 格式化知识库上下文
            context_parts = []
            for i, result in enumerate(results):
                content = result.get('content', '')
                source = result.get('source', '未知来源')
                score = result.get('score', 0)

                context_parts.append(
                    f"【知识点 {i+1}】来源: {source} (相关度: {score:.2f})\n{content}"
                )

            knowledge_context = "\n\n".join(context_parts)
            print(f"[知识库检索] 检索到 {len(results)} 个相关知识点")

            return knowledge_context

        except Exception as e:
            print(f"[知识库检索] 检索失败: {e}")
            import traceback
            traceback.print_exc()
            return ""

    @staticmethod
    async def generate_interview_questions(
        resume_data: Dict[str, Any],
        job_description: str,
        num_questions: int = 10,
        knowledge_context: str = ""
    ) -> List[Dict[str, Any]]:
        """
        基于简历和 JD 生成面试问题

        Args:
            resume_data: 简历数据
            job_description: 岗位描述
            num_questions: 问题数量
            knowledge_context: 知识库上下文（可选）

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
            job_description=job_description,
            knowledge_context=knowledge_context
        )

        try:
            # 使用较低的温度参数，使生成的问题更加确定和准确
            response = await llm.generate_text(prompt, temperature=0.6)

            # 去除可能存在的 markdown 代码块标记
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # 解析 JSON 响应
            questions = json.loads(response)
            # 验证返回的问题格式
            if not isinstance(questions, list) or len(questions) == 0:
                raise ValueError("LLM 返回的问题格式不正确")
            # 验证问题数量
            if len(questions) != num_questions:
                print(f"警告: 生成的问题数量({len(questions)})与要求({num_questions})不一致")
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
                    "difficulty": "简单",
                    "type": "行为面试",
                    "purpose": "了解候选人的基本背景和职业经历"
                },
                {
                    "id": 2,
                    "question": "请详细介绍一下你最引以为豪的项目",
                    "category": "项目经验",
                    "difficulty": "中等",
                    "type": "行为面试",
                    "purpose": "深入挖掘候选人的项目经验"
                },
                {
                    "id": 3,
                    "question": "你在项目中遇到的最大挑战是什么？如何解决的？",
                    "category": "问题解决",
                    "difficulty": "中等",
                    "type": "行为面试",
                    "purpose": "考察候选人的问题解决能力"
                }
            ]
        except Exception as e:
            # 其他错误，返回默认问题并记录日志
            print(f"警告: 生成面试问题失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return [
                {
                    "id": 1,
                    "question": "请简单介绍一下你自己",
                    "category": "自我介绍",
                    "difficulty": "简单",
                    "type": "行为面试",
                    "purpose": "了解候选人的基本背景和职业经历"
                },
                {
                    "id": 2,
                    "question": "请详细介绍一下你最引以为豪的项目",
                    "category": "项目经验",
                    "difficulty": "中等",
                    "type": "行为面试",
                    "purpose": "深入挖掘候选人的项目经验"
                },
                {
                    "id": 3,
                    "question": "你在项目中遇到的最大挑战是什么？如何解决的？",
                    "category": "问题解决",
                    "difficulty": "中等",
                    "type": "行为面试",
                    "purpose": "考察候选人的问题解决能力"
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

    @staticmethod
    async def generate_interview_questions_async(
        db: Session,
        interview_id: int,
        resume_data: Dict[str, Any],
        job_description: str,
        num_questions: int = 10,
        user_id: int = None,
        knowledge_doc_ids: List[int] = None,
        task_id: str = None
    ):
        """
        异步生成面试问题并在完成后更新数据库

        Args:
            db: 数据库会话
            interview_id: 面试ID
            resume_data: 简历数据
            job_description: 岗位描述
            num_questions: 问题数量
            user_id: 用户ID（用于知识库检索）
            knowledge_doc_ids: 指定的知识库文档ID列表（可选）
            task_id: 任务ID（用于状态推送）
        """
        from app.services.task_notification_service import task_notification_service
        
        try:
            # 通知任务开始
            if task_id:
                await task_notification_service.notify_started(
                    task_id,
                    message="正在生成面试问题..."
                )
            
            # 从知识库检索相关上下文（可选）
            knowledge_context = ""
            if user_id:
                print(f"[异步生成] 开始从知识库检索相关内容，用户ID: {user_id}")
                
                # 通知进度
                if task_id:
                    await task_notification_service.notify_progress(
                        task_id,
                        progress=20,
                        message="正在从知识库检索相关内容...",
                        step="知识库检索"
                    )
                
                knowledge_context = await InterviewService.retrieve_knowledge_context(
                    resume_data=resume_data,
                    job_description=job_description,
                    user_id=user_id,
                    knowledge_doc_ids=knowledge_doc_ids,
                    db=db
                )
                if knowledge_context:
                    print(f"[异步生成] 知识库检索成功，上下文长度: {len(knowledge_context)}")

            # 生成面试问题
            # 通知进度
            if task_id:
                await task_notification_service.notify_progress(
                    task_id,
                    progress=50,
                    message="正在调用 LLM 生成面试问题...",
                    step="问题生成"
                )
            
            questions = await InterviewService.generate_interview_questions(
                resume_data,
                job_description,
                num_questions,
                knowledge_context=knowledge_context
            )

            # 更新数据库
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if interview:
                interview.questions = json.dumps(questions)
                interview.status = InterviewStatus.pending
                interview.generation_error = None
                db.commit()
                print(f"[异步生成] 面试 {interview_id} 问题生成成功，共 {len(questions)} 个问题")
                
                # 通知任务完成
                if task_id:
                    await task_notification_service.notify_completed(
                        task_id,
                        result={
                            "interview_id": interview_id,
                            "questions_count": len(questions),
                            "status": interview.status
                        },
                        message=f"面试问题生成成功，共 {len(questions)} 个问题",
                        redirect_url=f"/interview/{interview_id}",
                        redirect_params={"interview_id": interview_id},
                        db=db
                    )
            else:
                print(f"[异步生成] 面试 {interview_id} 不存在")
                if task_id:
                    await task_notification_service.notify_failed(
                        task_id,
                        error=f"面试 {interview_id} 不存在"
                    )

        except Exception as e:
            # 生成失败，记录错误信息
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if interview:
                interview.status = InterviewStatus.pending
                interview.generation_error = json.dumps({
                    "error": str(e),
                    "type": type(e).__name__
                }, ensure_ascii=False)
                db.commit()
                print(f"[异步生成] 面试 {interview_id} 问题生成失败: {e}")
            else:
                print(f"[异步生成] 面试 {interview_id} 不存在")
            
            # 通知任务失败
            if task_id:
                await task_notification_service.notify_failed(
                    task_id,
                    error=str(e),
                    error_type=type(e).__name__
                )