import datetime

from sanic_security.models import BaseModel, Account
from tortoise import fields


class ResearchSession(BaseModel):
    account: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account", null=True
    )
    contributors: fields.ManyToManyRelation["Account"] = fields.ManyToManyField(
        "models.Account",
        through="research_contributor",
        related_name="contributed_research_sessions",
    )
    title: str = fields.CharField(max_length=255)

    class Meta:
        table = "research_session"

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "date_created": str(self.date_created),
            "date_updated": str(self.date_updated),
            "title": self.title,
            "account": self.account.id if isinstance(self.account, Account) else None,
        }


class Publication(BaseModel):
    title: str = fields.CharField(max_length=255)
    abstract: str = fields.TextField(null=True)
    url: str = fields.CharField(max_length=255)
    authors: fields.JSONField = fields.JSONField()
    submission_date: datetime.datetime = fields.DatetimeField(null=True)
    category: str = fields.CharField(max_length=255, null=True)
    metadata: str = fields.TextField()
    research_session: fields.ForeignKeyRelation["ResearchSession"] = (
        fields.ForeignKeyField("models.ResearchSession", null=True)
    )

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "research_session": (
                self.research_session.id
                if isinstance(self.research_session, ResearchSession)
                else None
            ),
            "date_created": str(self.date_created),
            "date_updated": str(self.date_updated),
            "title": self.title,
            "abstract": self.abstract,
            "url": self.url,
            "authors": self.authors,
            "submission_date": str(self.submission_date),
            "category": self.category,
            "metadata": self.metadata,
        }


class Memo(BaseModel):
    research_session: fields.ForeignKeyRelation["ResearchSession"] = (
        fields.ForeignKeyField("models.ResearchSession", null=True)
    )
    publication: fields.ForeignKeyRelation["Publication"] = fields.ForeignKeyField(
        "models.Publication", null=True
    )
    title: str = fields.CharField(max_length=255)
    content: str = fields.TextField()
    account: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account", null=True
    )

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "research_session": (
                self.research_session.id
                if isinstance(self.research_session, ResearchSession)
                else None
            ),
            "date_created": str(self.date_created),
            "date_updated": str(self.date_updated),
            "title": self.title,
            "content": self.content,
            "publication": (
                self.publication.title
                if isinstance(self.publication, Publication)
                else None
            ),
            "account": (
                self.account.username if isinstance(self.account, Account) else None
            ),
        }
