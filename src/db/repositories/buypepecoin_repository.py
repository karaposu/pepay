# db/repositories/buypepecoin_repository.py

from sqlalchemy.orm import Session
import logging
import uuid
from datetime import datetime

from db.models.transfer_builder import TransferBuilder
from models.buy_pepecoin_order_post_request import BuyPepecoinOrderPostRequest
from models.buy_pepecoin_order_post200_response import BuyPepecoinOrderPost200Response

logger = logging.getLogger(__name__)

class BuypepecoinRepository:
    def __init__(self, session: Session):
        self.session = session

    def generate_new_usdt_address(self):

        from impl.generate_usdt_wallet import USDTWallet
        wallet = USDTWallet()
        print("=== New USDT Wallet Generated ===")
        return wallet.get_public_address(), wallet.get_private_key_hex(),

       # print("=== New USDT Wallet Generated ===")
        # print("Private Key (Hex):", wallet.get_private_key_hex())
        # print("Public TRON Address:", wallet.get_public_address())

    def save_initial_request_to_transfer_builder(
        self,
        user_id: int,
        buy_pepecoin_order_post_request: BuyPepecoinOrderPostRequest
    ) -> BuyPepecoinOrderPost200Response:
        """
        Persists a new TransferBuilder row with all the relevant fields
        from BuyPepecoinOrderPostRequest plus user_id, then returns a
        BuyPepecoinOrderPost200Response.
        """
        try:
            # Generate a unique request_id (this will become your 'order_hash')
            request_id = str(uuid.uuid4())

            # Convert datetime fields to string if your columns are String in TransferBuilder
            timeout_str = (buy_pepecoin_order_post_request.timeout_time_in_fe.isoformat()
                           if buy_pepecoin_order_post_request.timeout_time_in_fe else None)
            latest_calc_time_str = (
                buy_pepecoin_order_post_request.rate_shown_in_fe_time.isoformat()
                if buy_pepecoin_order_post_request.rate_shown_in_fe_time
                else None
            )

            usdt_public_address, hex_private_key= self.generate_new_usdt_address()

            # Build the TransferBuilder entry
            new_transfer = TransferBuilder(
                user_id=user_id,
                request_id=request_id,
                be_incall_time=datetime.utcnow(),  # or None, or keep as is
                fe_incall_time=buy_pepecoin_order_post_request.fe_incall_time,
                
                give=buy_pepecoin_order_post_request.give,
                take=buy_pepecoin_order_post_request.take,
                give_amount=buy_pepecoin_order_post_request.give_amount,
                take_amount=buy_pepecoin_order_post_request.take_amount,
                
                latest_take_amount_calculation_time=latest_calc_time_str,

                email=buy_pepecoin_order_post_request.email,
                telegram=buy_pepecoin_order_post_request.telegram,
                customer_ip=buy_pepecoin_order_post_request.customer_ip,
                timeout_time=buy_pepecoin_order_post_request.timeout_time_in_fe,
                timeout_time_in_fe=timeout_str,
                
                
                hex_private_key= hex_private_key,
                generated_take_address= usdt_public_address
            )
            
            # Save to DB
            self.session.add(new_transfer)
            self.session.commit()
            self.session.refresh(new_transfer)
     
            logger.debug(
                f"Created new TransferBuilder row with id={new_transfer.id}, request_id={request_id}"
            )

            # Build the response. You can fill fields from new_transfer or the request:
            response = BuyPepecoinOrderPost200Response(
                payment_address=new_transfer.generated_take_address,  # deposit address
                payment_currency=new_transfer.give or "USDT",         # or whatever your logic dictates
                payment_protocol="TRC20",                            # or "ERC20", etc.
                fixed_rate=buy_pepecoin_order_post_request.rate_shown_in_fe,
                fixed_take_amount=new_transfer.take_amount,
                order_hash=request_id
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error saving TransferBuilder: {e}", exc_info=True)
            self.session.rollback()
            raise
