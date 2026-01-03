from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from datetime import timedelta
from config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户"""
    from app.core.security import decode_access_token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    import traceback
    from app.schemas.common import ApiResponse

    try:
        print(f"[DEBUG] 收到注册请求: {user.username}, {user.email}")

        # 检查用户名是否已存在
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        # 检查邮箱是否已存在
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        # 创建新用户
        print("[DEBUG] 开始创建密码哈希")
        hashed_password = get_password_hash(user.password)
        print("[DEBUG] 密码哈希创建成功")

        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        print("[DEBUG] 用户对象创建成功")

        db.add(db_user)
        print("[DEBUG] 用户添加到数据库")

        db.commit()
        print("[DEBUG] 数据库提交成功")

        db.refresh(db_user)
        print(f"[DEBUG] 用户ID: {db_user.id}")

        print("[DEBUG] 开始创建响应")
        response = ApiResponse(
            code=201,
            message="注册成功",
            data=UserResponse.model_validate(db_user)
        )
        print("[DEBUG] 响应创建成功")
        return response
    except Exception as e:
        print(f"[ERROR] 注册失败: {str(e)}")
        print(f"[ERROR] 详细错误: {traceback.format_exc()}")
        raise


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    from app.schemas.common import ApiResponse

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return ApiResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    from app.schemas.common import ApiResponse
    return ApiResponse(
        code=200,
        message="获取成功",
        data=UserResponse.model_validate(current_user)
    )