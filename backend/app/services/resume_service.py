import os
from typing import Dict, Any, List
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
import json


class ResumeParser:
    """简历解析服务"""

    @staticmethod
    def parse_resume(file_path: str) -> Dict[str, Any]:
        """
        解析简历文件，提取结构化信息

        Args:
            file_path: 简历文件路径

        Returns:
            包含结构化简历信息的字典
        """
        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            # 根据文件类型选择解析方法
            if file_ext == '.pdf':
                elements = partition_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                elements = partition_docx(file_path)
            else:
                elements = partition(file_path)

            # 提取文本内容
            text_content = "\n".join([str(el) for el in elements])

            # 解析各个部分
            result = {
                "personal_info": ResumeParser._extract_personal_info(text_content),
                "education": ResumeParser._extract_education(text_content),
                "experience": ResumeParser._extract_experience(text_content),
                "skills": ResumeParser._extract_skills(text_content),
                "projects": ResumeParser._extract_projects(text_content),
                "highlights": ResumeParser._extract_highlights(text_content)
            }

            return result

        except Exception as e:
            raise Exception(f"简历解析失败: {str(e)}")

    @staticmethod
    def _extract_personal_info(text: str) -> Dict[str, Any]:
        """提取个人信息"""
        info = {}

        # 简单的关键词匹配（实际应用中可以使用更复杂的 NLP）
        lines = text.split('\n')

        # 假设第一行是姓名
        if lines:
            info['name'] = lines[0].strip()

        # 提取邮箱
        import re
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, text)
        if emails:
            info['email'] = emails[0]

        # 提取电话
        phone_pattern = r'1[3-9]\d{9}'
        phones = re.findall(phone_pattern, text)
        if phones:
            info['phone'] = phones[0]

        return info

    @staticmethod
    def _extract_education(text: str) -> List[Dict[str, Any]]:
        """提取教育背景"""
        education_list = []
        # 简化的教育信息提取
        # 实际应用中需要更复杂的解析逻辑
        return education_list

    @staticmethod
    def _extract_experience(text: str) -> List[Dict[str, Any]]:
        """提取工作经历"""
        experience_list = []
        # 简化的工作经验提取
        # 实际应用中需要更复杂的解析逻辑
        return experience_list

    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """提取技能"""
        skills = []

        # 常见技能关键词
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Vue', 'FastAPI', 'Django',
            'SQL', 'MySQL', 'PostgreSQL', 'Docker', 'Kubernetes', 'Git',
            '机器学习', '深度学习', 'NLP', '数据分析', '爬虫'
        ]

        for skill in common_skills:
            if skill.lower() in text.lower():
                skills.append(skill)

        return skills

    @staticmethod
    def _extract_projects(text: str) -> List[Dict[str, Any]]:
        """提取项目经历"""
        project_list = []
        # 简化的项目信息提取
        # 实际应用中需要更复杂的解析逻辑
        return project_list

    @staticmethod
    def _extract_highlights(text: str) -> List[str]:
        """提取个人亮点"""
        highlights = []
        # 简化的亮点提取
        # 实际应用中可以使用 LLM 来提取
        return highlights


async def parse_resume_with_llm(file_path: str, llm_service) -> Dict[str, Any]:
    """
    使用 LLM 增强的简历解析

    Args:
        file_path: 简历文件路径
        llm_service: LLM 服务实例

    Returns:
        包含详细解析结果的字典
    """
    # 先用 Unstructured.io 提取基础信息
    base_result = ResumeParser.parse_resume(file_path)

    # 使用 LLM 进行更深入的分析
    text_content = "\n".join([
        "姓名: " + base_result['personal_info'].get('name', ''),
        "邮箱: " + base_result['personal_info'].get('email', ''),
        "技能: " + ", ".join(base_result['skills'])
    ])

    # 使用 LLM 提取亮点
    try:
        highlights_prompt = f"""
        请从以下简历信息中提取 3-5 个个人亮点和核心优势：
        {text_content}

        请以 JSON 数组格式返回亮点列表。
        """
        highlights_response = await llm_service.generate_text(highlights_prompt)
        base_result['highlights'] = json.loads(highlights_response)
    except Exception as e:
        base_result['highlights'] = []

    return base_result