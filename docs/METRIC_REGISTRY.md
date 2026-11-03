# Metric registry (contextual layer)

The registry tells the agent what each metric means, how to compute it, and when it misleads. Most "chat with your data" failures come from the model guessing definitions. The ablation (with vs without registry) is a headline result.

## Entry format (YAML in `agent/registry/`, loaded into `metric_registry`)
```yaml
- metric_id: epa_per_play
  name: EPA per play
  definition: >
    Average expected points added per offensive play. Positive values mean
    the offense improved its expected scoring on average.
  sql_expression: AVG(epa)
  filters: "(is_pass OR is_rush) AND epa IS NOT NULL"
  grain: team-season, team-week, game
  caveats:
    - Depends on the filters above; excluding spikes, kneels, and special teams changes the value.
    - Small samples (a single game) are noisy.
  source_tables: [plays]
  version: 1
```

## Starter metrics (write each fully; verify column names against the data)
| metric_id | Definition (project convention) | Main caveat |
|---|---|---|
| `epa_per_play` | Mean EPA over pass and rush plays | Filter choices change results |
| `success_rate` | Share of plays flagged successful | Definition comes from the data source |
| `yards_per_play` | Mean yards gained on pass and rush plays | Ignores down and distance |
| `pass_rate` | Pass plays divided by pass plus rush plays | Sensitive to game script |
| `early_down_pass_rate` | Pass rate on 1st and 2nd down | Game script, score, time |
| `third_down_conv_rate` | Third-down plays that gain a first down or score | Needs correct handling of penalties |
| `explosive_play_rate` | Rushes of 10+ yards or passes of 20+ yards, divided by plays | Thresholds are a convention, state them |
| `turnover_rate` | Interceptions plus lost fumbles, divided by plays | Rare events, noisy |
| `sack_rate` | Sacks divided by dropbacks | Dropback definition |
| `red_zone_td_rate` | Share of red zone drives ending in a touchdown | Needs drive-level fields (verify) |
| `fourth_down_go_rate` | Fourth-down plays that were pass/rush attempts, divided by fourth-down plays | Excludes punts and field goals |
| `points_per_game` | Mean points scored by a team per game | Playoff vs regular season |

## Rules for the agent's use of the registry
1. Always retrieve registry entries relevant to the question before writing SQL.
2. Use `sql_expression` and `filters` exactly as registered. Do not reinvent them.
3. If a requested metric is not in the registry, say so and propose a definition, flagged as ad hoc.
4. Mention relevant caveats in the answer when sample sizes are small.

## Adding a metric
1. Write the entry.
2. Add at least one golden question that depends on it.
3. Bump `version` if the definition changes and re-embed.
