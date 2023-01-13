from sqlalchemy import Column, Integer, String, Boolean, CheckConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY


from data.static import SIDE, FLEETORDER
from data.static_battle import BATTLE_TYPE_ORDER_MAPPING
from objects.models import ShipBase
from database.db import Base


class Battle(Base):
    """Stores data from one instance of battle, e.g. day battle or night battle.

    Attributes:
        id (int): Primary key.
        world (int): World number.
        map (int): Map number.
        node (int): Node number, not to be confused with the node letter.
        difficulty (int): Difficulty number. Goes from 1 to 4 for casual to hard.
        engagement (int): Engagement number. @see data.static_battle.ENGAGEMENT.
        debuffed (bool): Debuffed flag. This is checked by the viewer for the api_debuffed / api_xal01 field. TODO: Implement checks on parser-side.
        cleared (bool): Map clear flag. Debuff may automatically be applied post-clear, leading to higher bonuses.
        resupplied (bool): Resupply flag. May be unreliable.
        battle_type (str): Battle API endpoint.
        amount_of_nodes (int): Number of nodes unlocked. Used for debuff tracking.
        player_fleet_type (int): Combined fleet type. @see data.static.BATTLE_TYPE.
        enemy_fleet_type (int): Enemy fleet type. @see data.static.BATTLE_TYPE.
        player_formation (int): Player formation ID. @see data.static_battle.FORMATION.
        enemy_formation (int): Enemy formation ID. @see data.static_battle.FORMATION.
        fleets (List[Fleet]): Array of participating fleets.
        attacks (List[Attack]): Array of attacks.
        lbas (List[LBAS]): Array of participating LBAS.
        player_ships (List[PlayerShip]): Array of participating ships from the player side, excluding friendly fleet.
    """
    __tablename__ = "battle"

    id = Column(Integer, primary_key=True)
    world = Column(Integer, nullable=False)
    map = Column(Integer, nullable=False)
    node = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)
    engagement = Column(Integer, nullable=False)
    debuffed = Column(Boolean, nullable=False)
    cleared = Column(Boolean, nullable=False)
    resupplied = Column(Boolean, nullable=False) 
    battle_type = Column(String(50), nullable=False)
    amount_of_nodes = Column(Integer, nullable=False)

    player_fleet_type = Column(Integer, nullable=False)
    enemy_fleet_type = Column(Integer, nullable=False)
    player_formation = Column(Integer, nullable=False)
    enemy_formation = Column(Integer, nullable=False)

    fleets = relationship("Fleet", back_populates="battle")
    attacks = relationship("Attack", back_populates="battle")
    lbas = relationship("LBAS", back_populates="battle")
    player_ships = relationship("PlayerShip", back_populates="battle")

CheckConstraint(Battle.battletype in BATTLE_TYPE_ORDER_MAPPING.keys())

class Fleet(Base): # Is this a good idea? Enemy/FF comps are repeated en masse. We only need the HP values technically.
    """Stores an enemy or friendly fleet participating in a battle.

    Parameters:
        id (int): Primary key.
        ships (int[]): Array of ship IDs.
        levels (int[]): Array of ship levels.
        initial_hp (int[]): Array of initial HP at the start of the battle of the ships in fleet.
        max_hp (int[]): Array of max HP of the ships in the fleet.
        stats (int[][]): Array of array of stats [FP, TP, AA, AR] for each ship.
        equipment (int[][]): Array of array of equipment IDs for each ship.
    """
    __tablename__ = "fleet"

    id = Column(Integer, primary_key=True)
    ships = Column(ARRAY(Integer), nullable=False, dimensions=1)
    levels = Column(ARRAY(Integer), nullable=False, dimensions=1)
    initial_hp = Column(ARRAY(Integer), nullable=False, dimensions=1)
    max_hp = Column(ARRAY(Integer), nullable=False, dimensions=1)
    stats = Column(ARRAY(Integer), nullable=False, dimensions=2)
    equipment = Column(ARRAY(Integer), nullable=False, dimensions=2)
    side = Column(Integer, default=SIDE.ENEMY)
    order = Column(Integer, default=FLEETORDER.MAIN)

    battle = relationship("Battle", back_populates="fleets")

    def fetch_ship(self, position: int) -> ShipBase:
        return ShipBase(
            self.ships[position],
            position,
            (self.initial_hp[position], self.max_hp[position]),
            self.equipment[position],
            *self.stats[position],
        )

CheckConstraint(func.cardinality(Fleet.ships) > 0)
CheckConstraint(func.cardinality(Fleet.levels) > 0)
CheckConstraint(func.cardinality(Fleet.initial_hp) > 0)
CheckConstraint(func.cardinality(Fleet.max_hp) > 0)
CheckConstraint(func.cardinality(Fleet.stats) > 0)
CheckConstraint(func.cardinality(Fleet.equipment) > 0)
CheckConstraint(Fleet.side in [SIDE.ENEMY, SIDE.FRIEND])
CheckConstraint(Fleet.order in [FLEETORDER.MAIN, FLEETORDER.ESCORT])

class PlayerShip(Base):
    """Stores a 
    """
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True)
    mst_id = Column(Integer, nullable=False)
    initial_hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    equipment = Column(ARRAY(Integer), nullable=False)
    proficiency = Column(ARRAY(Integer), nullable=False)
    morale = Column(Integer, nullable=False)
    visible_stats = Column(ARRAY(Integer), nullable=False)

    # Total stats
    equipment = Column(ARRAY(Integer), nullable=False)
    firepower = Column(Integer, nullable=False)
    torpedo = Column(Integer, nullable=False)
    antiair = Column(Integer, nullable=False)
    asw = Column(Integer, nullable=False)
    armor = Column(Integer, nullable=False)
    evasion = Column(Integer, nullable=False)
    luck = Column(Integer, nullable=False)
    line_of_sight = Column(Integer, nullable=False)

    fuel = Column(Integer, nullable=False)
    ammo = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)

    battle = relationship("Battle", back_populates="playerships")
    attacks = relationship("Attack", back_populates="playership")

class Attack(Base):
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True)
    attacker = Column(Integer, nullable=True) # Null on aerial attacks
    defender = Column(Integer, nullable=False)
    defender_hp = Column(Integer, nullable=False)
    defender_id = Column(Integer, nullable=False)
    defender_armor = Column(Integer, nullable=False)
    inside_scratch_range = Column(Boolean, nullable=False) # This is only checked for player ships attacking enemy ships
    hit_status = Column(Integer, nullable=False)
    damage = Column(Integer, nullable=False) # Damage is usually floating point for flagship prot, but we just add the fs_prot flag to make it simpler
    fs_prot = Column(Boolean, default=False)
    phase = Column(String(50), nullable=False)
    cutin = Column(Integer, nullable=False)
    cutin_equips = Column(ARRAY(Integer), nullable=True)
    sp_list = Column(ARRAY(Integer), nullable=True) # Aerial attack unique trait
    night_carrier = Column(Boolean, nullable=True) # Night battle night carrier flag

    battle = relationship("Battle", back_populates="attacks")
    playership = relationship("PlayerShip")

CheckConstraint(Attack.damage >= 0)
CheckConstraint(Attack.defender >= 0)
CheckConstraint(Attack.hit_status in [0, 1, 2])

class LBAS(Base):
    __tablename__ = "lbas"
    id = Column(Integer, primary_key=True)
    planes = Column(ARRAY(Integer), nullable=False)
    slots = Column(ARRAY(Integer), nullable=False)
    ace = Column(ARRAY(Integer), nullable=False)
    morale = Column(ARRAY(Integer), nullable=False)
    strikepoints = Column(ARRAY(Integer), nullable=False)
    battle = relationship("Battle", back_populates="lbas")

CheckConstraint(func.cardinality(LBAS.planes) > 0)
CheckConstraint(func.cardinality(LBAS.slots) > 0)
CheckConstraint(func.cardinality(LBAS.ace) > 0)
CheckConstraint(func.cardinality(LBAS.morale) > 0)
CheckConstraint(func.cardinality(LBAS.strikepoints) > 0)
