# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

# from apis.price_info_api_base import BasePriceInfoApi
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
from models.price_pepecoin_to_usdt_get200_response import PricePepecoinToUsdtGet200Response


router = APIRouter()

ns_pkg = impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/price/pepecoin_to_usdt",
    responses={
        200: {"model": PricePepecoinToUsdtGet200Response, "description": "Returns the price in USDT"},
    },
    tags=["price_info"],
    summary="Get the current PepeCoin-to-USDT price",
    response_model_by_alias=True,
)
async def price_pepecoin_to_usdt_get(
) -> PricePepecoinToUsdtGet200Response:
    """Returns the real-time (or latest) price of PepeCoin in USDT."""
    if not BasePriceInfoApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePriceInfoApi.subclasses[0]().price_pepecoin_to_usdt_get()
