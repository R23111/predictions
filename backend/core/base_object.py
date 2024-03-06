import json
import os
import pickle
from datetime import date, datetime
from typing import Any

from pydantic import ValidationError
from sqlmodel import SQLModel


class BaseObject(SQLModel):
    """This class is the base class for all SQLModels objects."""

    class __Encoder(json.JSONEncoder):
        """This class is used to encode the Episode object to json or any other object that has a __dict__ attribute."""

        def default(self, o: Any) -> Any:
            """This method is used to encode the Episode object to json.

            Args:
                o (object): The object to be encoded.

            Returns:
                str: The json string.
            """
            try:
                if isinstance(o, datetime):
                    return o.isoformat()
                return o.isoformat() if isinstance(o, date) else o.__dict__
            except Exception as e:
                raise AttributeError(f"Unable to encode object. {e}") from e

    class Config:
        """This class is used to configure the BaseModel class."""

        validate_assignment = True
        extra = "forbid"
        frozen = False
        populate_by_name = False
        arbitrary_types_allowed = True
        allow_inf_nan = True
        strict = True
        revalidate_instances = "always"
        validate_default = False
        coerce_numbers_to_str = True
        validation_error_cause = True
        str_strip_whitespace = True

    def convert_to_json(self) -> str:
        """Converts an episode to a json string."""
        return json.dumps(self, indent=4, cls=self.__Encoder)

    def save_to_json_file(self, file_path: str) -> None:
        """Saves an episode to a json file.

        Args:
            file_path (str): The path to the file.
        """
        _, extension = os.path.splitext(file_path)
        if extension != ".json":
            raise ValueError(f"File extension must be .json, not {extension}")

        with open(file_path, "w") as file:
            file.write(self.convert_to_json())

    def save_to_pickle_file(self, file_path: str) -> None:
        """Saves an object to a pickle file.

        Args:
            file_path (str): The path to the file.
        """
        with open(file_path, "wb") as file:
            pickle.dump(self, file)

    def __str__(self) -> str:
        """Returns a string representation of the object."""
        try:
            return self.convert_to_string()
        except ValueError:
            return str(super().__str__())

    def convert_to_string(self) -> str:
        """Converts an object to a string."""
        try:
            text = f"\n==={self.__class__.__name__}===\n"
            for key, value in self.__dict__.items():
                if isinstance(value, list):
                    text += f"{key}: LIST[{len(value)}] \n"
                    for number, item in enumerate(value):
                        text += f" [{number}] <{item.__class__.__name__}> {self.__add_space(str(item))} \n"
                elif isinstance(value, tuple):
                    text += f"{key}: TUPLE[{len(value)}] \n"
                    for number, item in enumerate(value):
                        text += f" [{number}] <{item.__class__.__name__}> {self.__add_space(str(item))} \n"
                elif isinstance(value, dict):
                    text += f"{key}: DICT[{len(value.keys())}] \n"
                    for k, v in value.items():
                        text += f" [{k}] <{v.__class__.__name__}> {self.__add_space(str(v))} \n"
                else:
                    value_type = f"<{value.__class__.__name__}>"
                    text += f"{key}: {value_type} {self.__add_space(str(value))} \n"
            return text[:-1]
        except Exception as e:
            raise ValueError(f"Unable to convert object to string. {e}") from e

    def __add_space(self, text: str) -> str:
        spaces = 4
        return text.replace("\n", "\n" + spaces * " ")

    @classmethod
    def load_from_pickle_file(cls, file_path: str) -> Any:
        """Loads an object from a pickle file and returns the object.

        Args:
            file_path (str): The path to the file.

        Returns:
            object: The objects.
        """
        try:
            with open(file_path, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Unable to load file {file_path}. File not Found.") from e
        except Exception as e:
            raise Exception(f"Unable to load file {file_path}. {e}") from e

    @classmethod
    def load_from_json_file(cls, file_path: str) -> "BaseObject":
        """Loads an object from a json file and returns the object.

        Args:
            file_path (str): The path to the file.

        Returns:
            object: The objects.
        """
        try:
            with open(file_path, "r") as file:
                return cls(**json.load(file))
        except ValidationError as e:
            raise ValidationError(f"Unable to load file {file_path}. Some fields are missing . \n {e}") from e
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Unable to load file {file_path}. File not Found.") from e
        except Exception as e:
            raise Exception(f"Unable to load file {file_path}. {e}") from e
