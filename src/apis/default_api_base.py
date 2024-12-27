# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def admin_get(
        self,
    ) -> None:
        """Admin-only endpoint for monitoring and managing transactions and rates."""
        ...


    async def confirm_payment_post(
        self,
        confirm_payment_post_request: ConfirmPaymentPostRequest,
    ) -> ConfirmPaymentPost200Response:
        """Confirms that the user has sent USDT and triggers payment validation."""
        ...


    async def exchange_rate_get(
        self,
    ) -> ExchangeRateGet200Response:
        """Retrieves the latest exchange rate of USDT to PepeCoin."""
        ...


    async def feedback_post(
        self,
        feedback_post_request: FeedbackPostRequest,
    ) -> None:
        """Allows users to report issues or provide feedback."""
        ...


    async def generate_address_post(
        self,
    ) -> GenerateAddressPost200Response:
        """Generates a new USDT wallet address for a transaction."""
        ...


    async def payment_status_get(
        self,
        transaction_id: Annotated[StrictStr, Field(description="Transaction ID of the payment.")],
    ) -> PaymentStatusGet200Response:
        """Returns the status of the user’s payment."""
        ...


    async def purchase_post(
        self,
        purchase_post_request: PurchasePostRequest,
    ) -> PurchasePost200Response:
        """Initiates a purchase of PepeCoin."""
        ...
