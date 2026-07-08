# football-predictor

Portable football prediction engine for odds-driven match forecasts.

The first version is intentionally small and reproducible:

- Converts 1X2 decimal odds into no-vig market probabilities.
- Reads Asian handicap and total-goals snapshots.
- Applies a v5 rule layer for lineup, schedule, knockout, and market-movement adjustments.
- Uses a Poisson score grid to produce win/draw/loss and score probabilities.
- Provides a backtest command for historical snapshots.

## Quick start

```powershell
cd football-predictor
python -m football_predictor init-sample
python -m football_predictor predict --input data/samples/matches.json
python -m football_predictor backtest --input data/samples/matches.json
```

After installing the package, the same commands are available through `football`:

```powershell
pip install .
football predict --input data/samples/matches.json
```

## Data contract

`predict` expects a JSON file with a `matches` array. Each match can include:

- `odds_1x2`: decimal 1X2 odds snapshots.
- `asian_handicap`: home handicap line and water snapshots.
- `totals`: over/under snapshots.
- `strength`: Elo or other team-strength fields.
- `context`: rest days, travel, host edge, knockout flag, weather.
- `lineup`: expected-goals deltas after confirmed lineups.
- `result`: optional final score for backtesting.

Run `python -m football_predictor init-sample` to generate a template.

## Portability

To use on another computer:

```powershell
git clone <repo-url>
cd football-predictor
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install .
football predict --input data/samples/matches.json
```

For live crawling, install optional collector dependencies:

```powershell
pip install ".[collectors]"
```
