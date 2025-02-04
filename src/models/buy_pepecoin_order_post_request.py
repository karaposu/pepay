# coding: utf-8

"""
    Pepay Web App API

    API for purchasing PepeCoin using USDT.

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json




from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class BuyPepecoinOrderPostRequest(BaseModel):
    """
    BuyPepecoinOrderPostRequest
    """ # noqa: E501
    fe_incall_time: Optional[datetime] = Field(default=None, description="Timestamp of the button press in the frontend")
    give: Optional[StrictStr] = Field(default=None, description="Give currency code. All currency codes you can get through /buy_pepecoin/currencies/ method")
    give_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount you must pay. Specify take_amount or give_amount.")
    take: Optional[StrictStr] = Field(default=None, description="pep, since we only sell pep in pepay")
    take_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The pep amount you will receive")
    rate_shown_in_fe: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The snapshot price of Pepe shown in fe")
    rate_shown_in_fe_time: Optional[datetime] = Field(default=None, description="When the Pepe price was taken")
    email: Optional[StrictStr] = Field(default=None, description="The user’s email address")
    telegram: Optional[StrictStr] = Field(default=None, description="The user’s Telegram handle")
    customer_ip: Optional[StrictStr] = Field(default=None, description="pep, since we only sell pep in pepay")
    timeout_time_in_fe: Optional[datetime] = Field(default=None, description="When the buy request times out on the frontend")
    __properties: ClassVar[List[str]] = ["fe_incall_time", "give", "give_amount", "take", "take_amount", "rate_shown_in_fe", "rate_shown_in_fe_time", "email", "telegram", "customer_ip", "timeout_time_in_fe"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of BuyPepecoinOrderPostRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of BuyPepecoinOrderPostRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "fe_incall_time": obj.get("fe_incall_time"),
            "give": obj.get("give"),
            "give_amount": obj.get("give_amount"),
            "take": obj.get("take"),
            "take_amount": obj.get("take_amount"),
            "rate_shown_in_fe": obj.get("rate_shown_in_fe"),
            "rate_shown_in_fe_time": obj.get("rate_shown_in_fe_time"),
            "email": obj.get("email"),
            "telegram": obj.get("telegram"),
            "customer_ip": obj.get("customer_ip"),
            "timeout_time_in_fe": obj.get("timeout_time_in_fe")
        })
        return _obj


