from fastapi import Depends, HTTPException
from app.auth.models import RoleEnum, User
from app.auth.dependencies import get_current_user

# Permissions par rôle
ROLE_PERMISSIONS = {
    RoleEnum.ADMIN:  ["execute_trade", "view_dashboard", "manage_settings", "view_analytics", "view_audit"],
    RoleEnum.TRADER: ["execute_trade", "view_dashboard", "view_analytics"],
    RoleEnum.VIEWER: ["view_dashboard", "view_analytics"],
}

def require_permission(permission: str):
    async def checker(current_user: User = Depends(get_current_user)):
        user_role = RoleEnum(current_user.role)
        allowed = ROLE_PERMISSIONS.get(user_role, [])
        if permission not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Permission refusée — rôle '{user_role}' insuffisant"
            )
        return current_user
    return checker

def require_role(role: RoleEnum):
    async def checker(current_user: User = Depends(get_current_user)):
        if RoleEnum(current_user.role) != role:
            raise HTTPException(
                status_code=403,
                detail=f"Accès réservé au rôle '{role}'"
            )
        return current_user
    return checker