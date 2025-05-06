from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyTools")

@mcp.tool()
def lookup_wikipedia(topic: str) -> str:
    return f"First paragraph of {topic} …"

if __name__ == "__main__":
    mcp.run()