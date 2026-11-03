# ML plan

## Models
### 1. Win probability (classification)
- Target: whether the possession team (or home team) wins the game.
- Candidate features: score differential, game seconds remaining, down, yards to go, field position (`yardline_100`), timeouts remaining for both teams, possession team being home or away, quarter.
- Do not use `epa`, `wp`, `wpa`, or any column derived from the outcome. The source data's own `wp` is an external benchmark to compare against, never a feature.
- Baselines: always-predict-home-win rate; logistic regression on a small feature set.
- Main model: LightGBM.

### 2. Team points projection (regression)
- Target: points scored by a team in its next game.
- Features: trailing EPA per play, success rate, pace, and opponent trailing defense stats, all computed using only games before the target game.
- Baseline: trailing 3-game average of points.

### 3. Anomaly detection
- Play-level: flag plays whose absolute win-probability change is above a high percentile of the training distribution.
- Game-level (optional): Isolation Forest on game feature vectors.
- Evaluate by inspection and by precision on a small hand-labeled set of known notable plays (record how you labeled them).

## Validation
- Group all splits by `game_id` so plays from one game never appear in both train and test. Use `GroupKFold` for cross-validation.
- For time-aware evaluation, hold out the last N weeks as a final test set that is touched once.
- For the regression model, use only past games when building features (no lookahead).
- With one season, expect noisy estimates. Report confidence intervals or fold variance.

## Metrics
- Win probability: log loss, Brier score, accuracy, reliability curve (calibration), comparison against the external `wp` benchmark.
- Regression: MAE, RMSE, improvement over the baseline.
- Anomaly: flagged rate, precision on the labeled set.
- All models: inference latency (p50/p95) and model size.

## Tuning
- Optuna with the CV objective. Record the search space, number of trials, best params, and the objective curve.
- Fix random seeds. Log library versions.
- Calibrate probabilities (Platt or isotonic) on a validation fold, then re-check Brier score.

## Artifacts and serving
- Save models to S3 with a version, training data hash, git SHA, and metrics JSON.
- `ml/serve.py` loads the latest approved version at startup and exposes batch and single-play prediction.
- Unit tests: feature functions, no-leakage checks (assert forbidden columns absent), prediction shape and range.

## Notebooks
Exploration only. Anything that matters must live in importable modules with tests.
