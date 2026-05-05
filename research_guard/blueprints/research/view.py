import csv
import io
import os
from datetime import datetime

from sanic import Blueprint, redirect
from sanic.logging.loggers import logger
from sanic_security.authentication import requires_authentication, authenticate
from sanic_security.authorization import check_roles
from sanic_security.exceptions import SessionError, AuthorizationError
from sanic_security.utils import json
from tortoise.expressions import Q

from research_guard.blueprints.research.models import (
    ResearchSession,
    Publication,
    Memo,
)

research_bp = Blueprint("Research")
research_bp.static("/", "static/index.html", name="research_index")
research_bp.static(
    "/publications", "static/publications.html", name="research_publications"
)
research_bp.static(
    "/new-publication", "static/new-publication.html", name="research_new_publication"
)
research_bp.static("/admin", "static/admin.html", name="research_admin")


@research_bp.post("research/session")
@requires_authentication
async def create_research_session(request):
    session = await ResearchSession.create(
        title=request.form.get("title"),
        account=request.ctx.session.bearer,
    )
    return json("Research session created.", session.json)


@research_bp.get("research/session/invite")
async def research_session_invite(request):
    try:
        authentication_session = await authenticate(request)
        session = await ResearchSession.get(
            id=request.args.get("id"),
            deleted=False,
        )
        await session.contributors.add(authentication_session.bearer)
        return redirect("/")
    except SessionError:
        return redirect(f"/login?invite={request.args.get("id")}")


@research_bp.put("research/session")
@requires_authentication
async def update_research_session(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("id"),
        deleted=False,
    )
    session.title = request.form.get("title")
    await session.save(update_fields=["title"])
    return json("Research session updated.", session.json)


@research_bp.get("research/session")
@requires_authentication
async def get_all_research_sessions(request):
    sessions = (
        await ResearchSession.filter(
            Q(account=request.ctx.session.bearer)
            | Q(contributors__id=request.ctx.session.bearer.id),
            deleted=False,
        )
        .distinct()
        .all()
    )
    return json("Research sessions retrieved.", [s.json for s in sessions])


@research_bp.delete("research/session")
@requires_authentication
async def delete_research_session(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("id"),
        deleted=False,
    )
    session.deleted = True
    await session.save(update_fields=["deleted"])
    os.rmdir(f"resources/bucket/{session.id}")
    return json("Research session deleted.", session.json)


@research_bp.get("research/session/contributors")
@requires_authentication
async def research_session_contributors(request):
    session = (
        await ResearchSession.filter(
            Q(account=request.ctx.session.bearer)
            | Q(contributors__id=request.ctx.session.bearer.id),
            id=request.args.get("id"),
            deleted=False,
        )
        .prefetch_related("account")
        .get()
    )
    contributors = await session.contributors.filter(deleted=False).all()
    return json(
        "Research session contributors retrieved.",
        {
            "owner": session.account.username,
            "contributors": [
                {"id": contributor.id, "username": contributor.username}
                for contributor in contributors
            ],
        },
    )


@research_bp.delete("research/session/contributors")
@requires_authentication
async def remove_research_session_contributors(request):
    session = (
        await ResearchSession.filter(
            Q(account=request.ctx.session.bearer)
            | Q(contributors__id=request.ctx.session.bearer.id),
            id=request.args.get("id"),
            deleted=False,
        )
        .prefetch_related("account")
        .get()
    )
    if request.ctx.session.bearer.id == session.account.id:
        contributor_removed = await session.contributors.filter(
            id=request.args.get("account"), deleted=False
        ).get()
        await session.contributors.remove(contributor_removed)
    else:
        raise AuthorizationError("Only owner can remove contributors.")
    return json(
        "Research session contributor removed.",
        {"id": contributor_removed.id, "username": contributor_removed.username},
    )


@research_bp.post("research/publication")
@requires_authentication
async def create_publication(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publication = await Publication.create(
        title=request.form.get("title"),
        abstract=request.form.get("abstract"),
        url=request.form.get("url"),
        authors=request.form.get("authors").split(","),
        submission_date=datetime.strptime(
            request.form.get("submission-date"), "%Y-%m-%dT%H:%M"
        ),
        category=request.form.get("category"),
        metadata=request.form.get("metadata"),
        research_session=session,
    )
    return json("Publication created.", publication.json)


@research_bp.put("research/publication")
@requires_authentication
async def update_publication(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publication = await Publication.get(
        id=request.args.get("id"), research_session=session, deleted=False
    )
    publication.title = request.form.get("title")
    publication.abstract = request.form.get("abstract")
    publication.url = request.form.get("url")
    publication.authors = request.form.get("authors").split(", ")
    publication.submission_date = datetime.strptime(
        request.form.get("submission-date"), "%Y-%m-%dT%H:%M"
    )
    publication.category = request.form.get("category")
    publication.metadata = request.form.get("metadata")

    await publication.save(
        update_fields=[
            "title",
            "abstract",
            "url",
            "authors",
            "submission_date",
            "category",
            "metadata",
        ]
    )
    return json("Publication updated.", publication.json)


@research_bp.get("research/publication/all")
@requires_authentication
async def get_all_publications(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publications = await Publication.filter(
        research_session=session, deleted=False
    ).all()
    return json(
        "Publications retrieved.", [publication.json for publication in publications]
    )


@research_bp.get("research/publication")
@requires_authentication
async def get_publication(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publication = await Publication.get(
        research_session=session, id=request.args.get("id"), deleted=False
    )
    return json("Publication retrieved.", publication.json)


@research_bp.delete("research/publication")
@requires_authentication
async def delete_publication(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publication = await Publication.get(
        id=request.args.get("id"), research_session=session, deleted=False
    )
    publication.deleted = True
    await publication.save(update_fields=["deleted"])
    return json("Publication deleted.", publication.json)


@research_bp.post("research/publication/import")
@requires_authentication
async def import_publications(request):
    uploaded_file = request.files.get("dataset")
    if not uploaded_file:
        raise ValueError("No dataset uploaded.")
    if request.args.get("session"):
        session = await ResearchSession.get(
            Q(account=request.ctx.session.bearer)
            | Q(contributors__id=request.ctx.session.bearer.id),
            id=request.args.get("session"),
            deleted=False,
        )
    else:
        await check_roles(request, "Root")
        session = None
    publications = []
    file_stream = io.StringIO(uploaded_file.body.decode("utf-8"))
    reader = csv.reader(file_stream)
    next(reader)  # Skip header.
    for row in reader:
        try:
            publication = await Publication.create(
                title=row[0],
                abstract=row[1],
                authors=row[2].split(","),
                url=row[3],
                submission_date=datetime.strptime(row[5], "%Y-%m-%dT%H:%M:%S"),
                metadata=row[6],
                category=row[7] if len(row) >= 8 else None,
                research_session=session,
            )
            publications.append(publication.json)
        except Exception as e:
            logger.warning(f"Error occurred uploading publication {e}")
    return json("Publications imported.", publications)


@research_bp.get("research/publication/search")
@requires_authentication
async def search_publications(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    if not request.args.get("query"):
        return json("No query provided.", None, 400)
    publications = await Publication.filter(
        (
            Q(title__icontains=request.args.get("query"))
            | Q(abstract__icontains=request.args.get("query"))
            | Q(metadata__icontains=request.args.get("query"))
            | Q(url__icontains=request.args.get("query"))
            | Q(category__icontains=request.args.get("query"))
        ),
        research_session=session,
        deleted=False,
    ).all()
    return json("Recommendations retrieved.", [pub.json for pub in publications])


@research_bp.get("research/memo")
@requires_authentication
async def get_memos(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    memos = (
        await Memo.filter(research_session=session, deleted=False)
        .prefetch_related("publication", "account")
        .all()
    )
    return json("Memos retrieved.", [memo.json for memo in memos])


@research_bp.post("research/memo")
@requires_authentication
async def create_memo(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    publication = await Publication.get(
        research_session=request.args.get("session"),
        id=request.args.get("publication"),
        deleted=False,
    )
    memo = await Memo.create(
        title=request.form.get("title"),
        content=request.form.get("content"),
        research_session=session,
        publication=publication,
        account=request.ctx.session.bearer,
    )
    return json("Memo created.", memo.json)


@research_bp.put("research/memo")
@requires_authentication
async def update_memo(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    memo = await Memo.get(
        id=request.args.get("id"),
        research_session=session,
        deleted=False,
    )
    memo.title = request.form.get("title")
    memo.content = request.form.get("content")
    await memo.save(update_fields=["title", "content"])
    return json("Memo updated.", memo.json)


@research_bp.delete("research/memo")
@requires_authentication
async def delete_memo(request):
    session = await ResearchSession.get(
        Q(account=request.ctx.session.bearer)
        | Q(contributors__id=request.ctx.session.bearer.id),
        id=request.args.get("session"),
        deleted=False,
    )
    memo = await Memo.get(
        id=request.args.get("id"),
        research_session=session,
        deleted=False,
    )
    memo.deleted = True
    await memo.save(update_fields=["deleted"])
    return json("Memo deleted.", memo.json)
4