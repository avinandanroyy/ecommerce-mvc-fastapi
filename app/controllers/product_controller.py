from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Any

from app.services.product_service import ProductService
from app.core.deps import get_db, require_admin
from app.core.response import SuccessResponse, ErrorResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListWithPagination, ProductSearch

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
        
        return Response(
            content=SuccessResponse(
                data={"product": product_response.model_dump()},
                message="Product created successfully",
                code=201
            ).model_dump(),
            status_code=201,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Product creation failed",
                message=str(e),
                code=400
            ).model_dump(),
            status_code=400,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
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
        
        products_response = []
        for product in result["data"]:
            product_response = ProductListWithPagination(
                data=[{
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity,
                    "category_id": p.category_id,
                    "image_url": p.image_url,
                    "is_active": p.is_active,
                    "created_at": p.created_at
                } for p in result["data"]],
                total=result["meta"]["total"],
                page=result["meta"]["page"],
                page_size=result["meta"]["page_size"],
                total_pages=result["meta"]["total_pages"]
            )
            products_response.append(product_response.model_dump())
        
        return Response(
            content=SuccessResponse(
                data=result,
                message="Products retrieved successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
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
            return Response(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
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
        
        return Response(
            content=SuccessResponse(
                data={"product": product_response.model_dump()},
                message="Product retrieved successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
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
            return Response(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
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
        
        return Response(
            content=SuccessResponse(
                data={"product": product_response.model_dump()},
                message="Product retrieved successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
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
            return Response(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
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
        
        return Response(
            content=SuccessResponse(
                data={"product": product_response.model_dump()},
                message="Product updated successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        return Response(
            content=ErrorResponse(
                error="Product update failed",
                message=str(e),
                code=400
            ).model_dump(),
            status_code=400,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
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
            return Response(
                content=ErrorResponse(
                    error="Product not found",
                    message="Product does not exist",
                    code=404
                ).model_dump(),
                status_code=404,
                media_type="application/json"
            )
        
        return Response(
            content=SuccessResponse(
                data={},
                message="Product deleted successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
        )

@router.get("/top-rated", response_model=SuccessResponse)
async def get_top_rated_products(
    limit: int = 5,
    db: Session = Depends(get_db)
) -> Any:
    try:
        product_service = ProductService(db)
        products = product_service.get_top_rated_products(limit=limit)
        
        products_response = []
        for product in products:
            product_response = ProductListWithPagination(
                data=[{
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity,
                    "category_id": p.category_id,
                    "image_url": p.image_url,
                    "is_active": p.is_active,
                    "created_at": p.created_at
                } for p in products],
                total=len(products),
                page=1,
                page_size=limit,
                total_pages=1
            )
            products_response.append(product_response.model_dump())
        
        return Response(
            content=SuccessResponse(
                data={"products": products_response},
                message="Top rated products retrieved successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
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
        
        products_response = []
        for product in products:
            product_response = ProductListWithPagination(
                data=[{
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "stock_quantity": p.stock_quantity,
                    "category_id": p.category_id,
                    "image_url": p.image_url,
                    "is_active": p.is_active,
                    "created_at": p.created_at
                } for p in products],
                total=len(products),
                page=pagination.skip // pagination.limit + 1,
                page_size=pagination.limit,
                total_pages=(len(products) + pagination.limit - 1) // pagination.limit if products else 0
            )
            products_response.append(product_response.model_dump())
        
        return Response(
            content=SuccessResponse(
                data={"products": products_response, "total": len(products)},
                message="Products searched successfully",
                code=200
            ).model_dump(),
            status_code=200,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=ErrorResponse(
                error="Internal server error",
                message=str(e),
                code=500
            ).model_dump(),
            status_code=500,
            media_type="application/json"
        )
