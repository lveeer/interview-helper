"""面试官人设服务"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.persona import InterviewerPersona, PersonaConversationContext
from app.models.interview import Interview
import json


# 预设人设配置
PRESET_PERSONAS = {
    "strict": {
        "name": "严厉型面试官",
        "type": "strict",
        "description": "要求严格，注重技术深度和细节",
        "tone": "严肃",
        "focus_areas": ["技术深度", "实现细节", "边界情况", "性能优化"],
        "questioning_style": "challenging",
        "followup_frequency": "high",
        "encouragement_level": "low",
        "conversation_style": "formal",
        "personality_traits": ["严格", "注重细节", "喜欢挑战", "不容易满足"],
        "question_templates": [
            "请详细解释一下{topic}。",
            "你确定吗？{topic}有什么问题？",
            "为什么选择{solution}？有什么权衡？",
            "这个方案如何处理{edge_case}？"
        ],
        "transition_phrases": [
            "好的，我们继续下一个问题。",
            "明白了，那我们深入探讨一下。",
            "很好，下一个问题。"
        ],
        "feedback_phrases": [
            "你的回答还有待改进。",
            "这个问题需要更深入的思考。",
            "你的方案不够完善。"
        ],
        "encouragement_phrases": [
            "继续努力。",
            "再想想。"
        ],
        "is_default": False,
        "config": {
            "temperature": 0.5,
            "max_followup": 5,
            "question_difficulty": "hard",
            "response_length": "long",
            "strictness": 0.9,
            "patience": 0.3,
            "technical_depth": 0.9,
            "communication_focus": 0.4
        }
    },
    "gentle": {
        "name": "温和型面试官",
        "type": "gentle",
        "description": "语气友好，鼓励性强，注重学习态度",
        "tone": "友好",
        "focus_areas": ["学习能力", "沟通表达", "问题解决思路", "团队协作"],
        "questioning_style": "guiding",
        "followup_frequency": "medium",
        "encouragement_level": "high",
        "conversation_style": "casual",
        "personality_traits": ["友好", "鼓励性强", "善于引导", "开放包容"],
        "question_templates": [
            "能分享一下你对{topic}的理解吗？",
            "这个想法很有趣，能展开说说吗？",
            "你是怎么想到{solution}的？",
            "在这个过程中有什么收获吗？"
        ],
        "transition_phrases": [
            "很好，那我们继续。",
            "谢谢你的分享，下一个问题。",
            "很有意思，我们继续聊聊。"
        ],
        "feedback_phrases": [
            "你的回答很有见地。",
            "这个想法不错。",
            "你的思路很清晰。"
        ],
        "encouragement_phrases": [
            "做得很好！",
            "继续保持！",
            "你做得很好！"
        ],
        "is_default": True,
        "config": {
            "temperature": 0.8,
            "max_followup": 3,
            "question_difficulty": "adaptive",
            "response_length": "medium",
            "strictness": 0.3,
            "patience": 0.9,
            "technical_depth": 0.6,
            "communication_focus": 0.8
        }
    },
    "technical": {
        "name": "技术型面试官",
        "type": "technical",
        "description": "注重技术选型和架构设计",
        "tone": "专业",
        "focus_areas": ["技术选型", "架构设计", "代码质量", "工程实践"],
        "questioning_style": "technical",
        "followup_frequency": "high",
        "encouragement_level": "medium",
        "conversation_style": "professional",
        "personality_traits": ["专业", "技术导向", "喜欢讨论技术", "对新技术敏感"],
        "question_templates": [
            "你使用了什么技术栈来处理{topic}？",
            "{architecture}有什么优势？",
            "如何保证系统的{quality}？",
            "有没有考虑过其他技术方案？"
        ],
        "transition_phrases": [
            "好的，我们继续讨论技术问题。",
            "明白了，下一个技术问题。",
            "好的，我们继续。"
        ],
        "feedback_phrases": [
            "你的技术方案很专业。",
            "这个技术选型很合理。",
            "你的架构设计很清晰。"
        ],
        "encouragement_phrases": [
            "技术能力不错。",
            "继续深入。"
        ],
        "is_default": False,
        "config": {
            "temperature": 0.6,
            "max_followup": 4,
            "question_difficulty": "hard",
            "response_length": "long",
            "strictness": 0.7,
            "patience": 0.5,
            "technical_depth": 0.9,
            "communication_focus": 0.5
        }
    },
    "hr": {
        "name": "HR型面试官",
        "type": "hr",
        "description": "注重软技能和价值观匹配",
        "tone": "亲切",
        "focus_areas": ["软技能", "价值观", "团队协作", "职业规划"],
        "questioning_style": "conversational",
        "followup_frequency": "low",
        "encouragement_level": "high",
        "conversation_style": "warm",
        "personality_traits": ["亲切", "注重软技能", "善于挖掘", "重视团队"],
        "question_templates": [
            "请介绍一下你自己。",
            "你为什么选择我们公司？",
            "你有什么职业规划？",
            "你如何处理{situation}？"
        ],
        "transition_phrases": [
            "很好，我们继续聊聊。",
            "谢谢你的分享，下一个问题。",
            "很有意思，我们继续。"
        ],
        "feedback_phrases": [
            "你的回答很真诚。",
            "你的经历很丰富。",
            "你的价值观很符合我们。"
        ],
        "encouragement_phrases": [
            "你做得很好！",
            "继续保持！",
            "你很优秀！"
        ],
        "is_default": False,
        "config": {
            "temperature": 0.8,
            "max_followup": 2,
            "question_difficulty": "easy",
            "response_length": "medium",
            "strictness": 0.2,
            "patience": 0.9,
            "technical_depth": 0.3,
            "communication_focus": 0.9
        }
    },
    "senior_architect": {
        "name": "资深架构师型面试官",
        "type": "senior_architect",
        "description": "注重系统设计和架构思维",
        "tone": "沉稳",
        "focus_areas": ["系统设计", "架构思维", "设计模式", "性能优化"],
        "questioning_style": "architectural",
        "followup_frequency": "high",
        "encouragement_level": "medium",
        "conversation_style": "professional",
        "personality_traits": ["沉稳", "注重架构", "设计思维", "系统理解"],
        "question_templates": [
            "你如何设计{system}？",
            "这个设计有什么权衡？",
            "如何应对{scenario}？",
            "系统的瓶颈在哪里？"
        ],
        "transition_phrases": [
            "好的，我们继续讨论系统设计。",
            "明白了，下一个架构问题。",
            "好的，我们继续。"
        ],
        "feedback_phrases": [
            "你的架构设计很合理。",
            "这个方案很有见地。",
            "你的系统理解很深入。"
        ],
        "encouragement_phrases": [
            "架构能力不错。",
            "继续深入。"
        ],
        "is_default": False,
        "config": {
            "temperature": 0.5,
            "max_followup": 5,
            "question_difficulty": "hard",
            "response_length": "long",
            "strictness": 0.8,
            "patience": 0.4,
            "technical_depth": 1.0,
            "communication_focus": 0.6
        }
    }
}


class PersonaManager:
    """人设管理器"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_persona(self, persona_id: int) -> Optional[InterviewerPersona]:
        """获取人设"""
        result = await self.db.execute(
            select(InterviewerPersona).where(InterviewerPersona.id == persona_id)
        )
        return result.scalar_one_or_none()

    async def get_default_persona(self) -> Optional[InterviewerPersona]:
        """获取默认人设"""
        result = await self.db.execute(
            select(InterviewerPersona).where(InterviewerPersona.is_default == True)
        )
        return result.scalar_one_or_none()

    async def list_personas(self, user_id: int) -> List[InterviewerPersona]:
        """列出所有人设（包括系统预设和用户自定义）"""
        result = await self.db.execute(
            select(InterviewerPersona).where(
                or_(
                    InterviewerPersona.is_custom == False,
                    InterviewerPersona.user_id == user_id
                )
            )
        )
        return result.scalars().all()

    async def create_custom_persona(
        self,
        user_id: int,
        persona_data: Dict[str, Any]
    ) -> InterviewerPersona:
        """创建自定义人设"""
        persona = InterviewerPersona(
            name=persona_data.get("name", "自定义人设"),
            type="custom",
            description=persona_data.get("description", ""),
            tone=persona_data.get("tone", "professional"),
            focus_areas=persona_data.get("focus_areas", []),
            questioning_style=persona_data.get("questioning_style", "balanced"),
            followup_frequency=persona_data.get("followup_frequency", "medium"),
            encouragement_level=persona_data.get("encouragement_level", "medium"),
            conversation_style=persona_data.get("conversation_style", "professional"),
            personality_traits=persona_data.get("personality_traits", []),
            question_templates=persona_data.get("question_templates", []),
            transition_phrases=persona_data.get("transition_phrases", []),
            feedback_phrases=persona_data.get("feedback_phrases", []),
            encouragement_phrases=persona_data.get("encouragement_phrases", []),
            is_custom=True,
            user_id=user_id,
            config=persona_data.get("config", {})
        )

        self.db.add(persona)
        await self.db.commit()
        await self.db.refresh(persona)

        return persona

    async def update_persona(
        self,
        persona_id: int,
        user_id: int,
        persona_data: Dict[str, Any]
    ) -> Optional[InterviewerPersona]:
        """更新自定义人设"""
        persona = await self.get_persona(persona_id)

        if not persona or not persona.is_custom or persona.user_id != user_id:
            return None

        for key, value in persona_data.items():
            if hasattr(persona, key):
                setattr(persona, key, value)

        await self.db.commit()
        await self.db.refresh(persona)

        return persona

    async def delete_persona(self, persona_id: int, user_id: int) -> bool:
        """删除自定义人设"""
        persona = await self.get_persona(persona_id)

        if not persona or not persona.is_custom or persona.user_id != user_id:
            return False

        await self.db.delete(persona)
        await self.db.commit()
        return True


class PersonaContextManager:
    """人设对话上下文管理器"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_context(
        self,
        persona_id: int,
        interview_id: int,
        user_id: int
    ) -> PersonaConversationContext:
        """获取或创建对话上下文"""
        result = await self.db.execute(
            select(PersonaConversationContext).where(
                PersonaConversationContext.interview_id == interview_id
            )
        )
        context = result.scalar_one_or_none()

        if not context:
            context = PersonaConversationContext(
                persona_id=persona_id,
                interview_id=interview_id,
                user_id=user_id,
                conversation_history=[],
                current_mood="neutral",
                user_satisfaction=50,
                adjustment_history=[]
            )
            self.db.add(context)
            await self.db.commit()
            await self.db.refresh(context)

        return context

    async def update_context(
        self,
        context_id: int,
        conversation_turn: Dict[str, Any],
        user_satisfaction: Optional[int] = None
    ):
        """更新对话上下文"""
        result = await self.db.execute(
            select(PersonaConversationContext).where(
                PersonaConversationContext.id == context_id
            )
        )
        context = result.scalar_one_or_none()

        if context:
            context.conversation_history.append(conversation_turn)
            if user_satisfaction is not None:
                context.user_satisfaction = user_satisfaction
            await self.db.commit()

    async def get_context(self, interview_id: int) -> Optional[PersonaConversationContext]:
        """获取对话上下文"""
        result = await self.db.execute(
            select(PersonaConversationContext).where(
                PersonaConversationContext.interview_id == interview_id
            )
        )
        return result.scalar_one_or_none()


async def initialize_personas(db: AsyncSession):
    """初始化预设人设"""
    print("[人设初始化] 开始初始化预设人设...")

    for persona_type, persona_config in PRESET_PERSONAS.items():
        # 检查是否已存在
        result = await db.execute(
            select(InterviewerPersona).where(InterviewerPersona.type == persona_type)
        )
        existing = result.scalar_one_or_none()

        if not existing:
            persona = InterviewerPersona(**persona_config)
            db.add(persona)
            print(f"[人设初始化] 创建预设人设: {persona_config['name']}")
        else:
            print(f"[人设初始化] 预设人设已存在: {persona_config['name']}")

    await db.commit()
    print("[人设初始化] 预设人设初始化完成")