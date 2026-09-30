# NBA season simulator: attribute spec (v1)

This sheet defines every player rating, player tendency, and coach setting in the model. For each one it records what it means, what data it's estimated from, which possession-engine event it drives, and how much confidence the data supports.

## Conventions

**Two scales.** Every rating is stored internally in the unit the engine uses, usually a probability or a rate. It is shown on a 25–99 display scale by league percentile. The engine never reads the display number.

**Shrinkage.** Every measured value blends the player's observed rate with a prior (the average for his position and role), weighted by sample size. Recent seasons count more, for example 3/2/1 across the last three.

**Two kinds of tendency.**

- *Distribution* tendencies split a single decision into shares that sum to 100%, like shot type.
- *Rate* tendencies are how often a player does something when the chance arises, like drives per touch.

**Context-netting.** Player ratings and tendencies are estimated net of the context they were produced in, such as teammate spacing and team system. The engine then adds context back, so nothing is counted twice.

**Source tags.**

| Tag | Meaning |
| --- | --- |
| Measured | Estimated directly from public stats |
| Proxied | Estimated indirectly from related stats; noisier |
| Calibrated | Fitted so the simulation reproduces a real observed outcome. Used where the data can't separate two parameters |
| Assigned | No public data; set by design. In-game effect must be small and average out to zero |
| Derived | Computed from other attributes rather than stored |

**Projection mode.** A toggle that neutralizes every Assigned in-game effect, so win projections rest only on data-backed parameters.

## Data key

| Dataset | `nba_api` endpoint(s) |
| --- | --- |
| Box score, per-100, advanced | `leaguedashplayerstats`, `leaguedashteamstats` |
| Shot locations | `shotchartdetail` |
| Play-by-play (shot descriptions, fouls, substitutions) | `playbyplayv3` |
| Tracking (speed, drives, touches, passing, catch-and-shoot, pull-up, rebounding) | `leaguedashptstats` |
| Play types | `synergyplaytypes` (player and team) |
| Hustle | `leaguehustlestatsplayer` |
| Defense and rim protection | `leaguedashptdefend` |
| Matchups (who guarded whom) | `leagueseasonmatchups` |
| Opponent shots by closest defender | `leaguedashoppptshot` |
| Combine measurements and drills | `draftcombineplayeranthro`, `draftcombinedrillresults` |
| Lineups | `leaguedashlineups` |
| Defensive impact | Compute RAPM from play-by-play lineup stints, or use a public RAPM-family metric |

Verify endpoint names against the current `nba_api` docs. Coverage start years differ by dataset; tracking, play-type, hustle, and matchup data only exist from the mid-2010s onward.

---

# Player layer

## Physical

| Attribute | Definition | Estimated from | Drives in engine | Source |
| --- | --- | --- | --- | --- |
| Speed | Straight-line speed with and without the ball | Combine ¾-court sprint; transition frequency; tracking speed (role-adjusted) | Transition outcomes, running the floor, speed mismatches | Proxied |
| Agility | Lateral quickness and change of direction | Combine lane agility and shuttle; drive success; results guarding guards in matchup data | Blow-by chance on drives at both ends; switchability | Proxied |
| Vertical | Leaping ability | Combine max vertical; dunk rate; block and offensive rebound rates | Dunk access, block chance, rebound contests | Proxied |
| Strength | Winning physical contact | Weight; post-up efficiency at both ends; and-one rate; screen assists | Post-ups, contact finishing, screen quality, box-outs | Proxied |
| Stamina | How long performance holds up | Minutes per game; typical stint length | Fatigue build-up within stints; maximum minutes | Proxied |
| Height | Height without shoes | Combine measurements; listed height | Mismatch detection, contests, rebounding, post play | Measured |
| Wingspan | Arm span | Combine measurements; imputed from height and position when missing | Contests, deflections, blocks, steals | Measured |
| Durability | Resistance to injury | Games-missed history, injury types, age | Injury chance per game; injury length | Measured |

## Mental

| Attribute | Definition | Estimated from | Drives in engine | Source |
| --- | --- | --- | --- | --- |
| Off-ball movement | Getting open without the ball | Cut frequency and efficiency; catch-and-shoot volume relative to role | Chance of getting open off the ball; cut opportunities | Proxied |
| Offensive decisions | Avoiding turnovers relative to ball-handling load | Turnovers per touch and per usage; bad-pass vs lost-ball split | Turnover chance per action | Measured |
| Shot IQ | Taking good shots rather than forcing bad ones | Expected eFG% of his shot diet compared with role average | Quality of shot chosen; forced shots late in the clock | Proxied |
| Vision | Seeing and creating passing opportunities | Potential assists per pass; assist points created | Chance a pass finds the best-positioned teammate | Measured |
| Aggression | Defensive physicality (see open decisions) | Foul rate left unexplained by block, steal, and contest events | Foul chance on contests and post defense; small boost to contest effectiveness | Calibrated |
| Hustle | Effort plays | Deflections, loose balls recovered, contests, box-outs per 100 | Loose-ball recoveries, extra contests, second-effort rebounds | Measured |
| Defensive positioning | Help defense and rotations | Defensive impact after removing on-ball defense, blocks, and steals; rim contests as a help defender | Help effectiveness, rotation timing, defensive rebound position | Proxied |

## Technical

| Attribute | Definition | Estimated from | Drives in engine | Source |
| --- | --- | --- | --- | --- |
| Layup | Finishing layups | FG% on layups (play-by-play shot descriptions) | Layup make chance | Measured |
| Close shot | Floaters, hooks, and short shots in the paint outside the restricted area | FG% by zone and shot description | Close-shot make chance | Measured |
| Mid range (catch-and-shoot) | Two-point jumpers off the catch | Tracking catch-and-shoot splits; shot chart | Make chance | Measured |
| Mid range (pull-up) | Two-point jumpers off the dribble | Tracking pull-up splits; shot chart | Make chance | Measured |
| Three (catch-and-shoot) | Threes off the catch | Tracking catch-and-shoot splits; FT% as part of the prior | Make chance; shooting gravity for spacing | Measured |
| Three (pull-up) | Threes off the dribble | Tracking pull-up splits; FT% as part of the prior | Make chance; gravity; creation for ball-handler scarcity | Measured |
| Free throw | Free-throw shooting | FT% | Free-throw make chance; prior for jump shooting | Measured |
| Post shot | Scoring from post-ups | Post-up efficiency; hook-shot FG% | Post-shot make chance | Measured |
| Ball handle | Keeping and advancing the ball under pressure | Lost-ball turnovers per drive and touch; drive efficiency; turnover rates as isolation and pick-and-roll ball handler | Turnovers under pressure; beating a defender off the dribble; lineup handling score | Proxied |
| Passing | Executing passes accurately | Bad-pass turnovers per pass | Turnover chance on a pass; quality of the resulting shot | Proxied |
| Defensive rebounding | Securing defensive rebounds | DREB%; contested defensive rebound share | Share of defensive rebounds won | Measured |
| Offensive rebounding | Securing offensive rebounds when crashing | Offensive rebounds per tracked rebound chance (net of crash tendency) | Share of offensive rebounds won when crashing | Measured |
| Perimeter defense | Guarding on the perimeter | Matchup data (opponent shooting vs expected); defensive impact | Modifier on opponent jumpers and drives | Proxied |
| Interior defense | Protecting the rim and post | Opponent FG% at the rim when he defends it; post-up defense | Modifier on opponent rim, close, and post shots | Proxied |
| Block | Blocking shots without fouling | Blocks per opponent two-point attempt while on floor; fouls, fitted jointly with Block tendency | Success chance on a block attempt | Calibrated |
| Steal | Stealing without fouling | Steals and deflections per 100; fouls, fitted jointly with Steal tendency | Success chance on a steal attempt | Calibrated |
| Draw foul | Earning fouls when seeking contact | Shooting fouls drawn per shot; and-ones; fitted given Flop tendency | Chance a contact-seeking attempt is called a foul | Calibrated |

## Tendencies

| Tendency | Type | Definition | Estimated from | Drives in engine | Source |
| --- | --- | --- | --- | --- | --- |
| Drive | Rate | Drives per half-court touch | Tracking drives and touches | Whether a touch becomes a drive | Measured |
| Shot distribution | Distribution | Split across layup, close, post, mid (C&S), mid (pull-up), three (C&S), three (pull-up) | Shot chart, play-by-play, tracking splits; net of team system | Which shot is taken | Measured |
| Has ball | Rate | Share of team half-court time as primary handler | Tracking time of possession; front-court touches | Who initiates possessions | Measured |
| Iso | Rate | How often he isolates when initiating | Isolation frequency (play types) | Isolation vs other actions | Measured |
| Call for screen | Rate | How often he uses a ball screen when initiating | Pick-and-roll ball-handler frequency | Pick-and-roll vs other actions | Measured |
| Pass | Rate | Passing rather than shooting or driving on a touch | Tracking passes and touches | Pass decision | Measured |
| Dunk | Rate | Share of dunk-accessible rim attempts taken as dunks | Fitted so simulated dunk rate matches real | Dunk vs layup at the rim | Calibrated |
| Flop | Rate | How often he seeks contact to draw a foul | No public data | Foul-hunting attempts; failed attempts lower shot quality | Assigned |
| Block | Rate | How often he goes for blocks | Fitted jointly with Block rating to blocks and fouls | Block attempts | Calibrated |
| Steal | Rate | How often he gambles for steals | Fitted jointly with Steal rating to steals, deflections, and fouls | Steal attempts | Calibrated |
| Screen | Rate | Screens set per possession | Screen assists; roll-man frequency | Who sets screens | Proxied |
| Pop/roll | Distribution | Rolling vs popping after a screen (see open decisions) | Location of roll-man shots (rim vs three) | Screener's action after the screen | Proxied |
| Cut | Rate | Cuts per off-ball possession | Cut frequency (play types) | Cutting actions | Measured |
| Defensive rebound | Rate | Boxing out vs leaking out | Box-outs; transition frequency | Rebound contest vs leak-out | Proxied |
| Offensive rebound | Rate | Crash rate after team misses | Tracking offensive rebound chances | Crash vs get back | Measured |

## Hidden attributes

All in-game effects here average out to zero across the league, stay small, and switch off in projection mode.

| Attribute | In-game effect | Off-court role | Source |
| --- | --- | --- | --- |
| Professionalism | None | Progression rate; aging decline | Assigned |
| Consistency | Game-to-game performance variance | None | Proxied (mostly noise; keep small) |
| Pressure | Modifier in playoff and high-stakes games | Morale under scrutiny | Assigned |
| Clutch | Modifier in the last five minutes when within five points | None | Assigned |
| Loyalty | None | Re-signing; reactions to trades | Assigned |
| Controversy | None | Off-court incidents; chemistry events | Assigned |
| Sportsmanship | Flagrant-foul chance | Reputation | Assigned |
| Temperament | Technical fouls and ejections; reaction to adversity | Morale swings | Proxied (technicals, ejections) |
| Leadership | Small boost to teammates' consistency | Chemistry; morale | Assigned |
| Determination | None | Progression; injury recovery | Assigned |
| Versatility | Positions he can credibly guard and play | Position penalties in lineup selection; switchability | Derived from physical and defensive ratings |

---

# Team / coach layer

Every setting belongs to the coach, not the team. Estimate it from the coach's history across rosters, net of what those rosters would have done on their own, so his style moves with him when he changes teams. Every setting is also a base preference that the engine adjusts for the personnel on the floor.

## Offense

| Setting | Type | Definition | Estimated from | Drives in engine | Source |
| --- | --- | --- | --- | --- | --- |
| Pace | Rate | How early in the shot clock the team shoots in the half court, plus how often it pushes in transition | Seconds per possession (play-by-play); transition frequency | Possession length; transition chance | Measured |
| Shot preference | Distribution modifier | Tilt toward layup, close, mid, or three | Team shot distribution minus what the roster's tendencies predict | Reweights player shot distributions, then renormalizes | Proxied |
| Offensive rebounding aggressiveness | Rate | How many players crash vs get back | Team offensive rebound chances; opponent transition frequency | Crash vs get-back decision | Measured |
| Play-type mix | Distribution | Shares of isolation, pick-and-roll, post-up, handoff, off-screen, and cut | Team play types (spot-up, transition, and putbacks excluded) | Which half-court action is called | Measured |
| Usage concentration | Rate | Running the offense through a star vs sharing it | Spread of usage across the rotation | Who each action is run for | Measured |
| Mismatch hunting | Rate | How deliberately the offense targets mismatches | Matchup data: how often top scorers attack the weakest defender | Steering actions toward mismatches | Proxied |

## Defense

| Setting | Type | Definition | Estimated from | Drives in engine | Source |
| --- | --- | --- | --- | --- | --- |
| Zone frequency | Rate | Share of possessions played in zone | Little public data; default low | Zone vs man each possession | Assigned |
| Defensive rebounding aggressiveness | Rate | Gang rebounding vs leaking out | Opponent OREB% allowed; own transition frequency | Box-out vs leak-out | Proxied |
| Screen coverage | Distribution | Base shares of switch, drop, and blitz, adjusted for the defenders involved | Switch: how often bigs guard guards in matchup data. Drop and blitz: no public data | Coverage on each ball screen | Proxied / Assigned |
| Help defense | Rate | Helping off shooters vs staying home | Opponent rim frequency vs wide-open threes allowed | Help decision on drives | Proxied |
| Matchup assignment | Rate | Positional assignments vs best defender on best scorer | Matchup data: who guards opponents' top scorers | Initial defensive assignments | Measured |
| Ball pressure | Rate | Denying passing lanes and gambling for steals and blocks | Team deflections; opponent TOV%; team fouls | Scales player steal and block tendencies | Proxied |

## Lineup selection

All lineup settings drive one thing: minutes allocation. Quality is the baseline; the preferences tilt around it and never override it outright. Calibrate by checking each coach's simulated minutes against his real rotations.

| Setting | Definition | Estimated from | Source |
| --- | --- | --- | --- |
| Quality | Weight on overall player value | Real minutes compared with player value | Calibrated |
| Height preference | Tilt toward size | Minutes given compared with quality-predicted minutes | Calibrated |
| Offensive vs defensive preference | One slider between offensively and defensively skilled players (see open decisions) | Minutes given compared with quality-predicted minutes | Calibrated |
| Spacing preference | Tilt toward good, high-volume three-point shooters | Minutes given compared with quality-predicted minutes | Calibrated |
| Depth | Rotation size | Players above a minutes threshold | Measured |
| Stagger vs together | Whether top players share or split minutes | Lineup data: overlap of top players' minutes | Measured |
| Rest / load management | Resting players on back-to-backs and in blowouts | Game logs; play-by-play | Measured |
| Foul-trouble handling | When players sit after early fouls | Play-by-play fouls and substitutions | Measured |

---

# Identifiability notes

In these pairs, the data only shows the combined result, so one side is estimated and the other is fitted to match the real outcome.

| Pair | What the data shows | Approach |
| --- | --- | --- |
| Dunk ratings / Dunk tendency | Dunk rate only | Derive dunk ratings from Vertical, Height, and finishing; fit Dunk tendency |
| Draw foul / Flop | Fouls drawn, not attempts | Assign Flop; fit Draw foul given Flop |
| Block rating / Block tendency | Blocks and fouls | Fit both jointly; fouls separate attempts from success |
| Steal rating / Steal tendency | Steals, deflections, and fouls | Fit both jointly |
| Offensive rebounding / crash tendency | Tracking rebound chances vs rebounds | Tracking data separates them directly |
| Player shot distribution / coach shot preference | Team shot profile | Players who change teams separate player from system |

---

# Open decisions

These are provisional choices made in this spec. Confirm or change them.

1. **Aggression** is defined here as defensive physicality, holding the part of each player's foul rate that block, steal, and contest events don't explain. The alternative is to drop it, since the Drive, Iso, and Shot tendencies already cover offensive aggression.
2. **Pop/roll** was dropped from the latest list but is re-added here. Without it, the engine has no way to decide what a screener does after the screen.
3. **Offensive vs defensive preference** are merged into one slider, because as defined they are opposite ends of the same choice. Consider adding a separate creation preference, which would give the ball-handler scarcity system a coach-side counterpart.
4. **Versatility** is derived from other ratings rather than stored, so it can't drift out of sync with them.
5. **Clutch vs Pressure** are kept distinct: Clutch covers late-and-close situations in any game, and Pressure covers high-stakes games such as the playoffs.

Layout:
nba_sim/
  config/            seasons, endpoints, request settings
  data/
    raw/             untouched API responses, by endpoint/season
    staging/         cleaned tables (parquet)
    warehouse.duckdb core + feature tables
  pipeline/
    extract/         one module per data source
    transform/       raw → staging → core → features
    validate/        checks run after each layer
  estimation/        later: ratings from features
  engine/            later: possession sim
  notebooks/         exploration only, nothing the pipeline depends on