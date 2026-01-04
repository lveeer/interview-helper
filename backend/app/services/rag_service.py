from typing import List, Dict, Any, Optional
import os
import re
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
        import os
        from unstructured.partition.auto import partition

        try:
            # 1. 读取文档内容
            print(f"[RAG] 开始处理文档: {file_path}")

            # 使用 unstructured 自动识别文档类型并提取文本
            elements = partition(filename=file_path)

            # 提取文本内容
            text_content = "\n\n".join([str(el) for el in elements])

            # 清理文本
            text_content = RAGService.clean_text(text_content)

            if not text_content or len(text_content.strip()) < 10:
                print(f"[RAG] 文档内容为空或过短: {file_path}")
                return

            # 保存原始内容到数据库
            from app.models.knowledge import KnowledgeDocument
            doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
            if doc:
                doc.content = text_content
                doc.status = "processing"
                db.commit()

            print(f"[RAG] 文档内容长度: {len(text_content)} 字符")

            # 2. 文本切片
            from config import settings
            chunks = RAGService.chunk_text(
                text_content,
                chunk_size=settings.CHUNK_SIZE,
                overlap=settings.CHUNK_OVERLAP
            )

            print(f"[RAG] 切分为 {len(chunks)} 个文本块")

            # 3. 向量化并存储
            await RAGService.store_chunks(document_id, chunks, db)

            # 更新文档状态
            if doc:
                doc.status = "completed"
                doc.chunk_count = len(chunks)
                db.commit()

            print(f"[RAG] 文档处理完成: {file_path}")

        except Exception as e:
            print(f"[RAG] 文档处理失败: {e}")
            import traceback
            traceback.print_exc()

            # 更新文档状态为失败
            try:
                doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
                if doc:
                    doc.status = "failed"
                    doc.error_message = str(e)
                    db.commit()
            except:
                pass

            raise

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本内容

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        return text.strip()

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        将文本切分成小块（按段落优先）

        Args:
            text: 原始文本
            chunk_size: 每块大小
            overlap: 重叠大小

        Returns:
            文本块列表
        """
        chunks = []
        paragraphs = text.split('\n\n')

        current_chunk = ""
        current_size = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_size = len(para)

            # 如果单个段落超过 chunk_size，需要进一步分割
            if para_size > chunk_size:
                # 先保存当前 chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    current_size = 0

                # 按句子分割大段落
                sentences = re.split(r'([。！？!?；;])', para)
                sentences = [''.join(pair) for pair in zip(sentences[::2], sentences[1::2])]

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if current_size + len(sentence) > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                        current_size = len(sentence)
                    else:
                        current_chunk += sentence if not current_chunk else " " + sentence
                        current_size += len(sentence)

            # 如果当前 chunk 加上新段落超过大小
            elif current_size + para_size > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
                current_size = para_size
            else:
                current_chunk += para if not current_chunk else "\n\n" + para
                current_size += para_size

        # 添加最后一个 chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        # 如果没有切分出任何 chunk，使用简单切分
        if not chunks:
            chunks = RAGService.simple_chunk_text(text, chunk_size, overlap)

        return chunks

    @staticmethod
    def simple_chunk_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        简单文本切分（按字符）

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
            chunk = text[start:end].strip()

            if chunk:
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
        try:
            # 1. 将查询文本向量化
            from app.services.llm_service import create_embedding
            query_embedding = await create_embedding(query)

            # 2. 使用 pgvector 进行相似度搜索
            results = await RAGService.vector_search(
                query_embedding=query_embedding,
                user_id=user_id,
                top_k=top_k,
                db=db
            )

            # 3. 返回搜索结果
            return results

        except Exception as e:
            print(f"[RAG] 知识库搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []

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
        from app.services.llm_service import create_embedding

        for idx, chunk_text in enumerate(chunks):
            # 创建向量嵌入
            embedding = await create_embedding(chunk_text)

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
                    vc.id,
                    vc.chunk_text,
                    vc.chunk_index,
                    kd.file_name,
                    kd.id as document_id,
                    1 - (vc.embedding <=> :query_vector::vector) as similarity
                FROM vector_chunks vc
                JOIN knowledge_documents kd ON vc.document_id = kd.id
                WHERE kd.user_id = :user_id
                  AND kd.status = 'completed'
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
                    "id": row[0],
                    "content": row[1],
                    "chunk_index": row[2],
                    "source": row[3],
                    "document_id": row[4],
                    "score": float(row[5])
                }
                for row in result
            ]

        except Exception as e:
            print(f"[RAG] 向量搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    @staticmethod
    async def delete_document_chunks(
        document_id: int,
        db: Session
    ):
        """
        删除文档的所有文本块

        Args:
            document_id: 文档 ID
            db: 数据库会话
        """
        try:
            db.query(VectorChunk).filter(
                VectorChunk.document_id == document_id
            ).delete()
            db.commit()
        except Exception as e:
            print(f"[RAG] 删除文档块失败: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_document_status(
        document_id: int,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        获取文档处理状态

        Args:
            document_id: 文档 ID
            db: 数据库会话

        Returns:
            文档状态信息
        """
        try:
            doc = db.query(KnowledgeDocument).filter(
                KnowledgeDocument.id == document_id
            ).first()

            if not doc:
                return None

            return {
                "id": doc.id,
                "status": doc.status,
                "chunk_count": doc.chunk_count,
                "error_message": doc.error_message
            }

        except Exception as e:
            print(f"[RAG] 获取文档状态失败: {e}")
            return None