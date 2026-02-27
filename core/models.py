"""
Data models for Rach Scope
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """Enumeration for different types of events"""
    # Basic roast events
    MARK_EVENT = "MARK_EVENT"
    DRY_END = "DRY_END"
    FIRST_CRACK = "FIRST_CRACK"
    SECOND_CRACK = "SECOND_CRACK"

    # Coffee roasting operations
    CHARGE = "CHARGE"
    FC_START = "FC_START"
    FC_FINISH = "FC_FINISH"
    SC_START = "SC_START"
    SC_FINISH = "SC_FINISH"
    DROP = "DROP"


@dataclass
class RoastData:
    """Data model for roast data points"""
    timestamp: datetime
    bt: float  # Bean Temperature
    et: float  # Environmental Temperature
    ror: float = 0.0  # Rate of Rise

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'bt': self.bt,
            'et': self.et,
            'ror': self.ror
        }


@dataclass
class RoastEvent:
    """Data model for roast events (e.g., Dry End, First Crack, Coffee operations)"""
    event_type: EventType
    name: str
    timestamp: datetime
    bt: float
    et: float
    ror: float = 0.0
    description: str = ""
    # Additional fields for coffee operations
    end_bt: Optional[float] = None  # End temperature for FC/SC
    end_time: Optional[float] = None  # Elapsed time for FC/SC (seconds)
    bean_color: Optional[str] = None  # For coffee color tracking

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        base_dict = {
            'event_type': self.event_type.value,
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'bt': self.bt,
            'et': self.et,
            'ror': self.ror,
            'description': self.description
        }

        # Add optional fields if present
        if self.end_bt is not None:
            base_dict['end_bt'] = f"{self.end_bt:.1f}"
        if self.end_time is not None:
            base_dict['end_time'] = f"{self.end_time:.1f}"
        if self.bean_color:
            base_dict['bean_color'] = self.bean_color

        return base_dict


@dataclass
class RoastProfile:
    """Data model for a complete roast profile"""
    name: str
    data_points: List[RoastData] = field(default_factory=list)
    events: List[RoastEvent] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def add_data_point(self, data: RoastData):
        """Add a data point to the profile"""
        self.data_points.append(data)

    def add_event(self, event: RoastEvent):
        """Add an event to the profile"""
        self.events.append(event)

    def get_bt_values(self) -> List[float]:
        """Get all BT values"""
        return [point.bt for point in self.data_points]

    def get_et_values(self) -> List[float]:
        """Get all ET values"""
        return [point.et for point in self.data_points]

    def get_ror_values(self) -> List[float]:
        """Get all RoR values"""
        return [point.ror for point in self.data_points]

    def get_timestamps(self) -> List[datetime]:
        """Get all timestamps"""
        return [point.timestamp for point in self.data_points]
