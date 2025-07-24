import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.core import SessionLocal
from ..entities.candidate import Candidate
from src.candidates.model import CandidateUpdate
from ..entities.task import Task, TaskType
from sqlalchemy import select
import os
from src.ai.groq import generate_chat_completion
from src.emails.resend import send_enhancement_email

logger = logging.getLogger(__name__)

class CandidateTaskProcessor:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.queue_name = os.getenv("REDIS_QUEUE_NAME")
        self.retry_queue_name = os.getenv("REDIS_RETRY_QUEUE_NAME")
        self.lock_prefix = os.getenv("REDIS_LOCK_PREFIX")
        self.lock_ttl = int(os.getenv("REDIS_LOCK_TTL"))  # seconds
        self.polling_interval = int(os.getenv("WORKER_POLLING_INTERVAL"))  # seconds
        self.max_retries = int(os.getenv("WORKER_MAX_RETRIES"))
        
        # Metrics
        self.start_time = time.time()

    def enqueue_task(self, candidate_id: UUID, task_type: TaskType, payload: Dict[str, Any]) -> bool:
        """Enqueue a new task for processing"""
        # Replace the task dictionary with the Task entity
        new_task = Task(
            candidate_id=str(candidate_id),
            task_type=task_type,
            payload=payload
        )

        try:
            self.redis.rpush(self.queue_name, json.dumps(new_task.to_dict()))
            logger.info(f"Enqueued task {task_type} for candidate {candidate_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            return False
    
    def acquire_lock(self, candidate_id: str) -> bool:
        """Acquire a candidate-level lock using SETNX"""
        lock_key = f"{self.lock_prefix}{candidate_id}"
        
        # Use SETNX with expiration
        result = self.redis.set(
            lock_key, 
            f"locked_at_{time.time()}", 
            nx=True,  # Only set if not exists
            ex=self.lock_ttl  # Expire after TTL seconds
        )
        
        if result:
            logger.info(f"Acquired lock for candidate {candidate_id}")
            return True
        else:
            logger.debug(f"Lock already exists for candidate {candidate_id}")
            return False
    
    def release_lock(self, candidate_id: str) -> bool:
        """Release the candidate-level lock"""
        lock_key = f"{self.lock_prefix}{candidate_id}"
        result = self.redis.delete(lock_key)
        
        if result:
            logger.info(f"Released lock for candidate {candidate_id}")
            return True
        return False
    
    async def process_resume_parsing(self, candidate_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process resume parsing using Groq API"""
        logger.info(f"Starting resume parsing for candidate {candidate_id}")

        try:
            # Call Groq API for resume parsing
            resume_content = payload.get("resume_content", "")
            prompt = f"Extract programming skills from this resume: {resume_content}. Return them as a list of format ['skill1', 'skill2', ...]. Do not add any other text aside from the list of skills."
            skills_response = generate_chat_completion(prompt, model="llama-3.3-70b-versatile", stream=False)
            programming_skills = eval(skills_response)  # Convert string representation of a list to an actual list

            # Update candidate in database
            async with SessionLocal() as db:
                result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
                candidate = result.scalar_one_or_none()

                if candidate:
                    candidate.skills = programming_skills
                    await db.commit()

                    logger.info(f"Updated skills for candidate {candidate_id}: {candidate.skills}")

                    return {
                        "status": "success",
                        "parsed_skills": candidate.skills
                    }

            return {"status": "failed", "error": "Candidate not found"}

        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def process_external_enrichment(self, candidate_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process external enrichment using Groq API"""
        logger.info(f"Starting external enrichment for candidate {candidate_id}")

        try:
            # Call Groq API for enrichment
            enrichment_request = payload.get("enrichment_request", "")
            prompt = f"Create profile links from this candidate profile: {enrichment_request}. Return them as a list of format ['link1', 'link2', ...]. Do not add any other text aside from the list of links."
            links_response = generate_chat_completion(prompt, model="llama-3.3-70b-versatile", stream=False)
            profile_links = eval(links_response)  # Convert string representation of a list to an actual list

            # Update candidate in database
            async with SessionLocal() as db:
                result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
                candidate = result.scalar_one_or_none()

                if candidate:
                    logger.info(f"Enriched candidate {candidate_id} with profile links: {candidate.profile_links}")

                    html_content = f"<p>Profile links for candidate {candidate_id}: {', '.join(profile_links)}</p>"
                    send_enhancement_email(html_content)

                    return {
                        "status": "success",
                        "profile_links": candidate.profile_links
                    }

            return {"status": "failed", "error": "Candidate not found"}

        except Exception as e:
            logger.error(f"External enrichment failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task based on task_type"""
        task_type = task["task_type"]
        candidate_id = task["candidate_id"]
        payload = task["payload"]
        
        try:
            if task_type == "resume_parsing":
                return await self.process_resume_parsing(candidate_id, payload)
            elif task_type == "external_enrichment":
                return await self.process_external_enrichment(candidate_id, payload)
            else:
                logger.error(f"Unknown task type: {task_type}")
                return {"status": "failed", "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def move_to_retry_queue(self, task: Dict[str, Any]):
        """Move failed task to retry queue"""
        task["retry_count"] = task.get("retry_count", 0) + 1
        task["failed_at"] = time.time()
        
        try:
            self.redis.rpush(self.retry_queue_name, json.dumps(task))
            logger.info(f"Moved task to retry queue: {task['task_type']} for candidate {task['candidate_id']}")
        except Exception as e:
            logger.error(f"Failed to move task to retry queue: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        uptime = time.time() - self.start_time
        tasks_per_minute = (int(self.redis.get("processed_count") or 0) / uptime) * 60 if uptime > 0 else 0
        
        return {
            "processed_count": int(self.redis.get("processed_count") or 0),
            "failed_count": int(self.redis.get("failed_count") or 0),
            "uptime_seconds": uptime,
            "tasks_per_minute": round(tasks_per_minute, 2),
            "queue_length": self.redis.llen(self.queue_name),
            "retry_queue_length": self.redis.llen(self.retry_queue_name)
        }
    
    async def run_worker(self):
        """Main worker loop"""
        logger.info("Starting candidate task processor worker...")
        
        while True:
            try:
                # Poll the main queue
                task_data = self.redis.blpop(self.queue_name, timeout=self.polling_interval)
                
                if not task_data:
                    # Check retry queue
                    retry_task_data = self.redis.blpop(self.retry_queue_name, timeout=1)
                    if retry_task_data:
                        task_data = retry_task_data
                
                if task_data:
                    _, task_json = task_data
                    task = json.loads(task_json)
                    candidate_id = task["candidate_id"]
                    
                    # Try to acquire lock
                    if self.acquire_lock(candidate_id):
                        try:
                            logger.info(f"Processing task {task['task_type']} for candidate {candidate_id}")
                            
                            # Process the task
                            result = await self.process_task(task)
                            
                            if result["status"] == "success":
                                # Increment processed_count in Redis
                                self.redis.incr("processed_count")
                                
                                logger.info(f"Successfully processed task for candidate {candidate_id}")
                            else:
                                # Handle failure
                                self.redis.incr("failed_count")
                                retry_count = task.get("retry_count", 0)
                                
                                if retry_count < self.max_retries:
                                    self.move_to_retry_queue(task)
                                else:
                                    logger.error(f"Task permanently failed after {self.max_retries} retries: {task}")
                                    
                        finally:
                            # Always release the lock
                            self.release_lock(candidate_id)
                    else:
                        # Lock not acquired, put task back in queue
                        logger.info(f"Could not acquire lock for candidate {candidate_id}, requeueing...")
                        self.redis.rpush(self.queue_name, task_json)
                
                # Log metrics every minute
                if int(self.redis.get("processed_count") or 0) % 10 == 0:
                    metrics = self.get_metrics()
                    logger.info(f"Worker metrics: {metrics}")
                    
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)  # Wait before retrying