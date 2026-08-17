"""
Claims pipeline — placeholder only.

Per team decision: compensation claims are NOT auto-generated from survey
or damage-assessment records. This is a separate pipeline, to be designed
and built later, once damage-assessment work starts. Nothing here yet,
on purpose.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/claims", tags=["claims"])

# TODO: design and implement once the claims pipeline is scoped separately.
