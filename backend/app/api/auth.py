from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.farmer import Farmer, UserRole
from backend.app.schemas.farmer import FarmerCreate, FarmerLogin, FarmerResponse, Token, TokenData

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-form")

# Helper function to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Farmer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        mobile: str = payload.get("sub")
        role: str = payload.get("role")
        if mobile is None:
            raise credentials_exception
        token_data = TokenData(mobile=mobile, role=role)
    except JWTError:
        raise credentials_exception
        
    user = db.query(Farmer).filter(Farmer.mobile == token_data.mobile).first()
    if user is None:
        raise credentials_exception
    return user

# Helper to check if role is Admin
def get_current_admin(current_user: Farmer = Depends(get_current_user)) -> Farmer:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

# Helper to check if role is Admin or Sales Team
def get_current_sales_or_admin(current_user: Farmer = Depends(get_current_user)) -> Farmer:
    if current_user.role not in [UserRole.ADMIN, UserRole.SALES_TEAM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

@router.post("/register", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
def register(farmer_in: FarmerCreate, db: Session = Depends(get_db)):
    """
    Register a new farmer, admin, or sales team member.
    """
    db_user = db.query(Farmer).filter(Farmer.mobile == farmer_in.mobile).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )
    
    hashed_password = get_password_hash(farmer_in.password)
    db_farmer = Farmer(
        name=farmer_in.name,
        mobile=farmer_in.mobile,
        hashed_password=hashed_password,
        role=farmer_in.role,
        district=farmer_in.district,
        state=farmer_in.state,
        language=farmer_in.language
    )
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer

@router.post("/login", response_model=Token)
def login(login_in: FarmerLogin, db: Session = Depends(get_db)):
    """
    Login endpoint using raw JSON. Returns a JWT access token.
    """
    farmer = db.query(Farmer).filter(Farmer.mobile == login_in.mobile).first()
    if not farmer or not verify_password(login_in.password, farmer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile number or password"
        )
    
    access_token = create_access_token(subject=farmer.mobile, role=farmer.role.value)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": farmer.role.value
    }

# Standard form-url-encoded login for FastAPI Swagger OAuth2 integration
from fastapi.security import OAuth2PasswordRequestForm
@router.post("/login-form", response_model=Token, include_in_schema=False)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    farmer = db.query(Farmer).filter(Farmer.mobile == form_data.username).first()
    if not farmer or not verify_password(form_data.password, farmer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile number or password"
        )
    access_token = create_access_token(subject=farmer.mobile, role=farmer.role.value)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": farmer.role.value
    }

@router.get("/me", response_model=FarmerResponse)
def get_me(current_user: Farmer = Depends(get_current_user)):
    """
    Get current logged in user details.
    """
    return current_user
