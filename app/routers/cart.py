from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate, CartOut

router = APIRouter(prefix="/cart", tags=["Carrinho"])


def _get_or_create_cart(db: Session, user_id: int) -> Cart:
    """Busca o carrinho do usuário ou cria um novo caso não exista."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("/", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna o carrinho atual do usuário autenticado."""
    return _get_or_create_cart(db, current_user.id)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_item(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Adiciona um produto ao carrinho, validando o estoque disponível."""
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if product.stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {product.stock}",
        )

    cart = _get_or_create_cart(db, current_user.id)

    existing_item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == item_data.product_id)
        .first()
    )

    if existing_item:
        new_quantity = existing_item.quantity + item_data.quantity
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {product.stock}",
            )
        existing_item.quantity = new_quantity
    else:
        db.add(CartItem(cart_id=cart.id, product_id=item_data.product_id, quantity=item_data.quantity))

    db.commit()
    db.refresh(cart)
    return cart


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um item específico do carrinho."""
    cart = _get_or_create_cart(db, current_user.id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado no carrinho")

    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart