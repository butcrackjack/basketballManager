
# Pipeline

## Raw Stats

Box scores, lebron?, advanced stats (for stuff like defense and mental attributes)

## Adjust and Shrink

Normalize, regress

## Player Attributes

Skills + Tendencies

## Priors (temporary attribute changes) per match

Temporary

## Possession Engine

Simluates a possession

## Season Monte Carlo Engine

Schedule, simulates games in a season

## Outputs

Wins, player stats over season, playoff odds



# Steps

## Choose engine

Possession engine, with strong capability for small factors on a basketball court

## Correcting raw stats

Pace and Era, etc

## Designing Attributes (Player)

### Physical

Speed, Agility, Vertical, Strength, Stamina, Height, Wingspan, Durability

### Mental

Off ball movement, Offensive Decisions, Shot IQ, Vision, Aggression, Hustle, Defensive Positioning

### Technical

Layup, Close Shot, Mid Range (pull up/catch and shoot), Three Pointer (pull up/catch and shoot), Free Throw, Post shot, Ball Handle, Passing, defensive Rebounding, offensive Rebounding,
Perimeter Defense, Interior Defense, Block, Steal, Draw Foul

### Tendencies

Drive, shot (within that a value for each shot type: layup, close, post, mid (pull up/c&s), three(pull up/c&s)), Has ball, iso, call for screen, pass, dunk, flop (for foul bait), block, steal, screen, cut, defensive rebound, offensive rebound

### Personality / Hidden Attributes

Professionalism, Consistency, Pressure, Loyalty, Controversy, Sportsmanship, Versatility, Temperament, Clutch, Leadership, Determination

## Designing Attributes (Team/Coach)

### Offensive (all prefernces are somewhat dependent on team/lineup personel)
Pace (shot tendency for how quick they are likely to shoot, also how likely to run in transition), Shot preference (Layup, close, mid, three), offensive rebounding aggressiveness (get back or crash boards), isolation tendency, pick-and-roll tendency, post-ups tendency, handoffs tendency, off-screen actions tendency, cutting tendency, Usage concentration (high means play through star, low means share usage), mismatch hunting

### Defensive (all prefernces are somewhat dependent on team/lineup personel)
defensive system tendency (zone vs man), defensive rebounding aggressiveness (run transition or crash boards), defensive screen call preference (switch, drop, blitz),  help defense (drop in or stay on shooter), matchup assignment (strictly positional/size based or put best defender on best offensive player), ball pressure (clog off ball passing lanes / gamble for steals and blocks),  

### Lineup selection (only impacts minutes allocation and will be dependent on the player/teams general attributes, i.e. a bad shooting team wont absolutely prioritize shooting with that type of coach)
Quality, Height preference, Defensive preference, Offensive preference (preference to players that are generally skilled offensively over defensively skilled players), spacing preference (preference for many and good 3pt shooters), depth preference, stagger minutes vs play best players together, rest / load management (for choosing to include in the lineup / rest in junk time), foul trouble handling (do they come out with 3 fouls in the second quarter)
