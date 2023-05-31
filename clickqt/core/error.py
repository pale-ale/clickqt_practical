from enum import IntEnum

class ClickQtError(IntEnum):
    NO_ERROR = 0
    CONFIRMATION_INPUT_NOT_EQUAL_ERROR = 1
    ABORTED_ERROR = 2
    PATH_NOT_EXIST_ERROR = 3

    def __str__(self):
        match(self.value):
            case ClickQtError.NO_ERROR: return ""
            case ClickQtError.CONFIRMATION_INPUT_NOT_EQUAL_ERROR: return "Confirmation input is not equal"
            case ClickQtError.ABORTED_ERROR: return "Aborted"
            case ClickQtError.PATH_NOT_EXIST_ERROR: return "Path does not exist"

        return "Unknown"