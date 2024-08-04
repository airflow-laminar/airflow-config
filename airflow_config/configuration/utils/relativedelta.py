# https://github.com/jrdnh
# Pydantic-compatible wrapper for dateutil.relativedelta.relativedelta
from typing import Annotated, Any, Optional

from dateutil.relativedelta import relativedelta, weekday
from pydantic import BaseModel, Field, model_serializer, model_validator
from pydantic_core import core_schema


class WeekdayAnnotations(BaseModel):
    weekday: int = Field(ge=0, le=6)
    n: int | None = None

    @model_validator(mode="wrap")
    def _validate(value, handler: core_schema.ValidatorFunctionWrapHandler) -> relativedelta:
        # if already dateutil._common.weekday instance, return it
        if isinstance(value, weekday):
            return value

        # otherwise run model validation, which returns either a
        # a dateutil._common.weekday or a WeekdayAnnotations
        validated = handler(value)
        if isinstance(validated, weekday):
            return validated

        kwargs = {k: v for k, v in dict(validated).items() if v is not None}
        return weekday(**kwargs)

    @model_serializer(mode="plain")
    def _serialize(self: weekday) -> dict[str, Any]:
        return {"weekday": self.weekday, "n": self.n}


Weekday = Annotated[weekday, WeekdayAnnotations]


class RelativeDeltaAnnotation(BaseModel):
    years: int | None = None
    months: int | None = None
    days: int | None = None
    hours: int | None = None
    minutes: int | None = None
    seconds: int | None = None
    microseconds: int | None = None
    year: int | None = None
    # recommended way to avoid potential errors for compound types with constraints
    # https://docs.pydantic.dev/dev/concepts/fields/#numeric-constraints
    month: Optional[Annotated[int, Field(ge=1, le=12)]] = None
    day: Optional[Annotated[int, Field(ge=0, le=31)]] = None
    hour: Optional[Annotated[int, Field(ge=0, le=23)]] = None
    minute: Optional[Annotated[int, Field(ge=0, le=59)]] = None
    second: Optional[Annotated[int, Field(ge=0, le=59)]] = None
    microsecond: Optional[Annotated[int, Field(ge=0, le=999999)]] = None
    weekday: Weekday | None = None
    leapdays: int | None = None
    # validation only fields
    yearday: int | None = Field(None, exclude=True)
    nlyearday: int | None = Field(None, exclude=True)
    weeks: int | None = Field(None, exclude=True)
    dt1: int | None = Field(None, exclude=True)
    dt2: int | None = Field(None, exclude=True)

    @model_validator(mode="wrap")
    def _validate(value, handler: core_schema.ValidatorFunctionWrapHandler) -> relativedelta:
        if isinstance(value, relativedelta):
            return value

        validated = handler(value)
        if isinstance(validated, relativedelta):
            return validated

        kwargs = {k: v for k, v in dict(validated).items() if v is not None}
        return relativedelta(**kwargs)


RelativeDelta = Annotated[relativedelta, RelativeDeltaAnnotation]
