from fastapi import APIRouter, HTTPException, status
from app.models.spl import SPLRequest, SPLResponse, SPLValidationResponse, RelevanceCheckResponse
from app.services.spl_service import SPLService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# SPL service will be initialized lazily
spl_service = None

def get_spl_service():
    global spl_service
    if spl_service is None:
        try:
            from app.services.spl_service import SPLService
            spl_service = SPLService()
            logger.info("SPL Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SPL Service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"SPL service initialization failed: {str(e)}"
            )
    return spl_service


@router.get("/companies")
async def get_companies():
    """Get list of companies for debugging"""
    service = get_spl_service()
    return {
        "companies": service.company_data,
        "total": len(service.company_data)
    }


@router.post("/generate-spl", response_model=SPLResponse)
async def generate_spl(request: SPLRequest):
    """
    Generate SPL query from natural language input
    """
    service = get_spl_service()
    
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        result = service.generate_spl_query(request.query, request.verbose)
        return result
    except Exception as e:
        logger.error(f"Error generating SPL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/check-relevance", response_model=RelevanceCheckResponse)
async def check_splunk_relevance(request: SPLRequest):
    """
    Check if the input query is Splunk-related
    """
    service = get_spl_service()
    
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        result = service.check_relevance(request.query)
        return result
    except Exception as e:
        logger.error(f"Error checking relevance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/validate-spl", response_model=SPLValidationResponse)
async def validate_spl_syntax(spl_query: str):
    """
    Validate SPL query syntax
    """
    service = get_spl_service()
    
    if not spl_query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SPL query cannot be empty"
        )
    
    try:
        issues = service.validate_spl_syntax(spl_query)
        return SPLValidationResponse(
            valid=len(issues) == 0,
            issues=issues,
            suggestions=[]  # Can be enhanced later
        )
    except Exception as e:
        logger.error(f"Error validating SPL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/service-status")
async def get_service_status():
    """
    Get SPL service status
    """
    try:
        service = get_spl_service()
        return {
            "spl_service_available": True,
            "groq_configured": service.client is not None,
            "embedding_model_loaded": hasattr(service, 'embedding_model'),
            "vector_store_initialized": hasattr(service, 'vectorstore_doc')
        }
    except Exception as e:
        return {
            "spl_service_available": False,
            "groq_configured": False,
            "embedding_model_loaded": False,
            "vector_store_initialized": False,
            "error": str(e)
        }
