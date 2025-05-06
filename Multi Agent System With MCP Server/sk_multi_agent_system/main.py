import os
import asyncio
from dotenv import load_dotenv
import traceback
import json
import sys

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.google.google_ai.services.google_ai_chat_completion import GoogleAIChatCompletion
from semantic_kernel.functions.kernel_arguments import KernelArguments

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def clean_output(text: str) -> str:
    try:
        json.loads(text)
        return text.split('"text": "')[-1].split('"}')[0].strip()
    except json.JSONDecodeError:
        pass

    if "value=" in text:
        text = text.split("value=")[-1].strip()
    if "text=" in text:
        text = text.split("text=")[-1].strip()

    text = text.strip('"<>\'')
    text = text.replace('\\n', '\n').replace('\\t', '\t')

    return text.strip()

async def main(topic: str):
    try:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in .env")

        gemini_service = GoogleAIChatCompletion(
            gemini_model_id="gemini-1.5-flash",
            api_key=api_key,
            service_id="gemini"
        )
        kernel = Kernel()
        kernel.add_service(gemini_service)

        server_params = StdioServerParameters(
            command=sys.executable,
            args=["mcp_server.py"]
        )

        async with stdio_client(server_params) as (reader, writer):
            async with ClientSession(reader, writer) as mcp_session:
                await mcp_session.initialize()

                tools = await mcp_session.list_tools()
                print("Available MCP tools:", tools)

                mcp_session.service_id = "mcp"
                kernel.add_service(mcp_session, "mcp")

                mcp_tool_fn = kernel.add_function(
                    plugin_name="mcp",
                    function_name="lookup_wikipedia",
                    description="Fetch the first paragraph from Wikipedia",
                    prompt="{{ $input }}"
                )

                research_agent_fn = kernel.add_function(
                    plugin_name="gemini",
                    function_name="ResearchAgent",
                    description="Research the given topic",
                    prompt="You are a researcher. Provide a detailed, well-structured research summary on this topic: {{$input}}"
                )
                writing_agent_fn = kernel.add_function(
                    plugin_name="gemini",
                    function_name="WritingAgent",
                    description="Draft a narrative from the research",
                    prompt="You are a writer. Create a well-structured article from this research. Focus on clarity and engagement: {{$input}}"
                )
                finalizing_agent_fn = kernel.add_function(
                    plugin_name="gemini",
                    function_name="FinalizingAgent",
                    description="Polish and edit the draft",
                    prompt="You are an editor. Polish this article while maintaining its accuracy. Improve clarity and flow: {{$input}}"
                )

                output_content = []

                print("\nUsing MCP tool to define topic…")
                def_res = await kernel.invoke(
                    function=mcp_tool_fn,
                    arguments=KernelArguments(input=topic)
                )
                def_text = clean_output(str(def_res))
                output_content.append(f"# Definition of {topic}\n\n{def_text}\n")

                print("\nGenerating research…")
                research_res = await kernel.invoke(
                    function=research_agent_fn,
                    arguments=KernelArguments(input=topic)
                )
                research_text = clean_output(str(research_res))
                output_content.append(f"# Research Summary on {topic}\n\n{research_text}\n")

                print("\nDrafting article…")
                writing_res = await kernel.invoke(
                    function=writing_agent_fn,
                    arguments=KernelArguments(input=research_text)
                )
                writing_text = clean_output(str(writing_res))
                output_content.append(f"# Draft Article on {topic}\n\n{writing_text}\n")

                print("\nPolishing article…")
                final_res = await kernel.invoke(
                    function=finalizing_agent_fn,
                    arguments=KernelArguments(input=writing_text)
                )
                final_text = clean_output(str(final_res))
                output_content.append(f"# Final Article on {topic}\n\n{final_text}\n")

                with open("output.md", "w", encoding="utf-8") as f:
                    f.write("\n\n---\n\n".join(output_content))

                print("\nAll done! See output.md for results.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "The future of AI in healthcare"
    asyncio.run(main(topic))
