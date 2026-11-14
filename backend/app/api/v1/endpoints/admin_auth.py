from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models import AdminUser, AuditLog
from app.schemas.auth import LoginRequest, TokenResponse, AdminUserOut

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/admin/auth/login")


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """Dependency that verifies JWT token and extracts the authenticated admin user."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    stmt = select(AdminUser).where(AdminUser.id == user_id, AdminUser.is_active == True)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin user not found or inactive")
    return user


@router.post("/admin/auth/login", response_model=TokenResponse)
async def admin_login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate an administrator with username/email and password."""
    # Lookup by username or email
    stmt = select(AdminUser).where(
        (AdminUser.username == req.username) | (AdminUser.email == req.username)
    )
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator account is disabled"
        )

    # Create token
    access_token = create_access_token(subject=str(user.id), role=user.role)

    # Log audit event
    audit = AuditLog(
        admin_id=user.id,
        action="admin_login",
        resource_type="admin_user",
        resource_id=str(user.id),
        details={"username": user.username},
    )
    db.add(audit)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=AdminUserOut(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )
    )

