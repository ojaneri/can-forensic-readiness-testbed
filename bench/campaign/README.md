# bench/campaign — re-running the experiments

Everything here re-runs the archived experiments **without touching them** (in this repository they are under `dataset/experiments/`). That matters:
the archived runners write beside themselves, so running one in place overwrites the very
evidence it is meant to reproduce.

## Why this exists

Section VII of the manuscript names it as future work:

> *The current timing evidence (Exp. 010--012) is limited to single runs. Larger campaigns
> across varying bus loads, message rates, and hardware configurations would strengthen
> timing-preservation claims.*

Exp. 010 takes 20 s and Exp. 011 takes 30 s. Ten runs of each is minutes, not a campaign
that needed planning — it simply had not been done.

## Contents

```
runners/010|011|012/   copies of the archived runners, with SEED, DURATION_S, CHANNEL and
                       (for 012) the input trace overridable by environment variable.
                       Defaults are byte-identical in effect to the originals, so the
                       archived evidence stays reproducible from these copies.
run_campaign.py        driver: N runs of each, one directory per run, stats at the end.
socketcan/             self-contained re-run of Exp. 018/019 through the real kernel path.
campaign_report.json   the result.
```

Each runner keeps its **original filename** inside its run directory, because the archived
runners hash themselves into their own manifest by that name.

## Running

```
python3 bench/campaign/run_campaign.py --runs 10             # 010, 011, 012
python3 bench/campaign/run_campaign.py --runs 5 --only 011
sudo python3 bench/campaign/socketcan/run_socketcan.py       # needs root + can-utils
```

## The seed is held constant, on purpose

It fixes the payload content, so the only thing varying between runs is OS scheduling —
which is what a timing campaign is measuring. Varying the seed too would confound the two.

## What re-running is for

Not ceremony. Re-running found a real error: the unique-ID counts in Table II were wrong for
four experiments, and one of those wrong numbers was carrying a false claim about the HCRL
fuzzy subset having "an order of magnitude" more ID diversity than any synthetic experiment.
The authors' working results log (`RESULTS.md`) is not part of this repository; every number in the manuscript can be
regenerated from the scripts and data deposited here.

## Note for this repository

In this repository the archived experiment packages are under `dataset/experiments/`, not `estudo/dataset/experiments/`.
`run_campaign.py` was changed in one line to read the ICSim input from
`dataset/experiments/008_external_icsim_replay/frames_normalized.csv`; the SHA-256 of the as-run original is
`3965177a2fb654b4a33b525663870979aaf1e1443196e742286d210092c0fdc4`.

The per-run `frames_normalized.csv`, `manifest.json` and `summary.json` files in `runs/` are the evidence behind the
ten-run timing table of the paper. Timing is measured from the host, so re-running the campaign produces new values,
not these ones. The console log of the campaign and the SocketCAN re-runs of the campaign are not included.
