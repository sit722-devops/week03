# week03/example-1/backend/product_service/app/main.py

"""
FastAPI Product Service API.
Manages product information including creation, retrieval, updates, deletion,
and stock management. This service demonstrates a structured approach with
separate database models and Pydantic schemas.
"""
import os
import logging
import sys
import time
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Product
from .schemas import ProductCreate, ProductResponse, ProductUpdate

# -----------------------------
# Configure Logging
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Suppress noisy logs from third-party libraries for cleaner output
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

# Lood envrionment vairables
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_STORAGE_CONTAINER_NAME = os.getenv(
    "AZURE_STORAGE_CONTAINER_NAME", "product-images"
)
AZURE_SAS_TOKEN_EXPIRY_HOURS = int(os.getenv("AZURE_SAS_TOKEN_EXPIRY_HOURS", "24"))

# Initialize BlobServiceClient
if AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY:
    logger.info("Product Service: Azure environment variables populated correctly.")
else:
    logger.info("Product Service: Azure environment variables **NOT SET**")


# -----------------------------
# FastAPI App Initialization
# -----------------------------
app = FastAPI(
    title="Product Service API",
    description="Manages products and stock for mini-ecommerce app",
    version="1.0.0",
)

# Enable CORS (for frontend dev/testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- FastAPI Event Handlers ---
@app.on_event("startup")
async def startup_event():
    """
    Handles application startup events.
    Ensures database tables are created (if not exist).
    Includes a retry mechanism for database connection robustness.
    """
    max_retries = 10
    retry_delay_seconds = 5
    for i in range(max_retries):
        try:
            logger.info(
                f"Attempting to connect to PostgreSQL and create tables (attempt {i+1}/{max_retries})..."
            )
            Base.metadata.create_all(bind=engine)
            logger.info(
                "Successfully connected to PostgreSQL and ensured tables exist."
            )
            break  # Exit loop if successful
        except OperationalError as e:
            logger.warning(f"Failed to connect to PostgreSQL: {e}")
            if i < max_retries - 1:
                logger.info(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                logger.critical(
                    f"Failed to connect to PostgreSQL after {max_retries} attempts. Exiting application."
                )
                sys.exit(1)  # Critical failure: exit if DB connection is unavailable
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred during database startup: {e}",
                exc_info=True,
            )
            sys.exit(1)


# --- Root Endpoint ---
@app.get("/", status_code=status.HTTP_200_OK, summary="Root endpoint")
async def read_root():
    """
    Returns a welcome message for the Product Service.
    """
    return {"message": "Welcome to the Product Service!"}


# --- Health Check Endpoint ---
@app.get("/health", status_code=status.HTTP_200_OK, summary="Health check endpoint")
async def health_check():
    """
    A simple health check endpoint to verify the service is running.
    Returns 200 OK if the service is alive.
    """
    return {"status": "ok", "service": "product-service"}


# -----------------------------
# CRUD Endpoints
# -----------------------------


@app.post(
    "/products/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a new product entry in the database.

    - Takes a `ProductCreate` schema as input, ensuring validation of name, description, price, and stock.
    - Returns the created product's details, including its auto-generated `product_id` and timestamps.
    """
    logging.info(f"Creating product: {product.name}")
    try:
        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logging.info(
            f"Product '{db_product.name}' (ID: {db_product.product_id}) created successfully."
        )
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create product.",
        )


@app.get(
    "/products/",
    response_model=List[ProductResponse],
    summary="List all products with pagination and search",
)
def list_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip (for pagination)."),
    limit: int = Query(
        100,
        ge=1,
        le=100,
        description="Maximum number of items to return (for pagination).",
    ),
    search: str = Query(
        None,
        max_length=255,
        description="Search term for product name or description (case-insensitive).",
    ),
):
    """
    Retrieves a list of products from the database.

    - Supports pagination via `skip` and `limit` query parameters.
    - Allows searching products by `name` or `description` using a case-insensitive partial match.
    - Returns a list of `ProductResponse` objects.
    """
    logging.info(f"Listing products with skip={skip}, limit={limit}, search='{search}'")
    query = db.query(Product)
    if search:
        search_pattern = f"%{search}%"
        logging.info(f"Applying search filter for term: {search}")
        query = query.filter(
            (Product.name.ilike(search_pattern))
            | (Product.description.ilike(search_pattern))
        )
    products = query.offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(products)} products (skip={skip}, limit={limit}).")
    return products


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Retrieve a product by ID",
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieves details of a single product by its unique ID.

    - Returns a `ProductResponse` object if the product is found.
    - Raises a 404 HTTP exception if the product does not exist.
    """
    logging.info(f"Fetching product with ID: {product_id}")
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        logging.warning(f"Product with ID: {product_id} not found.")
        raise HTTPException(status_code=404, detail="Product not found")
    logging.info(f"Product '{product.name}' (ID: {product_id}) retrieved.")
    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Update an existing product",
)
async def update_product(
    product_id: int, updated: ProductUpdate, db: Session = Depends(get_db)
):
    """
    Updates existing product information in the database.

    - Takes a `ProductUpdate` schema, allowing only specified fields to be updated.
    - Returns the updated product's details.
    - Raises a 404 HTTP exception if the product does not exist.
    """
    logging.info(
        f"Updating product with ID: {product_id} with data: {updated.model_dump(exclude_unset=True)}"
    )
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        logging.warning(f"Product with ID: {product_id} not found for update.")
        raise HTTPException(status_code=404, detail="Product not found")

    # Iterate over fields in the updated schema that were actually provided
    for field, value in updated.dict(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        logging.info(
            f"Product '{product.name}' (ID: {product_id}) updated successfully."
        )
        return product
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update product.",
        )


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product by ID",
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Deletes a product from the database by its unique ID.

    - Returns a 204 No Content status code upon successful deletion.
    - Raises a 404 HTTP exception if the product does not exist.
    """
    logging.info(f"Attempting to delete product with ID: {product_id}")
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        logging.warning(f"Product with ID: {product_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        db.delete(product)
        db.commit()
        logging.info(f"Product (ID: {product_id}) deleted successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting product {product_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the product.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
