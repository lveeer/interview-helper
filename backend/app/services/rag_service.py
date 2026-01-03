from typing import List, Dict, Any, Optional
import os
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeDocument, VectorChunk
from sqlalchemy import text
import json


class RAGService:
    """RAG 知识库服务"""

    @staticmethod
    async def process_document(
        document_id: int,
        file_path: str,
        db: Session
    ):
        """
        处理知识库文档：切片、向量化、存储

        Args:
            document_id: 文档 ID
            file_path: 文件路径
            db: 数据库会话
        """
        # TODO: 实现文档处理逻辑
        # 1. 读取文档内容
        # 2. 文本切片
        # 3. 向量化（使用 embedding 模型）
        # 4. 存储到数据库

        pass

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[str]:
        """
        将文本切分成小块

        Args:
            text: 原始文本
            chunk_size: 每块大小
            overlap: 重叠大小

        Returns:
            文本块列表
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap

        return chunks

    @staticmethod
    async def search_knowledge(
        query: str,
        user_id: int,
        top_k: int = 5,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库

        Args:
            query: 查询文本
            user_id: 用户 ID
            top_k: 返回结果数量
            db: 数据库会话

        Returns:
            搜索结果列表
        """
        # TODO: 实现向量搜索
        # 1. 将查询文本向量化
        # 2. 使用 pgvector 进行相似度搜索
        # 3. 返回最相关的文本块

        # 临时返回示例数据
        return [
            {
                "content": "这是从知识库检索到的相关内容示例",
                "source": "文档1",
                "score": 0.95
            }
        ]

    @staticmethod
    async def create_embedding(text: str) -> List[float]:
        """
        创建文本的向量嵌入

        Args:
            text: 文本

        Returns:
            向量嵌入
        """
        from app.services.llm_service import get_llm
        llm = await get_llm()
        return await llm.generate_embedding(text)

    @staticmethod
    async def store_chunks(
        document_id: int,
        chunks: List[str],
        db: Session
    ):
        """
        存储文本块到数据库

        Args:
            document_id: 文档 ID
            chunks: 文本块列表
            db: 数据库会话
        """
        for idx, chunk_text in enumerate(chunks):
            # 创建向量嵌入
            embedding = await RAGService.create_embedding(chunk_text)

            # 存储到数据库
            vector_chunk = VectorChunk(
                document_id=document_id,
                chunk_text=chunk_text,
                embedding=embedding,
                chunk_index=idx
            )
            db.add(vector_chunk)

        db.commit()

    @staticmethod
    async def vector_search(
        query_embedding: List[float],
        user_id: int,
        top_k: int = 5,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        使用 pgvector 进行向量搜索

        Args:
            query_embedding: 查询向量
            user_id: 用户 ID
            top_k: 返回结果数量
            db: 数据库会话

        Returns:
            搜索结果列表
        """
        if db is None:
            return []

        try:
            # 使用 pgvector 的余弦相似度搜索
            query = text("""
                SELECT
                    vc.chunk_text,
                    kd.file_name,
                    1 - (vc.embedding <=> :query_vector::vector) as similarity
                FROM vector_chunks vc
                JOIN knowledge_documents kd ON vc.document_id = kd.id
                WHERE kd.user_id = :user_id
                ORDER BY vc.embedding <=> :query_vector::vector
                LIMIT :top_k
            """)

            result = db.execute(
                query,
                {
                    "query_vector": query_embedding,
                    "user_id": user_id,
                    "top_k": top_k
                }
            ).fetchall()

            return [
                {
                    "content": row[0],
                    "source": row[1],
                    "score": float(row[2])
                }
                for row in result
            ]

        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []