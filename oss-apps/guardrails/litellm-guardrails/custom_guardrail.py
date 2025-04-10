from typing import Any, Dict, List, Literal, Optional, Union, AsyncGenerator
import re
import litellm
from litellm._logging import verbose_proxy_logger
from litellm.caching.caching import DualCache
from litellm.integrations.custom_guardrail import CustomGuardrail
from litellm.proxy._types import UserAPIKeyAuth
from litellm.types.guardrails import GuardrailEventHooks
from litellm.proxy.utils import ModelResponse
import logging

# ロガーの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SecurityGuardrail(CustomGuardrail):
    def __init__(self, **kwargs):
        logger.debug(f"Initializing SecurityGuardrail with kwargs: {kwargs}")
        self.optional_params = kwargs
        super().__init__(**kwargs)

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "pass_through_endpoint",
            "rerank"
        ],
    ) -> Optional[Union[Exception, str, dict]]:
        """
        プロンプトインジェクション検出とPII情報のマスキングを行います
        """
        logger.debug(f"Pre-call hook received data: {data}")
        logger.debug(f"Call type: {call_type}")

        messages = data.get("messages", [])
        if messages:
            for message in messages:
                content = message.get("content")
                logger.debug(f"Processing message content: {content}")
                
                if isinstance(content, str):
                    # プロンプトインジェクション検出
                    suspicious_patterns = [
                        "system prompt",
                        "ignore previous",
                        "reveal instructions",
                        "ignore above",
                        "system message"
                    ]
                    for pattern in suspicious_patterns:
                        if pattern in content.lower():
                            logger.warning(f"Detected suspicious pattern: {pattern}")
                            raise ValueError(f"Potential prompt injection detected: {pattern}")

                    # PII情報のマスキング
                    original_content = content
                    
                    # メールアドレス
                    content = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', content)
                    # 電話番号 (日本の形式も含む)
                    content = re.sub(r'(\d{2,4}[-.]?\d{2,4}[-.]?\d{4}|\d{10,11}|\d{3}[-.]?\d{4}[-.]?\d{4})', '[PHONE]', content)
                    # クレジットカード番号
                    content = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]', content)
                    
                    if content != original_content:
                        logger.info("PII information was masked in the content")
                        logger.debug(f"Original: {original_content}")
                        logger.debug(f"Masked: {content}")
                    
                    message["content"] = content

        logger.debug(f"Pre-call messages after processing: {messages}")
        return data

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
    ):
        """
        LLMの出力を検証し、機密情報や不適切な内容が含まれていないかチェックします
        """
        logger.debug(f"Post-call hook received response: {response}")

        if isinstance(response, litellm.ModelResponse):
            for choice in response.choices:
                if isinstance(choice.message.content, str):
                    content = choice.message.content.lower()
                    logger.debug(f"Checking content: {content}")
                    
                    # 機密情報のチェック
                    sensitive_patterns = [
                        "password",
                        "secret",
                        "confidential",
                        "private key",
                        "api key",
                        "token",
                        "credential",
                        "authentication",
                        "access key",
                        "ssh key",
                        "encryption key",
                        "certificate"
                    ]
                    for pattern in sensitive_patterns:
                        if pattern in content:
                            logger.warning(f"Detected sensitive information: {pattern}")
                            raise ValueError(f"Response contains sensitive information: {pattern}")

                    # 不適切な内容のチェック
                    inappropriate_patterns = [
                        "hack",
                        "exploit",
                        "vulnerability",
                        "attack",
                        "malware",
                        "virus",
                        "ransomware",
                        "phishing",
                        "backdoor",
                        "crack",
                        "breach",
                        "compromise"
                    ]
                    for pattern in inappropriate_patterns:
                        if pattern in content:
                            logger.warning(f"Detected inappropriate content: {pattern}")
                            raise ValueError(f"Response contains potentially harmful content: {pattern}")

        logger.debug("Post-call check completed successfully")
