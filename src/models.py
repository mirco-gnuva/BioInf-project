from pydantic import BaseModel, Field
from enum import Enum
import uuid


class OmicData(BaseModel):
    patient_id: str = Field(description='Patient ID', regex='TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}')


class VitalStatus(Enum):
    ALIVE = 0
    DEAD = 1
    UNKNOWN = 2
    NOT_REPORTED = 3


class Gender(Enum):
    FEMALE = 0
    MALE = 1
    UNSPECIFIED = 2
    UNKNOWN = 3
    NOT_REPORTED = 4


class Race(Enum):
    AMERICAN_INDIAN_OR_ALASKA_NATIVE = 0
    ASIAN = 1
    BLACK_OR_AFRICAN_AMERICAN = 2
    NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = 3
    WHITE = 4
    OTHER = 5
    UNKNOWN = 6
    NOT_REPORTED = 7
    NOT_ALLOWED_TO_COLLECT = 8


class Ethnicity(Enum):
    HISPANIC_OR_LATINO = 0
    NOT_HISPANIC_OR_LATINO = 1
    UNKNOWN = 2
    NOT_REPORTED = 3
    NOT_ALLOWED_TO_COLLECT = 4

