import asyncio
import os
from redis import Redis
from .tasks import CandidateTaskProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main worker entry point"""
    redis_host = os.getenv('REDIS_HOST')
    redis_port = int(os.getenv('REDIS_PORT'))
    
    redis_client = Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    
    processor = CandidateTaskProcessor(redis_client)
    
    try:
        await processor.run_worker()
    except KeyboardInterrupt:
        logger.info("Worker shutting down...")
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
