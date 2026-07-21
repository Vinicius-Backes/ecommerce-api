from pydantic import BaseModel, ConfigDict

from app.schemas.product import ProductOut


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class CartOut(BaseModel):
    id: int
    items: list[CartItemOut] = []

    model_config = ConfigDict(from_attributes=True)