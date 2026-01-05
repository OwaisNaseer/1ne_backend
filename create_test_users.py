"""
Script to create test users with different roles for development and testing.
"""
import sys
import io
from sqlalchemy.orm import Session

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from app.db.session import SessionLocal
from app.domains.auth.models import Tenant, TenantType, Role, RoleName, User
from app.domains.auth.services import UserService, TenantService, SuperAdminService
from app.domains.auth.schemas import CreateUserRequest
from app.core.logging import get_logger

logger = get_logger(__name__)

# Test user credentials
TEST_USERS = [
    {
        "email": "admin@1ne.ai",
        "password": "Admin123!@#",
        "first_name": "Super",
        "last_name": "Admin",
        "role": "super_admin",
    },
    {
        "email": "orgadmin@1ne.ai",
        "password": "OrgAdmin123!@#",
        "first_name": "Organization",
        "last_name": "Admin",
        "role": "org_admin",
    },
    {
        "email": "schooladmin@1ne.ai",
        "password": "SchoolAdmin123!@#",
        "first_name": "School",
        "last_name": "Admin",
        "role": "school_admin",
    },
    {
        "email": "teacher@1ne.ai",
        "password": "Teacher123!@#",
        "first_name": "John",
        "last_name": "Teacher",
        "role": "teacher",
    },
    {
        "email": "student@1ne.ai",
        "password": "Student123!@#",
        "first_name": "Jane",
        "last_name": "Student",
        "role": "student",
    },
    {
        "email": "parent@1ne.ai",
        "password": "Parent123!@#",
        "first_name": "Mary",
        "last_name": "Parent",
        "role": "parent",
    },
]


def create_test_users(db: Session):
    """Create all test users."""
    print("=" * 70)
    print("Creating Test Users")
    print("=" * 70)
    print()
    
    # Get platform tenant
    platform = db.query(Tenant).filter(Tenant.type == TenantType.PLATFORM).first()
    if not platform:
        print("❌ Platform tenant not found. Run: python -m app.seed.cli --auth")
        return
    
    # Create organization and school for org_admin and school_admin
    org = None
    school = None
    
    try:
        # Create organization for org_admin
        tenant_service = TenantService(db)
        from app.domains.auth.schemas import CreateOrganizationRequest
        
        org_request = CreateOrganizationRequest(
            name="Test Organization",
            slug="test-org",
            admin_email="orgadmin@1ne.ai",
            admin_first_name="Organization",
            admin_last_name="Admin",
            admin_password="OrgAdmin123!@#",
        )
        
        try:
            org, org_admin_user = tenant_service.create_organization(org_request, None)
            print(f"✅ Created organization: {org.name}")
            print(f"   Organization admin: {org_admin_user.email}")
        except Exception as e:
            # Organization might already exist, try to find it
            org = db.query(Tenant).filter(
                Tenant.type == TenantType.ORGANIZATION,
                Tenant.slug == "test-org"
            ).first()
            if org:
                print(f"ℹ️  Organization already exists: {org.name}")
            else:
                print(f"⚠️  Could not create organization: {e}")
        
        # Create school for school_admin
        if org:
            from app.domains.auth.schemas import CreateSchoolRequest
            
            school_request = CreateSchoolRequest(
                name="Test School",
                slug="test-school",
                organization_id=org.id,
                admin_email="schooladmin@1ne.ai",
                admin_first_name="School",
                admin_last_name="Admin",
                admin_password="SchoolAdmin123!@#",
            )
            
            try:
                school, school_admin_user = tenant_service.create_school(school_request, None)
                print(f"✅ Created school: {school.name}")
                print(f"   School admin: {school_admin_user.email}")
            except Exception as e:
                # School might already exist
                school = db.query(Tenant).filter(
                    Tenant.type == TenantType.SCHOOL,
                    Tenant.slug == "test-school"
                ).first()
                if school:
                    print(f"ℹ️  School already exists: {school.name}")
                else:
                    print(f"⚠️  Could not create school: {e}")
        
        print()
        
        # Create users
        user_service = UserService(db)
        created_users = []
        
        for user_data in TEST_USERS:
            email = user_data["email"]
            role_name = RoleName[user_data["role"].upper()]
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email.lower()).first()
            if existing_user:
                print(f"ℹ️  User already exists: {email}")
                created_users.append({
                    "email": email,
                    "password": user_data["password"],
                    "role": user_data["role"],
                    "status": "existing"
                })
                continue
            
            # Determine tenant_id based on role
            if role_name == RoleName.SUPER_ADMIN:
                tenant_id = platform.id
            elif role_name == RoleName.ORG_ADMIN:
                tenant_id = org.id if org else platform.id
            elif role_name in [RoleName.SCHOOL_ADMIN, RoleName.TEACHER, RoleName.STUDENT, RoleName.PARENT]:
                tenant_id = school.id if school else platform.id
            else:
                tenant_id = platform.id
            
            try:
                # For super_admin, use SuperAdminService
                if role_name == RoleName.SUPER_ADMIN:
                    super_admin_service = SuperAdminService(db)
                    user = super_admin_service.create_super_admin(
                        email=email,
                        password=user_data["password"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        created_by=None,
                    )
                else:
                    # For other roles, use UserService
                    user = user_service.create_user(
                        CreateUserRequest(
                            email=email,
                            password=user_data["password"],
                            first_name=user_data["first_name"],
                            last_name=user_data["last_name"],
                            role_name=role_name,
                        ),
                        tenant_id=tenant_id,
                        created_by=None,
                    )
                
                print(f"✅ Created user: {email} ({user_data['role']})")
                created_users.append({
                    "email": email,
                    "password": user_data["password"],
                    "role": user_data["role"],
                    "status": "created"
                })
            except Exception as e:
                print(f"❌ Failed to create {email}: {e}")
                continue
        
        print()
        print("=" * 70)
        print("Test Users Summary")
        print("=" * 70)
        print()
        
        for user_info in created_users:
            status_icon = "✅" if user_info["status"] == "created" else "ℹ️"
            print(f"{status_icon} {user_info['role'].upper():15} | {user_info['email']:25} | {user_info['password']}")
        
        print()
        print("=" * 70)
        print("Credentials")
        print("=" * 70)
        print()
        
        for user_info in created_users:
            print(f"\n{user_info['role'].upper().replace('_', ' ')}:")
            print(f"  Email:    {user_info['email']}")
            print(f"  Password: {user_info['password']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return
    
    print()
    print("✅ All test users created successfully!")
    print()
    print("⚠️  IMPORTANT: Change passwords after first login!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_test_users(db)
    finally:
        db.close()
