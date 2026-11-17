# Match dataset dictionary

One row represents one completed match. Store source data unchanged in a private/local raw layer, then transform it into this normalized schema. Do not commit third-party raw data unless redistribution is permitted.

| Field | Required | Meaning |
|---|---:|---|
| `match_id` | Yes | Stable unique ID created by the project or source. |
| `date` | Yes | Match date/time in ISO 8601 where possible. |
| `home_team`, `away_team` | Yes | Canonical team names. |
| `home_goals`, `away_goals` | Yes | Full-time score for the defined match period; record 90-minute score for standard football modeling. |
| `competition` | Yes | Competition or tournament name. |
| `season` | No | Season label, e.g. 2023/24. |
| `match_type` | Yes | `club` or `national_team`. |
| `team_level` | Yes | `senior`, `u23`, `u20`, `u17`, `reserve`, or `unknown`. |
| `competition_type` | Yes | `league`, `cup`, `qualification`, `friendly`, `nations_league`, or `other`. |
| `gender` | No | `men`, `women`, `mixed`, or `unknown`. Keep men's and women's models separate. |
| `neutral_venue` | No | Whether the match was played at a neutral venue. |
| `fifa_a_match_status` | No | `yes`, `no`, or `unknown`; use evidence from a reliable source. |
| `data_source` | No | Source name or dataset identifier. |
| `source_match_id` | No | Original match ID in the source. |

## National-team inclusion rule

A row is eligible for the senior national-team A-international dataset only when:
- `match_type = national_team`
- `team_level = senior`
- `fifa_a_match_status = yes`

Friendlies remain tagged as `competition_type = friendly`; they can be included or excluded explicitly during analysis. Do not treat missing or unknown A-match status as verified. U-team, B-team, reserve, and league-selection matches are excluded from the senior A-international model.

## Score convention

For standard 90-minute modeling, use the score at the end of regulation time plus stoppage time, before extra time and penalty shootouts. Store extra-time and shootout information in separate fields in a future schema extension; do not mix shootout scores into goals-for/goals-against.
