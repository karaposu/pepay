# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

# from apis.buy_pepecoin_api_base import BaseBuyPepecoinApi
import impl

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

from models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from typing import Any, Optional, Tuple, Union
from typing_extensions import Annotated
from models.buy_pepecoin_dispute_post200_response import BuyPepecoinDisputePost200Response
from models.buy_pepecoin_order_confirm_manual_post200_response import BuyPepecoinOrderConfirmManualPost200Response
from models.buy_pepecoin_order_confirm_manual_post_request import BuyPepecoinOrderConfirmManualPostRequest
from models.buy_pepecoin_order_hash_cancel_post200_response import BuyPepecoinOrderHashCancelPost200Response
from models.buy_pepecoin_order_hash_get200_response import BuyPepecoinOrderHashGet200Response
from models.buy_pepecoin_order_post200_response import BuyPepecoinOrderPost200Response
from models.buy_pepecoin_order_post_request import BuyPepecoinOrderPostRequest


router = APIRouter()

ns_pkg = impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/buy-pepecoin/dispute",
    responses={
        200: {"model": BuyPepecoinDisputePost200Response, "description": "Dispute has been filed"},
    },
    tags=["buy_pepecoin"],
    summary="File a dispute for a transaction",
    response_model_by_alias=True,
)
async def buy_pepecoin_dispute_post(
    date_period: Annotated[Optional[StrictStr], Field(description="The date (or date range) the user made the transfer")] = Form(None, description="The date (or date range) the user made the transfer"),
    amount_sent: Annotated[Optional[Union[StrictFloat, StrictInt]], Field(description="How much USDT the user actually sent")] = Form(None, description="How much USDT the user actually sent"),
    error_screenshot: Annotated[Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]], Field(description="Screenshot or image file showing the error encountered")] = Form(None, description="Screenshot or image file showing the error encountered"),
    contact_email: Annotated[Optional[StrictStr], Field(description="Email address to reach the user")] = Form(None, description="Email address to reach the user"),
    contact_phone: Annotated[Optional[StrictStr], Field(description="Phone number to reach the user")] = Form(None, description="Phone number to reach the user"),
    contact_telegram: Annotated[Optional[StrictStr], Field(description="Telegram handle to reach the user")] = Form(None, description="Telegram handle to reach the user"),
) -> BuyPepecoinDisputePost200Response:
    """Allows the user to dispute an issue with their transaction by providing details and optional evidence (e.g., screenshot)."""
    if not BaseBuyPepecoinApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBuyPepecoinApi.subclasses[0]().buy_pepecoin_dispute_post(date_period, amount_sent, error_screenshot, contact_email, contact_phone, contact_telegram)


@router.post(
    "/buy-pepecoin/order/confirm_manual",
    responses={
        200: {"model": BuyPepecoinOrderConfirmManualPost200Response, "description": "waiting for the payment."},
    },
    tags=["buy_pepecoin"],
    summary="Confirm the user’s payment for the PepeCoin buy request",
    response_model_by_alias=True,
)
async def buy_pepecoin_order_confirm_manual_post(
    buy_pepecoin_order_confirm_manual_post_request: BuyPepecoinOrderConfirmManualPostRequest = Body(None, description=""),
) -> BuyPepecoinOrderConfirmManualPost200Response:
    """Called when the user has submitted the payment in the frontend."""
    if not BaseBuyPepecoinApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBuyPepecoinApi.subclasses[0]().buy_pepecoin_order_confirm_manual_post(buy_pepecoin_order_confirm_manual_post_request)


@router.post(
    "/buy-pepecoin/{order_hash}/cancel",
    responses={
        200: {"model": BuyPepecoinOrderHashCancelPost200Response, "description": "Successfully canceled"},
        400: {"description": "Unable to cancel (e.g., if already paid or completed)"},
        404: {"description": "Buy request not found"},
    },
    tags=["buy_pepecoin"],
    summary="Cancel a buy request",
    response_model_by_alias=True,
)
async def buy_pepecoin_order_hash_cancel_post(
    order_hash: Annotated[StrictStr, Field(description="The unique identifier of the buy request")] = Path(..., description="The unique identifier of the buy request"),
) -> BuyPepecoinOrderHashCancelPost200Response:
    """Cancels an existing buy request if it hasn’t been paid or processed yet."""
    if not BaseBuyPepecoinApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBuyPepecoinApi.subclasses[0]().buy_pepecoin_order_hash_cancel_post(order_hash)


@router.get(
    "/buy-pepecoin/{order_hash}",
    responses={
        200: {"model": BuyPepecoinOrderHashGet200Response, "description": "Successfully retrieved the buy request data"},
        404: {"description": "Buy request not found"},
    },
    tags=["buy_pepecoin"],
    summary="Get details of a specific buy request",
    response_model_by_alias=True,
)
async def buy_pepecoin_order_hash_get(
    order_hash: Annotated[StrictStr, Field(description="Unique identifier of the buy request")] = Path(..., description="Unique identifier of the buy request"),
) -> BuyPepecoinOrderHashGet200Response:
    """Retrieve the information and current status of a particular PepeCoin buy request."""
    if not BaseBuyPepecoinApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBuyPepecoinApi.subclasses[0]().buy_pepecoin_order_hash_get(order_hash)


@router.post(
    "/buy-pepecoin/order",
    responses={
        200: {"model": BuyPepecoinOrderPost200Response, "description": "Successful initiation of buy request"},
    },
    tags=["buy_pepecoin"],
    summary="order a buy request for pepecoin",
    response_model_by_alias=True,
)
async def buy_pepecoin_order_post(
    buy_pepecoin_order_post_request: BuyPepecoinOrderPostRequest = Body(None, description=""),
) -> BuyPepecoinOrderPost200Response:
    """Creates a new buy request for PepeCoin. Returns the USDT deposit address, the current Pepe price in USDT, and a request ID."""
    if not BaseBuyPepecoinApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBuyPepecoinApi.subclasses[0]().buy_pepecoin_order_post(buy_pepecoin_order_post_request)
