import numpy as np
import logging

from participants.consumer import *
from participants.producer import *
from market.line_search import *
from schema import *
from itertools import chain

np.set_printoptions(precision=4,suppress=True,threshold=12)
#logging.basicConfig(level=logging.DEBUG, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.INFO, format='%(message)s (%(levelname)s)')
logging.basicConfig(level=logging.WARNING, format='%(message)s (%(levelname)s)')
#logging.basicConfig(level=logging.ERROR, format='%(message)s (%(levelname)s)')

production_matrix = np.array([
    [5,1,0,0],
    [0,-0.5,1.5,0],
    [0,-1,-2,2],
    [0,5,0,-0.5] ])

local_schema = LabourSchema(["food", "wood", "ore", "tools"],[])
gs = GlobalSchema(local_schema, ["Switzerland", "Italy"])


switzerland = gs.province_of_name("Switzerland")
sw_pl = gs.placement_in_province(switzerland)

swiss_consumers = LabourerConsumer(np.array([2,1.2,0,2]), 800, sw_pl)

cow_farm = Producer.factory("Cow farm", np.array([3,2,0,0]), sw_pl)
swiss_mine = Producer.factory("Swiss mine", np.array([0,-0.5,1.5,0]), sw_pl)
swiss_artisans = Producer.factory("artisans", np.array([0,-1,2,0]), sw_pl)

swiss_participants = [swiss_consumers, cow_farm, swiss_mine, swiss_artisans]


italy = gs.province_of_name("Italy")
it_pl = gs.placement_in_province(italy)

italian_consumers = LabourerConsumer(np.array([2.1,1,0,1.8]), 6000, it_pl)

po_farm = Producer.factory("Po farm", np.array([6,0,0,0]), it_pl)
italian_wood_cutter = Producer.factory("wood cutter", np.array([-1,4,0,0]), it_pl)
italian_smith = Producer.factory("smith", np.array([0,-1,1.8,0]), it_pl)
italian_mine = Producer.factory("Italian mine", np.array([0,-0.5,2,0]), it_pl)

italian_participants = [italian_consumers, po_farm, italian_mine, italian_smith]

def concat_map(func, it):
    """Map a function over a list and concatenate the results."""
    return chain.from_iterable(map(func, it))

trade_factors = np.array([3,4,2,1])

def set_up_merchants(gs : GlobalSchema, home : int, foreign : int) -> Iterable[Producer]:
    def for_good(good : int) -> Iterable[Producer]:
        width = gs.global_width()
        li = gs.labour_in_province(home)
        hi = gs.good_in_province(home, good)
        fi = gs.good_in_province(foreign, good)
        tf = trade_factors[good]
        hname = gs.name_of_province(home) 
        fname = gs.name_of_province(foreign) 
        gname = gs.local_schema().name_of_good(good)
        exporter = Producer.trader(f"{gname} from {hname} to {fname}", li, hi, fi, tf, width)
        importer = Producer.trader(f"{gname} from {fname} to {hname}", li, fi, hi, tf, width)
        return [importer, exporter]
    return concat_map(for_good, gs.local_schema().trade_goods())

italian_merchants = list(set_up_merchants(gs, italy, switzerland))

participants = swiss_participants + italian_participants + italian_merchants

p0 = np.full((gs.global_width()), 10)
epsilon = 0.01


def run_once(t : float):
    config = LineSearchConfiguration(price_scaling=ScalingConfiguration(100))
    p = line_search_market(participants, p0, epsilon, config)
    print(f"iterations: {get_iteration()}    (t={t})")
    print(p)
    reset_iteration()

run_once(0.6)

"""
run_once(0.2)
run_once(0.3)
run_once(0.4)
run_once(0.5)
run_once(0.6)
run_once(0.7)
run_once(0.8)
run_once(0.9)
run_once(1.0)
"""
