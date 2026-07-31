#
from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import LLMManagerDep

router = APIRouter()
@router.get(
    "/",
    summary="List available models",
)
async def models(
    llm: LLMManagerDep,
):

    return await llm.available_models()


@router.get("/providers")
async def providers(
    llm: LLMManagerDep,
):

    return await llm.providers()

@router.get("/providers/{provider}")
async def provider(
    provider: str,
    llm: LLMManagerDep,
):

    return await llm.provider_info(
        provider,
    )
@router.get("/default")
async def default_model(
    llm: LLMManagerDep,
):

    return {

        "default": await llm.default_model()
    }
@router.post("/default")
async def set_default_model(
    model: str,
    llm: LLMManagerDep,
):

    await llm.set_default_model(
        model,
    )

    return {
        "success": True,
    }                  
@router.get("/health")
async def model_health(
    llm: LLMManagerDep,
):

    return await llm.health()
@router.get("/providers/{provider}/health")
async def provider_health(
    provider: str,
    llm: LLMManagerDep,
):

    return await llm.provider_health(
        provider,
    )
@router.get("/{model_name}/capabilities")
async def capabilities(
    model_name: str,
    llm: LLMManagerDep,
):

    return await llm.capabilities(
        model_name,
    )
@router.post("/{model_name}/tokens")
async def estimate_tokens(
    model_name: str,
    text: str,
    llm: LLMManagerDep,
):

    return {

        "tokens": await llm.count_tokens(

            model_name,

            text,
        )
    }
@router.post("/benchmark")
async def benchmark(
    prompt: str,
    llm: LLMManagerDep,
):

    return await llm.benchmark(
        prompt,
    )