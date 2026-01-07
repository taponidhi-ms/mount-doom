from fastapi import APIRouter
from app.models.shared import AvailableModelsResponse, ModelInfo
from app.core.config import settings

router = APIRouter(prefix="/models", tags=["Models"])

@router.get("", response_model=AvailableModelsResponse)
async def get_available_models():
    """Get list of all available model deployments."""
    models_data = settings.get_models()
    
    models = [
        ModelInfo(
            model_deployment_name=model["model_deployment_name"],
            display_name=model["display_name"],
            description=model.get("description", "")
        )
        for model in models_data
    ]
    
    return AvailableModelsResponse(models=models)
