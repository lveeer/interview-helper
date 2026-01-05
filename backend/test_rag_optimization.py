#!/usr/bin/env python3
"""
RAG 优化效果测试脚本
测试查询扩展、混合检索、重排序等功能
"""

import asyncio
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.rag_service import RAGService


async def test_query_expansion():
    """测试查询扩展功能"""
    print("\n" + "="*60)
    print("测试 1: 查询扩展（Query Expansion）")
    print("="*60)

    test_queries = [
        "如何优化 Python 程序性能",
        "数据库索引设计原则",
        "微服务架构优势"
    ]

    for query in test_queries:
        print(f"\n原始查询: {query}")
        expanded = await RAGService.expand_query(query, num_expansions=3)
        print(f"扩展查询 ({len(expanded)} 个):")
        for i, q in enumerate(expanded, 1):
            print(f"  {i}. {q}")


async def test_keyword_extraction():
    """测试关键词提取功能"""
    print("\n" + "="*60)
    print("测试 2: 关键词提取（Keyword Extraction）")
    print("="*60)

    test_texts = [
        "如何优化 Python 程序性能",
        "数据库索引设计原则和最佳实践",
        "微服务架构的优势和挑战"
    ]

    for text in test_texts:
        print(f"\n输入文本: {text}")
        keywords = RAGService._extract_keywords(text)
        print(f"提取关键词: {keywords}")


async def test_semantic_boundary_detection():
    """测试语义边界检测功能"""
    print("\n" + "="*60)
    print("测试 3: 语义边界检测（Semantic Boundary Detection）")
    print("="*60)

    test_cases = [
        ("这是第一段内容。", "这是第二段内容。"),
        ("Python 是一门编程语言。", "另外，Java 也是一门编程语言。"),
        ("微服务架构有很多优势。", "然而，它也有一些挑战。"),
    ]

    for current, previous in test_cases:
        is_boundary = RAGService._detect_semantic_boundary(current, previous)
        print(f"\n前一段: {previous}")
        print(f"当前段: {current}")
        print(f"语义边界: {'是' if is_boundary else '否'}")


async def test_chunk_optimization():
    """测试分块优化功能"""
    print("\n" + "="*60)
    print("测试 4: 分块优化（Chunk Optimization）")
    print("="*60)

    test_text = """
Python 是一门高级编程语言，由 Guido van Rossum 于 1991 年首次发布。
它具有简洁明了的语法，支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。

Python 的应用领域非常广泛，包括 Web 开发、数据分析、人工智能、自动化运维等。
在 Web 开发方面，有 Django、Flask 等流行的框架。
在数据分析方面，有 NumPy、Pandas 等强大的库。

另外，Python 在人工智能领域也占据重要地位。
TensorFlow、PyTorch 等深度学习框架都支持 Python。
这使得 Python 成为机器学习和深度学习的首选语言。

然而，Python 也有一些局限性。
由于是解释型语言，其执行速度相对较慢。
但对于大多数应用场景来说，Python 的开发效率优势远大于性能劣势。

总的来说，Python 是一门非常适合初学者和专业人士的编程语言。
它的生态系统丰富，社区活跃，学习资源充足。
无论是用于学术研究还是商业开发，Python 都是一个不错的选择。
"""

    chunks = RAGService.chunk_text(test_text, chunk_size=200, overlap=30)

    print(f"\n原始文本长度: {len(test_text)} 字符")
    print(f"分块数量: {len(chunks)}")
    print("\n分块详情:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- 块 {i} ({len(chunk)} 字符) ---")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)


async def test_rag_search_comparison():
    """测试 RAG 检索对比（优化前 vs 优化后）"""
    print("\n" + "="*60)
    print("测试 5: RAG 检索对比（优化前 vs 优化后）")
    print("="*60)

    # 获取数据库会话
    db_gen = get_db()
    db = next(db_gen)

    try:
        test_query = "如何优化程序性能"
        user_id = 1  # 假设用户 ID 为 1

        print(f"\n测试查询: {test_query}")
        print(f"用户 ID: {user_id}")

        # 测试 1: 仅向量检索（优化前）
        print("\n--- 仅向量检索（优化前） ---")
        from app.services.llm_service import create_embedding
        query_embedding = await create_embedding(test_query)
        results_basic = await RAGService.vector_search(
            query_embedding=query_embedding,
            user_id=user_id,
            top_k=5,
            db=db
        )

        for i, result in enumerate(results_basic, 1):
            print(f"\n结果 {i} (分数: {result['score']:.3f}):")
            print(f"  内容: {result['content'][:80]}...")
            print(f"  来源: {result['source']}")

        # 测试 2: 完整优化（查询扩展 + 混合检索 + 重排序）
        print("\n--- 完整优化（查询扩展 + 混合检索 + 重排序） ---")
        results_optimized = await RAGService.search_knowledge(
            query=test_query,
            user_id=user_id,
            top_k=5,
            use_query_expansion=True,
            use_hybrid_search=True,
            use_reranking=True,
            db=db
        )

        for i, result in enumerate(results_optimized, 1):
            print(f"\n结果 {i} (分数: {result['score']:.3f}):")
            print(f"  内容: {result['content'][:80]}...")
            print(f"  来源: {result['source']}")

        # 对比结果
        print("\n--- 对比总结 ---")
        print(f"优化前结果数: {len(results_basic)}")
        print(f"优化后结果数: {len(results_optimized)}")
        print(f"优化前平均分数: {sum(r['score'] for r in results_basic)/len(results_basic):.3f}")
        print(f"优化后平均分数: {sum(r['score'] for r in results_optimized)/len(results_optimized):.3f}")

    finally:
        db.close()


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("RAG 优化效果测试")
    print("="*60)

    try:
        # 测试 1: 查询扩展
        await test_query_expansion()

        # 测试 2: 关键词提取
        await test_keyword_extraction()

        # 测试 3: 语义边界检测
        await test_semantic_boundary_detection()

        # 测试 4: 分块优化
        await test_chunk_optimization()

        # 测试 5: RAG 检索对比
        await test_rag_search_comparison()

        print("\n" + "="*60)
        print("所有测试完成！")
        print("="*60)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())