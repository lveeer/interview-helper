"""动态问题生成服务"""
from typing import Dict, Any, List, Optional
import json
from app.services.llm_service import get_llm


class ConversationAnalyzer:
    """对话上下文分析器"""

    def __init__(self):
        self.llm = None

    async def _get_llm(self):
        """获取 LLM 实例"""
        if self.llm is None:
            self.llm = await get_llm()
        return self.llm

    async def analyze_answer(
        self,
        answer: str,
        question: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析用户回答"""
        llm = await self._get_llm()

        # 格式化对话历史
        history_text = self._format_conversation_history(conversation_history[-5:])

        prompt = f"""你是一个专业的面试评估专家。请分析候选人的回答。

**问题：**
{question.get('question', '')}
问题类型：{question.get('type', '')}
问题难度：{question.get('difficulty', '')}
问题目的：{question.get('purpose', '')}

**候选人回答：**
{answer}

**对话历史（最近5轮）：**
{history_text}

**分析要求：**
请从以下维度评估回答，并返回 JSON 格式：

1. **质量评分 (quality)**: 0-1，综合评价回答质量
2. **深度评分 (depth)**: 0-1，回答的深度和细节程度
3. **相关性 (relevance)**: 0-1，回答与问题的相关性
4. **完整性 (completeness)**: 0-1，回答的完整程度
5. **清晰度 (clarity)**: 0-1，表达的清晰程度
6. **技术准确性 (technical_accuracy)**: 0-1，技术内容的准确性
7. **关键点 (key_points)**: 列出回答中的关键点
8. **缺失点 (missing_points)**: 列出应该提及但未提及的点
9. **优势 (strengths)**: 列出回答的优势
10. **劣势 (weaknesses)**: 列出回答的不足

返回格式：
{{
  "quality": 0.8,
  "depth": 0.7,
  "relevance": 0.9,
  "completeness": 0.6,
  "clarity": 0.8,
  "technical_accuracy": 0.9,
  "key_points": ["关键点1", "关键点2"],
  "missing_points": ["缺失点1", "缺失点2"],
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["劣势1", "劣势2"]
}}"""

        try:
            response = await llm.generate_text(prompt, temperature=0.3)

            # 去除 markdown 标记
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            analysis = json.loads(response)
            return analysis
        except Exception as e:
            print(f"[对话分析] 分析失败: {e}")
            return {
                "quality": 0.5,
                "depth": 0.5,
                "relevance": 0.5,
                "completeness": 0.5,
                "clarity": 0.5,
                "technical_accuracy": 0.5,
                "key_points": [],
                "missing_points": [],
                "strengths": [],
                "weaknesses": []
            }

    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """格式化对话历史"""
        formatted = []
        for i, turn in enumerate(history, 1):
            formatted.append(f"第{i}轮：")
            formatted.append(f"Q: {turn.get('question', '')}")
            formatted.append(f"A: {turn.get('answer', '')}")
        return "\n".join(formatted)


class StrategyEngine:
    """问题生成策略引擎"""

    def __init__(self):
        pass

    async def decide_strategy(
        self,
        analysis: Dict[str, Any],
        question: Dict[str, Any],
        topic_coverage: Dict[str, int]
    ) -> Dict[str, Any]:
        """决定下一个问题的生成策略"""
        strategy = {
            "strategy_type": "difficulty_adaptation",
            "target_difficulty": "中等",
            "target_domain": question.get("category", ""),
            "reason": "根据回答质量调整难度"
        }

        # 根据回答质量调整难度
        quality = analysis.get("quality", 0.5)
        current_difficulty = question.get("difficulty", "中等")

        if quality >= 0.8:
            # 提高难度
            if current_difficulty == "简单":
                strategy["target_difficulty"] = "中等"
            elif current_difficulty == "中等":
                strategy["target_difficulty"] = "困难"
            else:
                strategy["target_difficulty"] = "困难"
            strategy["reason"] = "回答优秀，提高难度"
        elif quality >= 0.5:
            # 保持难度
            strategy["target_difficulty"] = current_difficulty
            strategy["reason"] = "回答一般，保持难度"
        else:
            # 降低难度
            if current_difficulty == "困难":
                strategy["target_difficulty"] = "中等"
            elif current_difficulty == "中等":
                strategy["target_difficulty"] = "简单"
            else:
                strategy["target_difficulty"] = "简单"
            strategy["reason"] = "回答困难，降低难度"

        # 检查话题覆盖度，决定是否切换领域
        current_domain = question.get("category", "")
        domain_count = topic_coverage.get(current_domain, 0)

        if domain_count >= 3:
            strategy["strategy_type"] = "domain_switch"
            strategy["reason"] = "该领域已深入多次，切换到其他领域"

        return strategy


class DynamicQuestionGenerator:
    """动态问题生成器"""

    def __init__(self):
        self.analyzer = ConversationAnalyzer()
        self.strategy_engine = StrategyEngine()

    async def generate_next_question(
        self,
        user_answer: str,
        current_question: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        resume_data: Dict[str, Any],
        job_description: str,
        topic_coverage: Dict[str, int],
        knowledge_context: str = ""
    ) -> Dict[str, Any]:
        """生成下一个问题"""

        # 1. 分析用户回答
        analysis = await self.analyzer.analyze_answer(
            user_answer,
            current_question,
            conversation_history
        )

        # 2. 决定生成策略
        strategy = await self.strategy_engine.decide_strategy(
            analysis,
            current_question,
            topic_coverage
        )

        # 3. 生成问题
        question = await self._generate_question(
            strategy,
            current_question,
            conversation_history,
            resume_data,
            job_description,
            knowledge_context
        )

        # 4. 更新话题覆盖度
        category = question.get("category", "")
        if category in topic_coverage:
            topic_coverage[category] += 1
        else:
            topic_coverage[category] = 1

        return {
            "question": question,
            "analysis": analysis,
            "strategy": strategy
        }

    async def _generate_question(
        self,
        strategy: Dict[str, Any],
        current_question: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        resume_data: Dict[str, Any],
        job_description: str,
        knowledge_context: str
    ) -> Dict[str, Any]:
        """生成具体问题"""
        llm = await self.analyzer._get_llm()

        # 格式化对话历史
        history_text = self.analyzer._format_conversation_history(conversation_history[-10:])

        prompt = f"""你是一个专业的面试官。请根据以下信息生成下一个面试问题。

**职位描述 (JD)：**
{job_description}

**候选人简历：**
{json.dumps(resume_data, ensure_ascii=False, indent=2)}

**对话历史（最近10轮）：**
{history_text}

**生成策略：**
策略类型：{strategy.get('strategy_type', '')}
目标难度：{strategy.get('target_difficulty', '')}
目标领域：{strategy.get('target_domain', '')}
策略原因：{strategy.get('reason', '')}

**知识库上下文（如果有）：**
{knowledge_context}

**生成要求：**
1. 问题必须针对候选人的具体经历和技能
2. 问题必须引用简历中的具体内容
3. 问题难度必须符合目标难度
4. 问题类型必须多样化（技术、行为、场景等）
5. 问题必须与 JD 高度相关
6. 问题必须避免重复之前的问题
7. 问题必须具有针对性和深度

返回格式：
{{
  "question": "问题内容",
  "category": "问题分类（如：后端开发、数据库、系统设计等）",
  "difficulty": "难度（简单/中等/困难）",
  "type": "问题类型（技术面试/行为面试/场景面试等）",
  "purpose": "问题目的（考察什么能力）",
  "expected_points": ["预期答案要点1", "预期答案要点2"]
}}"""

        try:
            response = await llm.generate_text(prompt, temperature=0.7)

            # 去除 markdown 标记
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            question = json.loads(response)
            return question
        except Exception as e:
            print(f"[动态问题生成] 生成失败: {e}")
            # 返回默认问题
            return {
                "question": "请介绍一下你在项目中遇到的最大挑战以及如何解决的。",
                "category": "问题解决",
                "difficulty": "中等",
                "type": "行为面试",
                "purpose": "考察问题解决能力",
                "expected_points": ["问题描述", "解决方案", "学习收获"]
            }