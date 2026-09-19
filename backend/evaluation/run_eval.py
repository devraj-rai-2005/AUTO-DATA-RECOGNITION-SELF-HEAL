import asyncio
from collections import Counter
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from evaluation.eval_pipeline import eval_pipeline
from evaluation.dataset import EVAL_CASES

N_RUNS_PER_CASE = 1
DESCRIPTION_TEMPLATE = "Anomalies detected in table {table}. Investigate the root cause."


async def run_case_once(case) -> dict:
    session_service = InMemorySessionService()
    runner = Runner(agent=eval_pipeline, app_name="eval", session_service=session_service)
    session = await session_service.create_session(
        app_name="eval",
        user_id="eval",
        state={"pipeline_run_id": f"eval-{getattr(case, 'name', 'test')}"},
    )

    message = types.Content(role="user", parts=[types.Part(text=DESCRIPTION_TEMPLATE.format(table=case.table))])
    async for _ in runner.run_async(user_id="eval", session_id=session.id, new_message=message):
        pass

    final = await session_service.get_session(app_name="eval", user_id="eval", session_id=session.id)
    incident = final.state.get("incident", {})
    return {
        "predicted_root_cause": incident.get("root_cause", "MISSING"),
        "severity": incident.get("severity"),
    }


async def run_case_with_retry(case, max_retries=5) -> dict:
    for attempt in range(max_retries):
        try:
            return await run_case_once(case)
        except Exception as e:
            err_name = type(e).__name__
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "ResourceExhausted" in err_name:
                wait_time = 20 + (attempt * 5)
                print(f"\n[Gemini 429 Rate Limit] Waiting {wait_time}s cooldown before retrying (attempt {attempt + 1}/{max_retries})...")
                await asyncio.sleep(wait_time)
            else:
                raise e
    raise RuntimeError(f"Max retries exceeded for case: {getattr(case, 'name', case)}")


async def run_all():
    cases = EVAL_CASES
    results = []
    print(f"Starting evaluation across {len(cases)} cases...")
    for idx, case in enumerate(cases, 1):
        case_name = getattr(case, "name", f"case_{idx}")
        print(f"\n[{idx}/{len(cases)}] Running eval case: {case_name} (table: {case.table})")
        await case.setup(case.table)

        predictions = []
        for _ in range(N_RUNS_PER_CASE):
            pred = await run_case_with_retry(case)
            predictions.append(pred)
            await asyncio.sleep(4)

        root_causes = [p["predicted_root_cause"] for p in predictions]
        print(f"  Expected:  {getattr(case, 'expected_root_cause', 'N/A')}")
        print(f"  Predicted: {root_causes}")

        results.append({
            "case": case_name,
            "expected": getattr(case, "expected_root_cause", None),
            "predictions": root_causes,
        })

    print("\n================ EVALUATION COMPLETED ================")
    return results


if __name__ == "__main__":
    results = asyncio.run(run_all())
