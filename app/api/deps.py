from __future__ import annotations
import asyncio
import httpx
from fastapi import Depends
from app.core.config import settings

# Пул асинхронного клиента и семафор для ограничения параллелизма
class ClientPool:
    def __init__(self):
        self.client = httpx.AsyncClient(headers={"User-Agent": settings.USER_AGENT})
        self.sem = asyncio.Semaphore(settings.ARSHIN_CONCURRENCY)

pool = ClientPool()

async def get_http_client() -> httpx.AsyncClient:
    return pool.client

def get_semaphore() -> asyncio.Semaphore:
    return pool.sem
