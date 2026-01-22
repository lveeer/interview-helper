"""召回测试服务"""
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.knowledge import RecallTestCase, RecallTestResult, VectorChunk
from app.schemas.knowledge import RecallTestResultResponse
from config import settings


class RecallTestService:
    """召回测试服务类"""

    @staticmethod
    def create_test_case(
        user_id: int,
        query: str,
        expected_chunk_ids: List[int],
        description: str,
        db: Session
    ) -> RecallTestCase:
        """创建召回测试用例"""
        test_case = RecallTestCase(
            user_id=user_id,
            query=query,
            expected_chunk_ids=json.dumps(expected_chunk_ids),
            description=description
        )
        db.add(test_case)
        db.commit()
        db.refresh(test_case)
        return test_case

    @staticmethod
    def get_test_cases(user_id: int, db: Session) -> List[RecallTestCase]:
        """获取用户的所有测试用例"""
        return db.query(RecallTestCase).filter(
            RecallTestCase.user_id == user_id
        ).order_by(RecallTestCase.created_at.desc()).all()

    @staticmethod
    def delete_test_case(test_case_id: int, user_id: int, db: Session) -> bool:
        """删除测试用例"""
        test_case = db.query(RecallTestCase).filter(
            RecallTestCase.id == test_case_id,
            RecallTestCase.user_id == user_id
        ).first()
        if not test_case:
            return False
        # 删除相关的测试结果
        db.query(RecallTestResult).filter(
            RecallTestResult.test_case_id == test_case_id
        ).delete()
        db.delete(test_case)
        db.commit()
        return True

    @staticmethod
    def calculate_metrics(
        retrieved_ids: List[int],
        expected_ids: List[int]
    ) -> Dict[str, float]:
        """
        计算召回测试指标
        - recall: 召回率 = 命中的期望分段数 / 总期望分段数
        - precision: 精确率 = 命中的期望分段数 / 总召回分段数
        - f1_score: F1 分数
        - mrr: 平均倒数排名
        """
        if not expected_ids:
            return {"recall": 0, "precision": 0, "f1_score": 0, "mrr": 0}

        # 计算命中的分段
        hit_count = 0
        mrr_sum = 0
        for i, chunk_id in enumerate(retrieved_ids):
            if chunk_id in expected_ids:
                hit_count += 1
                # 第一次命中的倒数排名
                if mrr_sum == 0:
                    mrr_sum = 1 / (i + 1)

        # 召回率
        recall = hit_count / len(expected_ids) if expected_ids else 0

        # 精确率
        precision = hit_count / len(retrieved_ids) if retrieved_ids else 0

        # F1 分数
        if recall + precision > 0:
            f1_score = 2 * recall * precision / (recall + precision)
        else:
            f1_score = 0

        # MRR
        mrr = mrr_sum if mrr_sum > 0 else 0

        return {
            "recall": recall,
            "precision": precision,
            "f1_score": f1_score,
            "mrr": mrr
        }

    @staticmethod
    async def run_test(
        user_id: int,
        test_case_id: int,
        top_k: int,
        use_query_expansion: bool,
        use_hybrid_search: bool,
        use_reranking: bool,
        db: Session
    ) -> RecallTestResult:
        """
        执行召回测试
        """
        # 获取测试用例
        test_case = db.query(RecallTestCase).filter(
            RecallTestCase.id == test_case_id,
            RecallTestCase.user_id == user_id
        ).first()
        if not test_case:
            raise ValueError("测试用例不存在")

        # 执行检索
        from app.services.rag_service import RAGService
        results = await RAGService.search_knowledge(
            query=test_case.query,
            user_id=user_id,
            top_k=top_k,
            use_query_expansion=use_query_expansion,
            use_hybrid_search=use_hybrid_search,
            use_reranking=use_reranking,
            db=db
        )

        # 提取召回的分段 ID 和分数
        retrieved_ids = []
        retrieved_scores = []
        for result in results:
            chunk_id = result.get("chunk_id")
            score = result.get("score", 0)
            if chunk_id:
                retrieved_ids.append(chunk_id)
                retrieved_scores.append(score)

        # 解析期望的分段 ID
        expected_ids = json.loads(test_case.expected_chunk_ids)

        # 计算指标
        metrics = RecallTestService.calculate_metrics(retrieved_ids, expected_ids)

        # 保存测试结果
        test_result = RecallTestResult(
            user_id=user_id,
            test_case_id=test_case_id,
            retrieved_chunk_ids=json.dumps(retrieved_ids),
            retrieved_scores=json.dumps(retrieved_scores),
            recall=int(metrics["recall"] * 100),  # 转换为百分比
            precision=int(metrics["precision"] * 100),
            f1_score=int(metrics["f1_score"] * 100),
            mrr=int(metrics["mrr"] * 100),
            use_query_expansion=1 if use_query_expansion else 0,
            use_hybrid_search=1 if use_hybrid_search else 0,
            use_reranking=1 if use_reranking else 0,
            top_k=top_k
        )
        db.add(test_result)
        db.commit()
        db.refresh(test_result)

        return test_result

    @staticmethod
    def get_test_results(
        user_id: int,
        test_case_id: int = None,
        db: Session = None
    ) -> List[RecallTestResult]:
        """获取测试结果"""
        query = db.query(RecallTestResult).filter(
            RecallTestResult.user_id == user_id
        )
        if test_case_id:
            query = query.filter(RecallTestResult.test_case_id == test_case_id)
        return query.order_by(RecallTestResult.created_at.desc()).all()

    @staticmethod
    def get_test_summary(
        user_id: int,
        test_case_id: int = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """获取测试汇总统计"""
        results = RecallTestService.get_test_results(user_id, test_case_id, db)

        if not results:
            return {
                "total_tests": 0,
                "avg_recall": 0,
                "avg_precision": 0,
                "avg_f1_score": 0,
                "avg_mrr": 0,
                "results": []
            }

        total = len(results)
        avg_recall = sum(r.recall for r in results) / total
        avg_precision = sum(r.precision for r in results) / total
        avg_f1_score = sum(r.f1_score for r in results) / total
        avg_mrr = sum(r.mrr for r in results) / total

        return {
            "total_tests": total,
            "avg_recall": round(avg_recall, 2),
            "avg_precision": round(avg_precision, 2),
            "avg_f1_score": round(avg_f1_score, 2),
            "avg_mrr": round(avg_mrr, 2),
            "results": results
        }

    @staticmethod
    def get_chunk_details(chunk_ids: List[int], db: Session) -> List[Dict[str, Any]]:
        """获取分段详情"""
        chunks = db.query(VectorChunk).filter(
            VectorChunk.id.in_(chunk_ids)
        ).all()
        return [
            {
                "id": chunk.id,
                "content": chunk.chunk_text,
                "document_id": chunk.document_id
            }
            for chunk in chunks
        ]