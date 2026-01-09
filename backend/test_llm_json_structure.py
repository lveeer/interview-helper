"""
测试面试问题生成的LLM服务返回的JSON结构
"""
import asyncio
import json
from app.services.interview_service import InterviewService
from app.utils.prompt_loader import PromptLoader


async def test_generate_interview_questions():
    """测试生成面试问题"""

    # 模拟简历数据
    resume_data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "education": [
            {
                "school": "清华大学",
                "major": "计算机科学与技术",
                "degree": "本科",
                "graduation_year": "2020"
            }
        ],
        "experience": [
            {
                "company": "阿里巴巴",
                "position": "后端开发工程师",
                "duration": "2020-2023",
                "description": "负责电商系统的后端开发，使用Spring Boot和MySQL，参与高并发场景的性能优化工作"
            },
            {
                "company": "腾讯",
                "position": "高级后端工程师",
                "duration": "2023-至今",
                "description": "负责社交平台的架构设计，使用Go和Redis，主导了微服务改造项目"
            }
        ],
        "skills": ["Java", "Spring Boot", "Go", "MySQL", "Redis", "Docker", "Kubernetes", "微服务"],
        "projects": [
            {
                "name": "电商系统性能优化",
                "description": "优化电商系统的高并发处理能力，将QPS从1000提升到10000",
                "technologies": ["Spring Boot", "Redis", "MySQL", "Kafka"]
            }
        ]
    }

    # 模拟岗位描述
    job_description = """
    岗位名称：高级后端工程师

    岗位要求：
    1. 5年以上后端开发经验，精通Java或Go语言
    2. 熟悉Spring Boot、MyBatis等主流框架
    3. 精通MySQL、Redis等数据库，有数据库优化经验
    4. 熟悉分布式系统设计，有高并发、高可用系统设计经验
    5. 熟悉Docker、Kubernetes等容器化技术
    6. 有微服务架构设计和实施经验
    7. 良好的沟通能力和团队协作能力
    """

    print("=" * 80)
    print("开始测试面试问题生成...")
    print("=" * 80)

    # 生成面试问题
    questions = await InterviewService.generate_interview_questions(
        resume_data=resume_data,
        job_description=job_description,
        num_questions=5
    )

    print(f"\n生成的问题数量: {len(questions)}")
    print("\n生成的JSON结构:")
    print(json.dumps(questions, ensure_ascii=False, indent=2))

    # 验证JSON结构
    print("\n" + "=" * 80)
    print("验证JSON结构...")
    print("=" * 80)

    required_fields = ["id", "question", "category", "difficulty", "type", "purpose"]
    optional_fields = []

    all_valid = True
    for i, q in enumerate(questions, 1):
        print(f"\n问题 {i}:")
        print(f"  - 字段: {list(q.keys())}")

        # 检查必需字段
        missing_fields = [f for f in required_fields if f not in q]
        if missing_fields:
            print(f"  ❌ 缺少必需字段: {missing_fields}")
            all_valid = False
        else:
            print(f"  ✓ 包含所有必需字段")

        # 检查字段类型
        if "id" in q:
            print(f"  - id 类型: {type(q['id']).__name__} (期望: int)")
        if "question" in q:
            print(f"  - question 类型: {type(q['question']).__name__} (期望: str)")
        if "category" in q:
            print(f"  - category 类型: {type(q['category']).__name__} (期望: str)")
        if "difficulty" in q:
            print(f"  - difficulty 类型: {type(q['difficulty']).__name__} (期望: str)")
        if "type" in q:
            print(f"  - type 类型: {type(q['type']).__name__} (期望: str)")
        if "purpose" in q:
            print(f"  - purpose 类型: {type(q['purpose']).__name__} (期望: str)")

    # 验证是否符合schema定义
    print("\n" + "=" * 80)
    print("与代码中定义的schema对比...")
    print("=" * 80)

    from app.schemas.interview import InterviewQuestion

    schema_fields = set(InterviewQuestion.model_fields.keys())
    print(f"\nInterviewQuestion schema 字段: {schema_fields}")
    print(f"LLM 返回的字段: {set(questions[0].keys()) if questions else set()}")

    schema_diff = set(questions[0].keys()) - schema_fields if questions else set()
    if schema_diff:
        print(f"\n⚠️  LLM 返回了 schema 中未定义的字段: {schema_diff}")
    else:
        print(f"\n✓ LLM 返回的字段都在 schema 定义中")

    # 最终结论
    print("\n" + "=" * 80)
    print("测试结论")
    print("=" * 80)

    if all_valid:
        print("✅ JSON 结构验证通过")
    else:
        print("❌ JSON 结构验证失败")

    return questions


async def test_followup_question():
    """测试追问生成"""

    print("\n" + "=" * 80)
    print("开始测试追问生成...")
    print("=" * 80)

    current_question = "请介绍一下你在阿里巴巴的电商系统项目中使用的技术栈"
    user_answer = "我在项目中使用了Spring Boot作为后端框架，MySQL作为主数据库，Redis用于缓存，Kafka用于消息队列"
    conversation_history = [
        {"role": "interviewer", "content": current_question},
        {"role": "candidate", "content": user_answer}
    ]
    resume_data = {
        "experience": [
            {
                "company": "阿里巴巴",
                "position": "后端开发工程师",
                "description": "负责电商系统的后端开发，使用Spring Boot和MySQL，参与高并发场景的性能优化工作"
            }
        ]
    }

    result = await InterviewService.generate_followup_question(
        current_question=current_question,
        user_answer=user_answer,
        conversation_history=conversation_history,
        resume_data=resume_data
    )

    print(f"\n生成的追问结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 验证字段
    print("\n验证字段:")
    if "type" in result:
        print(f"  ✓ type: {result['type']}")
    if "question" in result:
        print(f"  ✓ question: {result['question']}")
    if "reason" in result:
        print(f"  ✓ reason: {result['reason']}")

    return result


async def main():
    """主测试函数"""
    print("开始测试面试问题生成的LLM服务JSON结构\n")

    # 测试问题生成
    questions = await test_generate_interview_questions()

    # 测试追问生成
    await test_followup_question()

    print("\n" + "=" * 80)
    print("所有测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
