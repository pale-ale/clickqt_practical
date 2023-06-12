from enum import IntEnum

class ClickQtError():
    class ErrorType(IntEnum):
        NO_ERROR = 0
        CONFIRMATION_INPUT_NOT_EQUAL_ERROR = 1
        ABORTED_ERROR = 2
        CALLBACK_VALIDATION_ERROR = 3
        CONVERSION_ERROR = 4

    def __init__(self, type: ErrorType=ErrorType.NO_ERROR, trigger: str="", click_error_message: str=""):
         self.type = type
         self.trigger = trigger
         self.click_error_message = click_error_message

    def message(self) -> str:
        match(self.type.value):
            case ClickQtError.ErrorType.NO_ERROR: return ""
            case ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR: return f"Confirmation input ({self.trigger}) is not equal"
            case ClickQtError.ErrorType.ABORTED_ERROR: return "Aborted"
            case ClickQtError.ErrorType.CALLBACK_VALIDATION_ERROR: return f"Callback validation error ({self.trigger}): {self.click_error_message}"
            case ClickQtError.ErrorType.CONVERSION_ERROR: return f"Convertion error ({self.trigger}): {self.click_error_message}"
       
        return "Unknown"