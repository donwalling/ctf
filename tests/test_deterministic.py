
from ctf.arena import Arena
from ctf.teams.team_alpha import Team as TeamAlpha
from ctf.teams.team_bravo import Team as TeamBravo

def test_capture_sequence_auto_pickup_and_score():
    arena = Arena(teams=[TeamAlpha(), TeamBravo()])
    # find alpha attacker
    alpha_att = next(a for a in arena.agents if a.state.name=='alpha_att')
    # teleport onto Bravo flag and apply auto-pickup
    alpha_att.state.position = tuple(arena.flags['Team Bravo'].position)
    arena._auto_pickup_flags()
    assert alpha_att.state.has_flag is True
    # move to Alpha base and resolve
    alpha_att.state.position = tuple(arena.flags['Team Alpha'].position)
    pre = arena.scoreboard.get('Team Alpha')
    arena._resolve_flag_conditions()
    post = arena.scoreboard.get('Team Alpha')
    assert post >= pre + 5

def test_tag_scores_and_returns_flag():
    arena = Arena(teams=[TeamAlpha(), TeamBravo()])
    alpha_def = next(a for a in arena.agents if a.state.name=='alpha_def')
    bravo_scout = next(a for a in arena.agents if a.state.name=='bravo_scout')
    # give Bravo scout the Alpha flag and place adjacent to Alpha defender
    bravo_scout.state.has_flag = True
    arena.flags['Team Alpha'].taken_by = 'bravo_scout'
    alpha_def.state.position = (4,5)
    bravo_scout.state.position = (4,6)
    pre = arena.scoreboard.get('Team Alpha')
    arena._apply_action(alpha_def, ('tag','bravo_scout'))
    post = arena.scoreboard.get('Team Alpha')
    assert post == pre + 1
    # flag should be returned to owner base (i.e., not carried anymore)
    assert arena.flags['Team Alpha'].taken_by is None
    assert bravo_scout.state.has_flag is False
