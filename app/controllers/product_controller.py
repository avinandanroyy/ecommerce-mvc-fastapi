from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.services.product_service import ProductService
from app.core.database import get_db
from app.core.deps import require_admin
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.pagination import PaginationParams
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductSearch

router = APIRouter(prefix="/api/v1/products", tags=["Products"])

@router.post("/", response_model=SuccessResponse)
async def create_product(
    product_data: ProductCreate,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        product = product_service.create(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category_id=product_data.category_id
        )
        
        product_response = ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id,
            image_url=product.image_url,
            slug=product.slug,
            is_active=product.is_active,
            is_deleted=product.is_deleted,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"product": product_response.model_dump(mode="json")},
                message="Product created successfully",
                code=201
            ).model_dump(mode="json"),
            status_code=201
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Product creation failed",
                message=str(e),
                code=400
            ).model_dump(mode="json"),
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

@router.get("/", response_model=SuccessResponse)
async def list_products(
    skip: int = 0,
    limit: int = 10,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        result = product_service.list_all_with_pagination(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price
        )
        
        products_data = []
        for product in result["data"]:
            products_data.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock_quantity": product.stock_quantity,
                "category_id": product.category_id,
                "image_url": product.image_url,
                "is_active": product.is_active,
                "created_at": product.created_at
            })
        
        return JSONResponse(
            content=SuccessResponse(
                data={
                    "products": products_data,
                    "total": result["meta"]["total"],
                    "page": result["meta"]["page"],
                    "page_size": result["meta"]["page_size"],
                    "total_pages": result["meta"]["total_pages"]
                },
                message="Products retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

@router.get("/{product_id}", response_model=SuccessResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        product = product_service.get_by_id(product_id)
        
        if not product:
            return JSONResponse(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        product_response = ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id,
            image_url=product.image_url,
            slug=product.slug,
            is_active=product.is_active,
            is_deleted=product.is_deleted,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"product": product_response.model_dump(mode="json")},
                message="Product retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

@router.get("/slug/{slug}", response_model=SuccessResponse)
async def get_product_by_slug(
    slug: str,
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        product = product_service.get_by_slug(slug)
        
        if not product:
            return JSONResponse(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        product_response = ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id,
            image_url=product.image_url,
            slug=product.slug,
            is_active=product.is_active,
            is_deleted=product.is_deleted,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"product": product_response.model_dump(mode="json")},
                message="Product retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

@router.put("/{product_id}", response_model=SuccessResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        product = product_service.update(
            product_id=product_id,
            **product_data.model_dump(exclude_unset=True)
        )
        
        if not product:
            return JSONResponse(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        product_response = ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category_id=product.category_id,
            image_url=product.image_url,
            slug=product.slug,
            is_active=product.is_active,
            is_deleted=product.is_deleted,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        
        return JSONResponse(
            content=SuccessResponse(
                data={"product": product_response.model_dump(mode="json")},
                message="Product updated successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except ValueError as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Product update failed",
                message=str(e),
                code=400
            ).model_dump(mode="json"),
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(
    product_id: int,
    auth_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        success = product_service.delete(product_id)
        
        if not success:
            return JSONResponse(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(mode="json"),
                status_code=404
            )
        
        return JSONResponse(
            content=SuccessResponse(
                data={},
                message="Product deleted successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

@router.get("/top-rated", response_model=SuccessResponse)
async def get_top_rated_products(
    limit: int = 5,
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        products = product_service.get_top_rated_products(limit=limit)
        
        products_data = []
        for product in products:
            products_data.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock_quantity": product.stock_quantity,
                "category_id": product.category_id,
                "image_url": product.image_url,
                "is_active": product.is_active,
                "created_at": product.created_at
            })
        
        return JSONResponse(
            content=SuccessResponse(
                data={"products": products_data},
                message="Top rated products retrieved successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )

@router.get("/search", response_model=SuccessResponse)
async def search_products(
    query: str,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        products = product_service.search(query=query, skip=pagination.skip, limit=pagination.limit)
        
        products_data = [{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock_quantity": p.stock_quantity,
            "category_id": p.category_id,
            "image_url": p.image_url,
            "is_active": p.is_active,
            "created_at": p.created_at
        } for p in products]

        return JSONResponse(
            content=SuccessResponse(
                data={
                    "products": products_data,
                    "total": len(products),
                    "page": pagination.skip // pagination.limit + 1 if pagination.limit else 1,
                    "page_size": pagination.limit,
                    "total_pages": (len(products) + pagination.limit - 1) // pagination.limit if products and pagination.limit else 0
                },
                message="Products searched successfully",
                code=200
            ).model_dump(mode="json"),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(mode="json"),
            status_code=500
        )
