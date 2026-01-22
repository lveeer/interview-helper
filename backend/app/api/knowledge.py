from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.knowledge import KnowledgeDocument, QueryHistory
from app.schemas.knowledge import (
    KnowledgeDocumentResponse,
    KnowledgeQuery,
    DocumentPreviewResponse,
    CategoryUpdateRequest,
    QueryHistoryRequest,
    ChunkStrategyUpdateRequest,
    RecallTestCaseCreate,
    RecallTestCaseResponse,
    RecallTestRunRequest,
    RecallTestResultResponse,
    RecallTestSummaryResponse
)
from app.api.auth import get_current_user
import os
from config import settings

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload_knowledge(
    file: UploadFile = File(...),
    chunk_strategy: str = Query("semantic", description="分段策略：semantic(语义分段), parent_child(父子分段), recursive(递归分段)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传知识库文档"""
    from app.schemas.common import ApiResponse

    # 验证分段策略
    valid_strategies = ["semantic", "parent_child", "recursive"]
    if chunk_strategy not in valid_strategies:
        raise HTTPException(
            status_code=400,
            detail=f"分段策略必须是以下之一: {', '.join(valid_strategies)}"
        )

    # 保存文件
    upload_dir = os.path.join(settings.UPLOAD_DIR, "knowledge")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{current_user.id}_{file.filename}")

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 创建知识库文档记录
    db_doc = KnowledgeDocument(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        file_type=os.path.splitext(file.filename)[1][1:],
        chunk_strategy=chunk_strategy
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # 调用 RAG 服务处理文档
    try:
        from app.services.rag_service import RAGService
        await RAGService.process_document(db_doc.id, file_path, db, chunk_strategy=chunk_strategy)
    except Exception as e:
        print(f"知识库文档处理失败: {e}")
        # 处理失败不影响文档上传

    return ApiResponse(
        code=201,
        message="文档上传成功",
        data=KnowledgeDocumentResponse.model_validate(db_doc)
    )


@router.get("/")
async def get_knowledge_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有知识库文档"""
    from app.schemas.common import ListResponse

    docs = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.user_id == current_user.id
    ).all()
    return ListResponse(
        code=200,
        message="获取成功",
        data=[KnowledgeDocumentResponse.model_validate(d) for d in docs],
        total=len(docs)
    )


@router.delete("/{doc_id}")
async def delete_knowledge_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除知识库文档"""
    from app.schemas.common import SuccessResponse

    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(
            status_code=404,
            detail="文档不存在"
        )
    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    # 删除数据库记录
    db.delete(doc)
    db.commit()
    return SuccessResponse()


@router.post("/query")
async def query_knowledge(
    query: KnowledgeQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询知识库（支持查询扩展、混合检索、重排序）"""
    from app.services.rag_service import RAGService
    from app.schemas.common import ApiResponse

    # 使用配置默认值或用户指定的值
    use_query_expansion = query.use_query_expansion if query.use_query_expansion is not None else settings.ENABLE_QUERY_EXPANSION
    use_hybrid_search = query.use_hybrid_search if query.use_hybrid_search is not None else settings.ENABLE_HYBRID_SEARCH
    use_reranking = query.use_reranking if query.use_reranking is not None else settings.ENABLE_RERANKING

    results = await RAGService.search_knowledge(
        query.query,
        current_user.id,
        query.top_k,
        use_query_expansion=use_query_expansion,
        use_hybrid_search=use_hybrid_search,
        use_reranking=use_reranking,
        db=db
    )

    # 自动保存查询历史
    try:
        # 检查是否已存在相同的查询（避免重复保存）
        existing = db.query(QueryHistory).filter(
            QueryHistory.user_id == current_user.id,
            QueryHistory.query_text == query.query
        ).first()

        if existing:
            # 如果已存在，更新时间戳
            from sqlalchemy.sql import func
            existing.created_at = func.now()
            db.commit()
        else:
            # 创建新的查询历史记录
            new_history = QueryHistory(
                user_id=current_user.id,
                query_text=query.query
            )
            db.add(new_history)
            db.commit()

            # 检查是否超过10条记录，如果超过则删除最旧的
            history_count = db.query(QueryHistory).filter(
                QueryHistory.user_id == current_user.id
            ).count()

            if history_count > 10:
                # 获取最旧的记录并删除
                oldest = db.query(QueryHistory).filter(
                    QueryHistory.user_id == current_user.id
                ).order_by(QueryHistory.created_at.asc()).first()
                if oldest:
                    db.delete(oldest)
                    db.commit()
    except Exception as e:
        # 保存查询历史失败不影响查询结果
        print(f"保存查询历史失败: {e}")

    return ApiResponse(
        code=200,
        message="查询成功",
        data={
            "query": query.query,
            "results": results,
            "config": {
                "use_query_expansion": use_query_expansion,
                "use_hybrid_search": use_hybrid_search,
                "use_reranking": use_reranking
            }
        }
    )


@router.get("/query/history")
async def get_query_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取查询历史记录"""
    from app.schemas.common import ApiResponse

    # 获取最近的10条查询历史，按时间倒序
    history = db.query(QueryHistory).filter(
        QueryHistory.user_id == current_user.id
    ).order_by(QueryHistory.created_at.desc()).limit(10).all()

    # 提取查询文本
    queries = [h.query_text for h in history]

    return ApiResponse(
        code=200,
        message="success",
        data=queries
    )


@router.delete("/query/history")
async def clear_query_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空查询历史记录"""
    from app.schemas.common import SuccessResponse

    # 删除当前用户的所有查询历史
    db.query(QueryHistory).filter(
        QueryHistory.user_id == current_user.id
    ).delete()
    db.commit()

    return SuccessResponse(message="历史记录已清空")


@router.post("/query/history")
async def save_query_history(
    history_request: QueryHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存查询历史记录"""
    from app.schemas.common import SuccessResponse

    # 检查是否已存在相同的查询（避免重复保存）
    existing = db.query(QueryHistory).filter(
        QueryHistory.user_id == current_user.id,
        QueryHistory.query_text == history_request.query
    ).first()

    if existing:
        # 如果已存在，更新时间戳
        from sqlalchemy.sql import func
        existing.created_at = func.now()
        db.commit()
    else:
        # 创建新的查询历史记录
        new_history = QueryHistory(
            user_id=current_user.id,
            query_text=history_request.query
        )
        db.add(new_history)
        db.commit()

        # 检查是否超过10条记录，如果超过则删除最旧的
        history_count = db.query(QueryHistory).filter(
            QueryHistory.user_id == current_user.id
        ).count()

        if history_count > 10:
            # 获取最旧的记录并删除
            oldest = db.query(QueryHistory).filter(
                QueryHistory.user_id == current_user.id
            ).order_by(QueryHistory.created_at.asc()).first()
            if oldest:
                db.delete(oldest)
                db.commit()

    return SuccessResponse(message="查询记录已保存")


@router.get("/{doc_id}/preview")
async def get_document_preview(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取文档分段预览内容"""
    from app.schemas.common import ApiResponse
    from app.models.knowledge import VectorChunk

    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="文档不存在"
        )

    # 获取文档的所有分段，按 chunk_index 排序
    chunks = db.query(VectorChunk).filter(
        VectorChunk.document_id == doc_id
    ).order_by(VectorChunk.chunk_index).all()

    # 如果没有分段，返回原始内容
    if not chunks:
        content = doc.content or ""
        max_length = 5000
        if len(content) > max_length:
            content = content[:max_length] + "\n\n... (内容过长，已截断)"
        return ApiResponse(
            code=200,
            message="success",
            data={
                "chunks": [{"index": 0, "content": content}],
                "total_chunks": 1,
                "chunk_strategy": doc.chunk_strategy
            }
        )

    # 返回分段内容列表
    chunk_list = [
        {
            "index": chunk.chunk_index,
            "content": chunk.chunk_text,
            "parent_chunk_id": chunk.parent_chunk_id
        }
        for chunk in chunks
    ]

    return ApiResponse(
        code=200,
        message="success",
        data={
            "chunks": chunk_list,
            "total_chunks": len(chunks),
            "chunk_strategy": doc.chunk_strategy
        }
    )


@router.put("/{doc_id}/category")
async def update_document_category(
    doc_id: int,
    category_update: CategoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新文档分类"""
    from app.schemas.common import SuccessResponse

    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="文档不存在"
        )

    doc.category = category_update.category
    db.commit()

    return SuccessResponse(message="分类更新成功")


@router.put("/{doc_id}/chunk-strategy")
async def update_document_chunk_strategy(
    doc_id: int,
    strategy_update: ChunkStrategyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新文档分段策略并重新处理"""
    from app.schemas.common import ApiResponse
    from app.services.rag_service import RAGService

    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="文档不存在"
        )

    # 删除旧的文本块
    await RAGService.delete_document_chunks(doc_id, db)

    # 更新分段策略
    doc.chunk_strategy = strategy_update.chunk_strategy
    doc.status = "processing"
    doc.chunk_count = 0
    db.commit()

    # 重新处理文档
    try:
        await RAGService.process_document(doc_id, doc.file_path, db, chunk_strategy=strategy_update.chunk_strategy)
    except Exception as e:
        print(f"文档重新处理失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"文档重新处理失败: {str(e)}"
        )

    return ApiResponse(
        code=200,
        message="分段策略更新成功，文档已重新处理",
        data=KnowledgeDocumentResponse.model_validate(doc)
    )


# ==================== 召回测试相关接口 ====================

@router.post("/recall-test/cases", status_code=201)
async def create_recall_test_case(
    test_case: RecallTestCaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建召回测试用例"""
    from app.services.recall_test_service import RecallTestService
    from app.schemas.common import ApiResponse

    created_case = RecallTestService.create_test_case(
        user_id=current_user.id,
        query=test_case.query,
        expected_chunk_ids=test_case.expected_chunk_ids,
        description=test_case.description,
        db=db
    )

    return ApiResponse(
        code=201,
        message="测试用例创建成功",
        data=RecallTestCaseResponse.model_validate(created_case)
    )


@router.get("/recall-test/cases")
async def get_recall_test_cases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有召回测试用例"""
    from app.services.recall_test_service import RecallTestService
    from app.schemas.common import ListResponse

    test_cases = RecallTestService.get_test_cases(current_user.id, db)

    return ListResponse(
        code=200,
        message="获取成功",
        data=[RecallTestCaseResponse.model_validate(tc) for tc in test_cases],
        total=len(test_cases)
    )


@router.delete("/recall-test/cases/{test_case_id}")
async def delete_recall_test_case(
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除召回测试用例"""
    from app.services.recall_test_service import RecallTestService
    from app.schemas.common import SuccessResponse

    success = RecallTestService.delete_test_case(test_case_id, current_user.id, db)
    if not success:
        raise HTTPException(status_code=404, detail="测试用例不存在")

    return SuccessResponse(message="测试用例删除成功")


@router.post("/recall-test/run", status_code=201)
async def run_recall_test(
    test_request: RecallTestRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行召回测试"""
    from app.services.recall_test_service import RecallTestService
    from app.schemas.common import ApiResponse
    from config import settings

    # 使用配置默认值或用户指定的值
    use_query_expansion = test_request.use_query_expansion if test_request.use_query_expansion is not None else settings.ENABLE_QUERY_EXPANSION
    use_hybrid_search = test_request.use_hybrid_search if test_request.use_hybrid_search is not None else settings.ENABLE_HYBRID_SEARCH
    use_reranking = test_request.use_reranking if test_request.use_reranking is not None else settings.ENABLE_RERANKING

    test_result = await RecallTestService.run_test(
        user_id=current_user.id,
        test_case_id=test_request.test_case_id,
        top_k=test_request.top_k,
        use_query_expansion=use_query_expansion,
        use_hybrid_search=use_hybrid_search,
        use_reranking=use_reranking,
        db=db
    )

    return ApiResponse(
        code=201,
        message="测试执行成功",
        data=RecallTestResultResponse.model_validate(test_result)
    )


@router.get("/recall-test/results")
async def get_recall_test_results(
    test_case_id: int = Query(None, description="测试用例 ID，不传则返回所有测试结果"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取召回测试结果"""
    from app.services.recall_test_service import RecallTestService
    from app.schemas.common import ListResponse

    results = RecallTestService.get_test_results(current_user.id, test_case_id, db)

    return ListResponse(
        code=200,
        message="获取成功",
        data=[RecallTestResultResponse.model_validate(r) for r in results],
        total=len(results)
    )


@router.get("/recall-test/summary")
async def get_recall_test_summary(
    test_case_id: int = Query(None, description="测试用例 ID，不传则返回所有测试的汇总"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取召回测试汇总统计"""
    from app.services.recall_test_service import RecallTestService
    from app.schemas.common import ApiResponse

    summary = RecallTestService.get_test_summary(current_user.id, test_case_id, db)

    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "total_tests": summary["total_tests"],
            "avg_recall": summary["avg_recall"],
            "avg_precision": summary["avg_precision"],
            "avg_f1_score": summary["avg_f1_score"],
            "avg_mrr": summary["avg_mrr"],
            "results": [RecallTestResultResponse.model_validate(r) for r in summary["results"]]
        }
    )