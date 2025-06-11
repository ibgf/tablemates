# permission_guard.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Role, PermissionModule, RolePermission

# 模拟当前用户获取（应替换为真实 JWT 解码）
def get_current_user():
    # 示例用户，id 与角色 id 必须有效
    class DummyUser:
        def __init__(self):
            self.id = '1f0917df-e0dd-4ea3-b787-2f864edeea8c'
            self.role_id = '00000000-0000-0000-0000-000000000001'  # super_admin
    return DummyUser()

# 权限验证依赖
async def require_permission(module_name: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    role = db.query(Role).filter_by(id=user.role_id).first()
    if role and role.name == 'super_admin':
        return  # 超级管理员全权限

    module = db.query(PermissionModule).filter_by(name=module_name).first()
    if not module:
        raise HTTPException(status_code=404, detail="功能模块不存在")

    permission = db.query(RolePermission).filter_by(role_id=user.role_id, module_id=module.id).first()
    if not permission or not permission.can_access:
        raise HTTPException(status_code=403, detail="权限不足，无法访问该模块")

# 示例路由使用
from fastapi import APIRouter
router = APIRouter()

@router.get("/admin/secure", dependencies=[Depends(lambda: require_permission('permission_management'))])
async def secure_endpoint():
    return {"message": "已通过权限验证"}
