"""
Authentication and authorization API routes.
"""
import time
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.logging import get_logger
from app.core.rate_limit import rate_limit_login
from app.domains.auth.dependencies import (
    get_current_user,
    require_permission,
    require_role,
)
from app.domains.auth.models import User, Tenant, UserStatus, RoleName
from app.domains.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    LoginChallengeResponse,
    TokenRefreshRequest,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ChangePasswordRequest,
    AdminChangePasswordRequest,
    UserResponse,
    UserProfile,
    UserUpdate,
    CreateOrganizationRequest,
    CreateSchoolRequest,
    CreateUserRequest,
    TenantResponse,
    TeacherSignupRequest,
    StudentSignupRequest,
    ParentSignupRequest,
    SignupApprovalResponse,
    ApproveSignupRequest,
    RejectSignupRequest,
    AssignRoleRequest,
    UserRoleResponse,
    SignupRequest,
    SignupResponse,
    MembershipResponse,
    MembershipListResponse,
    MembershipSwitchRequest,
    MembershipSwitchResponse,
)
from app.domains.auth.services import (
    AuthService,
    UserService,
    TenantService,
    SelfRegistrationService,
    RBACService,
    SuperAdminService,
)
from app.domains.auth.services.signup_service import SignupService
from app.domains.auth.services.membership_service import MembershipService
from app.domains.auth.services.session_service import SessionService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["auth"])


# ========== Public Auth Endpoints ==========

@router.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    
    Note: This is a basic registration endpoint. In production, you may want to
    require a tenant_id or use self-registration endpoints for teachers/students.
    """
    try:
        auth_service = AuthService(db)
        
        # For now, we need a tenant_id - this should come from context or request
        # For MVP, we'll use the platform tenant or require tenant_id in request
        # This is a simplified version - adjust based on your requirements
        from app.domains.auth.models import TenantType
        # Use index on type for fast lookup
        platform = db.query(Tenant).filter(
            Tenant.type == TenantType.PLATFORM,
            Tenant.is_active == True
        ).first()
        if not platform:
            tenant_service = TenantService(db)
            platform = tenant_service.create_platform_tenant()
        
        user, token = auth_service.register(request, platform.id)
        
        return {
            "message": "Registration successful. Please check your email to verify your account.",
            "user_id": str(user.id),
        }
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        # Re-raise to let exception handlers process it
        raise


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    User login - supports multi-step challenge flow.
    
    Step 1: email + password → returns challenge or success
    Step 2: login_token + challenge resolution → returns tokens
    """
    try:
        logger.info(f"Login attempt for email: {login_data.email}")
        auth_service = AuthService(db)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Step 2: Handle challenge resolution
        if login_data.login_token and login_data.selected_membership_id:
            access_token, refresh_token, user = auth_service.complete_login_challenge(
                login_token=login_data.login_token,
                selected_membership_id=login_data.selected_membership_id,
                scope_type=login_data.scope_type or "institution",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            # Load user roles - check both UserRole and UserMembership tables
            from app.domains.auth.models import UserRole, Role, UserMembership
            from app.domains.auth.schemas import UserRoleInfo
            
            roles_data = []
            try:
                # First, try to get roles from UserRole table (preferred)
                user_roles = (
                    db.query(UserRole)
                    .join(Role)
                    .filter(UserRole.user_id == user.id)
                    .limit(20)  # Limit to prevent slow queries
                    .all()
                )
                
                if user_roles:
                    # Use UserRole records if available
                    roles_data = [
                        UserRoleInfo(
                            id=ur.role.id,
                            name=ur.role.name,
                            scope=ur.role.scope,
                            tenant_id=ur.tenant_id,
                            granted_at=ur.granted_at,
                        )
                        for ur in user_roles
                    ]
                else:
                    # Fallback: Get roles from UserMembership table
                    # This ensures teachers and other users get roles even if UserRole records are missing
                    logger.debug(f"No UserRole records found, checking UserMembership for user: {user.id}")
                    memberships_with_roles = (
                        db.query(UserMembership)
                        .join(Role, UserMembership.role_id == Role.id)
                        .filter(
                            UserMembership.user_id == user.id,
                            UserMembership.is_active == True
                        )
                        .limit(20)
                        .all()
                    )
                    
                    if memberships_with_roles:
                        # Extract unique roles from memberships
                        seen_role_ids = set()
                        for membership in memberships_with_roles:
                            if membership.role_id and membership.role_id not in seen_role_ids:
                                seen_role_ids.add(membership.role_id)
                                roles_data.append(
                                    UserRoleInfo(
                                        id=membership.role.id,
                                        name=membership.role.name,
                                        scope=membership.role.scope,
                                        tenant_id=user.tenant_id,  # Use user's tenant_id as fallback
                                        granted_at=membership.granted_at or user.created_at,
                                    )
                                )
            except Exception as role_error:
                logger.error(f"Error fetching user roles during challenge completion: {role_error}", exc_info=True)
                # Rollback transaction if it failed
                try:
                    db.rollback()
                except Exception:
                    pass  # Ignore rollback errors
                roles_data = []
            
            user_dict = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "username": user.username,
                "tenant_id": user.tenant_id,
                "status": user.status,
                "email_verified": user.email_verified,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "roles": roles_data if roles_data else None,
            }
            user_response = UserResponse(**user_dict)
            
            return LoginResponse(
                status="SUCCESS",
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user=user_response,
            )
        
        # Step 1: Authenticate email + password
        if not login_data.email or not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required for step 1"
            )
        
        access_token, refresh_token, user = auth_service.login(
            login_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        # Check if user has multiple memberships - optimize query
        logger.debug(f"Checking memberships for user: {user.id}")
        from app.domains.auth.services.membership_service import MembershipService
        membership_service = MembershipService(db)
        try:
            # Use direct query for speed - avoid service overhead if possible
            from app.domains.auth.models import UserMembership
            memberships = db.query(UserMembership).filter(
                UserMembership.user_id == user.id,
                UserMembership.is_active == True
            ).limit(10).all()  # Limit to prevent slow queries
            logger.debug(f"Found {len(memberships)} memberships for user")
        except Exception as membership_error:
            logger.error(f"Error fetching memberships: {membership_error}")
            # Rollback transaction if it failed, then continue with empty memberships
            try:
                db.rollback()
            except Exception:
                pass  # Ignore rollback errors
            memberships = []
        
        if len(memberships) > 1:
            # Return challenge response
            login_token, memberships_list = auth_service.get_login_challenge_data(user)
            
            # Build membership responses - optimize to avoid slow queries
            from app.domains.auth.services.membership_service import MembershipService
            membership_service = MembershipService(db)
            membership_responses = []
            for membership in memberships_list:
                try:
                    # Use simplified response to avoid slow queries
                    tenant = db.query(Tenant).filter(Tenant.id == membership.tenant_id).first()
                    membership_responses.append(MembershipResponse(
                        id=membership.id,
                        tenant_id=membership.tenant_id,
                        tenant_name=tenant.name if tenant else 'Unknown',
                        tenant_type=tenant.type if tenant else None,
                        is_active=membership.is_active,
                        joined_at=membership.joined_at,
                    ))
                except Exception as detail_error:
                    logger.warning(f"Error building membership response: {detail_error}")
                    # Rollback transaction if it failed, then skip this membership
                    try:
                        db.rollback()
                    except Exception:
                        pass  # Ignore rollback errors
                    continue
            
            challenge = LoginChallengeResponse(
                challenge_type="TENANT_SELECTION_REQUIRED",
                login_token=login_token,
                message="Please select which workspace you want to access",
                memberships=membership_responses,
            )
            
            return LoginResponse(
                status="CHALLENGE",
                challenge=challenge,
            )
        
        # Single membership - return success
        # Load user roles - check both UserRole and UserMembership tables
        logger.debug(f"Loading roles for user: {user.id}")
        from app.domains.auth.models import UserRole, Role, UserMembership
        from app.domains.auth.schemas import UserRoleInfo
        
        roles_data = []
        try:
            # First, try to get roles from UserRole table (preferred)
            user_roles = (
                db.query(UserRole)
                .join(Role)
                .filter(UserRole.user_id == user.id)
                .limit(20)  # Limit to prevent slow queries
                .all()
            )
            
            if user_roles:
                # Use UserRole records if available
                roles_data = [
                    UserRoleInfo(
                        id=ur.role.id,
                        name=ur.role.name,
                        scope=ur.role.scope,
                        tenant_id=ur.tenant_id,
                        granted_at=ur.granted_at,
                    )
                    for ur in user_roles
                ]
            else:
                # Fallback: Get roles from UserMembership table
                # This ensures teachers and other users get roles even if UserRole records are missing
                logger.debug(f"No UserRole records found, checking UserMembership for user: {user.id}")
                memberships_with_roles = (
                    db.query(UserMembership)
                    .join(Role, UserMembership.role_id == Role.id)
                    .filter(
                        UserMembership.user_id == user.id,
                        UserMembership.is_active == True
                    )
                    .limit(20)
                    .all()
                )
                
                if memberships_with_roles:
                    # Extract unique roles from memberships
                    seen_role_ids = set()
                    for membership in memberships_with_roles:
                        if membership.role_id and membership.role_id not in seen_role_ids:
                            seen_role_ids.add(membership.role_id)
                            roles_data.append(
                                UserRoleInfo(
                                    id=membership.role.id,
                                    name=membership.role.name,
                                    scope=membership.role.scope,
                                    tenant_id=user.tenant_id,  # Use user's tenant_id as fallback
                                    granted_at=membership.granted_at or user.created_at,
                                )
                            )
        except Exception as role_error:
            logger.error(f"Error loading roles: {role_error}", exc_info=True)
            # Rollback transaction if it failed, then continue without roles
            try:
                db.rollback()
            except Exception:
                pass  # Ignore rollback errors
            roles_data = []  # Continue without roles if query fails
        
        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "username": user.username,
            "tenant_id": user.tenant_id,
            "status": user.status,
            "email_verified": user.email_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": roles_data if roles_data else None,
        }
        user_response = UserResponse(**user_dict)
        
        return LoginResponse(
            status="SUCCESS",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_response,
        )
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        raise


@router.post("/auth/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """
    Unified signup endpoint - handles all signup types.
    
    Supports:
    - Organization Admin signup
    - Institution Admin signup
    - Individual Teacher/Student signup
    - Parent signup
    - Invite acceptance
    """
    try:
        start_time = time.time()
        logger.info(f"Signup request received for role: {request.role}, email: {request.email}")
        
        signup_service = SignupService(db)
        
        # Convert request to dict for service
        payload = request.model_dump(exclude_unset=True)
        
        # Route to appropriate strategy
        result = signup_service.route(request.role, payload)
        
        user = result['user']
        memberships = result.get('memberships', [])
        
        # Create tokens for new signup
        from app.core.security import create_access_token, create_refresh_token, hash_token
        from app.domains.auth.models import RefreshToken
        
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        
        active_membership_id = memberships[0].id if memberships else None
        
        # Generate access token
        access_token = create_access_token({
            "user_id": str(user.id),
            "email": user.email,
            "tenant_id": str(user.tenant_id),
            "membership_id": str(active_membership_id) if active_membership_id else None,
        })
        
        # Generate refresh token
        refresh_token_string = create_refresh_token({"user_id": str(user.id)})
        refresh_token_hash = hash_token(refresh_token_string)
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        
        # Store refresh token - with error handling
        try:
            refresh_token = RefreshToken(
                user_id=user.id,
                token_hash=refresh_token_hash,
                device_info={"ip_address": ip_address, "user_agent": user_agent} if ip_address or user_agent else None,
                expires_at=expires_at,
                active_membership_id=active_membership_id,
            )
            db.add(refresh_token)
            db.commit()
        except Exception as token_error:
            logger.error(f"Error saving refresh token: {token_error}")
            # Rollback and re-raise - tokens are critical
            db.rollback()
            raise
        
        # Build membership responses - optimize to avoid slow queries
        membership_responses = []
        for membership in memberships:
            try:
                # Use simplified response - get role and scope info quickly
                from app.domains.auth.models import Role, PersonalWorkspace, ScopeType
                role = db.query(Role).filter(Role.id == membership.role_id).first()
                
                scope_name = None
                scope_display_name = None
                
                # Quick lookup based on scope type
                if membership.scope_type == ScopeType.PERSONAL_WORKSPACE:
                    workspace = db.query(PersonalWorkspace).filter(PersonalWorkspace.id == membership.scope_id).first()
                    if workspace:
                        scope_name = workspace.name
                        scope_display_name = "Personal Workspace"
                # For other scope types, use minimal info to avoid slow queries
                
                membership_responses.append(MembershipResponse(
                    id=membership.id,
                    scope_type=membership.scope_type.value,
                    scope_id=membership.scope_id,
                    scope_name=scope_name or "Workspace",
                    scope_display_name=scope_display_name or "Workspace",
                    role={"id": str(role.id), "name": role.name.value} if role else None,
                    is_active=membership.is_active,
                    granted_at=membership.granted_at,
                ))
            except Exception as detail_error:
                logger.warning(f"Error building membership response: {detail_error}")
                # Rollback transaction if it failed, then use minimal response
                try:
                    db.rollback()
                except Exception:
                    pass  # Ignore rollback errors
                # Use minimal response if details fail
                membership_responses.append(MembershipResponse(
                    id=membership.id,
                    scope_type=membership.scope_type.value,
                    scope_id=membership.scope_id,
                    scope_name="Workspace",
                    scope_display_name="Workspace",
                    role=None,
                    is_active=membership.is_active,
                    granted_at=membership.granted_at,
                ))
        
        # Build user response - optimize to avoid slow queries
        from app.domains.auth.models import UserRole, Role
        from app.domains.auth.schemas import UserRoleInfo
        
        # Load user roles - optimize query with limit and error handling
        roles_data = []
        try:
            user_roles = (
                db.query(UserRole)
                .join(Role)
                .filter(UserRole.user_id == user.id)
                .limit(10)  # Limit to prevent slow queries
                .all()
            )
            roles_data = [
                UserRoleInfo(
                    id=ur.role.id,
                    name=ur.role.name,
                    scope=ur.role.scope,
                    tenant_id=ur.tenant_id,
                    granted_at=ur.granted_at,
                )
                for ur in user_roles
            ]
        except Exception as role_error:
            logger.warning(f"Error loading roles during signup (non-critical): {role_error}")
            # Rollback transaction if it failed, then continue without roles
            try:
                db.rollback()
            except Exception:
                pass  # Ignore rollback errors
            # Continue without roles - signup should still succeed
        
        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "username": user.username,
            "tenant_id": user.tenant_id,
            "status": user.status,
            "email_verified": user.email_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": roles_data if roles_data else None,
        }
        user_response = UserResponse(**user_dict)
        
        duration = time.time() - start_time
        logger.info(f"Signup successful for user: {user.email} (total time: {duration:.2f}s)")
        
        return SignupResponse(
            status="SUCCESS",
            user=user_response,
            access_token=access_token,
            refresh_token=refresh_token_string,
            memberships=membership_responses if membership_responses else None,
        )
    except Exception as e:
        duration = time.time() - start_time if 'start_time' in locals() else 0
        logger.error(f"Signup error after {duration:.2f}s: {e}", exc_info=True)
        raise


@router.get("/auth/memberships", response_model=MembershipListResponse)
async def get_memberships(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all memberships for the current user."""
    try:
        membership_service = MembershipService(db)
        memberships = membership_service.get_user_memberships(current_user.id, active_only=True)
        
        # Get active membership from refresh token if available
        active_membership_id = None
        # In a real implementation, you'd get this from the current session/refresh token
        # For now, we'll use the first membership as active
        if memberships:
            active_membership_id = memberships[0].id
        
        # Build membership responses
        membership_responses = []
        for membership in memberships:
            details = membership_service.get_membership_details(membership)
            membership_responses.append(MembershipResponse(**details))
        
        return MembershipListResponse(
            memberships=membership_responses,
            active_membership_id=active_membership_id,
        )
    except Exception as e:
        raise


@router.post("/auth/memberships/switch", response_model=MembershipSwitchResponse)
async def switch_membership(
    request: MembershipSwitchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Switch active membership for the current user."""
    try:
        membership_service = MembershipService(db)
        
        # Verify membership belongs to user
        membership = membership_service.switch_active_membership(
            user_id=current_user.id,
            membership_id=request.membership_id,
        )
        
        # Update refresh token's active membership
        # Get current refresh token from request (in production, get from session)
        # For now, we'll update all active refresh tokens for the user
        from app.domains.auth.models import RefreshToken
        from datetime import timezone as tz
        now = datetime.now(tz.utc)
        
        active_tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        ).all()
        
        for token in active_tokens:
            token.active_membership_id = request.membership_id
        db.commit()
        
        # Generate new tokens with updated membership context
        from app.core.security import create_access_token, create_refresh_token, hash_token
        
        access_token = create_access_token({
            "user_id": str(current_user.id),
            "email": current_user.email,
            "tenant_id": str(current_user.tenant_id),
            "membership_id": str(request.membership_id),
        })
        
        # Create new refresh token
        refresh_token_string = create_refresh_token({"user_id": str(current_user.id)})
        refresh_token_hash = hash_token(refresh_token_string)
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        
        new_refresh_token = RefreshToken(
            user_id=current_user.id,
            token_hash=refresh_token_hash,
            expires_at=expires_at,
            active_membership_id=request.membership_id,
        )
        db.add(new_refresh_token)
        db.commit()
        
        # Get membership details
        details = membership_service.get_membership_details(membership)
        active_membership = MembershipResponse(**details)
        
        return MembershipSwitchResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token_string,
            active_membership=active_membership,
        )
    except Exception as e:
        raise


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        auth_service = AuthService(db)
        access_token = auth_service.refresh_access_token(request.refresh_token)
        
        return Token(
            access_token=access_token,
            refresh_token=request.refresh_token,  # Keep same refresh token (rotation can be added)
            token_type="bearer",
        )
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        raise


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: TokenRefreshRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout user by revoking refresh token."""
    try:
        auth_service = AuthService(db)
        auth_service.logout(request.refresh_token, current_user.id)
        
        return None
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        raise


@router.get("/auth/sessions", response_model=List[dict])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active sessions for the current user."""
    try:
        session_service = SessionService(db)
        sessions = session_service.list_sessions(current_user.id, active_only=True)
        
        return [
            {
                "id": str(session.id),
                "device_info": session.device_info,
                "created_at": session.created_at.isoformat(),
                "last_used_at": session.last_used_at.isoformat() if session.last_used_at else None,
                "expires_at": session.expires_at.isoformat(),
                "active_membership_id": str(session.active_membership_id) if session.active_membership_id else None,
            }
            for session in sessions
        ]
    except Exception as e:
        raise


@router.post("/auth/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke all sessions for the current user."""
    try:
        session_service = SessionService(db)
        session_service.revoke_all_sessions(current_user.id, reason="User requested logout all")
        
        return None
    except Exception as e:
        raise


@router.delete("/auth/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke a specific session."""
    try:
        from app.domains.auth.models import RefreshToken
        from app.core.security import hash_token
        
        # Get session
        session = db.query(RefreshToken).filter(
            RefreshToken.id == session_id,
            RefreshToken.user_id == current_user.id,
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session_service = SessionService(db)
        # We need the token hash, but we only have session_id
        # For now, we'll revoke directly
        session.revoked_at = datetime.now(timezone.utc)
        session.revoked_reason = "User requested revocation"
        db.commit()
        
        return None
    except Exception as e:
        raise


@router.post("/auth/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    request: ForgotPasswordRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Request password reset email."""
    try:
        from app.utils.email import send_email
        
        auth_service = AuthService(db)
        ip_address = http_request.client.host if http_request.client else None
        email_data = auth_service.forgot_password(request.email, ip_address=ip_address)
        
        # Send email in background if email data was prepared
        if email_data:
            user_email, subject, html_content, text_content = email_data
            background_tasks.add_task(send_email, user_email, subject, html_content, text_content)
        
        return None
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        raise


@router.post("/auth/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Reset password using token."""
    try:
        auth_service = AuthService(db)
        auth_service.reset_password(request.token, request.new_password)
        
        return None
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        raise


@router.post("/auth/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """Verify email address using token."""
    try:
        auth_service = AuthService(db)
        auth_service.verify_email(request.token)
        
        return None
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        raise


@router.post("/auth/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification(
    request: ForgotPasswordRequest,  # Reuse - just needs email
    db: Session = Depends(get_db),
):
    """Resend email verification."""
    try:
        auth_service = AuthService(db)
        auth_service.resend_verification(request.email)
        
        return None
    except Exception as e:
        # Let the global exception handlers deal with known exceptions
        raise


# ========== Authenticated User Endpoints ==========

@router.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user profile with active membership context."""
    # Get memberships
    membership_service = MembershipService(db)
    memberships = membership_service.get_user_memberships(current_user.id, active_only=True)
    
    # Get active membership from refresh token (if available in request context)
    # For now, we'll use the first membership as active
    active_membership_id = None
    if memberships:
        active_membership_id = memberships[0].id
    
    # Build user profile with membership context
    profile = UserProfile.model_validate(current_user)
    
    # Add membership info to profile (extend the response)
    # Note: UserProfile doesn't have memberships field, so we'll add it via dict
    profile_dict = profile.model_dump()
    profile_dict['active_membership_id'] = str(active_membership_id) if active_membership_id else None
    profile_dict['memberships_count'] = len(memberships)
    
    return profile_dict


@router.put("/auth/me", response_model=UserResponse)
async def update_current_user_profile(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, request, current_user.id)
    
    return UserResponse.model_validate(updated_user)


@router.post("/auth/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change password (authenticated)."""
    user_service = UserService(db)
    user_service.change_password(
        current_user.id,
        request.current_password,
        request.new_password,
    )
    
    return None


# ========== Admin Endpoints ==========

# Super Admin - Organizations
@router.post("/admin/organizations", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    request: CreateOrganizationRequest,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Create organization (Super Admin only)."""
    tenant_service = TenantService(db)
    org, admin_user = tenant_service.create_organization(request, current_user.id)
    
    return TenantResponse.model_validate(org)


@router.get("/admin/organizations", response_model=List[TenantResponse])
async def list_organizations(
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """List all organizations (Super Admin only)."""
    from app.domains.auth.models import TenantType
    
    orgs = db.query(Tenant).filter(Tenant.type == TenantType.ORGANIZATION).all()
    return [TenantResponse.model_validate(org) for org in orgs]


# Super Admin - Super Admin Management
@router.post("/admin/super-admins", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_super_admin(
    request: CreateUserRequest,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Create a new super admin (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    user = super_admin_service.create_super_admin(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
        created_by=current_user.id,
    )
    
    return UserResponse.model_validate(user)


@router.get("/admin/super-admins", response_model=List[UserResponse])
async def list_super_admins(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """List all super admin users (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    users, total = super_admin_service.list_super_admins(
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
    )
    
    return [UserResponse.model_validate(user) for user in users]


@router.get("/admin/super-admins/{user_id}", response_model=UserResponse)
async def get_super_admin(
    user_id: UUID,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Get super admin details (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    user = super_admin_service.get_super_admin(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Super admin not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/admin/super-admins/{user_id}", response_model=UserResponse)
async def update_super_admin(
    user_id: UUID,
    request: UserUpdate,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Update super admin information (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    updated_user = super_admin_service.update_super_admin(
        user_id=user_id,
        request=request,
        updated_by=current_user.id,
    )
    
    return UserResponse.model_validate(updated_user)


@router.post("/admin/super-admins/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_super_admin_password(
    user_id: UUID,
    request: AdminChangePasswordRequest,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Change super admin password (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    super_admin_service.change_super_admin_password(
        user_id=user_id,
        new_password=request.new_password,
        changed_by=current_user.id,
    )
    
    return None


@router.delete("/admin/super-admins/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_super_admin(
    user_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Deactivate super admin (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    super_admin_service.deactivate_super_admin(
        user_id=user_id,
        deactivated_by=current_user.id,
        reason=reason,
    )
    
    return None


@router.post("/admin/super-admins/{user_id}/reactivate", response_model=UserResponse)
async def reactivate_super_admin(
    user_id: UUID,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Reactivate deactivated super admin (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    user = super_admin_service.reactivate_super_admin(
        user_id=user_id,
        reactivated_by=current_user.id,
    )
    
    return UserResponse.model_validate(user)


@router.delete("/admin/super-admins/{user_id}/role", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_super_admin_role(
    user_id: UUID,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    """Revoke super admin role from user (Super Admin only)."""
    super_admin_service = SuperAdminService(db)
    super_admin_service.revoke_super_admin_role(
        user_id=user_id,
        revoked_by=current_user.id,
    )
    
    return None


# Organization Admin - Institutions (formerly Schools)
@router.post("/admin/institutions", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_institution(
    request: CreateSchoolRequest,  # Keep old schema for backward compatibility
    current_user: User = Depends(require_role("org_admin")),
    db: Session = Depends(get_db),
):
    """Create institution (Organization Admin only)."""
    # Verify user's organization matches request
    if current_user.tenant_id != request.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create institutions in your organization",
        )
    
    tenant_service = TenantService(db)
    school, admin_user = tenant_service.create_school(request, current_user.id)  # Still uses create_school internally
    
    return TenantResponse.model_validate(school)


@router.get("/admin/institutions", response_model=List[TenantResponse])
async def list_institutions(
    current_user: User = Depends(require_role("org_admin")),
    db: Session = Depends(get_db),
):
    """List institutions in organization (Organization Admin only)."""
    from app.domains.auth.models import TenantType, Institution
    
    # Get organization from user's tenant
    org = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not org or org.type != TenantType.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an organization",
        )
    
    # Get institutions via organization_id
    institutions = db.query(Institution).filter(
        Institution.organization_id == org.id,
        Institution.is_active == True,
    ).all()
    
    # Convert to TenantResponse format (for backward compatibility)
    # In the future, we might return InstitutionResponse
    return [TenantResponse.model_validate(inst) for inst in institutions]


# Deprecated: Keep old endpoint for backward compatibility
@router.post("/admin/schools", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_school_deprecated(
    request: CreateSchoolRequest,
    current_user: User = Depends(require_role("org_admin")),
    db: Session = Depends(get_db),
):
    """Deprecated: Use /admin/institutions instead."""
    return await create_institution(request, current_user, db)


@router.get("/admin/schools", response_model=List[TenantResponse])
async def list_schools_deprecated(
    current_user: User = Depends(require_role("org_admin")),
    db: Session = Depends(get_db),
):
    """Deprecated: Use /admin/institutions instead."""
    return await list_institutions(current_user, db)


# Institution Admin - Users (formerly School Admin)
@router.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Create user (Institution Admin only)."""
    user_service = UserService(db)
    user = user_service.create_user(request, current_user.tenant_id, current_user.id)
    
    return UserResponse.model_validate(user)


@router.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[UserStatus] = None,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """List users in institution (Institution Admin only)."""
    user_service = UserService(db)
    users, total = user_service.list_users(
        current_user.tenant_id,
        skip=skip,
        limit=limit,
        status=status_filter,
    )
    
    return [UserResponse.model_validate(user) for user in users]


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Get user details (Institution Admin only)."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserResponse.model_validate(user)


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdate,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Update user (Institution Admin only)."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    updated_user = user_service.update_user(user_id, request, current_user.id)
    return UserResponse.model_validate(updated_user)


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Deactivate user (Institution Admin only)."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.status = UserStatus.INACTIVE
    db.commit()
    
    return None


@router.post("/admin/users/{user_id}/roles", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_role(
    user_id: UUID,
    request: AssignRoleRequest,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Assign role to user (Institution Admin only)."""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    rbac_service = RBACService(db)
    user_role = rbac_service.assign_role(
        user_id=user_id,
        role_id=request.role_id,
        tenant_id=current_user.tenant_id,
        granted_by=current_user.id,
        scope=request.scope,
    )
    
    return UserRoleResponse.model_validate(user_role)


@router.delete("/admin/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_role(
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Revoke role from user (Institution Admin only)."""
    from app.domains.auth.models import UserRole
    
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
        UserRole.tenant_id == current_user.tenant_id,
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    
    rbac_service = RBACService(db)
    rbac_service.revoke_role(user_role.id, current_user.id)
    
    return None


# ========== Deprecated Endpoint Wrappers ==========

@router.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_deprecated(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Deprecated: Use /auth/signup instead.
    This endpoint internally calls /auth/signup.
    """
    # Convert to signup request and call service directly
    signup_service = SignupService(db)
    payload = {
        "role": "teacher",  # Default role for basic registration
        "email": request.email,
        "password": request.password,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone": request.phone,
    }
    
    result = signup_service.route("teacher", payload)
    user = result['user']
    
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "user_id": str(user.id),
    }


@router.post("/auth/signup/teacher", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def teacher_signup(
    request: TeacherSignupRequest,
    db: Session = Depends(get_db),
):
    """
    Deprecated: Use /auth/signup with role=teacher instead.
    This endpoint internally calls /auth/signup.
    """
    signup_service = SignupService(db)
    payload = {
        "role": "teacher",
        "email": request.email,
        "password": request.password,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone": request.phone,
        "institution_code": request.school_code,  # Map school_code to institution_code
    }
    
    result = signup_service.route("teacher", payload)
    user = result['user']
    
    return UserResponse.model_validate(user)


@router.post("/auth/signup/student", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def student_signup(
    request: StudentSignupRequest,
    db: Session = Depends(get_db),
):
    """
    Deprecated: Use /auth/signup with role=student instead.
    This endpoint internally calls /auth/signup.
    """
    signup_service = SignupService(db)
    payload = {
        "role": "student",
        "email": request.email,
        "password": request.password,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone": request.phone,
        "institution_code": request.school_code,  # Map school_code to institution_code
    }
    
    result = signup_service.route("student", payload)
    user = result['user']
    
    return UserResponse.model_validate(user)


@router.post("/auth/signup/parent", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def parent_signup(
    request: ParentSignupRequest,
    db: Session = Depends(get_db),
):
    """
    Deprecated: Use /auth/signup with role=parent instead.
    This endpoint internally calls /auth/signup.
    """
    signup_service = SignupService(db)
    payload = {
        "role": "parent",
        "email": request.email,
        "password": request.password,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone": request.phone,
        "student_code": request.student_code,
    }
    
    result = signup_service.route("parent", payload)
    user = result['user']
    
    return UserResponse.model_validate(user)


@router.get("/auth/signup/approvals", response_model=List[SignupApprovalResponse])
async def list_pending_approvals(
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Get pending signup approvals (Institution Admin only)."""
    from app.domains.auth.models import Tenant
    
    pending_users = db.query(User).filter(
        User.tenant_id == current_user.tenant_id,
        User.status == UserStatus.PENDING_APPROVAL,
    ).all()
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    tenant_name = tenant.name if tenant else ""
    
    return [
        SignupApprovalResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
            created_at=user.created_at,
            tenant_id=user.tenant_id,
            tenant_name=tenant_name,
        )
        for user in pending_users
    ]


@router.post("/auth/signup/approve/{user_id}", response_model=UserResponse)
async def approve_signup(
    user_id: UUID,
    request: ApproveSignupRequest,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Approve signup request (Institution Admin only)."""
    registration_service = SelfRegistrationService(db)
    user = registration_service.approve_signup(user_id, current_user.id)
    
    return UserResponse.model_validate(user)


@router.post("/auth/signup/reject/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reject_signup(
    user_id: UUID,
    request: RejectSignupRequest,
    current_user: User = Depends(require_role("institution_admin")),  # Updated role
    db: Session = Depends(get_db),
):
    """Reject signup request (Institution Admin only)."""
    registration_service = SelfRegistrationService(db)
    registration_service.reject_signup(user_id, current_user.id, request.reason)
    
    return None

