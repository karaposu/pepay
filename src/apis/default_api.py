# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from my_package.apis.default_api_base import BaseDefaultApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from my_package.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated
from my_package.models.confirm_payment_post200_response import ConfirmPaymentPost200Response
from my_package.models.confirm_payment_post_request import ConfirmPaymentPostRequest
from my_package.models.exchange_rate_get200_response import ExchangeRateGet200Response
from my_package.models.feedback_post_request import FeedbackPostRequest
from my_package.models.generate_address_post200_response import GenerateAddressPost200Response
from my_package.models.payment_status_get200_response import PaymentStatusGet200Response
from my_package.models.purchase_post200_response import PurchasePost200Response
from my_package.models.purchase_post_request import PurchasePostRequest


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/admin",
    responses={
        200: {"description": "Admin data retrieved successfully."},
    },
    tags=["default"],
    summary="Admin Endpoint",
    response_model_by_alias=True,
)
async def admin_get(
) -> None:
    """Admin-only endpoint for monitoring and managing transactions and rates."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().admin_get()


@router.post(
    "/confirm-payment",
    responses={
        200: {"model": ConfirmPaymentPost200Response, "description": "Payment confirmation received."},
    },
    tags=["default"],
    summary="Confirm Payment",
    response_model_by_alias=True,
)
async def confirm_payment_post(
    confirm_payment_post_request: ConfirmPaymentPostRequest = Body(None, description=""),
) -> ConfirmPaymentPost200Response:
    """Confirms that the user has sent USDT and triggers payment validation."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().confirm_payment_post(confirm_payment_post_request)


@router.get(
    "/exchange-rate",
    responses={
        200: {"model": ExchangeRateGet200Response, "description": "Successful response with exchange rate."},
    },
    tags=["default"],
    summary="Get Exchange Rate",
    response_model_by_alias=True,
)
async def exchange_rate_get(
) -> ExchangeRateGet200Response:
    """Retrieves the latest exchange rate of USDT to PepeCoin."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().exchange_rate_get()


@router.post(
    "/feedback",
    responses={
        200: {"description": "Feedback received successfully."},
    },
    tags=["default"],
    summary="Feedback/Support",
    response_model_by_alias=True,
)
async def feedback_post(
    feedback_post_request: FeedbackPostRequest = Body(None, description=""),
) -> None:
    """Allows users to report issues or provide feedback."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().feedback_post(feedback_post_request)


@router.post(
    "/generate-address",
    responses={
        200: {"model": GenerateAddressPost200Response, "description": "Successful response with payment address."},
    },
    tags=["default"],
    summary="Generate Payment Address",
    response_model_by_alias=True,
)
async def generate_address_post(
) -> GenerateAddressPost200Response:
    """Generates a new USDT wallet address for a transaction."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().generate_address_post()


@router.get(
    "/payment-status",
    responses={
        200: {"model": PaymentStatusGet200Response, "description": "Payment status."},
    },
    tags=["default"],
    summary="Check Payment Status",
    response_model_by_alias=True,
)
async def payment_status_get(
    transaction_id: Annotated[StrictStr, Field(description="Transaction ID of the payment.")] = Query(None, description="Transaction ID of the payment.", alias="transactionId"),
) -> PaymentStatusGet200Response:
    """Returns the status of the user’s payment."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().payment_status_get(transaction_id)


@router.post(
    "/purchase",
    responses={
        200: {"model": PurchasePost200Response, "description": "Successful initiation of purchase."},
    },
    tags=["default"],
    summary="Initiate Purchase",
    response_model_by_alias=True,
)
async def purchase_post(
    purchase_post_request: PurchasePostRequest = Body(None, description=""),
) -> PurchasePost200Response:
    """Initiates a purchase of PepeCoin."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().purchase_post(purchase_post_request)
