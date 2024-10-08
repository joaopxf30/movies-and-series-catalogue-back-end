import regex as re
import logging
from uuid import UUID
from pydantic import (
    BaseModel,
    ConfigDict,
    AliasGenerator,
    AliasChoices,
    field_validator,
    Field,
)
from pydantic.alias_generators import to_camel, to_pascal, to_snake
from typing import Any, Optional
from model import Rating

LOG = logging.getLogger()


class AudiovisualPost(BaseModel):
    """It represents the form of a POST request for an Audiovisual's instance
    through OMDb API.

    """

    imdb_id: str | int | None = Field(
        default=None, description="Type: string, integer or empty value"
    )
    title: str | None = Field(default=None, description="Type: string or empty value")
    year: int | None = Field(default=None, description="Type: integer or empty value")

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_snake,
        ),
    )

    @field_validator("title")
    @classmethod
    def _replace_whitespaces_for_request(cls, v: str | None) -> str:
        return re.sub(r"\s", "+", v) if v else v


class Audiovisual(BaseModel):
    """It represents the content of a successful request to the OMDb Api."""

    title: str | None
    year: str | int | None
    rated: str | None
    released: str | None
    runtime: str | None
    genre: str | None
    director: str | None
    writer: str | None
    actors: str | None
    plot: str | None
    language: str | None
    country: str | None
    awards: str | None
    poster: str | None
    ratings: list["OMDbRating"] | None = None
    metascore: int | None
    imdb_rating: float | None
    imdb_votes: str | None
    imdb_id: str | None = Field(validation_alias="imdbID")
    type: str | None
    dvd: str | None = Field(default=None, validation_alias="DVD")
    total_seasons: str | None = None
    box_office: str | None = None
    production: str | None = None
    website: str | None = None
    response: bool

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        alias_generator=AliasGenerator(
            validation_alias=lambda f: AliasChoices(
                to_camel(f),
                to_pascal(f),
            ),
            serialization_alias=to_snake,
        ),
    )

    @field_validator("imdb_rating", mode="before")
    @classmethod
    def _change_commma_to_dot(cls, v: str | float | None) -> float | None:
        if v and isinstance(v, str) and re.search(r",", v):
            return float(re.sub(",", ".", v))

        return v

    @field_validator("*", mode="before")
    def _empty_field(cls, v: Any) -> str | None:
        if isinstance(v, str) and re.search(r"N/A", v):
            return None

        return v


class OMDbRating(BaseModel):
    source: str
    value: str

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_pascal,
            serialization_alias=to_snake,
        ),
    )


class AudiovisualView(BaseModel):
    """It represents how an instance of Audiovisual is returned."""

    id: UUID
    title: str | None
    year: str | int | None
    runtime: str | None
    genre: str | None
    director: str | None
    actors: str | None
    plot: str | None
    rating: float | None
    type: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "64e259a8-8512-415f-8f52-8b3d9103f6c6",
                "title": 3.5,
                "year": "2014–2020",
                "runtime": "43 min",
                "genre": "Crime, Drama, Mystery",
                "director": None,
                "actors": "Viola Davis, Billy Brown, Jack Falahee",
                "plot": (
                    "A group of ambitious law students and their brilliant criminal defense "
                    "professor become involved in a twisted murder plot that promises to change "
                    "the course of their lives.",
                ),
                "rating": 3.0,
                "type": "series",
            }
        },
    )

    @field_validator("rating", mode="before")
    def _return_rating(cls, v: Rating | None) -> float | None:
        if isinstance(v, Rating):
            return v.rating
        return v


class AudiovisualQuery(BaseModel):
    """It represents the parameters for a query to a movie or
    series.

    """

    id: str


class AudiovisualRemovedMessage(BaseModel):
    """It represents when a movie or series is removed."""

    message: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "Movie or series removed"}}
    )


class AudiovisualErrorMessage(BaseModel):
    """It represents a not sucessful request."""

    message: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "This is an error message"}}
    )
