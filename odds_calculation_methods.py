import json

def expected_odds(
        target_fighter_elo, opponent_elo, 
        target_fighter_last_game_was_loss=False, 
        opponent_last_game_was_loss=False, 
        target_opponent_weight_ratio=1,
        target_fighter_months_since_last_fight=0,
        opponent_months_since_last_fight=0,
        prediction_factors_file="prediction_factors.json"
        ) -> float:
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
    with open(prediction_factors_file, "r") as f:
        prediction_factors = json.load(f)

    elo_difference = target_fighter_elo - opponent_elo

    adjusted_elo_difference = elo_difference
    adjusted_elo_difference += (target_opponent_weight_ratio-1)*100 * prediction_factors["per_pound_advantage"]
    if target_fighter_last_game_was_loss: adjusted_elo_difference+=prediction_factors["prior_loss_effect"]
    if opponent_last_game_was_loss: adjusted_elo_difference-=prediction_factors["prior_loss_effect"]
    for i in range(target_fighter_months_since_last_fight):
        if i <= 4: continue
        adjusted_elo_difference+=prediction_factors["ring_rust_effect"]
    for i in range(opponent_months_since_last_fight):
        if i <= 4: continue
        adjusted_elo_difference-=prediction_factors["ring_rust_effect"]

    return 1 / (1 + 10 ** (-(adjusted_elo_difference) / 400))

def elo_change(
        expected_odds: float, 
        result: float, 
        newcomer: bool=False, 
        prediction_factors_file="prediction_factors.json"
        ) -> float:
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
    with open(prediction_factors_file, "r") as f:
        prediction_factors = json.load(f)
    
    k_factor = prediction_factors["k-factor"]
    if newcomer: k_factor = prediction_factors["newcomer_k-factor"]
    return k_factor * (result - expected_odds)