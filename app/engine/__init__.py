"""
WorthIT recommendation engine.

File-backed POC that ranks day plans by "joy per pound" (ExperienceRank).
Reads pre-processed Camden datasets from data/raw/ and does not require
PostgreSQL for recommendations — that comes in a later phase.

Pipeline overview:
  loaders  → read parquet files (weather, POIs, FHRS)
  routing  → walking-network graph and travel times
  scoring  → weather fit + per-POI experience scores
  planning → assemble ranked day-plan cards from templates
"""
