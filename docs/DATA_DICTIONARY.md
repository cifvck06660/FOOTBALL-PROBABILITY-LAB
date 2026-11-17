# Match dataset dictionary

One row represents one completed match. Store source data unchanged in a private/local raw layer, then transform it into this normalized schema. Do not commit third-party raw data unless its license permits redistribution.

| Field | Required | Meaning |
|---|---:|---|
| match_id | Yes | Stable unique ID derived from source and match identity fields. |
| date | Yes | Match date/time normalized to YYYY-MM-DD. |
| home_team, away_team | Yes | Team names as supplied by source; alias review is a separate step. |
| home_goals, away_goals | Yes | Goals for the score basis stated below. |
| competition | Yes | Competition or tournament name. |
| season | No | Season label, e.g. 2023/24. |
| match_type | Yes | club or national_team. |
| team_level | Yes | senior, u23, u20, u17, reserve, or unknown. |
| competition_type | Yes | league, cup, club_international_cup, qualification, friendly, nations_league, or other. |
| gender | No | men, women, mixed, or unknown. Keep men's and women's models separate. |
| neutral_venue | No | Whether the match was played at a neutral venue. |
| fifa_a_match_status | No | yes, no, or unknown; requires evidence-backed registry matching. |
| score_basis | No | regulation_90, full_time_extra_time_included, or unknown. |
| model_eligible_90m | No | True only when the score is confirmed as a regulation-time score and all applicable eligibility rules are met. |
| data_source | No | Source name or dataset identifier. |
| source_match_id | No | Original match ID in the source, when available. |

## National-team inclusion rule

A senior national-team row is a verified FIFA A international only when:
- match_type = national_team
- team_level = senior
- fifa_a_match_status = yes

Friendlies remain tagged as competition_type = friendly; they can be included or excluded explicitly during analysis. U-team, B-team, reserve, and league-selection matches are excluded from the senior A-international model. Unverified records remain candidates and are not silently included.

## Score convention

For standard 90-minute goal modeling, use the score at the end of regulation time plus stoppage time, before extra time and penalty shootouts. The club source provides a full_time flag; only F records are retained as regulation_90. The men's and women's international source CSVs report full-time scores including extra time and do not provide a regulation-time score field, so those rows are not marked model_eligible_90m.

Penalty shootout scores must never be included in goals-for/goals-against. If a future source includes extra-time and shootout fields, store them separately.
