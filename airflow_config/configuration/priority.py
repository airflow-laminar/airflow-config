from typing import Optional

from pydantic import BaseModel, Field

__all__ = (
    "PriorityConfiguration",
    "NewRelicConfiguration",
    "DatadogConfiguration",
    "DiscordConfiguration",
    "SlackConfiguration",
    "SymphonyConfiguration",
)


class NewRelicConfiguration(BaseModel):
    api_key: Optional[str] = Field(description="NewRelic API Key")


class DatadogConfiguration(BaseModel):
    api_key: Optional[str] = Field(description="Datadog API Key")


class DiscordConfiguration(BaseModel):
    token: Optional[str] = Field(description="Discord Bot Token")
    channel: Optional[str] = Field(description="Discord Channel")


class SlackConfiguration(BaseModel):
    token: Optional[str] = Field(description="Slack Token")
    channel: Optional[str] = Field(description="Slack Channel")


class SymphonyConfiguration(BaseModel):
    room_name: str = Field(description="the room name")
    message_create_url: str = Field(description="https://mycompany.symphony.com/agent/v4/stream/SID/message/create")
    cert_file: str = Field(description="path/to/my/cert.pem")
    key_file: str = Field(description="path/to/my/key.pem")
    session_auth: str = Field(description="https://mycompany-api.symphony.com/sessionauth/v1/authenticate")
    key_auth: str = Field(description="https://mycompany-api.symphony.com/keyauth/v1/authenticate")
    room_search_url: str = Field(description="https://mycompany.symphony.com/pod/v3/room/search")


class PriorityConfiguration(BaseModel):
    new_relic: Optional[NewRelicConfiguration] = Field(default=None, description="New Relic configuration")
    datadog: Optional[DatadogConfiguration] = Field(default=None, description="Datadog configuration")
    discord: Optional[DiscordConfiguration] = Field(default=None, description="Discord configuration")
    slack: Optional[SlackConfiguration] = Field(default=None, description="Slack configuration")
    symphony: Optional[SymphonyConfiguration] = Field(default=None, description="Symphony configuration")
