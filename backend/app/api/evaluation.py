from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.interview import Interview
from app.schemas.evaluation import InterviewReport
from app.api.auth import get_current_user
import json
import asyncio
import re

router = APIRouter()


async def search_learning_resources(keywords: list) -> list:
    """
    搜索学习资源（使用预定义的高质量资源库）

    Args:
        keywords: 搜索关键词列表

    Returns:
        学习资源列表
    """
    try:
        # 预定义的高质量学习资源库
        resource_library = [
            {
                "title": "【面试干货】2025求职必备：AI面试工具与高效复盘技巧",
                "url": "https://blog.csdn.net/offergoose/article/details/147768099",
                "keywords": ["面试", "技巧", "复盘", "AI工具"],
                "type": "article"
            },
            {
                "title": "2025 如何准备资深前端、全端工程师面试？",
                "url": "https://www.explainthis.io/zh-hans/career/2025-interview-prep",
                "keywords": ["前端", "全端", "技术", "面试准备"],
                "type": "article"
            },
            {
                "title": "2025年6大面试辅助软件全方位测评",
                "url": "https://blog.offergoose.com/zh-cn/post40/",
                "keywords": ["面试", "工具", "软件", "测评"],
                "type": "article"
            },
            {
                "title": "算法面试新趋势：2025年必须掌握的4个黑马学习平台",
                "url": "https://blog.csdn.net/2201_75694192/article/details/148067783",
                "keywords": ["算法", "面试", "平台", "学习"],
                "type": "article"
            },
            {
                "title": "2025秋招笔试面试全攻略：AI助手让你轻松拿下大厂Offer",
                "url": "https://www.cuemate.net/blog/7",
                "keywords": ["秋招", "笔试", "面试", "大厂"],
                "type": "article"
            },
            {
                "title": "AI面试官成主流？2025视频面试眼神/语速/背景避坑指南",
                "url": "https://www.wondercv.com/blog/kO1dX1L6.html",
                "keywords": ["AI面试", "视频面试", "技巧", "指南"],
                "type": "article"
            },
            {
                "title": "程序员必备简历面试课 - 15年经验大厂HR亲授",
                "url": "https://blog.csdn.net/weixin_33821003/article/details/106513777",
                "keywords": ["程序员", "简历", "面试", "课程"],
                "type": "course"
            },
            {
                "title": "2025省考面面俱到备考礼包",
                "url": "https://www.huatu.com/z/2025skbklb/",
                "keywords": ["公务员", "面试", "备考", "技巧"],
                "type": "course"
            },
            {
                "title": "参加面试 考生应作哪些准备",
                "url": "https://www.semanticscholar.org/paper/03264031b55d3f42e4e7d35f04a16ff6c49cd986",
                "keywords": ["面试", "准备", "技巧", "方法"],
                "type": "article"
            },
            {
                "title": "为技术面试做准备",
                "url": "https://cn.linkedin.com/learning/introduction-to-career-skills-in-software-development-19367950/3255082",
                "keywords": ["技术", "面试", "准备", "课程"],
                "type": "course"
            }
        ]

        if not keywords:
            # 如果没有关键词，返回前5个资源
            return resource_library[:5]

        print(f"搜索学习资源关键词: {keywords}")

        # 根据关键词匹配资源
        matched_resources = []
        for resource in resource_library:
            # 计算匹配分数
            match_score = 0
            for keyword in keywords:
                # 检查标题和关键词字段
                if keyword.lower() in resource['title'].lower():
                    match_score += 2
                for kw in resource['keywords']:
                    if keyword.lower() in kw.lower():
                        match_score += 1

            if match_score > 0:
                matched_resources.append({
                    'resource': resource,
                    'score': match_score
                })

        # 按匹配分数排序
        matched_resources.sort(key=lambda x: x['score'], reverse=True)

        # 返回匹配的资源（最多5个）
        result = [item['resource'] for item in matched_resources[:5]]

        # 如果匹配的资源少于5个，补充其他高质量资源
        if len(result) < 5:
            added_urls = {r['url'] for r in result}
            for resource in resource_library:
                if len(result) >= 5:
                    break
                if resource['url'] not in added_urls:
                    result.append(resource)
                    added_urls.add(resource['url'])

        print(f"匹配到的资源数量: {len(result)}")
        for i, res in enumerate(result):
            print(f"  {i+1}. {res['title'][:40]}... -> {res['url']}")

        return result

    except Exception as e:
        print(f"搜索学习资源失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def filter_search_results(search_results: list, max_results: int = 5) -> list:
    """
    过滤和格式化搜索结果

    Args:
        search_results: 搜索结果列表
        max_results: 最多返回的结果数

    Returns:
        过滤后的学习资源列表
    """
    valid_resources = []

    for result in search_results[:max_results]:
        url = result.get('url', '')
        title = result.get('title', '')

        # 验证URL有效性
        if not url or not title:
            continue

        # 简单的URL验证
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                continue
        except:
            continue

        # 过滤掉无效域名
        invalid_domains = ['example.com', 'localhost', '127.0.0.1']
        if any(domain in url for domain in invalid_domains):
            continue

        # 确定资源类型
        resource_type = 'article'
        if any(keyword in url.lower() for keyword in ['video', 'youtube', 'bilibili', 'course']):
            resource_type = 'video'
        elif any(keyword in url.lower() for keyword in ['course', 'mooc', 'edu']):
            resource_type = 'course'

        valid_resources.append({
            "type": resource_type,
            "title": title,
            "url": url
        })

    return valid_resources


@router.get("/report/{interview_id}")
async def get_interview_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试评估报告"""
    from app.schemas.common import ApiResponse

    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview:
        raise HTTPException(
            status_code=404,
            detail="面试不存在"
        )

    if interview.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="面试尚未完成"
        )

    # 检查是否已有缓存的评估报告
    if interview.evaluation_report:
        report_data = json.loads(interview.evaluation_report)
        return ApiResponse(
            code=200,
            message="获取成功",
            data=InterviewReport(
                interview_id=interview_id,
                **report_data,
                created_at=interview.evaluation_generated_at or interview.created_at
            )
        )

    # 获取对话记录
    conversation = json.loads(interview.conversation) if interview.conversation else []

    # 调用评估报告生成服务
    from app.services.evaluation_service import EvaluationService
    report_data = await EvaluationService.generate_interview_report(
        {
            "id": interview.id,
            "job_description": interview.job_description
        },
        conversation
    )

    # 搜索真实的学习资源
    overall_feedback = report_data.get('overall_feedback', '')
    keywords = []

    # 提取关键词用于搜索
    if "技术" in overall_feedback:
        keywords.append("技术面试准备")
    if "沟通" in overall_feedback:
        keywords.append("面试沟通技巧")
    if "项目" in overall_feedback:
        keywords.append("项目经验描述")
    if "算法" in overall_feedback:
        keywords.append("算法面试")

    # 如果没有特定关键词，使用通用关键词
    if not keywords:
        keywords = ["面试技巧提升", "面试准备"]

    # 搜索学习资源
    search_results = await search_learning_resources(keywords)

    # 过滤和格式化搜索结果
    filtered_resources = filter_search_results(search_results)

    # 如果成功获取到真实资源，替换LLM生成的资源
    if filtered_resources:
        # 去重（基于URL）
        seen_urls = set()
        unique_resources = []
        for resource in filtered_resources:
            if resource['url'] not in seen_urls:
                seen_urls.add(resource['url'])
                unique_resources.append(resource)

        report_data['recommended_resources'] = unique_resources[:5]  # 最多返回5个资源

    # 保存评估报告到数据库
    from datetime import datetime
    interview.evaluation_report = json.dumps(report_data, ensure_ascii=False)
    interview.evaluation_generated_at = datetime.now()
    interview.total_score = report_data.get("total_score", 0)
    db.commit()

    return ApiResponse(
        code=200,
        message="获取成功",
        data=InterviewReport(
            interview_id=interview_id,
            **report_data,
            created_at=interview.evaluation_generated_at
        )
    )