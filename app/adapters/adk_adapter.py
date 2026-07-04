from dotenv import load_dotenv
load_dotenv()
import asyncio
from app.adapters.base import BaseAdapter
from app.external_adk.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import (
    InMemorySessionService,
)
from google.genai import types


class ADKAdapter(BaseAdapter):
    name = "adk"

    async def _run(self, prompt: str):
        session_service = InMemorySessionService()

        runner = Runner(
            agent=root_agent,
            app_name="expense_approval_agent",
            session_service=session_service,
            auto_create_session=True,
        )

        final_text = ""

        async for event in runner.run_async(
            user_id="benchmark",
            session_id="benchmark",
            new_message=types.Content(
                parts=[types.Part(text=prompt)]
            ),
        ):
            

            if event.content and event.content.parts:
               

                for part in event.content.parts:
                   

                    if part.text:
                        final_text += part.text
        return final_text

    def invoke(self, prompt: str):
        return asyncio.run(
            self._run(prompt)
        )