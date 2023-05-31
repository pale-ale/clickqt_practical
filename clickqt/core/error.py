from enum import IntEnum

class ClickQtError():
    class ErrorType(IntEnum):
        NO_ERROR = 0
        CONFIRMATION_INPUT_NOT_EQUAL_ERROR = 1
        ABORTED_ERROR = 2
        PATH_NOT_EXIST_ERROR = 3
        FILE_NOT_EXIST_ERROR = 4
        INVALID_FILENAME_ERROR = 5

    def __init__(self, type: ErrorType=ErrorType.NO_ERROR, trigger: str=""):
         self.type = type
         self.trigger = trigger

    def message(self) -> str:
        match(self.type.value):
            case ClickQtError.ErrorType.NO_ERROR: return ""
            case ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR: return f"Confirmation input ({self.trigger}) is not equal"
            case ClickQtError.ErrorType.ABORTED_ERROR: return "Aborted"
            case ClickQtError.ErrorType.PATH_NOT_EXIST_ERROR: return f"Path ({self.trigger}) does not exist"
            case ClickQtError.ErrorType.FILE_NOT_EXIST_ERROR: return f"File ({self.trigger}) does not exist"
            case ClickQtError.ErrorType.INVALID_FILENAME_ERROR: return f"Invalid filename ({self.trigger})"
       
        return "Unknown"