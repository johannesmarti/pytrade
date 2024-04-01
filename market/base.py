import numpy as np
from numpy.linalg import norm
import logging
from dataclasses import dataclass

from typing import Callable,Iterable,Optional
#import numpy.typing as npt

from core.participant import *

#Market = Callable[[Iterable[Participant],Prices],Prices]

MIN_PRICE = 0.0001

iteration : int = 0

def reset_iteration() -> None:
    global iteration
    iteration = 0

def increment_iteration() -> None:
    global iteration
    iteration += 1

def get_iteration() -> int:
    global iteration
    return iteration


step: int = 0

def reset_step() -> None:
    global step
    step = 0

def increment_step() -> None:
    global step
    step += 1

def get_step() -> int:
    global step
    return step

def one_iteration(participants : Iterable[Participant], prices : Prices) -> VolumeBundle:
    increment_iteration()
    logging.debug(f"at iteration {get_iteration()}")
    eb = VolumeBundle.zero(prices.shape)
    for p in participants:
        eb += p.participate(prices)
    return eb

MIN_PRICE : float = 0.001

@dataclass(frozen=True)
class ScalingConfiguration:
    set_to_price: float = 10
    norm_listing: Optional[int] = None

def adapt_prices(price : Prices, error : VolumeBundle, t : float, price_scaling : Optional[ScalingConfiguration]) -> Prices:
    new_price = price * (1 - t * error.update_term())
    #assert (new_price > 0).all()
    if (price_scaling != None):
        leading = price_scaling.norm_listing
        if (leading == None):
            base = np.average(new_price)
        else:
            base = new_price[leading]
        scaling_factor = price_scaling.set_to_price / base
        new_price *= scaling_factor
    return np.maximum(new_price, MIN_PRICE)

def broad_adapt_prices(price : Prices, error : VolumeBundle, t : np.ndarray, price_scaling : Optional[ScalingConfiguration]) -> Prices:
    assert t.shape == price.shape
    new_price = price * (1 - t * error.update_term())
    #assert (new_price > 0).all()
    if (price_scaling != None):
        leading = price_scaling.norm_listing
        if (leading == None):
            base = np.average(new_price)
        else:
            base = new_price[leading]
        scaling_factor = price_scaling.set_to_price / base
        new_price *= scaling_factor
    return np.maximum(new_price, MIN_PRICE)

def relative_badness(error : VolumeBundle) -> float:
    #return norm(error)
    #return norm(error, ord=1)
    return norm(error.value/(error.volume + 0.0001), ord=1)

def absolute_badness(error : VolumeBundle) -> float:
    #return norm(error)
    #return norm(error, ord=1)
    return norm(error.value, ord=1)
