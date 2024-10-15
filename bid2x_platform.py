from abc import ABC, abstractmethod
from typing import Any
from pandas import DataFrame


class Platform(ABC):
    """
        Abstract class for the platform the script is being used.

        Attributes:
            None.

        Methods:
            process_script(self, service): Abstract method for running the
                script creation and uploading to the correct platform.
            print_dataframe(self, debug, input_df): Prints given dataframe.
    """
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def process_script(self, service):
        pass

    @abstractmethod
    def top_level_copy(self, source:Any) -> None:
        pass

    def print_dataframe(self, debug: bool, input_df: DataFrame) -> None:
        """Converts a dataframe to a string and prints it to stdout.

        Args:
            debug: prints output if debug is true.
            input_df: any dataframe.

        Returns:
            None.
        """
        # make sure indexes pair with number of rows
        df = input_df.reset_index()

        if debug:
            print(df.to_string())
