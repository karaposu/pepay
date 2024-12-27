import psutil
from pydantic import AnyUrl, BaseModel, EmailStr, Field

from impl.services.base_service import BaseService

class IncreaseLimitService(BaseService):

    def check_compatibility(self):
        # a=(user_id,payment_confirmation_id, new_limit)
        self.user_id
        return True
    def preprocess_request_data(self):

        self.user_id = self.request.user_id
        self.payment_confirmation_id = self.request.payment_confirmation_id
        self.new_limit = self.request.new_limit
        COMPATIBLE=self.check_compatibility()

        unpacked= {"COMPATIBLE": COMPATIBLE,
                             "user_id": self.user_id ,
                             "payment_confirmation_id":self.payment_confirmation_id,
                             "new_limit": self.new_limit}

        self.preprocessed_data=unpacked

    def increase_limit(self):
        COMPATIBLE=self.preprocessed_data["COMPATIBLE"]
        user_id = self.preprocessed_data["user_id"]
        payment_confirmation_id = self.preprocessed_data["payment_confirmation_id"]
        new_limit = self.preprocessed_data["new_limit"]

        if COMPATIBLE:
            return True, new_limit
        else:
            pass

    def process_request(self):
        success,new_limit = self.increase_limit()
        self.response = (success,new_limit )
        return success,new_limit


def payment_verification_function():
    pass

def user_limit_update_function():
    pass

def user_limit_retrieval_function():
    pass


class IncreaseLimitRequest(BaseModel):
    userId: str
    paymentConfirmationId: str
    newLimit: int

class IncreaseLimitResponse(BaseModel):
    message: str
    newLimit: int


class SystemMonitoringResponse(BaseModel):
    disk_space_usage: str
    memory_usage: str
    gpu_usage: str  # This requires a more specialized approach, possibly with a library like GPUtil
    queue_lengths: str  # This is highly application-specific


def prepare_response_for_source_monitoring():
    def bytes_to_gb(bytes, round_digits=2):
        return round(bytes / (1024 ** 3), round_digits)

    disk = psutil.disk_usage('/')
    memory = psutil.virtual_memory()

    # Convert each attribute to GB
    disk_total_gb = bytes_to_gb(disk.total)
    disk_used_gb = bytes_to_gb(disk.used)
    disk_free_gb = bytes_to_gb(disk.free)

    memory_total_gb = bytes_to_gb(memory.total)
    memory_available_gb = bytes_to_gb(memory.available)

    # Placeholder values
    gpu_usage = "50%"
    queue_lengths = "42"

    return SystemMonitoringResponse(
        disk_space_usage=f"Total: {disk_total_gb} GB, Used: {disk_used_gb} GB, Free: {disk_free_gb} GB",
        memory_usage=f"Total: {memory_total_gb} GB, Available: {memory_available_gb} GB",
        gpu_usage=gpu_usage,
        queue_lengths=queue_lengths
    )



