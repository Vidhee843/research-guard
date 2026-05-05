import os
import shutil

from bs4 import BeautifulSoup
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from sanic import Blueprint, file, text
from sanic_security.authentication import requires_authentication
from sanic_security.utils import json, str_to_bool
from tortoise.expressions import Q

from research_guard.blueprints.ai.common import train, classify
from research_guard.blueprints.research.models import ResearchSession, Publication
from research_guard.common.util import http_client, get_body_text, llm

ai_bp = Blueprint("AI")


@ai_bp.post("ai/model")
@requires_authentication
async def create_model(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publications = await Publication.filter(
        research_session=session, deleted=False
    ).all()
    trained_model = train(
        request.args.get("type"),
        session,
        publications,
    )
    return json(f"{request.args.get("type")} model saved to bucket.", trained_model)


@ai_bp.get("ai/model/all")
@requires_authentication
async def get_all_available_models(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    return json(
        "Models retrieved.",
        os.listdir(f"resources\\bucket\\{session.id}"),
    )


@ai_bp.get("ai/model")
@requires_authentication
async def download_model(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    filename = request.args.get("type").replace("-", "_") + (
        request.args.get("extension") or ".joblib"
    )
    return await file(
        os.path.join(
            "resources", "bucket", session.id, request.args.get("type"), filename
        ),
        filename=filename,
    )


@ai_bp.delete("ai/model")
@requires_authentication
async def delete_model(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    shutil.rmtree(f"resources/bucket/{session.id}/{request.args.get('type')}")
    return json("Model deleted.", request.args.get("type"))


@ai_bp.get("ai/summarize")
@requires_authentication
async def summarize_publication(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publication = await Publication.get(
        id=request.args.get("publication"), research_session=session, deleted=False
    )
    response = await http_client.get(publication.url)
    response.raise_for_status()
    body = get_body_text(BeautifulSoup(response.text, "html.parser"))[1000:4000]
    chain = (
        {
            "input": RunnablePassthrough(),
        }
        | ChatPromptTemplate.from_template(
            "Given the findings of the report and methodology for the research, what would be some next logical steps "
            "to advance the concept further.\n\n{input}"
        )
        | llm
        | StrOutputParser()
    )
    response = await request.respond()
    try:
        async for chunk in chain.astream(body):
            await response.send(chunk)
        await response.eof()
    except Exception as e:  # TODO: Better error handling
        print(e)


@ai_bp.put("ai/classify")
@requires_authentication
async def classify_publications(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publications = await Publication.filter(
        research_session=session, deleted=False
    ).all()
    response = await request.respond()
    total_publications = len(publications)
    try:
        for index, publication in enumerate(publications, start=1):
            if not publication.category or str_to_bool(request.args.get("override")):
                publication.category = classify(
                    session, publication.abstract, request.args.get("type")
                )
                await publication.save(update_fields=["category"])
            await response.send(f"{100 * (index / total_publications):.1f}%")
    except Exception:  # TODO: Better error handling.
        pass
