from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorldCupTeam(BaseModel):
    """Equipo del mundial (football-data.org). Ignora area, squad, coach, etc."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    tla: str = Field(min_length=3, max_length=3)


class WorldCupTeamsFile(BaseModel):
    """Raíz del JSON de equipos exportado desde football-data.org."""

    model_config = ConfigDict(extra="ignore")

    count: int | None = None
    teams: list[WorldCupTeam]


class WorldCupMatchTeamRef(BaseModel):
    """Equipo en un partido (puede estar TBD en eliminatorias)."""

    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    name: str | None = None
    tla: str | None = None


class WorldCupScoreLine(BaseModel):
    model_config = ConfigDict(extra="ignore")

    home: int | None = None
    away: int | None = None


class WorldCupScore(BaseModel):
    model_config = ConfigDict(extra="ignore")

    winner: str | None = None
    duration: str
    fullTime: WorldCupScoreLine
    halfTime: WorldCupScoreLine | None = None
    extraTime: WorldCupScoreLine | None = None
    penalties: WorldCupScoreLine | None = None


class WorldCupMatch(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    utcDate: datetime
    status: str
    matchday: int | None = None
    stage: str
    group: str | None = None
    lastUpdated: datetime | None = None
    homeTeam: WorldCupMatchTeamRef
    awayTeam: WorldCupMatchTeamRef
    score: WorldCupScore


class WorldCupMatchesFile(BaseModel):
    """Raíz del JSON de partidos. Ignora competition, filters, odds, referees, etc."""

    model_config = ConfigDict(extra="ignore")

    matches: list[WorldCupMatch]
