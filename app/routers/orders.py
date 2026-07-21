from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.order import Order
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.services.order_service import create_order_from_cart

router = APIRouter(prefix="/orders", tags=["Pedidos"])


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Transforma o carrinho atual do usuário em um pedido."""
    return create_order_from_cart(db, current_user.id)


@router.get("/", response_model=list[OrderOut])
def list_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Lista os pedidos do usuário autenticado."""
    return db.query(Order).filter(Order.user_id == current_user.id).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detalha um pedido específico do usuário autenticado."""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order


@router.get("/admin/all", response_model=list[OrderOut])
def list_all_orders(db: Session = Depends(get_db), _admin=Depends(get_current_admin_user)):
    """Lista todos os pedidos da loja (somente admin)."""
    return db.query(Order).all()


@router.patch("/admin/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    """Atualiza o status de um pedido (somente admin)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    order.status = status_data.status
    db.commit()
    db.refresh(order)
    return order