"""
Weather suitability scoring for outdoor vs indoor activities.

Outdoor categories (viewpoints, parks) score higher on dry, mild days.
Indoor categories (museums, cafes) are less penalised by rain. This
feeds into the weather_score component of ExperienceRank (max 15 pts).
"""

# POI categories that are primarily enjoyed outdoors.
OUTDOOR_CATEGORIES = {
    "viewpoint",
    "park",
    "garden",
    "playground",
    "nature_reserve",
    "attraction",
    "walk",
}

# POI categories that work well regardless of rain.
INDOOR_CATEGORIES = {
    "museum",
    "library",
    "cafe",
    "pub",
    "restaurant",
    "bar",
    "gallery",
    "theatre",
}


def outdoor_weather_score(weather: dict[str, float | str | bool]) -> float:
    """
    Score 0–1 for how pleasant outdoor activity would be right now.

    Weighted combination of:
      - dryness (precipitation + rain)
      - temperature (ideal ~18 °C)
      - wind speed
      - daylight (is_day flag from Open-Meteo)
      - cloud cover
    """
    precip = float(weather["precipitation_mm"])
    rain = float(weather["rain_mm"])
    cloud = float(weather["cloud_cover_pct"]) / 100
    wind = float(weather["wind_speed_kmh"])
    temp = float(weather["temperature_c"])
    is_day = bool(weather["is_day"])

    # Dry hours score 1.0; heavy rain trends toward 0.
    dry_score = 1.0 if precip + rain < 0.2 else max(0.0, 1.0 - (precip + rain) / 5)
    # Comfort peaks around 18 °C, falls off toward freezing or heat.
    temp_score = 1.0 - min(abs(temp - 18) / 18, 1.0)
    # Strong wind makes outdoor stops less appealing.
    wind_score = max(0.0, 1.0 - wind / 40)
    # Night-time outdoor viewpoints are less attractive for a day plan.
    daylight_score = 1.0 if is_day else 0.4
    cloud_score = 1.0 - cloud * 0.35

    return round(
        dry_score * 0.35
        + temp_score * 0.2
        + wind_score * 0.15
        + daylight_score * 0.15
        + cloud_score * 0.15,
        3,
    )


def category_weather_fit(category: str, weather: dict[str, float | str | bool]) -> float:
    """
    Return 0–1 suitability of current weather for a given POI category.

    Outdoor stops track the outdoor score directly; indoor stops invert
    it slightly (rain makes museums relatively more attractive).
    """
    outdoor_score = outdoor_weather_score(weather)
    if category in OUTDOOR_CATEGORIES:
        return outdoor_score
    if category in INDOOR_CATEGORIES:
        return round(1.0 - outdoor_score * 0.25, 3)
    # Unknown category — neutral default.
    return 0.75
