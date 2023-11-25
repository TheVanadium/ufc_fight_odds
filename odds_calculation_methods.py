def expected_odds(
        target_fighter_elo, opponent_elo, 
        target_fighter_last_game_was_loss=False, 
        opponent_last_game_was_loss=False, 
        target_opponent_weight_ratio=1) -> float:
    """ Calculates the expected odds of a fighter winning a fight using the elo system.

    Args:
        target_fighter_elo (int): the elo of the fighter whose odds are being calculated
        opponent_elo (int): the elo of the opponent
        target_fighter_last_game_was_loss (bool): whether the target fighter lost their last game
        opponent_last_game_was_loss (bool): whether the opponent lost their last game
        target_opponent_weight_ratio (float): the ratio of the target fighter's weight to the opponent's weight

    Returns:
        float: the expected odds of the target fighter winning, as a percentage from 0 to 1

    """
    
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

def elo_change(expected_odds: float, result: float, k_factor: int=32):
    """Calculates the elo change of a fighter after a fight.
    
        Using standard elo change formula
    """
    return k_factor * (result - expected_odds)