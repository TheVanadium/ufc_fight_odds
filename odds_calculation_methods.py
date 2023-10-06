# expected odds
def expected_odds(target_fighter_elo, opponent_elo, target_fighter_last_game_was_loss=False, opponent_last_game_was_loss=False, target_opponent_weight_ratio=1):
    elo_difference = target_fighter_elo - opponent_elo
    # test this variable later
    # LAST_GAME_WAS_LOST = 50
    
    # all else being equal, a fighter moving down 10% should have an 75% chance of winning
    WEIGHT_FACTOR = 10

    adjusted_elo_difference = elo_difference
    adjusted_elo_difference += (target_opponent_weight_ratio-1)*100 * WEIGHT_FACTOR
    # if target_fighter_last_game_was_loss: adjusted_elo_difference+=LAST_GAME_WAS_LOST
    # if opponent_last_game_was_loss: adjusted_elo_difference-=LAST_GAME_WAS_LOST

    return 1 / (1 + 10 ** (-(adjusted_elo_difference) / 400))

# elo change
def elo_change(expected_odds, result, k_factor=32):
    return k_factor * (result - expected_odds)