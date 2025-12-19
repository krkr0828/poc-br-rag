"""
Prompt Templates

Contains all prompt templates used for LLM generation.
"""

# RAG Prompt Template for Claude 3
# This template combines retrieved context with the user's query
RAG_PROMPT_TEMPLATE = """You are a helpful AI assistant. Answer the user's question based on the provided context from the knowledge base.

Context from Knowledge Base:
{context}

User Question:
{query}

Instructions:
1. Answer the question based primarily on the provided context
2. If the context doesn't contain enough information to fully answer the question, acknowledge this limitation
3. Be concise and direct in your response
4. If you reference specific information from the context, you can mention it came from the knowledge base
5. Do not make up information that is not in the context

Answer:"""


def build_rag_prompt(query: str, context: str) -> str:
    """
    Build RAG prompt from template

    Args:
        query: User's question
        context: Retrieved context from Knowledge Base

    Returns:
        str: Complete prompt ready for Bedrock invocation
    """
    return RAG_PROMPT_TEMPLATE.format(query=query, context=context)
