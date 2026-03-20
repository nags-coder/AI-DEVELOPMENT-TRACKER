"""Seed script — populates the database with MVP sources and sample content."""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import async_session_factory, engine
from app.models.content_item import ContentItem
from app.models.source import Source
from app.models.sub_source import SubSource

# ── MVP Sources ──────────────────────────────────────────

SOURCES = [
    {
        "name": "arXiv",
        "category": "A",
        "base_url": "https://arxiv.org",
        "source_type": "api",
        "priority": 1,
        "status": "active",
        "user_rating": 5,
        "notes": "AI research papers — cs.AI, cs.LG, cs.CL categories",
    },
    {
        "name": "GitHub Trending",
        "category": "B",
        "base_url": "https://github.com/trending",
        "source_type": "api",
        "priority": 1,
        "status": "active",
        "user_rating": 4,
        "notes": "Trending AI/ML repositories",
    },
    {
        "name": "Hugging Face",
        "category": "C",
        "base_url": "https://huggingface.co",
        "source_type": "api",
        "priority": 1,
        "status": "active",
        "user_rating": 5,
        "notes": "Daily papers, trending models, Spaces",
    },
]

# ── Sub-Sources ──────────────────────────────────────────

SUB_SOURCES = [
    # arXiv categories
    {
        "source_name": "arXiv",
        "platform": "arxiv",
        "handle": "cs.AI",
        "display_name": "AI (General)",
    },
    {
        "source_name": "arXiv",
        "platform": "arxiv",
        "handle": "cs.LG",
        "display_name": "Machine Learning",
    },
    # GitHub trending
    {
        "source_name": "GitHub Trending",
        "platform": "github",
        "handle": "trending/python",
        "display_name": "Trending Python Repos",
    },
    # Hugging Face
    {
        "source_name": "Hugging Face",
        "platform": "huggingface",
        "handle": "daily-papers",
        "display_name": "Daily Papers",
    },
    {
        "source_name": "Hugging Face",
        "platform": "huggingface",
        "handle": "trending-models",
        "display_name": "Trending Models",
    },
    {
        "source_name": "Hugging Face",
        "platform": "huggingface",
        "handle": "trending-spaces",
        "display_name": "Trending Spaces",
    },
]

# ── Sample Content Items ─────────────────────────────────

now = datetime.now()


def hours_ago(h: int) -> datetime:
    return now - timedelta(hours=h)


SAMPLE_CONTENT = [
    # arXiv papers (5)
    {
        "source_name": "arXiv",
        "title": "Scaling Laws for Neural Machine Translation with Mixture of Experts",
        "summary": "We study scaling laws for sparse Mixture-of-Experts models in neural machine translation. Our experiments reveal that MoE models follow predictable scaling behavior with respect to expert count and data size.",
        "original_url": "https://arxiv.org/abs/2202.01169",
        "author": "Smith, J., Chen, W., Kumar, A.",
        "published_at": hours_ago(2),
        "content_type": "paper",
        "topic_tags": ["scaling-laws", "moe", "nmt", "transformers"],
        "engagement_score": 0,
        "relevance_score": 0.8500,
    },
    {
        "source_name": "arXiv",
        "title": "Self-Play Fine-Tuning: Converting Weak Language Models to Strong",
        "summary": "We propose SPIN, a self-play mechanism that converts a weak LLM into a strong one without additional human-annotated data. Starting from supervised fine-tuned models, SPIN iteratively refines using self-generated data.",
        "original_url": "https://arxiv.org/abs/2401.01335",
        "author": "Li, Y., Park, J.",
        "published_at": hours_ago(5),
        "content_type": "paper",
        "topic_tags": ["llm", "fine-tuning", "self-play", "alignment"],
        "engagement_score": 0,
        "relevance_score": 0.9200,
    },
    {
        "source_name": "arXiv",
        "title": "Vision Transformers Need Registers",
        "summary": "We identify artifacts in feature maps of ViT models and propose a simple fix: appending register tokens to the input sequence. This improves performance on dense prediction tasks and object discovery.",
        "original_url": "https://arxiv.org/abs/2309.16588",
        "author": "Darcet, T., Oquab, M., Mairal, J., Bojanowski, P.",
        "published_at": hours_ago(8),
        "content_type": "paper",
        "topic_tags": ["vision", "transformers", "vit", "registers"],
        "engagement_score": 0,
        "relevance_score": 0.7800,
    },
    {
        "source_name": "arXiv",
        "title": "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits",
        "summary": "BitNet b1.58 uses ternary weights {-1, 0, 1} to match full-precision LLM performance while dramatically reducing memory and computation. This challenges the conventional approach to model quantization.",
        "original_url": "https://arxiv.org/abs/2402.17764",
        "author": "Ma, S., Wang, H., Ma, L., Wang, L.",
        "published_at": hours_ago(12),
        "content_type": "paper",
        "topic_tags": ["llm", "quantization", "efficiency", "bitnet"],
        "engagement_score": 0,
        "relevance_score": 0.9500,
    },
    {
        "source_name": "arXiv",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "summary": "We combine pre-trained parametric and non-parametric memory for language generation. RAG models access a Wikipedia dense vector index to generate more factual and diverse responses.",
        "original_url": "https://arxiv.org/abs/2005.11401",
        "author": "Lewis, P., Perez, E., Piktus, A.",
        "published_at": hours_ago(18),
        "content_type": "paper",
        "topic_tags": ["rag", "retrieval", "nlp", "knowledge"],
        "engagement_score": 0,
        "relevance_score": 0.7200,
    },
    # GitHub repos (5)
    {
        "source_name": "GitHub Trending",
        "title": "openai/whisper-large-v3-turbo",
        "summary": "Turbo variant of Whisper Large v3 — 5x faster inference with minimal quality loss. Supports 99 languages and automatic language detection.",
        "original_url": "https://github.com/openai/whisper",
        "author": "OpenAI",
        "published_at": hours_ago(3),
        "content_type": "repo",
        "topic_tags": ["speech", "whisper", "asr", "openai"],
        "engagement_score": 52400,
        "relevance_score": 0.8800,
    },
    {
        "source_name": "GitHub Trending",
        "title": "meta-llama/llama-recipes",
        "summary": "Examples and recipes for fine-tuning and deploying Llama 3.x models. Includes LoRA, QLoRA, FSDP, and vLLM integration guides.",
        "original_url": "https://github.com/meta-llama/llama-recipes",
        "author": "Meta AI",
        "published_at": hours_ago(6),
        "content_type": "repo",
        "topic_tags": ["llm", "llama", "fine-tuning", "meta"],
        "engagement_score": 11200,
        "relevance_score": 0.8100,
    },
    {
        "source_name": "GitHub Trending",
        "title": "langchain-ai/langgraph",
        "summary": "Build stateful, multi-agent applications with LLMs. LangGraph extends LangChain with cyclic graph support for complex agentic workflows.",
        "original_url": "https://github.com/langchain-ai/langgraph",
        "author": "LangChain",
        "published_at": hours_ago(10),
        "content_type": "repo",
        "topic_tags": ["agents", "langgraph", "langchain", "workflows"],
        "engagement_score": 8500,
        "relevance_score": 0.8400,
    },
    {
        "source_name": "GitHub Trending",
        "title": "vllm-project/vllm",
        "summary": "High-throughput LLM serving engine with PagedAttention. Supports continuous batching, speculative decoding, and quantized models.",
        "original_url": "https://github.com/vllm-project/vllm",
        "author": "vLLM Team",
        "published_at": hours_ago(14),
        "content_type": "repo",
        "topic_tags": ["inference", "serving", "vllm", "performance"],
        "engagement_score": 34000,
        "relevance_score": 0.7900,
    },
    {
        "source_name": "GitHub Trending",
        "title": "browser-use/browser-use",
        "summary": "Make websites accessible for AI agents. Automates browser interactions using natural language commands with vision-language models.",
        "original_url": "https://github.com/browser-use/browser-use",
        "author": "Browser Use",
        "published_at": hours_ago(20),
        "content_type": "repo",
        "topic_tags": ["agents", "browser", "automation", "vlm"],
        "engagement_score": 6200,
        "relevance_score": 0.7500,
    },
    # Hugging Face (5)
    {
        "source_name": "Hugging Face",
        "title": "Qwen/Qwen2.5-72B-Instruct",
        "summary": "Latest 72B parameter instruction-tuned model from Qwen team. State-of-the-art on multiple benchmarks including MMLU, HumanEval, and GSM8K.",
        "original_url": "https://huggingface.co/Qwen/Qwen2.5-72B-Instruct",
        "author": "Qwen Team",
        "published_at": hours_ago(4),
        "content_type": "model",
        "topic_tags": ["llm", "qwen", "instruction-tuning", "open-weights"],
        "engagement_score": 45000,
        "relevance_score": 0.9100,
    },
    {
        "source_name": "Hugging Face",
        "title": "black-forest-labs/FLUX.1-dev",
        "summary": "Open-weight 12B parameter text-to-image model. Generates high-quality images with strong prompt adherence and photorealistic output.",
        "original_url": "https://huggingface.co/black-forest-labs/FLUX.1-dev",
        "author": "Black Forest Labs",
        "published_at": hours_ago(7),
        "content_type": "model",
        "topic_tags": ["image-gen", "flux", "diffusion", "text-to-image"],
        "engagement_score": 28000,
        "relevance_score": 0.8300,
    },
    {
        "source_name": "Hugging Face",
        "title": "Training Language Models to Self-Correct via Reinforcement Learning",
        "summary": "Google DeepMind proposes SCoRe, using multi-turn RL to train LLMs to self-correct their responses. Achieves 15.6% improvement on MATH and 9.1% on HumanEval over base models.",
        "original_url": "https://huggingface.co/papers/2409.12917",
        "author": "Google DeepMind",
        "published_at": hours_ago(9),
        "content_type": "paper",
        "topic_tags": ["llm", "rl", "self-correction", "deepmind"],
        "engagement_score": 320,
        "relevance_score": 0.8700,
    },
    {
        "source_name": "Hugging Face",
        "title": "microsoft/phi-4",
        "summary": "Small language model (14B parameters) that punches well above its weight. Strong reasoning and coding capabilities despite compact size.",
        "original_url": "https://huggingface.co/microsoft/phi-4",
        "author": "Microsoft Research",
        "published_at": hours_ago(15),
        "content_type": "model",
        "topic_tags": ["llm", "small-models", "phi", "microsoft"],
        "engagement_score": 18000,
        "relevance_score": 0.8000,
    },
    {
        "source_name": "Hugging Face",
        "title": "Gradio 5.0: Build AI Web Apps in Python",
        "summary": "Major release of Gradio with SSR support, built-in auth, custom components, and improved streaming. Create production-ready AI demos in minutes.",
        "original_url": "https://huggingface.co/spaces/gradio/gradio-5",
        "author": "Gradio Team",
        "published_at": hours_ago(22),
        "content_type": "space",
        "topic_tags": ["gradio", "demos", "tools", "ui"],
        "engagement_score": 5400,
        "relevance_score": 0.7000,
    },
]


async def seed():
    """Insert seed data. Skips if data already exists."""
    async with async_session_factory() as session:
        # Check if already seeded
        result = await session.execute(select(Source).limit(1))
        if result.scalar_one_or_none():
            print("⚠️  Database already has data — skipping seed.")
            return

        # Insert sources
        source_map: dict[str, Source] = {}
        for s in SOURCES:
            source = Source(**s)
            session.add(source)
            source_map[s["name"]] = source

        await session.flush()  # Get IDs assigned
        print(f"✅ Inserted {len(SOURCES)} sources")

        # Insert sub-sources
        for ss in SUB_SOURCES:
            source = source_map[ss.pop("source_name")]
            sub = SubSource(source_id=source.id, **ss)
            session.add(sub)

        await session.flush()
        print(f"✅ Inserted {len(SUB_SOURCES)} sub-sources")

        # Insert content items
        for item_data in SAMPLE_CONTENT:
            source = source_map[item_data.pop("source_name")]
            item = ContentItem(source_id=source.id, **item_data)
            session.add(item)

        await session.commit()
        print(f"✅ Inserted {len(SAMPLE_CONTENT)} content items")
        print("🎉 Seed complete!")


async def main():
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
