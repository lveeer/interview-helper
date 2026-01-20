import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeParser:
    """简历解析服务 - 使用 Unstructured.io 提取文本，LLM 增强结构化信息"""

    @staticmethod
    def _extract_text_with_unstructured(file_path: str) -> str:
        """
        提取文档文本 - 使用多种方法

        Args:
            file_path: 文档文件路径

        Returns:
            提取的文本内容
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"开始提取文档文本，文件类型: {file_ext}")

        # 1. 优先处理文本文件
        if file_ext == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                logger.info(f"成功提取文本文件，共 {len(text_content)} 字符")
                return text_content
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        text_content = f.read()
                    logger.info(f"成功提取文本文件（GBK编码），共 {len(text_content)} 字符")
                    return text_content
                except Exception as e:
                    logger.error(f"文本文件读取失败: {e}")
                    raise Exception(f"文本文件读取失败: {str(e)}")

        # 2. 处理 PDF 文件
        if file_ext == '.pdf':
            try:
                import pdfplumber
                text_content = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        # 提取文本，保持布局顺序
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                        
                        # 提取表格（PDF 中的表格信息）
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                for row in table:
                                    row_text = " | ".join([str(cell) if cell else "" for cell in row])
                                    if row_text.strip():
                                        text_content += row_text + "\n"
                logger.info(f"pdfplumber 成功提取 PDF，共 {len(text_content)} 字符，{len(pdf.pages)} 页")
                return text_content
            except ImportError:
                logger.warning("pdfplumber 未安装，尝试使用 pypdf")
                # 回退到 pypdf
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    text_content = ""
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
                    logger.info(f"pypdf 成功提取 PDF，共 {len(text_content)} 字符，{len(reader.pages)} 页")
                    return text_content
                except Exception as e:
                    logger.error(f"pypdf 也失败: {e}")
            except Exception as e:
                logger.error(f"PDF 提取失败: {e}")

        # 3. 处理 Word 文件
        if file_ext in ['.docx', '.doc']:
            try:
                import docx2txt
                text_content = docx2txt.process(file_path)
                logger.info(f"docx2txt 成功提取 Word 文档，共 {len(text_content)} 字符")
                return text_content
            except ImportError:
                logger.warning("docx2txt 未安装，尝试使用其他方法")
            except Exception as e:
                logger.error(f"Word 文档提取失败: {e}")

        # 4. 尝试使用 unstructured（处理其他格式）
        try:
            from unstructured.partition.auto import partition
            elements = partition(filename=file_path)
            text_content = ""
            for element in elements:
                text_content += str(element) + "\n"
            logger.info(f"unstructured.io 成功提取，共 {len(text_content)} 字符，{len(elements)} 个元素")
            return text_content
        except ImportError:
            logger.warning("unstructured 未安装")
        except Exception as e:
            logger.warning(f"unstructured 提取失败: {e}")

        # 5. 如果所有方法都失败，返回错误
        raise Exception(f"无法提取文件 {file_ext} 的文本内容，请检查文件格式或安装相应的依赖库")

    @staticmethod
    def parse_resume(file_path: str) -> Dict[str, Any]:
        """
        解析简历文件，提取结构化信息（基础版，建议使用 LLM 增强版）

        Args:
            file_path: 简历文件路径

        Returns:
            包含结构化简历信息的字典
        """
        logger.info(f"开始解析简历: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            # 提取文本内容（使用 unstructured.io）
            text_content = ResumeParser._extract_text_with_unstructured(file_path)

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

        # 提取姓名（格式：姓名（职位）或纯姓名）
        for line in lines[:10]:  # 检查前10行
            line = line.strip()
            # 匹配格式：谭永锋（后端开发工程师）
            match = re.match(r'^([\u4e00-\u9fa5]{2,4})\（[\u4e00-\u9fa5（）]{2,10}）$', line)
            if match:
                info['name'] = match.group(1)
                break
            
            # 匹配纯姓名（2-4个汉字）
            if re.match(r'^[\u4e00-\u9fa5]{2,4}$', line):
                # 排除明显不是姓名的行
                if not any(keyword in line for keyword in ['简历', '个人', '姓名', '电话', '邮箱', '地址', '经历', '教育', '项目', '技能', '证书']):
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
                    # 清理地址（去除多余空格）
                    address = re.sub(r'\s+', '', line.strip())
                    if len(address) > 3:  # 至少3个字符
                        info['address'] = address
                        break

        # 提取年龄
        age_pattern = r'(\d{1,3})\s*岁'
        age_match = re.search(age_pattern, text)
        if age_match:
            age = int(age_match.group(1))
            if 1 < age < 100:  # 合理的年龄范围
                info['age'] = age

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

    @staticmethod
    def _extract_experience_description(text: str, exp_info: Dict[str, Any]) -> str:
        """
        从原始文本中提取完整的工作经历描述
        
        Args:
            text: 简历全文
            exp_info: LLM 解析的工作经历信息（包含 company, position, start_date 等）
        
        Returns:
            完整的工作经历描述
        """
        lines = text.split('\n')
        company = exp_info.get('company', '')
        position = exp_info.get('position', '')
        
        # 查找包含公司名称的行
        start_idx = -1
        for i, line in enumerate(lines):
            if company in line:
                start_idx = i
                break
        
        if start_idx == -1:
            return ""
        
        # 收集从该行开始，直到下一个公司或章节标题的所有内容
        description_lines = []
        for i in range(start_idx, min(start_idx + 30, len(lines))):
            line = lines[i].strip()
            
            # 如果遇到新的公司、教育、项目等章节，停止
            if i > start_idx:
                # 检查是否是新的公司（不包含当前公司名）
                if any(keyword in line for keyword in ['公司', '有限公司', '科技']):
                    if company not in line:
                        break
                # 检查是否是新的章节
                if any(keyword in line for keyword in ['教育经历', '项目经历', '校园经历', '专业技能', '个人总结']):
                    break
            
            # 跳过公司名、职位、时间等基本信息行
            if i == start_idx:
                continue
            if re.match(r'^\d{4}', line):  # 时间行
                continue
            if position and position in line:  # 职位行
                continue
            
            # 收集描述内容
            if line and len(line) > 5:  # 至少5个字符
                # 过滤掉明显的技能关键词行
                if any(keyword in line for keyword in ['git', 'mysql', 'redis', '掌握', '熟悉', '了解']):
                    # 如果这行很短且看起来像技能列表，跳过
                    if len(line) < 20 and ' ' in line:
                        continue
                description_lines.append(line)
        
        return '\n'.join(description_lines)

    @staticmethod
    def _extract_project_description(text: str, proj_info: Dict[str, Any]) -> str:
        """
        从原始文本中提取完整的项目经历描述
        
        Args:
            text: 简历全文
            proj_info: LLM 解析的项目信息（包含 name, role, start_date 等）
        
        Returns:
            完整的项目经历描述
        """
        lines = text.split('\n')
        project_name = proj_info.get('name', '')
        
        # 查找包含项目名称的行
        start_idx = -1
        for i, line in enumerate(lines):
            if project_name in line:
                start_idx = i
                break
        
        if start_idx == -1:
            return ""
        
        # 收集从该行开始，直到下一个项目或章节标题的所有内容
        description_lines = []
        for i in range(start_idx, min(start_idx + 20, len(lines))):
            line = lines[i].strip()
            
            # 如果遇到新的项目、公司、教育等章节，停止
            if i > start_idx and any(keyword in line for keyword in ['项目', 'Project', '公司', '大学', '学院']):
                # 检查是否是新的项目（不包含当前项目名）
                if project_name not in line:
                    break
            
            # 跳过项目名、角色、时间等基本信息行
            if i == start_idx:
                continue
            if re.match(r'^\d{4}', line):  # 时间行
                continue
            if any(keyword in line for keyword in ['负责人', '参与者', '角色', 'Role']):
                continue
            
            # 收集描述内容
            if line and len(line) > 5:  # 至少5个字符
                description_lines.append(line)
        
        return '\n'.join(description_lines)


async def parse_resume_with_llm(file_path: str, llm_service) -> Dict[str, Any]:
    """
    使用 LLM 增强的简历解析 - 直接上传文件到 LLM

    Args:
        file_path: 简历文件路径
        llm_service: LLM 服务实例

    Returns:
        包含详细解析结果的字典，包括原始文本内容
    """
    logger.info(f"开始使用 LLM 解析简历文件: {file_path}")

    try:
        # 1. 提取原始文本内容
        text_content = ResumeParser._extract_text_with_unstructured(file_path)
        logger.info(f"原始文本提取完成，长度: {len(text_content)} 字符")

        from app.utils.prompt_loader import PromptLoader

        # 2. 构建完整的解析提示词
        full_parse_prompt = PromptLoader.format_prompt(
            'resume_full',
            resume_text="[请直接解析上传的文档文件]"
        )

        logger.info("调用 LLM 文档解析 API...")
        full_response = await llm_service.parse_document(
            file_path=file_path,
            prompt=full_parse_prompt,
            temperature=0.3
        )

        logger.info(f"LLM 文档解析完成，响应长度: {len(full_response)} 字符")

        # 3. 解析 JSON 响应
        full_response = full_response.strip()

        # 尝试提取 markdown 代码块中的 JSON
        import re
        json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        json_match = re.search(json_pattern, full_response)
        if json_match:
            full_response = json_match.group(1).strip()

        # 再次清理，确保没有多余的标记
        full_response = full_response.strip()

        try:
            parsed_data = json.loads(full_response)

            # 验证并补全字段
            result = {
                "personal_info": parsed_data.get("personal_info", {}),
                "education": parsed_data.get("education", []),
                "experience": parsed_data.get("experience", []),
                "skills": parsed_data.get("skills", []),
                "skills_raw": parsed_data.get("skills_raw", []),
                "projects": parsed_data.get("projects", []),
                "highlights": parsed_data.get("highlights", [])
            }

            # 不再从原始文本中重新提取描述，直接使用 LLM 返回的完整信息
            # 因为提示词已经要求 LLM 保留原始简历的完整信息

            logger.info(f"LLM 解析成功 - "
                               f"技能: {len(result['skills'])}, "
                               f"教育: {len(result['education'])}, "
                   f"经历: {len(result['experience'])}, "
                   f"项目: {len(result['projects'])}")

            return result
        except json.JSONDecodeError as je:
            logger.error(f"LLM 文档解析 JSON 失败: {je}")
            logger.error(f"响应内容前500字符: {full_response[:500]}")
            raise Exception(f"JSON 解析失败: {str(je)}")

    except Exception as e:
        logger.error(f"LLM 文档解析失败: {e}", exc_info=True)
        raise Exception(f"简历解析失败: {str(e)}")