import time
from dataclasses import dataclass

@dataclass
class Ability:
    name: str
    cooldown_seconds: float
    duration_seconds: float
    last_activation_time: float = 0.0
    active_until: float = 0.0
    
    @property
    def is_active(self) -> bool:
        return time.time() < self.active_until
        
    @property
    def is_ready(self) -> bool:
        return time.time() > (self.last_activation_time + self.cooldown_seconds)
        
    @property
    def cooldown_remaining(self) -> float:
        remaining = (self.last_activation_time + self.cooldown_seconds) - time.time()
        return max(0.0, remaining)
        
    def activate(self) -> bool:
        if self.is_ready:
            now = time.time()
            self.last_activation_time = now
            self.active_until = now + self.duration_seconds
            return True
        return False

class PhaseAbility(Ability):
    def __init__(self):
        super().__init__(
            name="Phase",
            cooldown_seconds=10.0,
            duration_seconds=3.0
        )

class BoostAbility(Ability):
    """
    Boost behaves slightly differently: 
    It consumes energy ('fist' gesture) rather than a fixed cooldown.
    """
    def __init__(self):
        super().__init__(
            name="Boost",
            cooldown_seconds=0.0,
            duration_seconds=0.5 # Active for a short burst per call
        )
        self.energy = 100.0
        self.consumption_rate = 20.0 # per second
        self.recharge_rate = 5.0 # per second
        
    def update(self, dt: float, currently_boosting: bool):
        if currently_boosting and self.energy > 0:
            self.energy = max(0.0, self.energy - self.consumption_rate * dt)
            self.active_until = time.time() + 0.1 # Keep active while held
        else:
            self.energy = min(100.0, self.energy + self.recharge_rate * dt)
            
    @property
    def is_active(self) -> bool:
        return super().is_active and self.energy > 0
