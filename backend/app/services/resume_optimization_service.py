import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.resume import Resume, ResumeOptimization, ResumeOptimizationHistory
from app.schemas.resume import (
    ResumeAnalysisResult,
    OptimizationSuggestion,
    PersonalAnalysis,
    EducationAnalysis,
    ExperienceAnalysis,
    SkillsAnalysis
)

logger = logging.getLogger(__name__)


class ResumeOptimizationService:
    """简历优化服务"""

    @staticmethod
    async def analyze_resume(
        db: Session,
        resume_id: int,
        llm_service,
        force_refresh: bool = False,
        jd: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析简历，生成多维度评分和分析报告

        Args:
            db: 数据库会话
            resume_id: 简历ID
            llm_service: LLM 服务实例
            force_refresh: 是否强制重新分析
            jd: 职位描述（可选），用于针对性分析

        Returns:
            分析结果字典
        """
        logger.info(f"开始分析简历 {resume_id}, force_refresh={force_refresh}, jd={bool(jd)}")
        if jd:
            logger.info(f"JD 内容: {jd[:100]}...")

        # 获取简历
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("简历不存在")

        # 如果已有缓存且不强制刷新，直接返回
        if resume.analysis_result and not force_refresh:
            logger.info(f"使用缓存的分析结果")
            try:
                return json.loads(resume.analysis_result)
            except json.JSONDecodeError:
                pass

        logger.info(f"准备使用 LLM 分析简历")
        # 准备简历数据
        resume_data = {
            "personal_info": json.loads(resume.personal_info) if resume.personal_info else {},
            "education": json.loads(resume.education) if resume.education else [],
            "experience": json.loads(resume.experience) if resume.experience else [],
            "skills": json.loads(resume.skills) if resume.skills else [],
            "projects": json.loads(resume.projects) if resume.projects else [],
            "highlights": json.loads(resume.highlights) if resume.highlights else []
        }

        logger.info(f"简历数据准备完成，技能数量: {len(resume_data.get('skills', []))}")

        # 使用 LLM 分析简历
        analysis_prompt = ResumeOptimizationService._build_analysis_prompt(resume_data, jd)
        logger.info(f"分析提示词已构建，长度: {len(analysis_prompt)}")

        try:
            analysis_response = await llm_service.generate_text(
                analysis_prompt,
                temperature=0.3,
                max_tokens=65535  # 使用最大 token 数以支持最详细的分析
            )

            logger.info(f"LLM 原始响应: {analysis_response[:500]}...")

            # 去除可能存在的 markdown 代码块标记
            analysis_response = analysis_response.strip()
            if analysis_response.startswith("```json"):
                analysis_response = analysis_response[7:]
            elif analysis_response.startswith("```"):
                analysis_response = analysis_response[3:]
            if analysis_response.endswith("```"):
                analysis_response = analysis_response[:-3]
            analysis_response = analysis_response.strip()

            # 解析 LLM 响应
            try:
                analysis_result = json.loads(analysis_response)
                logger.info(f"LLM JSON 解析成功，综合评分: {analysis_result.get('overall_score', 0)}")
            except json.JSONDecodeError as e:
                logger.error(f"LLM JSON 解析失败: {e}")
                logger.error(f"LLM 原始响应: {analysis_response}")
                # 如果解析失败，使用基础分析
                analysis_result = ResumeOptimizationService._basic_analysis(resume_data)

            # 缓存分析结果
            resume.analysis_result = json.dumps(analysis_result, ensure_ascii=False)
            db.commit()

            logger.info(f"简历 {resume_id} 分析完成，综合评分: {analysis_result.get('overall_score', 0)}")
            return analysis_result

        except Exception as e:
            logger.error(f"简历分析失败: {e}", exc_info=True)
            # 使用基础分析作为后备
            analysis_result = ResumeOptimizationService._basic_analysis(resume_data)
            resume.analysis_result = json.dumps(analysis_result, ensure_ascii=False)
            db.commit()
            return analysis_result

    @staticmethod
    def _build_analysis_prompt(resume_data: Dict[str, Any], jd: Optional[str] = None) -> str:
        """构建简历分析的提示词"""
        if jd:
            # 有 JD 时的针对性分析提示词
            return f"""
你是一位专业的简历分析师。请仔细分析以下简历与目标职位描述（JD）的匹配度，并以JSON格式返回详细的分析结果。

【目标职位描述 (JD)】
{jd}

【简历信息】
姓名: {resume_data['personal_info'].get('name', '未知')}
邮箱: {resume_data['personal_info'].get('email', '未知')}
电话: {resume_data['personal_info'].get('phone', '未知')}

教育背景:
{json.dumps(resume_data['education'], ensure_ascii=False, indent=2)}

工作经历:
{json.dumps(resume_data['experience'], ensure_ascii=False, indent=2)}

项目经历:
{json.dumps(resume_data['projects'], ensure_ascii=False, indent=2)}

技能列表:
{', '.join(resume_data['skills'])}

【分析要求】
1. **必须仔细对比 JD 和简历**，逐项分析匹配情况
2. **在 skills_analysis 中必须包含以下字段**：
   - jd_required_skills: JD明确要求的技能列表
   - resume_matched_skills: 简历中匹配JD要求的技能
   - resume_missing_skills: JD要求但简历缺失的技能
   - match_details: 匹配度详细说明（如"5/8技能匹配"）
3. **在 experience_analysis 中必须包含**：
   - jd_experience_requirements: JD对经验的要求
   - resume_experience_match: 简历经验是否满足JD要求
4. **在 strengths 中优先列出与JD高度匹配的技能和经验**
5. **在 weaknesses 中必须明确列出JD要求但简历缺失的技能、经验**
6. **match_score 必须基于实际的匹配情况计算**（技能匹配数/总技能数 × 60% + 经验匹配度 × 40%）

请按以下JSON格式返回分析结果：
{{
    "overall_score": 0-100,
    "content_score": 0-100,
    "match_score": 0-100,
    "clarity_score": 0-100,
    "strengths": ["优势1（必须包含与JD匹配的具体技能和经验，50-100字详细说明）", "优势2"],
    "weaknesses": ["不足1（必须包含JD要求但简历缺失的技能，50-100字详细说明）", "不足2"],
    "personal_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（50-100字）",
        "included": ["已包含项"],
        "missing": ["缺失项"]
    }},
    "education_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（50-100字）",
        "suggestions": "改进建议（50-100字）"
    }},
    "experience_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（必须说明是否满足JD经验要求，50-100字）",
        "jd_experience_requirements": "JD对经验的具体要求（50-100字）",
        "resume_experience_match": "简历经验匹配情况说明（50-100字）",
        "issues": "存在问题（50-100字）",
        "suggestions": "针对JD的改进建议（80-150字）"
    }},
    "skills_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（50-100字）",
        "jd_required_skills": ["JD要求技能1", "JD要求技能2"],
        "resume_matched_skills": ["简历匹配技能1", "简历匹配技能2"],
        "resume_missing_skills": ["缺失技能1", "缺失技能2"],
        "match_details": "匹配度详细说明（如：5/8技能匹配，缺失MyBatis、分布式经验等，50-100字）",
        "hard_skills": ["硬技能1", "硬技能2"],
        "soft_skills": ["软技能1", "软技能2"],
        "suggestions": "针对JD的技能改进建议（80-150字）"
    }}
}}

评分标准：
- overall_score: 综合评分 = (content_score + match_score + clarity_score) / 3
- content_score: 内容完整性（个人信息、教育、工作经历、技能）
- match_score: **与JD匹配度** = (匹配技能数/JD要求技能数 × 60) + (经验匹配度 × 40)
- clarity_score: 表达清晰度

【重要提醒】
- 必须在 skills_analysis 中明确列出 JD 要求的技能和简历的匹配情况
- 必须在 experience_analysis 中说明简历经验是否满足 JD 要求
- 必须在 weaknesses 中明确指出 JD 要求但简历缺失的内容
- 所有建议必须针对 JD，提供具体的改进方向

请确保返回的是合法的JSON格式，不要包含任何其他文字说明。
"""
        else:
            # 无 JD 时的通用分析提示词
            return f"""
请分析以下简历，从多个维度评估简历质量，并以JSON格式返回分析结果。
请从通用角度评估简历质量。

简历信息：
姓名: {resume_data['personal_info'].get('name', '未知')}
邮箱: {resume_data['personal_info'].get('email', '未知')}
电话: {resume_data['personal_info'].get('phone', '未知')}

教育背景:
{json.dumps(resume_data['education'], ensure_ascii=False, indent=2)}

工作经历:
{json.dumps(resume_data['experience'], ensure_ascii=False, indent=2)}

项目经历:
{json.dumps(resume_data['projects'], ensure_ascii=False, indent=2)}

技能:
{', '.join(resume_data['skills'])}

请按以下JSON格式返回分析结果：
{{
    "overall_score": 0-100,
    "content_score": 0-100,
    "match_score": 0-100,
    "clarity_score": 0-100,
    "strengths": ["优势1（50-100字详细说明）", "优势2"],
    "weaknesses": ["不足1（50-100字详细说明）", "不足2"],
    "personal_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（50-100字）",
        "included": ["已包含项"],
        "missing": ["缺失项"]
    }},
    "education_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（50-100字）",
        "suggestions": "改进建议（50-100字）"
    }},
    "experience_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（50-100字）",
        "issues": "存在问题（50-100字）",
        "suggestions": "改进建议（80-150字）"
    }},
    "skills_analysis": {{
        "status": "good/warning/error",
        "message": "分析说明（50-100字）",
        "hard_skills": ["硬技能1", "硬技能2"],
        "soft_skills": ["软技能1", "软技能2"],
        "suggestions": "改进建议（80-150字）"
    }}
}}

评分标准：
- overall_score: 综合评分，基于其他三个分数的加权平均
- content_score: 内容完整性，包括个人信息、教育、工作经历、技能等是否完整
- match_score: 专业匹配度，技能和经历是否符合职业发展路径
- clarity_score: 表达清晰度，描述是否清晰、有条理

请确保返回的是合法的JSON格式，不要包含任何其他文字说明。
"""

    @staticmethod
    def _basic_analysis(resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """基础简历分析（不依赖LLM）"""
        # 计算内容完整性
        content_score = 0
        personal_info = resume_data.get('personal_info', {})
        if personal_info.get('name'):
            content_score += 20
        if personal_info.get('email'):
            content_score += 20
        if personal_info.get('phone'):
            content_score += 20
        if resume_data.get('education'):
            content_score += 20
        if resume_data.get('experience'):
            content_score += 20

        # 计算专业匹配度（简化版）
        skills = resume_data.get('skills', [])
        match_score = min(100, len(skills) * 10)

        # 计算表达清晰度（简化版）
        experience = resume_data.get('experience', [])
        clarity_score = 50
        for exp in experience:
            if exp.get('description') and len(exp['description']) > 50:
                clarity_score += 10
        clarity_score = min(100, clarity_score)

        # 综合评分
        overall_score = int((content_score + match_score + clarity_score) / 3)

        # 优势
        strengths = []
        if content_score >= 80:
            strengths.append("简历信息完整，结构清晰")
        if len(skills) >= 5:
            strengths.append(f"技能丰富，掌握{len(skills)}项技能")
        if len(experience) >= 2:
            strengths.append("工作经历丰富")

        # 不足
        weaknesses = []
        if content_score < 60:
            weaknesses.append("简历信息不完整，建议补充")
        if match_score < 50:
            weaknesses.append("技能描述不足，建议添加更多技能")
        if clarity_score < 60:
            weaknesses.append("工作经历描述不够详细，建议使用STAR法则")

        # 个人信息分析
        personal_analysis = {
            "status": "good" if content_score >= 60 else "warning",
            "message": "个人信息完整" if content_score >= 60 else "个人信息不完整",
            "included": [],
            "missing": []
        }
        if personal_info.get('name'):
            personal_analysis['included'].append('姓名')
        else:
            personal_analysis['missing'].append('姓名')
        if personal_info.get('email'):
            personal_analysis['included'].append('邮箱')
        else:
            personal_analysis['missing'].append('邮箱')
        if personal_info.get('phone'):
            personal_analysis['included'].append('电话')
        else:
            personal_analysis['missing'].append('电话')

        # 教育背景分析
        education = resume_data.get('education', [])
        education_analysis = {
            "status": "good" if education else "warning",
            "message": "教育背景清晰" if education else "缺少教育背景信息",
            "suggestions": None
        }
        if not education:
            education_analysis['suggestions'] = "建议添加教育背景信息"

        # 工作经历分析
        experience_analysis = {
            "status": "good" if experience else "warning",
            "message": "工作经历描述详细" if experience else "缺少工作经历信息",
            "issues": None,
            "suggestions": None
        }
        if experience:
            # 检查是否有量化成果
            has_quantification = False
            for exp in experience:
                desc = exp.get('description', '')
                if any(char.isdigit() for char in desc):
                    has_quantification = True
                    break

            if not has_quantification:
                experience_analysis['status'] = 'warning'
                experience_analysis['message'] = '工作经历描述需要优化'
                experience_analysis['issues'] = '缺少量化成果和数据支撑'
                experience_analysis['suggestions'] = '建议使用具体数字和数据来展示工作成果'
        else:
            experience_analysis['suggestions'] = '建议添加工作经历信息'

        # 技能分析
        skills_analysis = {
            "status": "good" if skills else "warning",
            "message": "技能描述清晰" if skills else "缺少技能信息",
            "hard_skills": [],
            "soft_skills": [],
            "suggestions": None
        }

        # 简单分类硬技能和软技能
        soft_skill_keywords = ['沟通', '团队', '协作', '管理', '领导', '学习', '解决问题']
        for skill in skills:
            if any(keyword in skill for keyword in soft_skill_keywords):
                skills_analysis['soft_skills'].append(skill)
            else:
                skills_analysis['hard_skills'].append(skill)

        if not skills:
            skills_analysis['suggestions'] = '建议添加技能信息'

        return {
            "overall_score": overall_score,
            "content_score": content_score,
            "match_score": match_score,
            "clarity_score": clarity_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "personal_analysis": personal_analysis,
            "education_analysis": education_analysis,
            "experience_analysis": experience_analysis,
            "skills_analysis": skills_analysis
        }

    @staticmethod
    async def generate_suggestions(
        db: Session,
        resume_id: int,
        llm_service,
        force_refresh: bool = False,
        jd: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        生成简历优化建议

        Args:
            db: 数据库会话
            resume_id: 简历ID
            llm_service: LLM 服务实例
            force_refresh: 是否强制重新生成
            jd: 职位描述（可选），用于针对性优化

        Returns:
            优化建议列表
        """
        # 获取简历
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("简历不存在")

        # 获取已有的优化建议
        existing_suggestions = db.query(ResumeOptimization).filter(
            ResumeOptimization.resume_id == resume_id
        ).all()

        # 如果已有建议且不强制刷新，返回已有的
        if existing_suggestions and not force_refresh:
            return [
                {
                    "id": s.id,
                    "priority": s.priority,
                    "title": s.title,
                    "description": s.description,
                    "before": s.before,
                    "after": s.after,
                    "reason": s.reason
                }
                for s in existing_suggestions
            ]

        # 准备简历数据和之前的分析结果
        resume_data = {
            "personal_info": json.loads(resume.personal_info) if resume.personal_info else {},
            "education": json.loads(resume.education) if resume.education else [],
            "experience": json.loads(resume.experience) if resume.experience else [],
            "skills": json.loads(resume.skills) if resume.skills else [],
            "projects": json.loads(resume.projects) if resume.projects else [],
        }

        analysis_result = {}
        if resume.analysis_result:
            try:
                analysis_result = json.loads(resume.analysis_result)
            except json.JSONDecodeError:
                pass

        # 使用 LLM 生成优化建议
        suggestions_prompt = ResumeOptimizationService._build_suggestions_prompt(resume_data, analysis_result, jd)

        try:
            suggestions_response = await llm_service.generate_text(
                suggestions_prompt,
                temperature=0.5,
                max_tokens=65535  # 使用最大 token 数以支持最详细的建议
            )

            # 去除可能存在的 markdown 代码块标记
            suggestions_response = suggestions_response.strip()
            if suggestions_response.startswith("```json"):
                suggestions_response = suggestions_response[7:]
            elif suggestions_response.startswith("```"):
                suggestions_response = suggestions_response[3:]
            if suggestions_response.endswith("```"):
                suggestions_response = suggestions_response[:-3]
            suggestions_response = suggestions_response.strip()

            # 解析 LLM 响应
            try:
                suggestions = json.loads(suggestions_response)
            except json.JSONDecodeError:
                # 如果解析失败，使用基础建议生成
                suggestions = ResumeOptimizationService._basic_suggestions(resume_data, analysis_result)

            # 删除旧建议
            db.query(ResumeOptimization).filter(
                ResumeOptimization.resume_id == resume_id
            ).delete()

            # 保存新建议
            for idx, suggestion in enumerate(suggestions):
                db_suggestion = ResumeOptimization(
                    resume_id=resume_id,
                    priority=suggestion.get('priority', 'medium'),
                    title=suggestion.get('title', ''),
                    description=suggestion.get('description', ''),
                    before=suggestion.get('before'),
                    after=suggestion.get('after'),
                    reason=suggestion.get('reason')
                )
                db.add(db_suggestion)

            db.commit()

            logger.info(f"简历 {resume_id} 生成 {len(suggestions)} 条优化建议")
            return suggestions

        except Exception as e:
            logger.error(f"生成优化建议失败: {e}", exc_info=True)
            # 使用基础建议作为后备
            suggestions = ResumeOptimizationService._basic_suggestions(resume_data, analysis_result)

            # 删除旧建议
            db.query(ResumeOptimization).filter(
                ResumeOptimization.resume_id == resume_id
            ).delete()

            # 保存建议
            for idx, suggestion in enumerate(suggestions):
                db_suggestion = ResumeOptimization(
                    resume_id=resume_id,
                    priority=suggestion.get('priority', 'medium'),
                    title=suggestion.get('title', ''),
                    description=suggestion.get('description', ''),
                    before=suggestion.get('before'),
                    after=suggestion.get('after'),
                    reason=suggestion.get('reason')
                )
                db.add(db_suggestion)

            db.commit()
            return suggestions

    @staticmethod
    def _build_suggestions_prompt(resume_data: Dict[str, Any], analysis_result: Dict[str, Any], jd: Optional[str] = None) -> str:
        """构建优化建议生成的提示词"""
        jd_info = f"\n目标职位描述 (JD):\n{jd}\n\n请特别关注简历与该职位的匹配度，提供针对性的优化建议。\n" if jd else ""

        return f"""
请分析以下简历，生成具体的优化建议，并以JSON格式返回。
{jd_info if jd else "请从通用角度提供优化建议。"}

简历信息：
姓名: {resume_data['personal_info'].get('name', '未知')}
邮箱: {resume_data['personal_info'].get('email', '未知')}
电话: {resume_data['personal_info'].get('phone', '未知')}

教育背景:
{json.dumps(resume_data['education'], ensure_ascii=False, indent=2)}

工作经历:
{json.dumps(resume_data['experience'], ensure_ascii=False, indent=2)}

项目经历:
{json.dumps(resume_data['projects'], ensure_ascii=False, indent=2)}

技能:
{', '.join(resume_data['skills'])}

分析结果:
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

请按以下JSON格式返回优化建议（建议3-5条）：
[
    {{
        "priority": "high/medium/low",
        "title": "建议标题（简明扼要，10-20字）",
        "description": "详细描述这个建议（80-150字，说明具体的问题、影响和改进方向）",
        "before": "优化前的内容示例（直接引用简历原文，50-100字）",
        "after": "优化后的内容示例（具体改写后的内容，100-200字，展示如何改进）",
        "reason": "为什么需要这样优化（80-150字，说明改进的理由和预期效果）"
    }}
]

优化建议应该针对简历中存在的问题，提供具体可行的改进方案。
**重要要求：**
1. **description** 必须详细说明问题的具体表现、产生的影响以及改进方向，不少于 80 字
2. **before** 必须直接引用简历中的原文，展示问题所在
3. **after** 必须提供具体的改写示例，展示优化后的效果，不少于 100 字
4. **reason** 必须详细说明为什么需要这样优化，以及优化后的预期效果，不少于 80 字
5. 优先提供针对 JD 的建议（如果提供了 JD），其次提供通用优化建议

优先级说明：
- high: 重要的、必须改进的问题（如缺少关键技能、经验描述不清、缺少量化成果等）
- medium: 建议改进的问题（如描述不够具体、缺少亮点等）
- low: 可以优化的细节（如格式、措辞等）

请确保返回的是合法的JSON数组格式，不要包含任何其他文字说明。
"""

    @staticmethod
    def _basic_suggestions(resume_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基础优化建议生成（不依赖LLM）"""
        suggestions = []

        # 检查个人信息
        personal_info = resume_data.get('personal_info', {})
        if not personal_info.get('name'):
            suggestions.append({
                "priority": "high",
                "title": "添加姓名",
                "description": "简历中缺少姓名信息，这是简历的基本要素",
                "before": "",
                "after": "张三",
                "reason": "姓名是简历的基本信息，必须包含"
            })

        # 检查工作经历
        experience = resume_data.get('experience', [])
        if experience:
            # 检查是否有量化成果
            has_quantification = False
            for exp in experience:
                desc = exp.get('description', '')
                if any(char.isdigit() for char in desc):
                    has_quantification = True
                    break

            if not has_quantification:
                suggestions.append({
                    "priority": "high",
                    "title": "添加量化成果",
                    "description": "在工作经历中添加具体的数字和成果，如\"提升性能50%\"、\"管理10人团队\"等",
                    "before": "负责项目开发，提升了系统性能",
                    "after": "负责核心模块开发，通过优化数据库查询和缓存策略，将系统响应时间从500ms降低到250ms，性能提升50%",
                    "reason": "量化成果能让HR更直观地了解你的能力和贡献"
                })

            # 检查项目描述
            for exp in experience:
                desc = exp.get('description', '')
                if desc and len(desc) < 50:
                    suggestions.append({
                        "priority": "medium",
                        "title": "优化项目描述",
                        "description": "使用STAR法则（情境-任务-行动-结果）重新组织项目经历",
                        "before": "参与了电商平台的开发",
                        "after": "在电商平台项目中（情境），负责用户模块开发（任务），使用Vue.js和Node.js构建了完整的用户注册登录功能（行动），支持日均10万+用户访问（结果）",
                        "reason": "STAR法则能让项目经历更有条理，突出你的贡献和成果"
                    })
                    break

        # 检查技能
        skills = resume_data.get('skills', [])
        if len(skills) < 3:
            suggestions.append({
                "priority": "medium",
                "title": "丰富技能列表",
                "description": "添加更多相关的技能，包括编程语言、框架、工具等",
                "before": "JavaScript, CSS",
                "after": "JavaScript, TypeScript, Vue.js, React, Node.js, Express, MongoDB, MySQL, Git, Docker",
                "reason": "丰富的技能列表能展示你的技术栈广度"
            })

        # 检查教育背景
        education = resume_data.get('education', [])
        if education and len(education) > 0:
            edu = education[0]
            if not edu.get('major'):
                suggestions.append({
                    "priority": "low",
                    "title": "补充专业信息",
                    "description": "在教育背景中添加专业信息",
                    "before": "某某大学",
                    "after": "某某大学 - 计算机科学与技术专业",
                    "reason": "专业信息能帮助HR了解你的专业背景"
                })

        return suggestions

    @staticmethod
    def apply_optimizations(
        db: Session,
        resume_id: int,
        suggestions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        应用优化建议到简历

        Args:
            db: 数据库会话
            resume_id: 简历ID
            suggestions: 要应用的优化建议列表

        Returns:
            应用结果
        """
        # 获取简历
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("简历不存在")

        # 更新版本号
        old_version = resume.current_version
        version_parts = old_version[1:].split('.')
        version_parts[0] = str(int(version_parts[0]) + 1)
        new_version = f"v{version_parts[0]}.{version_parts[1] if len(version_parts) > 1 else '0'}"
        resume.current_version = new_version

        # 标记建议为已应用
        applied_count = 0
        for suggestion in suggestions:
            suggestion_id = suggestion.get('id')
            if suggestion_id:
                db_suggestion = db.query(ResumeOptimization).filter(
                    ResumeOptimization.id == suggestion_id,
                    ResumeOptimization.resume_id == resume_id
                ).first()
                if db_suggestion:
                    db_suggestion.is_applied = True
                    applied_count += 1

        # 记录优化历史
        history = ResumeOptimizationHistory(
            resume_id=resume_id,
            version=new_version,
            version_before=old_version,
            version_after=new_version,
            title="应用优化建议",
            description=f"应用了{applied_count}条优化建议",
            status="success",
            changes={"applied_suggestions": suggestions}
        )
        db.add(history)

        db.commit()

        logger.info(f"简历 {resume_id} 应用 {applied_count} 条优化建议，版本更新为 {new_version}")

        return {
            "version": new_version,
            "optimized_at": datetime.utcnow(),
            "applied_count": applied_count
        }

    @staticmethod
    def get_optimization_history(
        db: Session,
        resume_id: int
    ) -> List[Dict[str, Any]]:
        """
        获取简历优化历史

        Args:
            db: 数据库会话
            resume_id: 简历ID

        Returns:
            优化历史列表
        """
        # 获取简历
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("简历不存在")

        # 获取优化历史
        history_list = db.query(ResumeOptimizationHistory).filter(
            ResumeOptimizationHistory.resume_id == resume_id
        ).order_by(ResumeOptimizationHistory.created_at.desc()).all()

        return [
            {
                "id": h.id,
                "version": h.version,
                "version_before": h.version_before,
                "version_after": h.version_after,
                "title": h.title,
                "description": h.description,
                "status": h.status,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in history_list
        ]

    @staticmethod
    def compare_versions(
        db: Session,
        resume_id: int,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """
        比较两个版本的简历差异

        Args:
            db: 数据库会话
            resume_id: 简历ID
            version1: 版本1
            version2: 版本2

        Returns:
            比较结果
        """
        # 获取简历
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("简历不存在")

        # 获取两个版本的历史记录
        history1 = db.query(ResumeOptimizationHistory).filter(
            ResumeOptimizationHistory.resume_id == resume_id,
            ResumeOptimizationHistory.version == version1
        ).first()

        history2 = db.query(ResumeOptimizationHistory).filter(
            ResumeOptimizationHistory.resume_id == resume_id,
            ResumeOptimizationHistory.version == version2
        ).first()

        if not history1 or not history2:
            raise ValueError("指定的版本不存在")

        # 构建比较结果
        result = {
            "before": version1,
            "after": version2,
            "diff": []
        }

        # 比较变更内容
        if history1.changes and history2.changes:
            # 简化的差异比较
            result["diff"] = [
                {
                    "type": "modified",
                    "section": "整体",
                    "content": {
                        "old": f"版本 {version1}",
                        "new": f"版本 {version2}"
                    }
                }
            ]

        return result

    @staticmethod
    def restore_version(
        db: Session,
        resume_id: int,
        version: str
    ) -> Dict[str, Any]:
        """
        恢复简历到指定版本

        Args:
            db: 数据库会话
            resume_id: 简历ID
            version: 要恢复的版本

        Returns:
            恢复结果
        """
        # 获取简历
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("简历不存在")

        # 获取历史记录
        history = db.query(ResumeOptimizationHistory).filter(
            ResumeOptimizationHistory.resume_id == resume_id,
            ResumeOptimizationHistory.version == version
        ).first()

        if not history:
            raise ValueError("指定的版本不存在")

        # 更新当前版本
        old_version = resume.current_version
        resume.current_version = version

        # 记录恢复历史
        restore_history = ResumeOptimizationHistory(
            resume_id=resume_id,
            version=version,
            version_before=old_version,
            version_after=version,
            title="恢复到历史版本",
            description=f"从版本 {old_version} 恢复到 {version}",
            status="success",
            changes={"restored_from": old_version}
        )
        db.add(restore_history)

        db.commit()

        logger.info(f"简历 {resume_id} 从版本 {old_version} 恢复到 {version}")

        return {
            "version": version,
            "restored_at": datetime.utcnow()
        }