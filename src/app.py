
# here is app.py

from indented_logger import setup_logging
import logging
from fastapi import Depends, Request

import os

log_file_path = os.path.expanduser("~/my_logs/app.log")
# log_file_path = "/var/log/my_app/app.log"

log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)


setup_logging(level=logging.DEBUG,
            log_file=log_file_path, 
            include_func=True, 
            include_module=False, 
            no_datetime=True )


logging.getLogger("passlib").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

logger.debug("start")
import logging


from fastapi import FastAPI
from core.dependencies import setup_dependencies

from apis.auth_api import router as AuthApiRouter
from apis.data_api import router as DataApiRouter
from apis.files_api import router as FilesApiRouter
from apis.records_api import router as RecordsApiRouter
from apis.reports_api import router as ReportsApiRouter

from apis.budget_api import router as BudgetApiRouter
from apis.business_api import router as BusinessApiRouter
from apis.exchange_api import router as ExchangeApiRouter
from apis.family_api import router as FamilyApiRouter

from apis.system_api import router as SystemApiRouter
from apis.user_api import router as UserApiRouter

from apis.dependencies_api import router as DependenciesApiRouter

from starlette.middleware.base import BaseHTTPMiddleware
import uuid


import logging
# from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware





logging.getLogger("pdfplumber").setLevel(logging.WARNING)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("fitz").setLevel(logging.WARNING)  # If usi

app = FastAPI(
    title="Budgety.ai API",
    description="API for processing bank statement PDFs and creating reports",
    version="1.0.0",
)


origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://enes-talk-w-sql.vercel.app",
    "https://enes-gcp-test-293803933129.europe-central2.run.app",
    "https://budgety-ui-gcp-test-293803933129.europe-west9.run.app",
    "https://gcp-budgety-281411985275.europe-west3.run.app",
    "https://budgety-ui-70638306280.europe-west1.run.app",
    "https://budgety.ai" ,
    "https://www.budgety.ai"

]


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a new UUID for this request
        request_id = str(uuid.uuid4())
        
        # Optionally, add the request_id to headers for downstream usage
        # (e.g., logging or returning to the client)
        request.state.request_id = request_id

        # You can also add it as a header in the response
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins , # Adjust this to more specific domains for security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.add_middleware(RequestIDMiddleware)

app.include_router(AuthApiRouter)
app.include_router(DataApiRouter)
app.include_router(FilesApiRouter)
app.include_router(RecordsApiRouter)
app.include_router(ReportsApiRouter)

app.include_router(BusinessApiRouter)
app.include_router(ExchangeApiRouter)
app.include_router(FamilyApiRouter)

app.include_router(SystemApiRouter)
app.include_router(UserApiRouter)

app.include_router(BudgetApiRouter)

app.include_router(DependenciesApiRouter)

services = setup_dependencies()

@app.on_event("startup")
async def startup_event():
    app.state.services = services
    logger.debug("Configurations loaded and services initialized")






#
# # Configure logging
# logger = logging.getLogger("Analyser")
# logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize DI containers

# def list_loggers():
#     loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
#     for logger in loggers:
#         print(f'Logger: {logger.name}, Level: {logging.getLevelName(logger.level)}')
#
# list_loggers()



#origins=['http://localhost:3000', 'http://127.0.0.1:3000']
# origins=["*"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins , # Adjust this to more specific domains for security
#    # allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=["*"],
#     expose_headers=["*"]
# )


#
# # List of logger names you provided
# loggers = [
#     "__main__",
#     "aiohttp.access",
#     "aiohttp",
#     "aiohttp.client",
#     "aiohttp.internal",
#     "aiohttp.server",
#     "aiohttp.web",
#     "aiohttp.websocket",
#     ",,",
#     "Analyser",
#     "dotenv.main",
#     "dotenv",
#     "openai._legacy_response",
#     "openai",
#
#     "openai._response",
#     "openai._base_client",
#     "openai.resources.uploads.uploads",
#     "openai.resources.uploads",
#     "openai.resources",
#     "langchain_core.utils.mustache",
#
#     "langchain_openai.chat_models.azure",
#     "langchain_openai.embeddings.base",
#     "langchain_openai.embeddings",
#     "langchain_openai.llms.base",
#
#     "categorizer.record_manager",
#
# ]
#
# # Step 1: Split the loggers into two parts
# mid_index = len(loggers) // 2
# first_half = loggers[:mid_index]
# second_half = loggers[mid_index:]
#
#
# for logger_name in second_half:
#     logging.getLogger(logger_name).setLevel(logging.WARNING)



