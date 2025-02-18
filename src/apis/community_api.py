# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil


import logging
logger = logging.getLogger(__name__)


import impl

# from security_api import get_token_bearerAuth


def get_request_handler():
    from app import app
    from impl.request_handler import RequestHandler
    return RequestHandler(app)

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
from typing import List
from models.community_graph_get200_response_inner import CommunityGraphGet200ResponseInner


router = APIRouter()

ns_pkg = impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/community/graph",
    responses={
        200: {"model": List[CommunityGraphGet200ResponseInner], "description": "Successful retrieval of community growth data"},
    },
    tags=["community"],
    summary="Get community user growth graph data",
    response_model_by_alias=True,
)
async def community_graph_get( 
  #   token_bearerAuth: TokenModel = Security( get_token_bearerAuth ),
     passcode: str = Query(None, alias="passcode"),
) -> List[CommunityGraphGet200ResponseInner]:
    """Returns a list of community growth data over time."""
    if passcode=="sanane":
        try:
        
           # user_id = int(token_bearerAuth.sub)
            rh = get_request_handler()
            return rh.handle_get_community_size()

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)  # Log the exception details
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    


