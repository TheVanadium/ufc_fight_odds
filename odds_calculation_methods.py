import json
def get_prediction_factors():
    """Gets the prediction factors from the prediction_factors.json file.

    Returns:
        dict: the prediction factors
    """
    with open("prediction_factors.json", "r") as f:
        return json.load(f)

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
    WEIGHT_FACTOR = get_prediction_factors()["per_pound_advantage"]

    adjusted_elo_difference = elo_difference
    adjusted_elo_difference += (target_opponent_weight_ratio-1)*100 * WEIGHT_FACTOR
    if target_fighter_last_game_was_loss: adjusted_elo_difference+=get_prediction_factors()["prior_loss_effect"]
    if opponent_last_game_was_loss: adjusted_elo_difference-=get_prediction_factors()["prior_loss_effect"]

    return 1 / (1 + 10 ** (-(adjusted_elo_difference) / 400))

def elo_change(expected_odds: float, result: float, newcomer: bool=False) -> float:
    """Calculates the elo change of a fighter after a fight.
    
        Using standard elo change formula

    Args:
        expected_odds (float): the expected odds of the fighter winning
        result (float): the result of the fight, 1 for win, 0 for loss
        newcomer (bool, optional): whether the fighter is a newcomer. Defaults to False.
            a newcomer is a fighter with less than 2 fights

    Returns:
        float: the elo change of the fighter
    """
    k_factor = get_prediction_factors()["k-factor"]
    if newcomer: k_factor = get_prediction_factors()["newcomer_k-factor"]
    return k_factor * (result - expected_odds)