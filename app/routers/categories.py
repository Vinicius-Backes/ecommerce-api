from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.category import Category
from app.schemas.product import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Lista todas as categorias (acesso público)."""
    return db.query(Category).all()


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    """Cria uma nova categoria (somente admin)."""
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Categoria já existe")

    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    """Remove uma categoria (somente admin)."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    db.delete(category)
    db.commit()