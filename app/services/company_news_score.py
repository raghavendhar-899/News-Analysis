from datetime import datetime, timedelta

from app.repository.article import Article

# Recency weights aligned with 4-day article TTL.
_RECENCY_WEIGHT_TODAY = 4.0
_RECENCY_WEIGHT_YESTERDAY = 3.0
_RECENCY_WEIGHT_TWO_DAYS_AGO = 2.0
_RECENCY_WEIGHT_THREE_DAYS_AGO = 1.0
_SCORE_AGE_BUCKETS = (
    (0, _RECENCY_WEIGHT_TODAY),
    (1, _RECENCY_WEIGHT_YESTERDAY),
    (2, _RECENCY_WEIGHT_TWO_DAYS_AGO),
    (3, _RECENCY_WEIGHT_THREE_DAYS_AGO),
)


def _parse_article_score(score):
    if score == '--':
        return None
    try:
        return float(score)
    except (TypeError, ValueError):
        return None


def _is_weekend_date(day):
    return day.weekday() >= 5


def _article_calendar_age_days(article_date, reference):
    if article_date is None:
        return None
    ref_day = reference.date() if isinstance(reference, datetime) else reference
    if isinstance(article_date, datetime):
        art_day = article_date.date()
    else:
        return None
    return (ref_day - art_day).days


def _recency_weight_for_age(age_days):
    if age_days is None:
        return _RECENCY_WEIGHT_THREE_DAYS_AGO
    if age_days <= 0:
        return _RECENCY_WEIGHT_TODAY
    if age_days == 1:
        return _RECENCY_WEIGHT_YESTERDAY
    if age_days == 2:
        return _RECENCY_WEIGHT_TWO_DAYS_AGO
    return _RECENCY_WEIGHT_THREE_DAYS_AGO


def _article_age_bucket(age_days):
    if age_days is None:
        return None
    if age_days < 0:
        return 0
    if age_days > 3:
        return 3
    return age_days


def _weight_for_scored_article(article_date, age_days, ref_day):
    """
    On Monday, Sat/Sun/Mon articles all use today's weight (4).
    On Tue–Fri, weekend articles use normal age-based weights.
    """
    if isinstance(article_date, datetime) and ref_day.weekday() == 0:
        art_day = article_date.date()
        if art_day.weekday() >= 5 or art_day == ref_day:
            return _RECENCY_WEIGHT_TODAY
    return _recency_weight_for_age(age_days)


def calculate_score(company):
    """
    Weighted company score with missing-day penalties.

    Empty weekday buckets add tier_weight to the denominator (0 in the numerator).
    Empty Sat/Sun buckets are never penalized. On Mondays, articles from Sat/Sun/Mon
    use today's weight; from Tuesday onward, weekend articles use normal age weights.
    """
    articleobj = Article(company)
    reference = datetime.utcnow()
    ref_day = reference.date()

    bucket_articles = {age: [] for age, _ in _SCORE_AGE_BUCKETS}

    for article in articleobj.get_scored_articles():
        score = _parse_article_score(article.get("score"))
        if score is None:
            continue
        age_days = _article_calendar_age_days(article.get("date"), reference)
        bucket = _article_age_bucket(age_days)
        if bucket is None:
            continue
        bucket_articles[bucket].append((score, article.get("date")))

    weighted_sum = 0.0
    weight_total = 0.0

    for age_days, tier_weight in _SCORE_AGE_BUCKETS:
        entries = bucket_articles[age_days]
        bucket_day = ref_day - timedelta(days=age_days)

        if entries:
            for score, article_date in entries:
                w = _weight_for_scored_article(article_date, age_days, ref_day)
                weighted_sum += score * w
                weight_total += w
        elif not _is_weekend_date(bucket_day):
            weight_total += tier_weight

    if weight_total > 0:
        return weighted_sum / weight_total
    return 0.0
