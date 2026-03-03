"""改进追问机制服务"""
from typing import Dict, Any, List, Optional
import json
from app.services.llm_service import get_llm


class AnswerAnalyzer:
    """回答分析器"""

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
        conversation_history: List[Dict[str, Any]],
        followup_count: int,
        max_followup: int
    ) -> Dict[str, Any]:
        """分析用户回答，判断是否需要追问"""
        llm = await self._get_llm()

        # 格式化对话历史
        history_text = self._format_conversation_history(conversation_history[-10:])

        prompt = f"""你是一个专业的面试评估专家。请分析候选人的回答，判断是否需要追问。

**当前问题：**
{question.get('question', '')}
问题类型：{question.get('type', '')}
问题难度：{question.get('difficulty', '')}
问题目的：{question.get('purpose', '')}

**候选人回答：**
{answer}

**对话历史（最近10轮）：**
{history_text}

**追问次数：**
{followup_count}/{max_followup}

**分析要求：**
请从以下维度评估回答，并返回 JSON 格式：

1. **深度评分 (depth)**: 0-1，回答的深度和细节程度
2. **完整性评分 (completeness)**: 0-1，回答的完整程度
3. **准确性评分 (accuracy)**: 0-1，技术内容的准确性
4. **清晰度评分 (clarity)**: 0-1，表达的清晰程度
5. **关键点 (key_points)**: 列出回答中的关键点
6. **缺失点 (missing_points)**: 列出应该提及但未提及的点
7. **模糊表述 (vague_expressions)**: 列出模糊或不清楚的表达
8. **技术细节 (technical_details)**: 识别技术细节是否充分
9. **案例或实例 (examples)**: 是否有具体的案例或实例
10. **追问必要性 (followup_necessity)**: 0-1，追问的必要性评分
11. **追问方向 (followup_directions)**: 建议的追问方向列表
12. **追问类型 (followup_types)**: 建议的追问类型（deep/detail/case/comparison/extension/clarification）

返回格式：
{{
  "depth": 0.7,
  "completeness": 0.6,
  "accuracy": 0.9,
  "clarity": 0.8,
  "key_points": ["关键点1", "关键点2"],
  "missing_points": ["缺失点1", "缺失点2"],
  "vague_expressions": ["模糊表述1", "模糊表述2"],
  "technical_details": "sufficient/insufficient",
  "examples": "present/absent",
  "followup_necessity": 0.8,
  "followup_directions": ["方向1", "方向2"],
  "followup_types": ["detail", "case"]
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
            print(f"[回答分析] 分析失败: {e}")
            return {
                "depth": 0.5,
                "completeness": 0.5,
                "accuracy": 0.5,
                "clarity": 0.5,
                "key_points": [],
                "missing_points": [],
                "vague_expressions": [],
                "technical_details": "insufficient",
                "examples": "absent",
                "followup_necessity": 0.3,
                "followup_directions": [],
                "followup_types": []
            }

    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """格式化对话历史"""
        formatted = []
        for i, turn in enumerate(history, 1):
            formatted.append(f"第{i}轮：")
            formatted.append(f"Q: {turn.get('question', '')}")
            formatted.append(f"A: {turn.get('answer', '')}")
        return "\n".join(formatted)


class FollowupDecisionEngine:
    """追问决策引擎"""

    def __init__(self):
        self.max_followup = 3
        self.time_threshold = 300  # 剩余时间少于5分钟时减少追问

    async def decide_followup(
        self,
        analysis: Dict[str, Any],
        followup_count: int,
        max_followup: int,
        time_remaining: int = 0,
        persona_type: str = "gentle"
    ) -> Dict[str, Any]:
        """决定是否追问"""
        decision = {
            "should_followup": False,
            "followup_type": "",
            "followup_strategy": "",
            "necessity_score": 0.0,
            "reason": "",
            "suggested_topics": []
        }

        # 1. 检查追问次数限制
        if followup_count >= max_followup:
            decision["reason"] = "已达到最大追问次数"
            return decision

        # 2. 检查时间限制
        if time_remaining < self.time_threshold:
            if followup_count >= 1:
                decision["reason"] = "剩余时间不足"
                return decision

        # 3. 计算追问必要性评分
        decision["necessity_score"] = self._calculate_necessity_score(analysis)

        # 4. 根据人设调整阈值
        threshold = self._get_threshold(persona_type)

        # 5. 决定是否追问
        if decision["necessity_score"] >= threshold:
            decision["should_followup"] = True
            decision["reason"] = f"回答需要进一步澄清（必要性评分：{decision['necessity_score']:.2f}）"
        else:
            decision["reason"] = f"回答充分（必要性评分：{decision['necessity_score']:.2f}）"

        # 6. 决定追问类型
        if decision["should_followup"]:
            decision["followup_type"] = self._select_followup_type(analysis, persona_type)
            decision["followup_strategy"] = self._select_followup_strategy(persona_type)
            decision["suggested_topics"] = analysis.get("followup_directions", [])

        return decision

    def _calculate_necessity_score(self, analysis: Dict[str, Any]) -> float:
        """计算追问必要性评分"""
        score = 0.0

        # 深度不足（权重：0.3）
        depth = analysis.get("depth", 0.0)
        if depth < 0.5:
            score += 0.3 * (1 - depth)

        # 完整性不足（权重：0.25）
        completeness = analysis.get("completeness", 0.0)
        if completeness < 0.6:
            score += 0.25 * (1 - completeness)

        # 有缺失点（权重：0.2）
        missing_points = analysis.get("missing_points", [])
        if missing_points:
            score += 0.2 * min(len(missing_points) / 3, 1.0)

        # 有模糊表述（权重：0.15）
        vague_expressions = analysis.get("vague_expressions", [])
        if vague_expressions:
            score += 0.15 * min(len(vague_expressions) / 2, 1.0)

        # 缺少案例（权重：0.1）
        examples = analysis.get("examples", "")
        if examples == "absent":
            score += 0.1

        return min(score, 1.0)

    def _get_threshold(self, persona_type: str) -> float:
        """根据人设获取追问阈值"""
        if persona_type == "strict":
            return 0.4  # 严厉型更容易追问
        elif persona_type == "gentle":
            return 0.7  # 温和型更少追问
        elif persona_type == "technical":
            return 0.5  # 技术型中等
        else:
            return 0.6  # 默认阈值

    def _select_followup_type(self, analysis: Dict[str, Any], persona_type: str) -> str:
        """选择追问类型"""
        suggested_types = analysis.get("followup_types", [])

        # 根据人设偏好调整
        if persona_type == "technical":
            # 技术型偏好深度和细节追问
            if "deep" in suggested_types:
                return "deep"
            elif "detail" in suggested_types:
                return "detail"
        elif persona_type == "gentle":
            # 温和型偏好案例和澄清追问
            if "case" in suggested_types:
                return "case"
            elif "clarification" in suggested_types:
                return "clarification"

        # 默认选择第一个建议的类型
        return suggested_types[0] if suggested_types else "detail"

    def _select_followup_strategy(self, persona_type: str) -> str:
        """选择追问策略"""
        if persona_type == "strict":
            return "challenging"
        elif persona_type == "gentle":
            return "guiding"
        else:
            return "balanced"


class ImprovedFollowupService:
    """改进追问服务"""

    def __init__(self):
        self.analyzer = AnswerAnalyzer()
        self.decision_engine = FollowupDecisionEngine()

    async def process_answer(
        self,
        user_answer: str,
        current_question: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        followup_count: int,
        max_followup: int = 3,
        time_remaining: int = 0,
        resume_data: Dict[str, Any] = None,
        job_description: str = "",
        persona_type: str = "gentle"
    ) -> Dict[str, Any]:
        """处理用户回答并决定是否追问"""

        # 1. 分析回答
        analysis = await self.analyzer.analyze_answer(
            user_answer,
            current_question,
            conversation_history,
            followup_count,
            max_followup
        )

        # 2. 决定是否追问
        decision = await self.decision_engine.decide_followup(
            analysis,
            followup_count,
            max_followup,
            time_remaining,
            persona_type
        )

        # 3. 如果需要追问
        if decision["should_followup"]:
            # 生成追问
            followup = await self._generate_followup(
                decision,
                current_question,
                user_answer,
                conversation_history,
                resume_data,
                job_description
            )

            return {
                "type": "followup",
                "data": {
                    "question": followup["question"],
                    "reason": followup["reason"],
                    "followup_type": decision["followup_type"],
                    "followup_count": followup_count + 1,
                    "expected_points": followup.get("expected_points", [])
                },
                "analysis": analysis,
                "decision": decision
            }

        # 4. 不需要追问
        return {
            "type": "next_question",
            "reason": decision["reason"],
            "analysis": analysis,
            "decision": decision
        }

    async def _generate_followup(
        self,
        decision: Dict[str, Any],
        current_question: Dict[str, Any],
        user_answer: str,
        conversation_history: List[Dict[str, Any]],
        resume_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """生成追问"""
        llm = await self.analyzer._get_llm()

        # 格式化对话历史
        history_text = self.analyzer._format_conversation_history(conversation_history[-10:])

        prompt = f"""你是一个专业的面试官。请根据以下信息生成一个追问。

**当前问题：**
{current_question.get('question', '')}
问题类型：{current_question.get('type', '')}
问题难度：{current_question.get('difficulty', '')}

**候选人回答：**
{user_answer}

**对话历史（最近10轮）：**
{history_text}

**追问决策：**
是否追问：{decision.get('should_followup', False)}
追问类型：{decision.get('followup_type', '')}
追问策略：{decision.get('followup_strategy', '')}
追问方向：{', '.join(decision.get('suggested_topics', []))}
决策原因：{decision.get('reason', '')}

**候选人简历：**
{json.dumps(resume_data or {}, ensure_ascii=False, indent=2)}

**职位描述：**
{job_description}

**追问类型说明：**
- deep（深度追问）：深入探讨某个概念或原理
- detail（细节追问）：询问实现细节和具体方案
- case（案例追问）：要求举例说明或场景应用
- comparison（对比追问）：比较不同方案的优劣
- extension（扩展追问）：扩展到相关领域或技术
- clarification（澄清追问）：澄清模糊或不清楚的表达

**生成要求：**
1. 追问必须针对回答中的不足或模糊之处
2. 追问必须符合指定的追问类型
3. 追问必须具体明确，不能太宽泛
4. 追问必须与简历和 JD 相关
5. 追问必须避免重复之前的问题
6. 追问必须有助于深入理解候选人的能力

返回格式：
{{
  "question": "追问内容",
  "reason": "追问原因",
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

            followup = json.loads(response)
            return followup
        except Exception as e:
            print(f"[追问生成] 生成失败: {e}")
            # 返回默认追问
            return {
                "question": "能详细说明一下吗？",
                "reason": "需要更多细节",
                "expected_points": ["详细说明", "具体实例"]
            }