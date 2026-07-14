import json
from typing import Dict,List,Optional
from pydantic import EmailStr

class RedisMemoryService:
    def __init__(self, url : str, ttl_seconds : int):
        self.url = url
        self.ttl_seconds = ttl_seconds
        self._client = None
        self._memory_store : Dict[str,List[Dict[str,str]]]={}
        self._kv_store : Dict[str,str] = {}

        try:
            import importlib

            redis_module = importlib.import_module("redis")
            self._client = redis_module.from_url(url,decode_response=True)
            self._client.ping()
        except Exception:
            self._client = None

        
    def conversation_key(self,conversation_id : str) -> str:
        return f"conversation:{conversation_id}:messages"
    
    def user_key(self,email:EmailStr) ->str:
        return f"user;{email}"
    
    def get_messages(self,conversation_id:str)->List[Dict[str,str]]:

        if self._client:
            try:
                items = self._client.lrange(self.conversation_key(conversation_id),0,-1)
                return [json.loads(item) for item in items]
            except Exception:
                return self._memory_store.get(conversation_id,[])
        return self._memory_store.get(conversation_id,[])