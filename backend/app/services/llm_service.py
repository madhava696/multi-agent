import logging
from typing import Dict, List, Optional
from enum import Enum
from openai import OpenAI
from app.prompts.LLMPrompts import LLMPrompts
from app.config.settings import settings

if settings.langfuse_enabled:
    try:
        from langfuse import observe
    except ImportError:
        def observe(*args,**kwargs):
            def decorator(func):
                return func
            return decorator if args and callable(args[0]) else decorator
else:
     def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if args and callable(args[0]) else decorator
    
logger  = logging.getLogger(__name__)

class ModelCapability(Enum):
    """Define unique capabilities for different models"""
    SUMMARIZATION = "summarization"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    QUESTION_ANSWERING = "question_answering"
    
    
class ModelConfig:
    """Configuration for top 4 HuggingFace Router models"""
    
    MODELS = {
        "deepseek-ai/DeepSeek-V4-Pro":{
            "capabilities": [ModelCapability.REASONING, ModelCapability.SUMMARIZATION],
            "max_tokens": 4096,
            "temperature": 0.7,
            "best_for": "Complex reasoning, analysis, and summarization",
            "size": "862B"
        },
        
        "Qwen/Qwen2.5-Coder-7B-Instruct": {
            "capabilities": [ModelCapability.CODE_GENERATION],
            "max_tokens": 8192,
            "temperature": 0.2,
            "best_for": "Code generation and programming tasks",
            "size": "8B"
        },
        
         "meta-llama/Llama-3.2-3B-Instruct": {
            "capabilities": [ModelCapability.QUESTION_ANSWERING],
            "max_tokens": 2048,
            "temperature": 0.7,
            "best_for": "Fast Q&A and simple tasks",
            "size": "3B"
        },
         
        "meta-llama/Llama-3.1-8B-Instruct": {
            "capabilities": [ModelCapability.SUMMARIZATION, ModelCapability.QUESTION_ANSWERING],
            "max_tokens": 4096,
            "temperature": 0.7,
            "best_for": "General purpose tasks and Q&A",
            "size": "8B"
        },
    }
    
class LLMService:
    """
    LLM Service using HuggingFace Router with OpenAI-compatible API
    Uses 4 specialized models for different tasks
    """
    
    def __init__(self):
        self.client = None
        self.langfuse_enabled = settings.langfuse_enabled
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize OpenAI client with HuggingFace Router"""
        
        if not settings.huggingface_api_key:
            logger.warning("HuggingFace API key not configured")
            return
        
        # Initialize standard OpenAI client
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=settings.huggingface_api_key,
        )
        
        if self.langfuse_enabled:
            logger.info("HuggingFace Router client initialized with Langfuse tracing enabled")
        else:
            logger.info("HuggingFace Router client initialized (Langfuse disabled)")
            
    def get_model_for_capability(self, capability: ModelCapability) -> str:
        """
        Select the best model for a given capability
        Returns the model name to use
        """
        capability_models = {
            ModelCapability.SUMMARIZATION: settings.model_summarization,
            ModelCapability.CODE_GENERATION: settings.model_code_generation,
            ModelCapability.QUESTION_ANSWERING: settings.model_question_answering,
            ModelCapability.REASONING: settings.model_reasoning,
        }
        
        custom_model = capability_models.get(capability)
        if custom_model:
            logger.info(f"Using custom model for {capability.value}: {custom_model}")
            return custom_model
        
        default_models = {
            ModelCapability.SUMMARIZATION: settings.huggingface_model,
            ModelCapability.CODE_GENERATION: "Qwen/Qwen2.5-Coder-7B-Instruct",
            ModelCapability.QUESTION_ANSWERING: settings.huggingface_model,
            ModelCapability.REASONING: settings.huggingface_model,
        }
        
        model = default_models.get(capability, settings.huggingface_model)
        logger.info(f"Using default model for {capability.value}: {model}")
        return model

    def _get_fallback_models(
        self,
        selected_model: str,
        capability: Optional[ModelCapability] = None,
    ) -> List[str]:
        fallback_models = [
            selected_model,
            settings.huggingface_model,
            "meta-llama/Llama-3.1-8B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
        ]

        if capability == ModelCapability.CODE_GENERATION:
            fallback_models.insert(1, "Qwen/Qwen2.5-Coder-7B-Instruct")

        unique_models = []
        for fallback_model in fallback_models:
            if fallback_model and fallback_model not in unique_models:
                unique_models.append(fallback_model)

        return unique_models

    @staticmethod
    def _is_model_not_supported_error(error: Exception) -> bool:
        error_text = str(error).lower()
        return (
            "model_not_supported" in error_text
            or "not supported by any provider" in error_text
            or "invalid_request_error" in error_text and "model" in error_text
        )
    
    
    @observe(name="llm_generate")
    async def generate(
        self,
        prompt:str,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        capability: Optional[ModelCapability] = None,
        ) -> str:
        
        """
        Generate text using HuggingFace Router
        
        Args:
            prompt: The input prompt
            model: Specific model to use (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            capability: Model capability to use for automatic model selection
            
        Returns:
            Generated text
        """
        
        if not self.client:
            raise RuntimeError("HuggingFace Router client not initialized. Check HF_TOKEN.")
        
        if not model and capability:
            model = self.get_model_for_capability(capability)
        elif not model:
            model = settings.huggingface_model
            
        for candidate_model in self._get_fallback_models(model, capability):
            logger.info(
                "Generating with HuggingFace Router",
                extra={"model": candidate_model, "temperature": temperature, "max_tokens": max_tokens}
            )

            try:
                completion = self.client.chat.completions.create(
                    model=candidate_model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                response = completion.choices[0].message.content or ""
                logger.info(
                    "HuggingFace Router generation completed",
                    extra={"model": candidate_model, "response_length": len(response)},
                )

                return response
            except Exception as e:
                if self._is_model_not_supported_error(e) and candidate_model != self._get_fallback_models(model, capability)[-1]:
                    logger.warning(
                        "HuggingFace Router rejected configured model; trying fallback.",
                        extra={"model": candidate_model, "reason": str(e)},
                    )
                    continue

                logger.error(f"Error generating with HuggingFace Router: {e}")
                raise

        raise RuntimeError("HuggingFace Router generation failed for all configured fallback models.")
        
    async def summarize(self,text:str,context:str="") -> str:
        """Summarize text using DeepSeek-V4-Pro (best for reasoning/summarization)"""
        prompt = LLMPrompts.summarization(text=text, context=context)
        
        return await self.generate(
            prompt=prompt,
            capability=ModelCapability.SUMMARIZATION,
            max_tokens=1024,
            temperature=0.5,
        )
        
    async def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code using Qwen2.5-Coder (best for code generation)"""
        prompt = LLMPrompts.code_generation(description=description, language=language)
        
        return await self.generate(
            prompt=prompt,
            capability=ModelCapability.CODE_GENERATION,
            max_tokens=2048,
            temperature=0.2,
        )

    async def answer_question(self, question: str, context: str = "") -> str:
        """Answer a question using Llama-3.2-3B (fast Q&A)"""
        prompt = LLMPrompts.question_answering(question=question, context=context)
        
        return await self.generate(
            prompt=prompt,
            capability=ModelCapability.QUESTION_ANSWERING,
            max_tokens=1024,
            temperature=0.7,
        )

    async def grounded_answer(
        self,
        question: str,
        retrieved_documents: str,
        conversation_history: str = "",
    ) -> str:
        """Answer a question from retrieved documents with conversation context."""
        prompt = LLMPrompts.grounded_answer(
            user_message=question,
            retrieved_documents=retrieved_documents,
            conversation_history=conversation_history,
        )

        return await self.generate(
            prompt=prompt,
            capability=ModelCapability.QUESTION_ANSWERING,
            max_tokens=1024,
            temperature=0.2,
        )

    async def reason(self, problem: str) -> str:
        """Solve a complex reasoning problem using DeepSeek-V4-Pro"""
        prompt = LLMPrompts.reasoning(problem=problem)
        
        return await self.generate(
            prompt=prompt,
            capability=ModelCapability.REASONING,
            max_tokens=2048,
            temperature=0.7,
        )

    def list_available_models(self) -> List[Dict]:
        """List all 4 available models with their capabilities"""
        return [
            {
                "name": name,
                "capabilities": [cap.value for cap in config["capabilities"]],
                "best_for": config["best_for"],
                "size": config["size"],
                "max_tokens": config["max_tokens"],
            }
            for name, config in ModelConfig.MODELS.items()
        ]
