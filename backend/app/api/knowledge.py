from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.knowledge import KnowledgeDocument
from app.schemas.knowledge import KnowledgeDocumentResponse, KnowledgeQuery
from app.api.auth import get_current_user
import os
from config import settings

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload_knowledge(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传知识库文档"""
    from app.schemas.common import ApiResponse

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
        file_type=os.path.splitext(file.filename)[1][1:]
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # 调用 RAG 服务处理文档
    try:
        from app.services.rag_service import RAGService
        await RAGService.process_document(db_doc.id, file_path, db)
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