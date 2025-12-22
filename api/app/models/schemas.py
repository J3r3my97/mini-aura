"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class SubscriptionTier(str, Enum):
    """Subscription tier enum"""
    FREE = "free"
    STARTER = "starter"
    CREATOR = "creator"
    PRO = "pro"


class JobStatus(str, Enum):
    """Job status enum"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Generate Endpoint Models
class GenerateResponse(BaseModel):
    """Response from /api/generate"""
    job_id: str
    status: JobStatus
    message: str = "Job created successfully"


# Job Endpoint Models
class JobMetadata(BaseModel):
    """Job metadata"""
    detected_colors: List[str] = []
    generated_prompt: Optional[str] = None
    style: str = "lego"
    processing_time_ms: Optional[int] = None
    avatar_url: Optional[str] = None  # Isolated avatar for customization


class JobResponse(BaseModel):
    """Response from /api/jobs/{job_id}"""
    job_id: str
    user_id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    input_image_url: Optional[str] = None
    output_image_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[JobMetadata] = None


class JobListResponse(BaseModel):
    """Response from /api/jobs (list)"""
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int


# User Endpoint Models
class UserProfile(BaseModel):
    """User profile"""
    user_id: str
    email: str
    subscription_tier: SubscriptionTier
    usage_count: int
    usage_limit: int
    created_at: datetime
    last_login: Optional[datetime] = None


class UsageResponse(BaseModel):
    """Response from /api/user/usage"""
    usage_count: int
    usage_limit: int
    subscription_tier: SubscriptionTier
    remaining: int


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None


# Payment Models
class CheckoutSessionRequest(BaseModel):
    """Request to create checkout session for credit purchase"""
    package: Literal["1_credit", "5_credits", "10_credits"] = Field(
        ...,
        description="Credit package to purchase: '1_credit', '5_credits', or '10_credits'"
    )
    success_url: Optional[str] = Field(
        None,
        description="Custom success redirect URL (for Vercel preview deployments)"
    )
    cancel_url: Optional[str] = Field(
        None,
        description="Custom cancel redirect URL (for Vercel preview deployments)"
    )


class CheckoutSessionResponse(BaseModel):
    """Response from creating checkout session"""
    session_id: str
    url: str


class SubscriptionStatus(BaseModel):
    """User's current credit balance and usage"""
    user_id: str
    credits: int  # Available credits
    free_credits_used: int  # How many free credits used
    total_generated: int  # Total avatars generated (all time)
    has_watermark: bool  # True if using free credits
