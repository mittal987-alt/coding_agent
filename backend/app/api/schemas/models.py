from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.api.schemas.common import BaseSchema

class ModelCapability(BaseSchema):
    """
    Features supported by an LLM.
    """

    chat: bool = True

    streaming: bool = True

    function_calling: bool = False

    vision: bool = False

    audio: bool = False

    embeddings: bool = False

    reasoning: bool = False

    json_mode: bool = False
class ModelPricing(BaseSchema):

    input_cost_per_million: float

    output_cost_per_million: float

    currency: str = "USD"

class ContextWindow(BaseSchema):

    max_input_tokens: int

    max_output_tokens: int
class ModelInfo(BaseSchema):

    id: str

    provider: str

    display_name: str

    description: str | None = None

    version: str

    released_at: datetime | None = None

    context_window: ContextWindow

    capabilities: ModelCapability

    pricing: ModelPricing

    enabled: bool = True

class ModelListResponse(BaseSchema):

    models: list[ModelInfo]

class ProviderInfo(BaseSchema):

    name: str

    enabled: bool

    default_model: str

    models: list[str]

class ProviderListResponse(BaseSchema):

    providers: list[ProviderInfo]



class DefaultModelResponse(BaseSchema):

    model: str

class SetDefaultModelRequest(BaseSchema):

    model: str
class ProviderHealth(BaseSchema):

    provider: str

    healthy: bool

    latency_ms: float

    checked_at: datetime
class ProviderHealthResponse(BaseSchema):

    providers: list[ProviderHealth]
class TokenEstimateRequest(BaseSchema):

    model: str

    text: str
class TokenEstimateResponse(BaseSchema):

    estimated_tokens: int

class CostEstimateRequest(BaseSchema):

    model: str

    prompt_tokens: int

    completion_tokens: int
class CostEstimateResponse(BaseSchema):

    estimated_cost: float

    currency: str = "USD"

class BenchmarkRequest(BaseSchema):

    model: str

    prompt: str

class BenchmarkResult(BaseSchema):

    provider: str

    model: str

    latency_ms: float

    input_tokens: int

    output_tokens: int

    total_tokens: int

    estimated_cost: float

    success: bool
class BenchmarkResponse(BaseSchema):

    results: list[BenchmarkResult]
class ModelStatistics(BaseSchema):

    requests: int

    successful_requests: int

    failed_requests: int

    average_latency_ms: float

    total_tokens: int

    estimated_cost: float
class ProviderStatistics(BaseSchema):

    provider: str

    stats: ModelStatistics