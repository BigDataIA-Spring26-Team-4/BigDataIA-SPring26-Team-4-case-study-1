"""
API routers package for PE Org-AI-R Platform.
"""

from app.routers import health, companies, assessments, scores, industries, config

__all__ = ["health", "companies", "assessments", "scores", "industries", "config"]
