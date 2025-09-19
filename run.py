import sys
import asyncio
from dotenv import load_dotenv

from workflow import TourPlannerWorkflow


async def main():
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: python run.py \"Plan a trip from <FROM> to <TO> from <YYYY-MM-DD> to <YYYY-MM-DD>\"")
        sys.exit(1)
    query = sys.argv[1]
    workflow = TourPlannerWorkflow(language="english")
    result = await workflow.run(query=query)
    print(result[:500])


if __name__ == "__main__":
    asyncio.run(main())
