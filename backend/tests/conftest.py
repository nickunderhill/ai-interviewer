"""
Pytest configuration and fixtures for testing.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
import os
import uuid

from httpx import AsyncClient
import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Ensure security settings are available during tests even if the developer
# hasn't exported them in the shell running pytest.
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DB_HOST", "localhost")
# Generate a valid Fernet key for testing encryption
from cryptography.fernet import Fernet

os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Uses test database from environment variables.
    """
    # Use test database URL
    test_database_url = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

    schema_name = f"test_{uuid.uuid4().hex}"

    engine = create_async_engine(
        test_database_url,
        echo=False,
        connect_args={"server_settings": {"search_path": schema_name}},
    )

    # Import models so they're registered with Base.metadata
    from app.models import user as _user  # noqa: F401
    from app.models import resume as _resume  # noqa: F401
    from app.models import job_posting as _job_posting  # noqa: F401
    from app.models import interview_session as _interview_session  # noqa: F401
    from app.models import session_message as _session_message  # noqa: F401
    from app.models import operation as _operation  # noqa: F401

    # Create isolated schema + tables (prevents dropping dev DB objects)
    async with engine.begin() as conn:
        await conn.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        await conn.execute(sa.text(f'SET search_path TO "{schema_name}"'))
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Cleanup: drop the isolated schema and everything created in it
    async with engine.begin() as conn:
        await conn.execute(sa.text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))

    await engine.dispose()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency to use test database."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test HTTP client with database override."""
    # Add test protected endpoint for auth dependency testing
    from tests.api.v1.test_auth_dependency import create_test_protected_endpoint

    create_test_protected_endpoint(app)

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


class _HybridClient:
    """
    Hybrid client that supports:
    - Sync usage for .get() (used by some tests)
    - Async usage for .post() and .get() via awaiting
    This avoids event loop mismatches with TestClient when using AsyncSession.
    """

    def __init__(
        self, app, loop: asyncio.AbstractEventLoop, base_url: str = "http://test"
    ):
        self._app = app
        self._loop = loop
        self._base_url = base_url

    def get(self, *args, **kwargs):
        """Synchronous GET for tests that don't use asyncio.

        IMPORTANT: Reuse the same event loop that created async fixtures (e.g.
        AsyncSession) to avoid cross-event-loop SQLAlchemy/asyncpg errors.
        """
        from httpx import AsyncClient

        async def _call():
            async with AsyncClient(app=self._app, base_url=self._base_url) as ac:
                return await ac.get(*args, **kwargs)

        if self._loop.is_closed():
            raise RuntimeError("Test event loop is closed; cannot run sync HTTP call")
        if self._loop.is_running():
            raise RuntimeError(
                "client.get() cannot run while the loop is running; "
                "use the 'async_client' fixture instead"
            )

        return self._loop.run_until_complete(_call())

    async def post(self, *args, **kwargs):
        from httpx import AsyncClient

        async with AsyncClient(app=self._app, base_url=self._base_url) as ac:
            return await ac.post(*args, **kwargs)

    async def get_async(self, *args, **kwargs):
        from httpx import AsyncClient

        async with AsyncClient(app=self._app, base_url=self._base_url) as ac:
            return await ac.get(*args, **kwargs)


@pytest.fixture
def client(override_get_db, event_loop) -> Generator:
    """Provide a hybrid test client compatible with both sync and async tests."""
    # Add test protected endpoint for auth dependency testing
    from tests.api.v1.test_auth_dependency import create_test_protected_endpoint

    create_test_protected_endpoint(app)

    yield _HybridClient(app, loop=event_loop)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user in the database."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict[str, str]:
    """Create authentication headers with valid JWT token for test user."""
    from app.core.security import create_access_token

    token = create_access_token({"user_id": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_job_posting(db_session: AsyncSession, test_user):
    """Create a test job posting for the test user."""
    from app.models.job_posting import JobPosting

    job_posting = JobPosting(
        user_id=test_user.id,
        title="Senior Python Developer",
        company="Test Corp",
        description="Test job description for interview practice",
        experience_level="Senior",
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)
    return {
        "id": job_posting.id,
        "title": job_posting.title,
        "company": job_posting.company,
        "description": job_posting.description,
        "user_id": job_posting.user_id,
    }


@pytest_asyncio.fixture
async def other_user_job_posting(db_session: AsyncSession):
    """Create a job posting owned by another user."""
    from app.models.user import User
    from app.models.job_posting import JobPosting
    from app.core.security import hash_password

    other_user = User(
        email="otheruser@example.com",
        hashed_password=hash_password("password123"),
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    job_posting = JobPosting(
        user_id=other_user.id,
        title="Other User's Job",
        description="Job posting for another user",
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)
    return {
        "id": job_posting.id,
        "title": job_posting.title,
        "user_id": job_posting.user_id,
    }


@pytest_asyncio.fixture
async def test_sessions(db_session: AsyncSession, test_user, test_job_posting):
    """Create multiple test sessions with different statuses."""
    from app.models.interview_session import InterviewSession

    sessions = []
    for status in ["active", "paused", "completed"]:
        session = InterviewSession(
            user_id=test_user.id,
            job_posting_id=test_job_posting["id"],
            status=status,
            current_question_number=0,
        )
        db_session.add(session)
        sessions.append(session)

    await db_session.commit()
    for session in sessions:
        await db_session.refresh(session)

    return [
        {
            "id": session.id,
            "user_id": session.user_id,
            "status": session.status,
        }
        for session in sessions
    ]


@pytest_asyncio.fixture
async def other_user_session(db_session: AsyncSession, other_user_job_posting):
    """Create a session owned by another user."""
    from app.models.interview_session import InterviewSession

    session = InterviewSession(
        user_id=other_user_job_posting["user_id"],
        job_posting_id=other_user_job_posting["id"],
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return {
        "id": session.id,
        "user_id": session.user_id,
    }


@pytest_asyncio.fixture
async def test_session_with_resume(
    db_session: AsyncSession, test_user, test_job_posting
):
    """Create a test session with user having a resume."""
    from app.models.interview_session import InterviewSession
    from app.models.resume import Resume

    # Create resume for test user
    resume = Resume(
        user_id=test_user.id,
        content="Test resume content with skills and experience",
    )
    db_session.add(resume)
    await db_session.commit()

    # Create session
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting["id"],
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    return {
        "id": session.id,
        "user_id": session.user_id,
        "has_resume": True,
    }


@pytest_asyncio.fixture
async def test_session_no_resume(db_session: AsyncSession, test_user):
    """Create a test session for the authenticated user who has no resume."""
    from app.models.interview_session import InterviewSession
    from app.models.job_posting import JobPosting

    # Create job posting for the existing test_user (who has no resume here)
    job_posting = JobPosting(
        user_id=test_user.id,
        title="Test Job",
        company="Test Corp",
        description="Test description",
        experience_level="Junior",
        tech_stack=["Python"],
    )
    db_session.add(job_posting)
    await db_session.commit()

    # Create session
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    return {
        "id": session.id,
        "user_id": test_user.id,
        "has_resume": False,
    }


@pytest_asyncio.fixture
async def test_active_session(db_session: AsyncSession, test_user, test_job_posting):
    """Create a test session with active status."""
    from app.models.interview_session import InterviewSession

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting["id"],
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return {
        "id": session.id,
        "user_id": session.user_id,
        "status": session.status,
    }


@pytest_asyncio.fixture
async def test_completed_session(db_session: AsyncSession, test_user, test_job_posting):
    """Create a test session with completed status."""
    from app.models.interview_session import InterviewSession

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting["id"],
        status="completed",
        current_question_number=5,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return {
        "id": session.id,
        "user_id": session.user_id,
        "status": session.status,
    }


@pytest_asyncio.fixture
async def test_paused_session(db_session: AsyncSession, test_user, test_job_posting):
    """Create a test session with paused status."""
    from app.models.interview_session import InterviewSession

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting["id"],
        status="paused",
        current_question_number=2,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return {
        "id": session.id,
        "user_id": session.user_id,
        "status": session.status,
    }


@pytest_asyncio.fixture
async def test_session_with_messages(
    db_session: AsyncSession, test_user, test_job_posting
):
    """Create a session populated with a question and an answer."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage

    # Create session
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting["id"],
        status="active",
        current_question_number=2,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Add a question message
    question = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="What is your experience with Python?",
        question_type="technical",
    )
    db_session.add(question)

    # Add an answer message
    answer = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content="I have 5 years of experience...",
        question_type=None,
    )
    db_session.add(answer)

    await db_session.commit()

    return {"id": session.id}
