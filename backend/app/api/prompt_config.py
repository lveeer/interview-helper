"""配置中心 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.api.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.prompt_config_service import PromptConfigService
from app.schemas.common import ApiResponse, ListResponse
from app.schemas.prompt_config import (
    PromptConfigCreate,
    PromptConfigUpdate,
    PromptConfigResponse,
    PromptConfigListResponse,
    PromptVersionCreate,
    PromptVersionUpdate,
    PromptVersionResponse,
    PromptVersionBrief,
    ABTestCreate,
    ABTestUpdate,
    ABTestResponse,
    ABTestListResponse,
    ABTestResultCreate,
    ABTestResultResponse,
    ABTestStatistics,
    ABTestStatus,
    SetActiveVersionRequest,
    ActivateABTestRequest,
    ABTestStatusChangeRequest,
    ResolvedPromptResponse
)

router = APIRouter()


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


def get_config_service(db: AsyncSession = Depends(get_db)) -> PromptConfigService:
    """获取配置服务实例"""
    return PromptConfigService(db)


# ============ Prompt 配置管理 ============

@router.post("", response_model=ApiResponse[PromptConfigResponse], summary="创建 Prompt 配置")
async def create_config(
    config_data: PromptConfigCreate,
    service: PromptConfigService = Depends(get_config_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """创建新的 Prompt 配置"""
    try:
        config = await service.create_config(
            config_data,
            user_id=current_user.id if current_user else None
        )
        
        # 获取版本数量
        version_count = await service.get_version_count(config.id)
        
        response = PromptConfigResponse(
            **{c.name: getattr(config, c.name) for c in config.__table__.columns},
            active_version=PromptVersionBrief.model_validate(config.active_version) if config.active_version else None,
            version_count=version_count
        )
        
        return ApiResponse(code=200, message="创建成功", data=response)
    except Exception as e:
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="配置名称已存在")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ListResponse[PromptConfigListResponse], summary="获取配置列表")
async def list_configs(
    category: Optional[str] = Query(None, description="分类过滤"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: PromptConfigService = Depends(get_config_service)
):
    """获取 Prompt 配置列表"""
    configs, total = await service.list_configs(
        category=category,
        is_active=is_active,
        search=search,
        page=page,
        page_size=page_size
    )
    
    items = []
    for config in configs:
        version_count = await service.get_version_count(config.id)
        items.append(PromptConfigListResponse(
            id=config.id,
            name=config.name,
            display_name=config.display_name,
            category=config.category,
            is_active=config.is_active,
            enable_ab_test=config.enable_ab_test,
            active_version_id=config.active_version_id,
            version_count=version_count,
            created_at=config.created_at,
            updated_at=config.updated_at
        ))
    
    return ListResponse(
        code=200,
        message="获取成功",
        data=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{config_id}", response_model=ApiResponse[PromptConfigResponse], summary="获取配置详情")
async def get_config(
    config_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """获取单个 Prompt 配置详情"""
    config = await service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    version_count = await service.get_version_count(config.id)
    
    response = PromptConfigResponse(
        **{c.name: getattr(config, c.name) for c in config.__table__.columns},
        active_version=PromptVersionBrief.model_validate(config.active_version) if config.active_version else None,
        version_count=version_count
    )
    
    return ApiResponse(code=200, message="获取成功", data=response)


@router.put("/{config_id}", response_model=ApiResponse[PromptConfigResponse], summary="更新配置")
async def update_config(
    config_id: int,
    config_data: PromptConfigUpdate,
    service: PromptConfigService = Depends(get_config_service)
):
    """更新 Prompt 配置"""
    config = await service.update_config(config_id, config_data)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    version_count = await service.get_version_count(config.id)
    
    response = PromptConfigResponse(
        **{c.name: getattr(config, c.name) for c in config.__table__.columns},
        active_version=PromptVersionBrief.model_validate(config.active_version) if config.active_version else None,
        version_count=version_count
    )
    
    return ApiResponse(code=200, message="更新成功", data=response)


@router.delete("/{config_id}", summary="删除配置")
async def delete_config(
    config_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """删除 Prompt 配置（级联删除版本和测试）"""
    success = await service.delete_config(config_id)
    if not success:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return ApiResponse(code=200, message="删除成功")


@router.post("/{config_id}/activate-version", response_model=ApiResponse, summary="设置激活版本")
async def set_active_version(
    config_id: int,
    request: SetActiveVersionRequest,
    service: PromptConfigService = Depends(get_config_service)
):
    """设置配置的激活版本"""
    config = await service.set_active_version(config_id, request.version_id)
    if not config:
        raise HTTPException(status_code=400, detail="设置失败，请检查配置和版本ID")
    
    return ApiResponse(code=200, message="设置成功")


# ============ 版本管理 ============

@router.post("/{config_id}/versions", response_model=ApiResponse[PromptVersionResponse], summary="创建版本")
async def create_version(
    config_id: int,
    version_data: PromptVersionCreate,
    service: PromptConfigService = Depends(get_config_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """创建新版本"""
    version = await service.create_version(
        config_id,
        version_data,
        user_id=current_user.id if current_user else None
    )
    if not version:
        raise HTTPException(status_code=400, detail="创建失败，配置不存在或版本号已存在")
    
    return ApiResponse(
        code=200,
        message="创建成功",
        data=PromptVersionResponse.model_validate(version)
    )


@router.get("/{config_id}/versions", response_model=ApiResponse[list], summary="获取版本列表")
async def list_versions(
    config_id: int,
    include_unpublished: bool = Query(True, description="是否包含未发布版本"),
    service: PromptConfigService = Depends(get_config_service)
):
    """获取配置的版本列表"""
    versions = await service.list_versions(config_id, include_unpublished)
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=[PromptVersionResponse.model_validate(v) for v in versions]
    )


@router.get("/versions/{version_id}", response_model=ApiResponse[PromptVersionResponse], summary="获取版本详情")
async def get_version(
    version_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """获取版本详情"""
    version = await service.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=PromptVersionResponse.model_validate(version)
    )


@router.put("/versions/{version_id}", response_model=ApiResponse[PromptVersionResponse], summary="更新版本")
async def update_version(
    version_id: int,
    version_data: PromptVersionUpdate,
    service: PromptConfigService = Depends(get_config_service)
):
    """更新版本（仅未发布版本）"""
    version = await service.update_version(version_id, version_data)
    if not version:
        raise HTTPException(status_code=400, detail="更新失败，版本不存在或已发布")
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data=PromptVersionResponse.model_validate(version)
    )


@router.post("/versions/{version_id}/publish", response_model=ApiResponse[PromptVersionResponse], summary="发布版本")
async def publish_version(
    version_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """发布版本"""
    version = await service.publish_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    return ApiResponse(
        code=200,
        message="发布成功",
        data=PromptVersionResponse.model_validate(version)
    )


@router.delete("/versions/{version_id}", summary="删除版本")
async def delete_version(
    version_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """删除版本（仅未发布版本）"""
    success = await service.delete_version(version_id)
    if not success:
        raise HTTPException(status_code=400, detail="删除失败，版本不存在或已发布")
    
    return ApiResponse(code=200, message="删除成功")


# ============ A/B 测试管理 ============

@router.post("/{config_id}/ab-tests", response_model=ApiResponse[ABTestResponse], summary="创建 A/B 测试")
async def create_ab_test(
    config_id: int,
    test_data: ABTestCreate,
    service: PromptConfigService = Depends(get_config_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """创建 A/B 测试"""
    ab_test = await service.create_ab_test(
        config_id,
        test_data,
        user_id=current_user.id if current_user else None
    )
    if not ab_test:
        raise HTTPException(status_code=400, detail="创建失败，请检查配置和版本ID")
    
    return ApiResponse(
        code=200,
        message="创建成功",
        data=ABTestResponse.model_validate(ab_test)
    )


@router.get("/{config_id}/ab-tests", response_model=ListResponse[ABTestListResponse], summary="获取 A/B 测试列表")
async def list_ab_tests(
    config_id: int,
    status: Optional[str] = Query(None, description="状态过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: PromptConfigService = Depends(get_config_service)
):
    """获取配置的 A/B 测试列表"""
    tests, total = await service.list_ab_tests(
        config_id=config_id,
        status=status,
        page=page,
        page_size=page_size
    )
    
    items = [ABTestListResponse.model_validate(t) for t in tests]
    
    return ListResponse(
        code=200,
        message="获取成功",
        data=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/ab-tests/{test_id}", response_model=ApiResponse[ABTestResponse], summary="获取 A/B 测试详情")
async def get_ab_test(
    test_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """获取 A/B 测试详情"""
    ab_test = await service.get_ab_test(test_id)
    if not ab_test:
        raise HTTPException(status_code=404, detail="A/B 测试不存在")
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=ABTestResponse.model_validate(ab_test)
    )


@router.put("/ab-tests/{test_id}", response_model=ApiResponse[ABTestResponse], summary="更新 A/B 测试")
async def update_ab_test(
    test_id: int,
    test_data: ABTestUpdate,
    service: PromptConfigService = Depends(get_config_service)
):
    """更新 A/B 测试配置（仅草稿状态）"""
    ab_test = await service.update_ab_test(test_id, test_data)
    if not ab_test:
        raise HTTPException(status_code=400, detail="更新失败，测试不存在或非草稿状态")
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data=ABTestResponse.model_validate(ab_test)
    )


@router.post("/ab-tests/{test_id}/status", response_model=ApiResponse[ABTestResponse], summary="变更 A/B 测试状态")
async def change_ab_test_status(
    test_id: int,
    request: ABTestStatusChangeRequest,
    service: PromptConfigService = Depends(get_config_service)
):
    """变更 A/B 测试状态"""
    ab_test = await service.change_ab_test_status(test_id, request.status)
    if not ab_test:
        raise HTTPException(status_code=400, detail="状态变更失败，无效的状态转换")
    
    return ApiResponse(
        code=200,
        message="状态变更成功",
        data=ABTestResponse.model_validate(ab_test)
    )


@router.post("/{config_id}/activate-ab-test", response_model=ApiResponse, summary="激活 A/B 测试")
async def activate_ab_test(
    config_id: int,
    request: ActivateABTestRequest,
    service: PromptConfigService = Depends(get_config_service)
):
    """激活 A/B 测试（配置级别）"""
    config = await service.activate_ab_test(config_id, request.ab_test_id)
    if not config:
        raise HTTPException(status_code=400, detail="激活失败，请检查配置和测试状态")
    
    return ApiResponse(code=200, message="激活成功")


@router.post("/{config_id}/deactivate-ab-test", response_model=ApiResponse, summary="停用 A/B 测试")
async def deactivate_ab_test(
    config_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """停用 A/B 测试"""
    config = await service.deactivate_ab_test(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return ApiResponse(code=200, message="停用成功")


@router.delete("/ab-tests/{test_id}", summary="删除 A/B 测试")
async def delete_ab_test(
    test_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """删除 A/B 测试（仅草稿状态）"""
    success = await service.delete_ab_test(test_id)
    if not success:
        raise HTTPException(status_code=400, detail="删除失败，测试不存在或非草稿状态")
    
    return ApiResponse(code=200, message="删除成功")


# ============ A/B 测试结果 ============

@router.post("/ab-tests/{test_id}/results", response_model=ApiResponse[ABTestResultResponse], summary="记录测试结果")
async def record_ab_test_result(
    test_id: int,
    result_data: ABTestResultCreate,
    service: PromptConfigService = Depends(get_config_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """记录 A/B 测试结果"""
    result = await service.record_ab_test_result(
        test_id,
        result_data,
        user_id=current_user.id if current_user else None
    )
    if not result:
        raise HTTPException(status_code=400, detail="记录失败，测试不存在或未运行")
    
    return ApiResponse(
        code=200,
        message="记录成功",
        data=ABTestResultResponse.model_validate(result)
    )


@router.get("/ab-tests/{test_id}/statistics", response_model=ApiResponse[ABTestStatistics], summary="获取测试统计")
async def get_ab_test_statistics(
    test_id: int,
    service: PromptConfigService = Depends(get_config_service)
):
    """获取 A/B 测试统计数据"""
    stats = await service.get_ab_test_statistics(test_id)
    if not stats:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return ApiResponse(code=200, message="获取成功", data=stats)


# ============ Prompt 获取 ============

@router.get("/resolve/{config_name}", response_model=ApiResponse[ResolvedPromptResponse], summary="获取生效的 Prompt")
async def get_effective_prompt(
    config_name: str,
    user_id: Optional[int] = Query(None, description="用户ID（用于一致性分流）"),
    session_id: Optional[str] = Query(None, description="会话ID（用于一致性分流）"),
    service: PromptConfigService = Depends(get_config_service)
):
    """获取生效的 Prompt（考虑 A/B 测试）"""
    resolved = await service.get_effective_prompt(config_name, user_id, session_id)
    if not resolved:
        raise HTTPException(status_code=404, detail="配置不存在或未激活")
    
    return ApiResponse(code=200, message="获取成功", data=resolved)


# ============ 初始化 ============

@router.post("/init-from-files", response_model=ApiResponse, summary="从文件系统初始化")
async def init_from_files(
    service: PromptConfigService = Depends(get_config_service),
    current_user: User = Depends(get_current_user)
):
    """从 prompts/ 目录初始化配置到数据库"""
    count = await service.init_from_file_system()
    return ApiResponse(code=200, message=f"成功导入 {count} 个配置", data={"imported_count": count})
