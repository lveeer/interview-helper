"""面试官人设适配器服务"""
from typing import Dict, Any, List
import random
from app.services.llm_service import get_llm
from app.models.persona import InterviewerPersona, PersonaConversationContext
import json


class PersonaAdapter:
    """人设适配器"""

    def __init__(self):
        self.llm = None

    async def _get_llm(self):
        """获取 LLM 实例"""
        if self.llm is None:
            self.llm = await get_llm()
        return self.llm

    async def adapt_question(
        self,
        question: str,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """根据人设调整问题语气和风格"""
        llm = await self._get_llm()

        prompt = self._build_adaptation_prompt(question, persona, context)

        adapted_question = await llm.generate_text(
            prompt=prompt,
            temperature=persona.config.get("temperature", 0.7)
        )

        return adapted_question.strip()

    async def adapt_feedback(
        self,
        feedback: str,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """根据人设调整反馈语气和风格"""
        llm = await self._get_llm()

        prompt = self._build_feedback_adaptation_prompt(feedback, persona, context)

        adapted_feedback = await llm.generate_text(
            prompt=prompt,
            temperature=persona.config.get("temperature", 0.7)
        )

        return adapted_feedback.strip()

    async def generate_transition(
        self,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """生成过渡语句"""
        if not persona.transition_phrases:
            return "好的，我们继续。"

        # 从预设过渡语句中随机选择，或生成新的
        if random.random() < 0.5:  # 50% 概率使用预设
            return random.choice(persona.transition_phrases)
        else:
            llm = await self._get_llm()
            prompt = self._build_transition_prompt(persona, context)
            transition = await llm.generate_text(
                prompt=prompt,
                temperature=0.8
            )
            return transition.strip()

    async def generate_encouragement(
        self,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """生成鼓励语句"""
        if persona.encouragement_phrases:
            if random.random() < 0.7:  # 70% 概率使用预设
                return random.choice(persona.encouragement_phrases)

        llm = await self._get_llm()
        prompt = self._build_encouragement_prompt(persona, context)
        encouragement = await llm.generate_text(
            prompt=prompt,
            temperature=0.8
        )
        return encouragement.strip()

    def _build_adaptation_prompt(
        self,
        question: str,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """构建问题调整提示词"""
        prompt = f"""你是一个{persona.type}面试官。请根据以下信息调整问题的语气和风格。

**原始问题：**
{question}

**面试官人设：**
人设类型：{persona.type}
语气风格：{persona.tone}
提问风格：{persona.questioning_style}
个性特征：{', '.join(persona.personality_traits or [])}

**对话上下文：**
当前问题数：{context.get('current_question_index', 0)}
用户表现：{context.get('user_performance', '一般')}

**调整要求：**
1. 保持问题的核心内容不变
2. 调整语气和风格以符合人设
3. 使用人设特有的表达方式
4. 保持问题清晰易懂

请返回调整后的问题，不要添加任何其他内容。"""
        return prompt

    def _build_feedback_adaptation_prompt(
        self,
        feedback: str,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """构建反馈调整提示词"""
        prompt = f"""你是一个{persona.type}面试官。请根据以下信息调整反馈的语气和风格。

**原始反馈：**
{feedback}

**面试官人设：**
人设类型：{persona.type}
语气风格：{persona.tone}
鼓励程度：{persona.encouragement_level}
个性特征：{', '.join(persona.personality_traits or [])}

**对话上下文：**
用户表现：{context.get('user_performance', '一般')}
回答质量：{context.get('answer_quality', 0.5)}

**调整要求：**
1. 保持反馈的核心内容不变
2. 调整语气和风格以符合人设
3. 根据鼓励程度调整反馈的积极性
4. 使用人设特有的表达方式

请返回调整后的反馈，不要添加任何其他内容。"""
        return prompt

    def _build_transition_prompt(
        self,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """构建过渡语句生成提示词"""
        prompt = f"""你是一个{persona.type}面试官。请生成一个自然的过渡语句。

**面试官人设：**
人设类型：{persona.type}
语气风格：{persona.tone}
对话风格：{persona.conversation_style}

**对话上下文：**
上一个问题：{context.get('last_question', '')}
上一个回答：{context.get('last_answer', '')}
回答质量：{context.get('answer_quality', 0.5)}

**过渡要求：**
1. 自然流畅，不生硬
2. 符合人设的语气和风格
3. 适当总结上一个回答
4. 引导到下一个问题
5. 不超过50字

请返回过渡语句，不要添加任何其他内容。"""
        return prompt

    def _build_encouragement_prompt(
        self,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> str:
        """构建鼓励语句生成提示词"""
        prompt = f"""你是一个{persona.type}面试官。请生成一句鼓励性的话。

**面试官人设：**
人设类型：{persona.type}
鼓励程度：{persona.encouragement_level}
语气风格：{persona.tone}

**对话上下文：**
用户表现：{context.get('user_performance', '一般')}

**鼓励要求：**
1. 积极正面
2. 符合人设的语气
3. 简洁有力
4. 不超过30字

请返回鼓励语句，不要添加任何其他内容。"""
        return prompt


class PersonaDynamicAdjuster:
    """人设动态调整器"""

    def __init__(self):
        self.adapter = PersonaAdapter()

    async def adjust_persona(
        self,
        persona: InterviewerPersona,
        context: PersonaConversationContext
    ) -> InterviewerPersona:
        """根据对话情况动态调整人设"""
        user_satisfaction = context.user_satisfaction / 100.0  # 转换为 0-1

        # 根据满意度调整人设参数
        if user_satisfaction < 0.3:
            # 用户不满意，降低严格程度，增加鼓励
            await self._make_more_gentle(persona)
        elif user_satisfaction > 0.8:
            # 用户很满意，可以适当提高要求
            await self._make_more_strict(persona)

        return persona

    async def _make_more_gentle(self, persona: InterviewerPersona):
        """让人设更温和"""
        config = persona.config or {}
        config["strictness"] = max(0.0, config.get("strictness", 0.5) - 0.1)
        config["patience"] = min(1.0, config.get("patience", 0.5) + 0.1)
        persona.encouragement_level = "high"
        persona.config = config

    async def _make_more_strict(self, persona: InterviewerPersona):
        """让人设更严厉"""
        config = persona.config or {}
        config["strictness"] = min(1.0, config.get("strictness", 0.5) + 0.1)
        config["patience"] = max(0.0, config.get("patience", 0.5) - 0.1)
        persona.encouragement_level = "low"
        persona.config = config


class PersonaEnhancedQuestionGenerator:
    """人设增强的问题生成器"""

    def __init__(self):
        self.adapter = PersonaAdapter()

    async def generate_question_with_persona(
        self,
        base_question: str,
        persona: InterviewerPersona,
        context: Dict[str, Any],
        resume_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """生成带人设的问题"""
        # 1. 生成过渡语句
        transition = await self.adapter.generate_transition(persona, context)

        # 2. 根据人设调整问题
        adapted_question = await self.adapter.adapt_question(
            base_question,
            persona,
            context
        )

        # 3. 生成问题背景（根据人设风格）
        question_context = await self._generate_question_context(
            base_question,
            persona,
            context,
            resume_data,
            job_description
        )

        return {
            "transition": transition,
            "question": adapted_question,
            "context": question_context,
            "persona_id": persona.id,
            "persona_name": persona.name
        }

    async def _generate_question_context(
        self,
        question: str,
        persona: InterviewerPersona,
        context: Dict[str, Any],
        resume_data: Dict[str, Any],
        job_description: str
    ) -> str:
        """生成问题背景"""
        llm = await self.adapter._get_llm()

        prompt = f"""你是一个{persona.type}面试官。请为以下问题生成背景说明。

**问题：**
{question}

**面试官人设：**
人设类型：{persona.type}
关注重点：{', '.join(persona.focus_areas or [])}

**候选人简历：**
{json.dumps(resume_data, ensure_ascii=False, indent=2)}

**职位描述：**
{job_description}

**背景要求：**
1. 说明为什么问这个问题
2. 结合候选人的具体经历
3. 符合人设的关注重点
4. 简洁明了，不超过100字

请返回问题背景，不要添加任何其他内容。"""

        question_context = await llm.generate_text(
            prompt=prompt,
            temperature=0.7
        )

        return question_context.strip()


class PersonaEnhancedFeedbackGenerator:
    """人设增强的反馈生成器"""

    def __init__(self):
        self.adapter = PersonaAdapter()

    async def generate_feedback_with_persona(
        self,
        answer: str,
        question: str,
        persona: InterviewerPersona,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成带人设的反馈"""
        # 1. 生成基础反馈
        base_feedback = await self._generate_base_feedback(
            answer,
            question,
            context
        )

        # 2. 根据人设调整反馈
        adapted_feedback = await self.adapter.adapt_feedback(
            base_feedback,
            persona,
            context
        )

        # 3. 生成鼓励语句（如果需要）
        encouragement = None
        if persona.encouragement_level in ["high", "medium"]:
            encouragement = await self.adapter.generate_encouragement(persona, context)

        return {
            "feedback": adapted_feedback,
            "encouragement": encouragement,
            "persona_id": persona.id
        }

    async def _generate_base_feedback(
        self,
        answer: str,
        question: str,
        context: Dict[str, Any]
    ) -> str:
        """生成基础反馈"""
        llm = await self.adapter._get_llm()

        prompt = f"""请对以下回答给出反馈。

**问题：**
{question}

**回答：**
{answer}

**反馈要求：**
1. 指出回答的优点
2. 指出可以改进的地方
3. 给出具体建议
4. 语气客观中立
5. 不超过150字

请返回反馈内容，不要添加任何其他内容。"""

        feedback = await llm.generate_text(
            prompt=prompt,
            temperature=0.5
        )

        return feedback.strip()