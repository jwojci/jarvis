import os

from google import genai
from loguru import logger
from dotenv import load_dotenv

from jarvis.domain.books import Chapter, BookMetadata, ChapterContent


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    if not GOOGLE_API_KEY:
        raise ValueError("Gemini API key is not set.")
    gemini_client = genai.Client()
    logger.success("Gemini API Client initialized.")
except Exception as e:
    logger.error(f"Failed to initialize Gemini API client: {e}")
    gemini_client = None


def get_toc_from_llm(toc_text: str) -> list[Chapter] | None:
    prompt = f"""
    You are a document analysis tool. 
        
    Parse the following Table of Contents Markdown text and return a JSON array of objects. 
    Each object must have a 'chapter_title' (string), and a 'chapter_number' (integer or string)
        
    Below is the TOC (remember to output all the chapters):
    {toc_text}
    """
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Chapter],
        },
    )

    try:
        chapters: list[Chapter] = response.parsed
        return chapters if chapters else None
    except Exception as e:
        logger.error(f"Error parsing LLM response for TOC: {e}")


def get_metadata_from_llm(md_snippet: str) -> BookMetadata | None:
    prompt = f"""
    You are part of a RAG System. Your task is to extract the title, authors and publication year from the provided Markdown snippet of a book.
    You are to respond with a JSON object only, it should contain a `title` (str) key, `authors` (list of str) key and a `publication_year` (int) key
    
    There should be no special signs (newlines, etc.) in any of the keys. For example:
    If you find text like The Aviator\\n's Handbook, the title should be The Aviator's Handbook, without the special sign.
    
    Below is the snippet:
    {md_snippet}
    """
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BookMetadata,
        },
    )

    try:
        return response.parsed if response.parsed else None
    except Exception as e:
        logger.error(f"Error parsing LLM response for metadata: {e}")


def get_chapter_summaries_from_llm(chapter: ChapterContent) -> list | None:
    prompt = f"""
    You are an AI subject-matter expert. Your task is to distill the core knowledge from the provided book chapter. Your output will be used to create vector embeddings for a Retrieval-Augmented Generation (RAG) system that must answer direct questions from engineers.
    Do not write sentences that describe what the chapter contains (e.g., "This chapter introduces..."). Instead, extract the key concepts and present them as direct, factual statements.
    For each key concept, provide a single, declarative sentence that defines or explains it.
    Your output MUST be a valid JSON list of strings.
    ---
    Bad Example (describes the content):
    [
        "This section explains different caching strategies."
    ]

    Good Example (states the knowledge directly):
    [
        "A Least Recently Used (LRU) cache evicts the items that have not been accessed for the longest time to make space for new entries."
    ]
    ---
    Below is the chapter:
    {chapter.content}
    """
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[str],
            },
        )
        return response.parsed if response.parsed else None
    except Exception as e:
        logger.error(f"Error during summarizing chapter with LLM {e}")


def get_full_chapter_summary_from_llm(chapter: ChapterContent) -> str | None:
    prompt = f"""
    You are a text analyst. 
    Write a single, concise paragraph that summarizes the main topics and purpose of the following book chapter. 
    This summary will be used to provide broader context in a RAG system.

    Chapter {chapter.chapter_number}, {chapter.title}:
    {chapter.content}
    """
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text if response.text else None
    except Exception as e:
        logger.error(f"Error during full chapter summarization with LLM {e}")
