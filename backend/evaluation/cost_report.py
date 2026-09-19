from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.db.models import AgentTrace

# Placeholder rate — check Google's current published Gemini pricing for
# whichever model you're actually using before trusting this number for
# anything beyond a rough order-of-magnitude estimate.
COST_PER_1K_PROMPT_TOKENS = 0.00
COST_PER_1K_COMPLETION_TOKENS = 0.00


async def report():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(
                AgentTrace.agent_name,
                func.avg(AgentTrace.duration_ms).label("avg_ms"),
                func.sum(AgentTrace.prompt_tokens).label("total_prompt"),
                func.sum(AgentTrace.completion_tokens).label("total_completion"),
                func.count(AgentTrace.id).label("n_runs"),
            ).group_by(AgentTrace.agent_name)
        )
        print(f"{'Agent':<28} {'Avg ms':<10} {'Runs':<6} {'Prompt tok':<12} {'Completion tok':<14}")
        for row in result:
            print(f"{row.agent_name:<28} {row.avg_ms or 0:<10.0f} {row.n_runs:<6} {row.total_prompt or 0:<12} {row.total_completion or 0:<14}")