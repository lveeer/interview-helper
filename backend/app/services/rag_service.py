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

        try:
            # 1. 读取文档内容
            print(f"[RAG] 开始处理文档: {file_path}")

            # 根据文件类型选择不同的处理方法
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                # 使用 pypdf 处理 PDF
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n\n"
            elif file_ext in ['.docx', '.doc']:
                # 使用 python-docx 处理 Word 文档
                from docx import Document
                doc = Document(file_path)
                text_content = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            else:
                # 其他文本文件直接读取
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()

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
        将文本切分成小块（按段落优先，智能语义边界检测）

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

            # 检测语义边界
            is_new_topic = RAGService._detect_semantic_boundary(para, current_chunk)

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

            # 如果检测到新主题或当前 chunk 加上新段落超过大小
            elif is_new_topic or current_size + para_size > chunk_size:
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

        # 动态调整块大小，确保每个块都在合理范围内
        chunks = RAGService._adjust_chunk_sizes(chunks, chunk_size)

        return chunks

    @staticmethod
    def _detect_semantic_boundary(
        current_para: str,
        previous_chunk: str
    ) -> bool:
        """
        检测语义边界（新主题开始）

        Args:
            current_para: 当前段落
            previous_chunk: 前一个文本块

        Returns:
            是否为新主题
        """
        if not previous_chunk:
            return False

        # 检测主题转换关键词
        transition_keywords = [
            '另外', '此外', '再者', '接下来', '然后', '此外',
            '另一方面', '同时', '与此同时', '另外一方面',
            '此外还有', '不仅如此', '更重要的是',
            '首先', '其次', '再次', '最后',
            '第一', '第二', '第三', '第四',
            '总之', '综上所述', '因此', '所以',
            '然而', '但是', '不过', '相反',
            '例如', '比如', '举例来说'
        ]

        # 检查段落开头是否包含主题转换词
        for keyword in transition_keywords:
            if current_para.startswith(keyword):
                return True

        # 检查段落长度差异（如果新段落很短，可能是新主题）
        if len(previous_chunk) > 300 and len(current_para) < 100:
            return True

        return False

    @staticmethod
    def _adjust_chunk_sizes(
        chunks: List[str],
        target_size: int
    ) -> List[str]:
        """
        动态调整块大小，确保每个块都在合理范围内

        Args:
            chunks: 文本块列表
            target_size: 目标块大小

        Returns:
            调整后的文本块列表
        """
        adjusted_chunks = []

        for chunk in chunks:
            # 如果块太大，进一步分割
            if len(chunk) > target_size * 1.5:
                sub_chunks = RAGService.simple_chunk_text(chunk, target_size, 0)
                adjusted_chunks.extend(sub_chunks)
            # 如果块太小，尝试合并
            elif len(chunk) < target_size * 0.3 and adjusted_chunks:
                # 合并到前一个块
                last_chunk = adjusted_chunks[-1]
                if len(last_chunk) + len(chunk) < target_size * 1.2:
                    adjusted_chunks[-1] = last_chunk + "\n\n" + chunk
                else:
                    adjusted_chunks.append(chunk)
            else:
                adjusted_chunks.append(chunk)

        return adjusted_chunks

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
    async def expand_query(
        query: str,
        num_expansions: int = 3
    ) -> List[str]:
        """
        使用 LLM 扩展查询，生成多个查询变体

        Args:
            query: 原始查询
            num_expansions: 生成的扩展查询数量

        Returns:
            扩展后的查询列表（包含原始查询）
        """
        try:
            from app.services.llm_service import get_llm

            llm = await get_llm()

            prompt = f"""请为以下查询生成 {num_expansions} 个不同的查询变体，以提高检索的召回率。

原始查询：{query}

要求：
1. 查询变体应该保持原意，但使用不同的表达方式
2. 可以包含同义词、相关概念、更具体或更宽泛的表述
3. 每个变体应该简洁明了
4. 只返回查询变体，每行一个，不要编号

例如：
原始查询：如何优化 Python 程序性能
扩展查询：
Python 代码性能优化技巧
提升 Python 运行速度的方法
Python 性能调优最佳实践

请生成 {num_expansions} 个查询变体："""

            response = await llm.generate_text(prompt, temperature=0.7)

            # 解析响应，提取查询变体
            expanded_queries = [query]  # 包含原始查询
            lines = [line.strip() for line in response.split('\n') if line.strip()]

            for line in lines[:num_expansions]:
                # 移除编号（如果有）
                cleaned = re.sub(r'^\d+[\.\、]\s*', '', line)
                if cleaned and cleaned not in expanded_queries:
                    expanded_queries.append(cleaned)

            print(f"[RAG] 查询扩展: {len(expanded_queries)} 个查询变体")
            for i, q in enumerate(expanded_queries):
                print(f"  {i+1}. {q}")

            return expanded_queries

        except Exception as e:
            print(f"[RAG] 查询扩展失败: {e}")
            # 失败时返回原始查询
            return [query]

    @staticmethod
    async def search_knowledge(
        query: str,
        user_id: int,
        top_k: int = 5,
        use_query_expansion: bool = True,
        use_hybrid_search: bool = True,
        use_reranking: bool = True,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库（支持查询扩展、混合检索、重排序）

        Args:
            query: 查询文本
            user_id: 用户 ID
            top_k: 返回结果数量
            use_query_expansion: 是否使用查询扩展
            use_hybrid_search: 是否使用混合检索
            use_reranking: 是否使用重排序
            db: 数据库会话

        Returns:
            搜索结果列表
        """
        try:
            # 1. 查询扩展（可选）
            queries = [query]
            if use_query_expansion:
                queries = await RAGService.expand_query(query, num_expansions=3)

            # 2. 混合检索（向量 + 关键词）
            all_results = []
            if use_hybrid_search:
                # 向量检索
                vector_results = await RAGService._vector_search_multiple(queries, user_id, top_k * 2, db)
                all_results.extend(vector_results)

                # 关键词检索
                keyword_results = await RAGService._keyword_search(query, user_id, top_k * 2, db)
                all_results.extend(keyword_results)

                # 合并并去重
                all_results = RAGService._merge_results(all_results)
            else:
                # 仅向量检索
                from app.services.llm_service import create_embedding
                query_embedding = await create_embedding(query)
                all_results = await RAGService.vector_search(
                    query_embedding=query_embedding,
                    user_id=user_id,
                    top_k=top_k * 2,
                    db=db
                )

            # 3. 重排序（可选）
            if use_reranking and len(all_results) > top_k:
                all_results = await RAGService._rerank_results(query, all_results, top_k)
            else:
                # 截取 top_k
                all_results = all_results[:top_k]

            # 4. 返回搜索结果
            return all_results

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
    async def _vector_search_multiple(
        queries: List[str],
        user_id: int,
        top_k: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        对多个查询进行向量检索并合并结果

        Args:
            queries: 查询列表
            user_id: 用户 ID
            top_k: 返回结果数量
            db: 数据库会话

        Returns:
            搜索结果列表
        """
        from app.services.llm_service import create_embedding

        all_results = []

        for query in queries:
            try:
                query_embedding = await create_embedding(query)
                results = await RAGService.vector_search(
                    query_embedding=query_embedding,
                    user_id=user_id,
                    top_k=top_k,
                    db=db
                )
                all_results.extend(results)
            except Exception as e:
                print(f"[RAG] 向量检索失败: {query} - {e}")
                continue

        return all_results

    @staticmethod
    async def _keyword_search(
        query: str,
        user_id: int,
        top_k: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        关键词检索（使用全文搜索）

        Args:
            query: 查询文本
            user_id: 用户 ID
            top_k: 返回结果数量
            db: 数据库会话

        Returns:
            搜索结果列表
        """
        if db is None:
            return []

        try:
            # 提取关键词
            keywords = RAGService._extract_keywords(query)

            if not keywords:
                return []

            # 构建全文搜索查询
            keyword_pattern = '|'.join(keywords)

            sql = f"""
                SELECT
                    vc.id,
                    vc.chunk_text,
                    vc.chunk_index,
                    kd.file_name,
                    kd.id as document_id,
                    0.5 as similarity
                FROM vector_chunks vc
                JOIN knowledge_documents kd ON vc.document_id = kd.id
                WHERE kd.user_id = {user_id}
                  AND kd.status = 'completed'
                  AND vc.chunk_text ~* '{keyword_pattern}'
                LIMIT {top_k}
            """

            result = db.execute(text(sql)).fetchall()

            # 计算关键词匹配分数
            results = []
            for row in result:
                chunk_text = row[1]
                match_count = sum(1 for kw in keywords if kw.lower() in chunk_text.lower())
                score = 0.5 + (match_count / len(keywords)) * 0.5

                results.append({
                    "id": row[0],
                    "content": row[1],
                    "chunk_index": row[2],
                    "source": row[3],
                    "document_id": row[4],
                    "score": score
                })

            return results

        except Exception as e:
            print(f"[RAG] 关键词检索失败: {e}")
            return []

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """
        从文本中提取关键词

        Args:
            text: 输入文本

        Returns:
            关键词列表
        """
        # 移除停用词
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                     '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
                     '自己', '这', '那', '什么', '怎么', '如何', '为什么', '吗', '呢', '啊', '吧'}

        # 简单分词（按空格和标点）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)

        # 过滤停用词和短词
        keywords = [
            word for word in words
            if len(word) > 1 and word not in stopwords
        ]

        return keywords

    @staticmethod
    def _merge_results(
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        合并并去重搜索结果

        Args:
            results: 搜索结果列表

        Returns:
            合并后的结果列表
        """
        # 按 chunk_id 去重，保留最高分数
        seen = {}
        for result in results:
            chunk_id = result['id']
            if chunk_id not in seen or result['score'] > seen[chunk_id]['score']:
                seen[chunk_id] = result

        # 按分数排序
        merged = sorted(seen.values(), key=lambda x: x['score'], reverse=True)

        return merged

    @staticmethod
    async def _rerank_results(
        query: str,
        results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        使用 LLM 对搜索结果进行重排序

        Args:
            query: 原始查询
            results: 搜索结果列表
            top_k: 返回结果数量

        Returns:
            重排序后的结果列表
        """
        try:
            from app.services.llm_service import get_llm

            llm = await get_llm()

            # 构建重排序 prompt
            candidates_text = ""
            for i, result in enumerate(results[:top_k * 2]):  # 只重排序前 2*top_k 个结果
                candidates_text += f"\n{i+1}. {result['content']}\n"

            prompt = f"""请根据查询内容，对以下候选文档片段进行相关性评分。

查询：{query}

候选文档片段：
{candidates_text}

请评估每个片段与查询的相关性，并返回一个 JSON 数组，包含以下字段：
- index: 片段编号（1-{len(results[:top_k * 2])}）
- score: 相关性分数（0-1，保留3位小数）
- reason: 评分理由（简短说明）

只返回 JSON 数组，不要其他内容。"""

            response = await llm.generate_text(prompt, temperature=0.3)

            # 解析响应
            import json
            rerank_scores = json.loads(response)

            # 应用重排序分数
            for score_info in rerank_scores:
                idx = score_info.get('index', 0) - 1
                if 0 <= idx < len(results):
                    # 混合原始分数和重排序分数
                    original_score = results[idx]['score']
                    rerank_score = score_info.get('score', 0.5)
                    results[idx]['score'] = (original_score * 0.3 + rerank_score * 0.7)

            # 重新排序
            results = sorted(results, key=lambda x: x['score'], reverse=True)

            print(f"[RAG] 重排序完成，返回前 {top_k} 个结果")
            return results[:top_k]

        except Exception as e:
            print(f"[RAG] 重排序失败: {e}")
            # 失败时返回原始排序
            return results[:top_k]

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
            # 将向量转换为字符串格式
            vector_str = f"[{','.join(map(str, query_embedding))}]"

            # 使用 pgvector 的余弦相似度搜索
            # 注意: 使用字符串格式化来避免参数绑定问题
            sql = f"""
                SELECT
                    vc.id,
                    vc.chunk_text,
                    vc.chunk_index,
                    kd.file_name,
                    kd.id as document_id,
                    1 - (vc.embedding <=> '{vector_str}'::vector) as similarity
                FROM vector_chunks vc
                JOIN knowledge_documents kd ON vc.document_id = kd.id
                WHERE kd.user_id = {user_id}
                  AND kd.status = 'completed'
                ORDER BY vc.embedding <=> '{vector_str}'::vector
                LIMIT {top_k}
            """

            result = db.execute(text(sql)).fetchall()

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