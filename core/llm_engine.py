from typing import Protocol, Dict, Any, AsyncGenerator, List
import httpx
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger("core.llm_engine")

class LLMProvider(Protocol):
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        ...
        
    async def generate_stream(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        ...

    async def generate_with_image(self, prompt: str, system_prompt: str, base64_image: str) -> str:
        ...

class OllamaProvider:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        logger.info(f"Initialized OllamaProvider with model {self.model}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            response = await client.post(f"{self.base_url}/api/generate", json=payload, timeout=60.0)
            response.raise_for_status()
            return response.json().get("response", "")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_with_image(self, prompt: str, system_prompt: str, base64_image: str) -> str:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": "llava", # Assuming LLaVA is pulled for vision
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "images": [base64_image]
            }
            response = await client.post(f"{self.base_url}/api/generate", json=payload, timeout=120.0)
            response.raise_for_status()
            return response.json().get("response", "")

    async def generate_stream(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": True
            }
            async with client.stream("POST", f"{self.base_url}/api/generate", json=payload, timeout=60.0) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        yield data.get("response", "")
                        if data.get("done"):
                            break

    async def embed(self, text: str) -> List[float]:
        async with httpx.AsyncClient() as client:
            payload = {
                "model": "nomic-embed-text",
                "prompt": text
            }
            response = await client.post(f"{self.base_url}/api/embeddings", json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json().get("embedding", [])

class LlamaCPPProvider:
    def __init__(self, tenant_id: str = None):
        try:
            import os
            from llama_cpp import Llama
            self.model_path = f"models/{settings.LLM_MODEL}.gguf"
            logger.info(f"Initializing LlamaCPPProvider with {self.model_path} for tenant {tenant_id}")
            
            # Check for tenant specific LoRA adapter
            lora_path = None
            if tenant_id:
                potential_lora = f"models/adapters/{tenant_id}/adapter_model.bin"
                if os.path.exists(potential_lora):
                    lora_path = potential_lora
                    logger.info(f"Loading LoRA adapter for tenant {tenant_id}: {lora_path}")
                    
            # Initialize with default parameters, offload to GPU if available
            self.llm = Llama(
                model_path=self.model_path,
                lora_path=lora_path,
                lora_base=self.model_path if lora_path else None,
                n_gpu_layers=-1, # Offload all to GPU if possible
                n_ctx=4096,      # Context window
                verbose=False
            )
        except ImportError:
            logger.error("llama-cpp-python not installed. Cannot use LlamaCPPProvider.")
            raise

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        # Run synchronous llama.cpp inference in an executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        
        def _generate():
            full_prompt = f"System: {system_prompt}\nUser: {prompt}\nAssistant:"
            response = self.llm(
                full_prompt,
                max_tokens=2048,
                stop=["User:", "\nSystem:"],
                echo=False
            )
            return response['choices'][0]['text']

        return await loop.run_in_executor(None, _generate)

    async def generate_stream(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        # Stream is not truly async here because llama-cpp-python is sync, 
        # but we can simulate it or yield chunks. For now, we return full text.
        text = await self.generate(prompt, system_prompt)
        yield text

class OpenAIProvider:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment or settings")
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            # Default to gpt-4o or use LLM_MODEL if it's an OpenAI model name
            self.model = settings.LLM_MODEL if "gpt" in settings.LLM_MODEL else "gpt-4o"
            logger.info(f"Initialized OpenAIProvider with model {self.model}")
        except ImportError:
            logger.error("openai package not installed. Run 'pip install openai'")
            raise

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content

    async def generate_stream(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

class LLMEngine:
    def __init__(self, tenant_id: str = None):
        self.provider_type = settings.LLM_PROVIDER
        if self.provider_type == "ollama":
            self.provider: LLMProvider = OllamaProvider()
        elif self.provider_type == "llamacpp":
            self.provider: LLMProvider = LlamaCPPProvider(tenant_id)
        elif self.provider_type == "openai":
            self.provider: LLMProvider = OpenAIProvider()
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider_type}")

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a complete string response."""
        return await self.provider.generate(prompt, system_prompt)

    async def generate_stream(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        """Generate response as a stream of tokens."""
        async for chunk in self.provider.generate_stream(prompt, system_prompt):
            yield chunk

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        if hasattr(self.provider, "embed"):
            return await self.provider.embed(text)
        return []

    async def generate_with_image(self, prompt: str, system_prompt: str, base64_image: str) -> str:
        """Generate response given an image and a prompt."""
        if hasattr(self.provider, "generate_with_image"):
            return await self.provider.generate_with_image(prompt, system_prompt, base64_image)
        # Fallback if provider doesn't support vision
        return await self.generate(prompt, system_prompt)
