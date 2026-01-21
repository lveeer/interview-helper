"""
测试异步修复是否有效
验证 LLM 服务和 RAG 服务是否真正异步
"""
import asyncio
import time
from app.services.llm_service import get_llm
from app.services.rag_service import RAGService
from app.core.database import AsyncSessionLocal


async def test_llm_async():
    """测试 LLM 服务是否真正异步"""
    print("\n=== 测试 LLM 服务异步性 ===")
    llm = await get_llm()

    async def task1():
        start = time.time()
        try:
            result = await llm.generate_text("简单回答：1+1等于几？", temperature=0.1)
            elapsed = time.time() - start
            print(f"任务 1 完成，耗时: {elapsed:.2f}秒")
            return elapsed
        except Exception as e:
            print(f"任务 1 失败: {e}")
            return 0

    async def task2():
        start = time.time()
        try:
            result = await llm.generate_text("简单回答：2+2等于几？", temperature=0.1)
            elapsed = time.time() - start
            print(f"任务 2 完成，耗时: {elapsed:.2f}秒")
            return elapsed
        except Exception as e:
            print(f"任务 2 失败: {e}")
            return 0

    # 并发执行两个任务
    start = time.time()
    elapsed1, elapsed2 = await asyncio.gather(task1(), task2())
    total_elapsed = time.time() - start

    print(f"总耗时: {total_elapsed:.2f}秒")
    print(f"任务 1 耗时: {elapsed1:.2f}秒")
    print(f"任务 2 耗时: {elapsed2:.2f}秒")

    # 如果总耗时接近两个任务中较长的那个，说明是真正异步的
    # 如果总耗时接近两个任务之和，说明是阻塞的
    if total_elapsed < max(elapsed1, elapsed2) * 1.2:
        print("✅ LLM 服务是真正异步的（并发执行）")
        return True
    else:
        print("❌ LLM 服务仍然是阻塞的（串行执行）")
        return False


async def test_rag_async():
    """测试 RAG 服务是否真正异步"""
    print("\n=== 测试 RAG 服务异步性 ===")

    async with AsyncSessionLocal() as db:
        async def task1():
            start = time.time()
            try:
                results = await RAGService.search_knowledge(
                    query="Python 编程",
                    user_id=1,
                    top_k=3,
                    use_query_expansion=False,
                    use_hybrid_search=False,
                    use_reranking=False,
                    db=db
                )
                elapsed = time.time() - start
                print(f"任务 1 完成，耗时: {elapsed:.2f}秒，结果数: {len(results)}")
                return elapsed
            except Exception as e:
                print(f"任务 1 失败: {e}")
                return 0

        async def task2():
            start = time.time()
            try:
                results = await RAGService.search_knowledge(
                    query="JavaScript 编程",
                    user_id=1,
                    top_k=3,
                    use_query_expansion=False,
                    use_hybrid_search=False,
                    use_reranking=False,
                    db=db
                )
                elapsed = time.time() - start
                print(f"任务 2 完成，耗时: {elapsed:.2f}秒，结果数: {len(results)}")
                return elapsed
            except Exception as e:
                print(f"任务 2 失败: {e}")
                return 0

        # 并发执行两个任务
        start = time.time()
        elapsed1, elapsed2 = await asyncio.gather(task1(), task2())
        total_elapsed = time.time() - start

        print(f"总耗时: {total_elapsed:.2f}秒")
        print(f"任务 1 耗时: {elapsed1:.2f}秒")
        print(f"任务 2 耗时: {elapsed2:.2f}秒")

        # 如果总耗时接近两个任务中较长的那个，说明是真正异步的
        if total_elapsed < max(elapsed1, elapsed2) * 1.2:
            print("✅ RAG 服务是真正异步的（并发执行）")
            return True
        else:
            print("❌ RAG 服务仍然是阻塞的（串行执行）")
            return False


async def main():
    print("=" * 50)
    print("测试异步修复是否有效")
    print("=" * 50)

    llm_ok = await test_llm_async()
    rag_ok = await test_rag_async()

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"LLM 服务异步性: {'✅ 通过' if llm_ok else '❌ 失败'}")
    print(f"RAG 服务异步性: {'✅ 通过' if rag_ok else '❌ 失败'}")

    if llm_ok and rag_ok:
        print("\n🎉 所有测试通过！异步修复成功！")
    else:
        print("\n⚠️  部分测试失败，需要进一步检查")


if __name__ == "__main__":
    asyncio.run(main())
