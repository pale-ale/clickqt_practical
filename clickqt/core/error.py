from enum import IntEnum
import enum_tools.documentation

class ClickQtError:
    """Shows whether an error occured during value validation of the widgets

    :param type: The type of the error, defaults to ErrorType.NO_ERROR
    :param trigger: The source where the error occured, defaults to ''
    :param click_error_message: The error message which was created by click, defaults to ''
    """

    @enum_tools.documentation.document_enum
    class ErrorType(IntEnum):
        """Specifies the possible error types"""

        NO_ERROR = 0 # doc: No error occured.
        CONFIRMATION_INPUT_NOT_EQUAL_ERROR = 1 # doc: The values of the elements of a ConfirmationWidget do not match.
        ABORTED_ERROR = 2 # doc: A clickqt dialog / the click.Context-object of the command was aborted.
        PROCESSING_VALUE_ERROR = 3 # doc: An error was triggered in a (user-defined) callback of a click.Parameter.
        CONVERTING_ERROR = 4 # doc: A value could not be converted into a click.ParamType.
        REQUIRED_ERROR = 5 # doc: The value of a required option is missing.
        EXIT_ERROR = 6 # doc: exit() was called on click.Context-object of the command.

    
    def __init__(self, type: ErrorType=ErrorType.NO_ERROR, trigger: str="", click_error_message: str=""):
         self.type = type
         self.trigger = trigger
         self.click_error_message = click_error_message

    def message(self) -> str:
        """Returns the message of the error as string. 
        If there was no error, an empty string will be returned.
        """
        
        match(self.type.value):
            case ClickQtError.ErrorType.NO_ERROR: return ""
            case ClickQtError.ErrorType.CONFIRMATION_INPUT_NOT_EQUAL_ERROR: return f"Confirmation input ({self.trigger}) is not equal"
            case ClickQtError.ErrorType.ABORTED_ERROR: return "Aborted!"
            case ClickQtError.ErrorType.PROCESSING_VALUE_ERROR: return f"Processing value error ({self.trigger}): {self.click_error_message}"
            case ClickQtError.ErrorType.CONVERTING_ERROR: return f"Converting error ({self.trigger}): {self.click_error_message}"
            case ClickQtError.ErrorType.REQUIRED_ERROR: return f"Required error ({self.trigger}): {self.click_error_message} is empty" #Argument/Option
            case ClickQtError.ErrorType.EXIT_ERROR: return "" # Don't print an error (click behaviour)

        raise NotImplementedError(f"Message for this error ({self.type.value}) not implemented yet")