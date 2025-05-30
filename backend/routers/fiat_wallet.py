from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..core.security import get_current_user, get_current_active_user
from ..database import get_db
import logging

# Set up logging
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="",
    tags=['fiat_wallets'],
    responses={404: {"description": "Not found"}},
    redirect_slashes=False  # Handle both with and without trailing slashes
)

@router.post("/", response_model=schemas.FiatWalletResponse, status_code=status.HTTP_201_CREATED)
def create_fiat_wallet(
    wallet: schemas.FiatWalletCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new fiat wallet for the current user.
    """
    # Check if user already has a wallet with this currency
    existing_wallet = db.query(models.FiatWallet).filter(
        models.FiatWallet.user_id == current_user.id,
        models.FiatWallet.currency == wallet.currency
    ).first()
    
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have a {wallet.currency.value} wallet"
        )
    
    # If this is the first wallet, set it as primary
    is_first_wallet = not db.query(models.FiatWallet).filter(
        models.FiatWallet.user_id == current_user.id
    ).first()
    
    new_wallet = models.FiatWallet(
        **wallet.dict(),
        user_id=current_user.id,
        is_primary=is_first_wallet
    )
    
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    
    return {"data": new_wallet}

@router.get("/", response_model=schemas.FiatWalletListResponse)
def get_user_fiat_wallets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all fiat wallets for the current user.
    """
    wallets = db.query(models.FiatWallet).filter(
        models.FiatWallet.user_id == current_user.id
    ).all()
    
    return {"data": wallets}

@router.get("/{wallet_id}", response_model=schemas.FiatWalletResponse)
def get_fiat_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a specific fiat wallet by ID.
    """
    wallet = db.query(models.FiatWallet).filter(
        models.FiatWallet.id == wallet_id,
        models.FiatWallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    return {"data": wallet}

@router.patch("/{wallet_id}", response_model=schemas.FiatWalletResponse)
def update_fiat_wallet(
    wallet_id: int,
    wallet_updates: schemas.FiatWalletUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a fiat wallet's details.
    """
    wallet_query = db.query(models.FiatWallet).filter(
        models.FiatWallet.id == wallet_id,
        models.FiatWallet.user_id == current_user.id
    )
    
    wallet = wallet_query.first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    update_data = wallet_updates.dict(exclude_unset=True)
    
    # If setting as primary, unset primary status from other wallets
    if update_data.get('is_primary', False):
        db.query(models.FiatWallet).filter(
            models.FiatWallet.user_id == current_user.id,
            models.FiatWallet.id != wallet_id
        ).update({"is_primary": False})
    
    wallet_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(wallet)
    
    return {"data": wallet}

@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fiat_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a fiat wallet.
    """
    wallet = db.query(models.FiatWallet).filter(
        models.FiatWallet.id == wallet_id,
        models.FiatWallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Prevent deletion if it's the only wallet
    wallet_count = db.query(models.FiatWallet).filter(
        models.FiatWallet.user_id == current_user.id
    ).count()
    
    if wallet_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your only wallet"
        )
    
    db.delete(wallet)
    db.commit()
    
    return None
