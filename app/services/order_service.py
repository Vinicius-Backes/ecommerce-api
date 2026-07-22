from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product


def create_order_from_cart(db: Session, user_id: int) -> Order:
    """
    Converte o carrinho do usuário em um pedido:
    - valida estoque de cada item
    - dá baixa no estoque
    - calcula o total
    - esvazia o carrinho
    Tudo dentro de uma única transação.
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Carrinho vazio")

    order = Order(user_id=user_id, status=OrderStatus.PENDING, total=0)
    db.add(order)
    db.flush()  # gera o order.id sem commitar ainda

    total = 0.0

    for cart_item in cart.items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).with_for_update().first()

        if not product or product.stock < cart_item.quantity:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto '{product.name if product else cart_item.product_id}'",
            )

        # Baixa de estoque
        product.stock -= cart_item.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            unit_price=product.price,
        )
        db.add(order_item)

        total += product.price * cart_item.quantity

    order.total = total

    # Esvazia o carrinho após confirmar o pedido
    for cart_item in list(cart.items):
        db.delete(cart_item)

    db.commit()
    db.refresh(order)
    return order