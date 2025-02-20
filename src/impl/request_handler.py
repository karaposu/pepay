
# from models.upload_and_process_pdf200_response import UploadAndProcessPdf200Response


# from impl.services.record_management import RecordCategoryUpdater, RecordSplitter
# from impl.services.report_management import ReportMaker, HistoricalReportMaker
# from impl.services.info_management import BankInfoManagement

from typing import Optional




import os
import sys
from pathlib import Path



script_dir = os.path.dirname(__file__)
sys.path.append(script_dir)  # Appe

# sys.path.append(str(Path(__file__).resolve().parent.parent / "llmec"))
# print("syspath>", sys.path)


# from celery_app import async_text_to_image_service
# from models.bug_report_request import BugReportRequest
from collections import OrderedDict
# from models.operation_status import OperationStatus

import logging
logger = logging.getLogger(__name__)


# def verify_user_id(user_id: int, db: Session) -> User:
#     """
#     Verifies the user_id by checking the database.
#
#     :param user_id: The user ID extracted from the JWT token.
#     :param db: The database session.
#     :return: The User object if the user exists and is valid.
#     :raises HTTPException: If the user_id is not valid or does not exist.
#     """
#     user = db.query(User).filter(User.id == user_id).first()
#
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid user ID or user does not exist")
#
#     if not user.is_active:  # Assuming you have an 'is_active' flag in your User model
#         raise HTTPException(status_code=401, detail="User account is inactive")
#
#     return user


class RequestHandler:
    #def __init__(self, iie,ch, et=False):
    def __init__(self, app):
        self.app = app
        self.package_content = None
        self.requester_id = None
        self.package_sent_time = None
        self.response = None
        # self.iie=iie
        # self.ch=ch
        self.DATA_IS_VALID = None
        self.META_IS_VALID = None
        self.USER_HAS_PERMISSION = None

        self.REQUEST_IS_VALID=None
        self.error_code=None

        # logger = logging.getLogger(__name__)
        #
        # logger.setLevel(logging.DEBUG)
        logger.debug("Request Handler ")
        self.logger= logger

        #self.elapsed_time =et
        self.elapsed_time=None
        if not self.elapsed_time:

            self.elapsed_time= OrderedDict()

        # self.elapsed_time = OrderedDict()

        # self.elapsed_time["start_time"] = time.time()
    def op_validity(self,meta_data):

        is_permitted=self.check_metadata_validity(meta_data)
        if is_permitted:
            return True
        else:
           # raise HTTPException(status_code=400, detail="user doesnt have permission for this operation")
            return False

    def check_metadata_validity(self, meta_data):
        return True

    
    def generate_usdt_deposit_address(self, user_id):

        class MyRequest:
            def __init__(self):
                self.user_id = user_id
            

        mr = MyRequest()
         
        from impl.services.tron.deposit_address_generator_service import DepositAddressGeneratorService
        dependency = self.app.state.services

        p = DepositAddressGeneratorService(mr, dependencies=dependency)
        return p.response
    


    




   



    
    

   
    

    def handle_get_community_size(self):

        
        from impl.services.get_size_service import GetCommunitySize
       
        dependency = self.app.state.services
        p = GetCommunitySize( dependencies=dependency)
        return p.response

 
    
    # this is in request_handler.py
    def handle_buy_pepecoin_order_post(self, user_id, buy_pepecoin_order_post_request ):

        
        from impl.services.buy_pepecoin.ordering_service import BuyPepecoinOrderingService
        self.logger.debug("handle_buy_pepecoin_order_post ", extra={'lvl': 3})

        dependency = self.app.state.services
        p = BuyPepecoinOrderingService(user_id, buy_pepecoin_order_post_request, dependencies=dependency)
        return p.response

 

    def handle_register(self, auth_register_post_request):

        from impl.services.auth.register_service import RegisterService

        self.logger.debug("handle_register ", extra={'lvl': 3})

        dependency = self.app.state.services
        p = RegisterService(auth_register_post_request, dependencies=dependency)
        return p.response

    def handle_login(self, email, password):
        class MyRequest:
            def __init__(self):
                self.email = email
                self.password = password

        from impl.services.auth.login_service import LoginService
        dependency = self.app.state.services

        mr = MyRequest()
        p = LoginService(mr, dependencies=dependency)

        return p.response

    def handle_reset_password(self, auth_reset_password_post_request):
        self.logger.debug("handle_verify_email ", extra={'lvl': 3})


        from impl.services.auth.user_services import ResetPasswordService
        p=ResetPasswordService(auth_reset_password_post_request)
        return p.response


    def handle_verify_email(self, token):


        self.logger.debug("handle_verify_email ", extra={'lvl': 3})
       # self.logger.debug("Total ready records =%s ", self.record_manager.get_number_of_ready_records(), extra={'lvl': 2})

        class MyRequest :
            def __init__(self, logger):
                self.token=token
                self.logger= logger

        mr = MyRequest(self.logger)

        from impl.services.auth.user_services import VerifyService

        p= VerifyService(mr)
        return p.response

    # def handle_upload_file(self,pdf_file,extension, user_id ,bank_id,  country_code, process_as_test, use_auto_extractor) -> UploadAndProcessPdf200Response:

    #     class MyRequest :
    #         def __init__(self):
    #             self.pdf_file=pdf_file
    #             self.user_id = user_id

    #             self.bank_id = bank_id
    #             self.extension = extension
    #             self.country_code=country_code
    #             self.process_as_test = process_as_test
    #             self.use_auto_extractor = use_auto_extractor

    #     from impl.services.file.upload_file_service import UploadFileService

    #     dependency = self.app.state.services

    #     mr=MyRequest()
    #     p =UploadFileService(mr,dependency )

    #     return p.response

    # def handle_upload_file_background(self,pdf_file,extension, user_id ,bank_id,  country_code, process_as_test,bank_name, use_auto_extractor, background_tasks) -> UploadAndProcessPdf200Response:

    #     class MyRequest :
    #         def __init__(self):
    #             self.pdf_file=pdf_file
    #             self.user_id = user_id

    #             self.bank_id = bank_id
    #             self.extension = extension
    #             self.country_code=country_code
    #             self.process_as_test = process_as_test
    #             self.bank_name = bank_name
    #             self.use_auto_extractor = use_auto_extractor
    #             self.background_tasks = background_tasks




    #     from impl.services.file.upload_file_service_background import UploadFileBackgroundService

    #     dependency = self.app.state.services

    #     mr=MyRequest()
    #     p =UploadFileBackgroundService(mr,dependency )

    #     return p.response

