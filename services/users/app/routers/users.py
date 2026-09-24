# services/users/app/routers/users.py
from app.security import create_access_token, get_current_user, verify_reset_token
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import models, schemas
from app.database import get_db

router = APIRouter()

# Setup for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register", response_model=models.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: models.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(schemas.User).filter(schemas.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump(exclude={"password"})
    new_user = schemas.User(**user_data, password_hash=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
async def login(credentials: models.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(schemas.User).filter(schemas.User.email == credentials.email).first()
    
    
    if not db_user or not verify_password(credentials.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": db_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=models.UserResponse)
async def get_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.put("/me")
async def update_me(update_data: models.UserUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No update data provided")
        
    for key, value in update_dict.items():
        setattr(current_user, key, value)
        
    db.commit()
    db.refresh(current_user)
    
    return {"updated": True, "user": current_user}


@router.post("/password-recovery", status_code=status.HTTP_202_ACCEPTED)
async def recover_password(recovery_data: models.PasswordRecovery, db: Session = Depends(get_db)):
    user = db.query(schemas.User).filter(schemas.User.email == recovery_data.email).first()
    
    if user:
        reset_token = create_access_token(data={"sub": user.id, "type": "reset"})
        print("\n" + "="*50)
        print(f"SIMULACIÓN DE CORREO PARA: {user.email}")
        print(f"Tu token de recuperación es:\n{reset_token}")
        print("="*50 + "\n")
        
    return {"message": "If the email exists, a recovery link has been sent."}


@router.post("/password-reset")
async def reset_password(reset_data: models.PasswordReset, db: Session = Depends(get_db)):
    user_id = verify_reset_token(reset_data.token)
    if not user_id:

        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(schemas.User).filter(schemas.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = get_password_hash(reset_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}