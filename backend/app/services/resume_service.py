import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeParser:
    """简历解析服务 - 使用 Unstructured.io 和正则表达式提取结构化信息"""

    @staticmethod
    def _extract_text_with_pdfplumber(file_path: str, fallback_text: str = "") -> str:
        """
        使用 pdfplumber 提取 PDF 文本（支持图片型PDF的OCR）

        Args:
            file_path: PDF文件路径
            fallback_text: 备用文本（如果pdfplumber也失败）

        Returns:
            提取的文本内容
        """
        if not pdfplumber:
            logger.warning("pdfplumber 未安装，使用备用文本")
            return fallback_text

        try:
            with pdfplumber.open(file_path) as pdf:
                text_content = ""
                for page in pdf.pages:
                    # 先尝试直接提取文本
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n"
                    else:
                        # 如果没有文本，可能是图片型PDF
                        # 尝试使用OCR（需要系统安装tesseract）
                        logger.warning(f"第{pdf.pages.index(page) + 1}页未检测到文本，尝试OCR")
                        try:
                            # 检查是否有图片对象
                            if page.images:
                                logger.info(f"检测到 {len(page.images)} 个图片对象")
                                # 注意：完整的OCR需要安装tesseract-ocr和pytesseract
                                # 这里先记录日志，实际OCR功能需要额外配置
                                logger.warning("OCR功能需要安装tesseract-ocr和pytesseract库")
                        except Exception as e:
                            logger.warning(f"OCR尝试失败: {e}")

                if len(text_content.strip()) > 50:
                    logger.info(f"pdfplumber成功提取 {len(text_content)} 字符")
                    return text_content
                else:
                    logger.warning("pdfplumber提取的文本仍然过少")
                    return fallback_text

        except Exception as e:
            logger.error(f"pdfplumber解析失败: {e}")
            return fallback_text

    @staticmethod
    def parse_resume(file_path: str) -> Dict[str, Any]:
        """
        解析简历文件，提取结构化信息

        Args:
            file_path: 简历文件路径

        Returns:
            包含结构化简历信息的字典
        """
        logger.info(f"开始解析简历: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            # 提取文本内容
            text_content = ""

            if file_ext == '.pdf':
                if pypdf:
                    # 使用 pypdf 解析 PDF
                    with open(file_path, 'rb') as f:
                        reader = pypdf.PdfReader(f)
                        for page in reader.pages:
                            text_content += page.extract_text() + "\n"
                    
                    # 如果提取的文本过少，可能是图片型PDF，尝试使用pdfplumber
                    if len(text_content.strip()) < 100:
                        logger.warning("pypdf提取的文本过少，尝试使用pdfplumber")
                        text_content = ResumeParser._extract_text_with_pdfplumber(file_path, text_content)
                else:
                    raise Exception("pypdf 未安装，无法解析 PDF")
            elif file_ext in ['.docx', '.doc']:
                # 使用 python-docx 解析 Word 文档
                try:
                    from docx import Document
                    doc = Document(file_path)
                    for para in doc.paragraphs:
                        text_content += para.text + "\n"
                except ImportError:
                    raise Exception("python-docx 未安装，无法解析 Word 文档")
            elif file_ext == '.txt':
                # 直接读取文本文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            else:
                raise Exception(f"不支持的文件类型: {file_ext}")

            logger.info(f"提取文本内容长度: {len(text_content)} 字符")

            # 解析各个部分
            result = {
                "personal_info": ResumeParser._extract_personal_info(text_content),
                "education": ResumeParser._extract_education(text_content),
                "experience": ResumeParser._extract_experience(text_content),
                "skills": ResumeParser._extract_skills(text_content),
                "projects": ResumeParser._extract_projects(text_content),
                "highlights": []  # 亮点将由 LLM 提取
            }

            logger.info(f"简历解析完成，提取到 {len(result['skills'])} 个技能")
            return result

        except Exception as e:
            logger.error(f"简历解析失败: {str(e)}", exc_info=True)
            raise Exception(f"简历解析失败: {str(e)}")

    @staticmethod
    def _extract_personal_info(text: str) -> Dict[str, Any]:
        """提取个人信息"""
        info = {}
        lines = text.split('\n')

        # 提取姓名（通常在开头，2-4个汉字）
        for line in lines[:5]:  # 检查前5行
            line = line.strip()
            # 排除明显不是姓名的行
            if len(line) >= 2 and len(line) <= 4 and not any(
                keyword in line for keyword in ['简历', '个人', '姓名', '电话', '邮箱', '地址']
            ):
                # 简单验证：主要是汉字
                if re.match(r'^[\u4e00-\u9fa5]{2,4}$', line):
                    info['name'] = line
                    break

        # 提取邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            info['email'] = emails[0]

        # 提取电话（支持多种格式）
        phone_patterns = [
            r'1[3-9]\d{9}',  # 中国手机号
            r'\d{3,4}-\d{7,8}',  # 座机
            r'\+86\s*1[3-9]\d{9}'  # 带国际区号
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                # 清理电话号码
                phone = phones[0].replace('-', '').replace(' ', '').replace('+86', '')
                if len(phone) == 11:
                    info['phone'] = phone
                    break

        # 提取地址（包含省市区关键词）
        address_keywords = ['省', '市', '区', '县', '街道', '路', '号']
        for line in lines:
            if any(keyword in line for keyword in address_keywords):
                # 排除电话行
                if not re.search(r'1[3-9]\d{9}', line):
                    info['address'] = line.strip()
                    break

        # 提取性别
        if '男' in text or '女' in text:
            if '男' in text and '女' not in text:
                info['gender'] = '男'
            elif '女' in text and '男' not in text:
                info['gender'] = '女'

        # 提取年龄/出生日期
        age_pattern = r'(\d{2,3})\s*岁'
        age_match = re.search(age_pattern, text)
        if age_match:
            info['age'] = int(age_match.group(1))

        birth_pattern = r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
        birth_match = re.search(birth_pattern, text)
        if birth_match:
            info['birth_date'] = f"{birth_match.group(1)}-{birth_match.group(2)}-{birth_match.group(3)}"

        return info

    @staticmethod
    def _extract_education(text: str) -> List[Dict[str, Any]]:
        """提取教育背景"""
        education_list = []
        lines = text.split('\n')

        # 教育关键词
        edu_keywords = ['大学', '学院', '学校', '本科', '硕士', '博士', '研究生']
        
        # 学位关键词
        degree_keywords = {
            '博士': '博士',
            '硕士': '硕士',
            '研究生': '硕士',
            '本科': '本科',
            '学士': '本科',
            '大专': '专科',
            '专科': '专科',
            '高职': '专科'
        }

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检查是否包含教育相关关键词
            if any(keyword in line for keyword in edu_keywords):
                edu = {}
                
                # 提取学校名称
                edu['school'] = line
                if '大学' in line or '学院' in line:
                    edu['school'] = line.split('|')[0].strip()

                # 提取学位
                for keyword, degree in degree_keywords.items():
                    if keyword in line:
                        edu['degree'] = degree
                        break
                
                # 查找专业和时间
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if any(k in next_line for k in ['专业', '系', '学院']):
                        edu['major'] = next_line.split('|')[0].strip()
                    elif re.search(r'\d{4}', next_line):
                        # 时间信息
                        time_match = re.search(r'(\d{4})\s*[-–年至到]\s*(\d{4}|至今|现在)', next_line)
                        if time_match:
                            edu['start_date'] = time_match.group(1)
                            if time_match.group(2) in ['至今', '现在']:
                                edu['end_date'] = '至今'
                            else:
                                edu['end_date'] = time_match.group(2)

                # 如果找到了有效信息，添加到列表
                if 'school' in edu:
                    education_list.append(edu)
            
            i += 1

        return education_list

    @staticmethod
    def _extract_experience(text: str) -> List[Dict[str, Any]]:
        """提取工作经历"""
        experience_list = []
        lines = text.split('\n')

        # 工作经历关键词
        exp_keywords = ['公司', '有限公司', '科技', '网络', '集团', '企业', '工作', '经历', '实习']
        
        # 部门/职位关键词
        position_keywords = ['工程师', '经理', '主管', '总监', '开发', '设计', '运营', '产品', '测试', '实习']

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检查是否包含公司相关关键词
            if any(keyword in line for keyword in exp_keywords):
                exp = {}
                
                # 提取公司名称
                exp['company'] = line.split('|')[0].strip()

                # 提取职位
                for keyword in position_keywords:
                    if keyword in line:
                        # 尝试提取完整职位
                        position_match = re.search(r'([^\|]*?' + keyword + r'[^\|]*)', line)
                        if position_match:
                            exp['position'] = position_match.group(1).strip()
                        break
                
                if 'position' not in exp and i + 1 < len(lines):
                    # 检查下一行是否有职位信息
                    next_line = lines[i + 1].strip()
                    for keyword in position_keywords:
                        if keyword in next_line:
                            exp['position'] = next_line.split('|')[0].strip()
                            break

                # 提取工作时间
                time_patterns = [
                    r'(\d{4})\s*[-–年至到]\s*(\d{4}|至今|现在)',
                    r'(\d{4})\.(\d{1,2})\s*[-–至到]\s*(\d{4}|至今|现在)\.?(\d{1,2})?'
                ]
                
                for line_idx in range(i, min(i + 3, len(lines))):
                    check_line = lines[line_idx].strip()
                    for pattern in time_patterns:
                        time_match = re.search(pattern, check_line)
                        if time_match:
                            exp['start_date'] = time_match.group(1)
                            if time_match.group(2) in ['至今', '现在']:
                                exp['end_date'] = '至今'
                            else:
                                exp['end_date'] = time_match.group(2)
                            break
                    if 'start_date' in exp:
                        break

                # 提取工作内容（后续几行）
                description_lines = []
                for j in range(i + 1, min(i + 10, len(lines))):
                    desc_line = lines[j].strip()
                    # 如果遇到新的公司或章节，停止
                    if any(k in desc_line for k in exp_keywords) and j > i + 2:
                        break
                    # 如果是描述性内容（以数字、符号开头）
                    if desc_line and (desc_line[0] in ['•', '-', '*', '1', '2', '3', '4', '5'] or 
                                      desc_line.startswith('负责') or 
                                      desc_line.startswith('参与')):
                        description_lines.append(desc_line)
                
                if description_lines:
                    exp['description'] = '\n'.join(description_lines)

                # 如果找到了有效信息，添加到列表
                if 'company' in exp:
                    experience_list.append(exp)
            
            i += 1

        return experience_list

    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """提取技能"""
        skills = set()

        # 编程语言
        programming_languages = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C', 'C#', 'Go', 'Rust',
            'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Shell', 'SQL'
        ]

        # 前端框架
        frontend_frameworks = [
            'React', 'Vue', 'Angular', 'Svelte', 'jQuery', 'Bootstrap', 'Tailwind', 'Element',
            'HTML', 'CSS', 'Sass', 'Less', 'Webpack', 'Vite'
        ]

        # 后端框架
        backend_frameworks = [
            'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', 'Express', 'Koa',
            'NestJS', 'Laravel', 'Rails', 'ASP.NET', 'Gin', 'Beego', 'Egg'
        ]

        # 数据库
        databases = [
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server',
            'SQLite', 'Elasticsearch', 'Cassandra', 'DynamoDB', 'Neo4j'
        ]

        # DevOps/工具
        devops_tools = [
            'Docker', 'Kubernetes', 'Git', 'Jenkins', 'CI/CD', 'Linux', 'Nginx',
            'Apache', 'Tomcat', 'AWS', 'Azure', 'GCP', 'Terraform', 'Ansible'
        ]

        # AI/数据科学
        ai_tools = [
            'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy',
            'Matplotlib', 'Jupyter', 'NLP', '机器学习', '深度学习', '数据分析',
            '爬虫', 'OpenCV', 'YOLO', 'BERT', 'GPT'
        ]

        # 合并所有技能
        all_skills = programming_languages + frontend_frameworks + backend_frameworks + \
                      databases + devops_tools + ai_tools

        # 在文本中查找匹配的技能
        text_lower = text.lower()
        for skill in all_skills:
            if skill.lower() in text_lower:
                skills.add(skill)

        # 查找技能列表（常见格式）
        skill_section_patterns = [
            r'技能[列表]*[:：]\s*([^\n]+)',
            r'专业技能[:：]\s*([^\n]+)',
            r'技术栈[:：]\s*([^\n]+)',
            r'Skills[:：]\s*([^\n]+)'
        ]
        
        for pattern in skill_section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # 按分隔符分割
                for separator in [',', '、', '，', ';', '；', '|', '/']:
                    if separator in match:
                        parts = match.split(separator)
                        for part in parts:
                            part = part.strip()
                            if part and len(part) >= 2:
                                skills.add(part)
                        break

        return sorted(list(skills))

    @staticmethod
    def _extract_projects(text: str) -> List[Dict[str, Any]]:
        """提取项目经历"""
        project_list = []
        lines = text.split('\n')

        # 项目关键词
        project_keywords = ['项目', 'Project', '系统', '平台', '应用', '网站']

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 检查是否包含项目相关关键词
            if any(keyword in line for keyword in project_keywords):
                project = {}
                
                # 提取项目名称
                project['name'] = line.split('|')[0].strip()

                # 提取项目角色
                role_keywords = ['负责人', '开发者', '参与者', '设计者', 'Leader', 'Lead']
                for keyword in role_keywords:
                    if keyword in line:
                        role_match = re.search(r'([^\|]*?' + keyword + r'[^\|]*)', line)
                        if role_match:
                            project['role'] = role_match.group(1).strip()
                        break

                # 提取项目时间
                time_pattern = r'(\d{4})\s*[-–年至到]\s*(\d{4}|至今|现在)'
                for line_idx in range(i, min(i + 3, len(lines))):
                    check_line = lines[line_idx].strip()
                    time_match = re.search(time_pattern, check_line)
                    if time_match:
                        project['start_date'] = time_match.group(1)
                        if time_match.group(2) in ['至今', '现在']:
                            project['end_date'] = '至今'
                        else:
                            project['end_date'] = time_match.group(2)
                        break

                # 提取项目描述和技术栈
                description_lines = []
                tech_stack = []
                
                for j in range(i + 1, min(i + 15, len(lines))):
                    desc_line = lines[j].strip()
                    
                    # 如果遇到新的项目或章节，停止
                    if any(k in desc_line for k in project_keywords) and j > i + 2:
                        break
                    
                    # 提取技术栈
                    tech_keywords = ['技术栈', '技术', '使用', '基于', '采用', 'Tools']
                    if any(k in desc_line for k in tech_keywords):
                        # 提取技术栈内容
                        tech_content = re.sub(r'技术栈[:：]?\s*', '', desc_line)
                        for separator in [',', '、', '，', ';', '；', '|', '/']:
                            if separator in tech_content:
                                tech_stack = [t.strip() for t in tech_content.split(separator)]
                                break
                        if not tech_stack:
                            tech_stack = [tech_content.strip()]
                    
                    # 提取描述
                    if desc_line and (desc_line[0] in ['•', '-', '*', '1', '2', '3', '4', '5'] or 
                                      desc_line.startswith('实现') or 
                                      desc_line.startswith('开发') or
                                      desc_line.startswith('负责')):
                        description_lines.append(desc_line)
                
                if description_lines:
                    project['description'] = '\n'.join(description_lines)
                
                if tech_stack:
                    project['tech_stack'] = tech_stack

                # 如果找到了有效信息，添加到列表
                if 'name' in project:
                    project_list.append(project)
            
            i += 1

        return project_list

    @staticmethod
    def _extract_highlights(text: str) -> List[str]:
        """提取个人亮点（基础版，建议使用 LLM 增强）"""
        highlights = []
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
    logger.info(f"开始使用 LLM 增强解析简历: {file_path}")
    
    try:
        # 先用 Unstructured.io 提取基础信息
        base_result = ResumeParser.parse_resume(file_path)

        # 准备完整的简历文本
        resume_text = f"""
姓名: {base_result['personal_info'].get('name', '未知')}
邮箱: {base_result['personal_info'].get('email', '未知')}
电话: {base_result['personal_info'].get('phone', '未知')}

教育背景:
{json.dumps(base_result['education'], ensure_ascii=False, indent=2)}

工作经历:
{json.dumps(base_result['experience'], ensure_ascii=False, indent=2)}

项目经历:
{json.dumps(base_result['projects'], ensure_ascii=False, indent=2)}

技能:
{', '.join(base_result['skills'])}
"""

        # 使用 LLM 增强技能提取
        try:
            skills_prompt = f"""
请从以下简历信息中提取更全面的技能列表，包括但不限于编程语言、框架、工具、数据库等。
简历信息:
{resume_text}

请以 JSON 数组格式返回技能列表，例如:
["Python", "Java", "React", "MySQL", "Docker"]

只返回 JSON 数组，不要包含其他内容。
"""
            skills_response = await llm_service.generate_text(skills_prompt, temperature=0.3)
            try:
                llm_skills = json.loads(skills_response)
                if isinstance(llm_skills, list):
                    # 合并原有技能和 LLM 提取的技能
                    base_result['skills'] = list(set(base_result['skills'] + llm_skills))
                    logger.info(f"LLM 增强技能提取完成，共 {len(base_result['skills'])} 个技能")
            except json.JSONDecodeError:
                logger.warning("LLM 技能解析失败，使用基础提取结果")
        except Exception as e:
            logger.warning(f"LLM 技能提取失败: {e}，使用基础提取结果")

        # 使用 LLM 提取亮点
        try:
            highlights_prompt = f"""
请从以下简历信息中提取 3-5 个个人亮点和核心优势，突出候选人的独特价值和核心竞争力。
简历信息:
{resume_text}

请以 JSON 数组格式返回亮点列表，例如:
["拥有5年全栈开发经验", "主导过多个高并发项目", "精通微服务架构"]

只返回 JSON 数组，不要包含其他内容。
"""
            highlights_response = await llm_service.generate_text(highlights_prompt, temperature=0.5)
            try:
                llm_highlights = json.loads(highlights_response)
                if isinstance(llm_highlights, list) and llm_highlights:
                    base_result['highlights'] = llm_highlights
                    logger.info(f"LLM 亮点提取完成，共 {len(base_result['highlights'])} 个亮点")
            except json.JSONDecodeError:
                logger.warning("LLM 亮点解析失败")
        except Exception as e:
            logger.warning(f"LLM 亮点提取失败: {e}")

        # 使用 LLM 增强教育背景
        if base_result['education']:
            try:
                education_prompt = f"""
请从以下教育背景信息中提取并规范化数据，确保包含学校名称、学位、专业、起止时间。
教育背景:
{json.dumps(base_result['education'], ensure_ascii=False, indent=2)}

请以 JSON 数组格式返回，每个对象包含: school, degree, major, start_date, end_date
只返回 JSON 数组，不要包含其他内容。
"""
                education_response = await llm_service.generate_text(education_prompt, temperature=0.3)
                try:
                    llm_education = json.loads(education_response)
                    if isinstance(llm_education, list) and llm_education:
                        base_result['education'] = llm_education
                        logger.info(f"LLM 教育背景增强完成")
                except json.JSONDecodeError:
                    logger.warning("LLM 教育背景解析失败")
            except Exception as e:
                logger.warning(f"LLM 教育背景增强失败: {e}")

        # 使用 LLM 增强工作经历
        if base_result['experience']:
            try:
                experience_prompt = f"""
请从以下工作经历信息中提取并规范化数据，确保包含公司名称、职位、起止时间、工作描述。
工作经历:
{json.dumps(base_result['experience'], ensure_ascii=False, indent=2)}

请以 JSON 数组格式返回，每个对象包含: company, position, start_date, end_date, description
只返回 JSON 数组，不要包含其他内容。
"""
                experience_response = await llm_service.generate_text(experience_prompt, temperature=0.3)
                try:
                    llm_experience = json.loads(experience_response)
                    if isinstance(llm_experience, list) and llm_experience:
                        base_result['experience'] = llm_experience
                        logger.info(f"LLM 工作经历增强完成")
                except json.JSONDecodeError:
                    logger.warning("LLM 工作经历解析失败")
            except Exception as e:
                logger.warning(f"LLM 工作经历增强失败: {e}")

        logger.info("LLM 增强简历解析完成")
        return base_result

    except Exception as e:
        logger.error(f"LLM 增强简历解析失败: {e}", exc_info=True)
        # 如果 LLM 解析失败，返回基础解析结果
        return ResumeParser.parse_resume(file_path)