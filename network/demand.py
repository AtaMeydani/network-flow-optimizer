from dataclasses import dataclass


@dataclass
class TrafficDemand:
    """Class for holding traffic demand information"""
    source: str
    target: str
    bandwidth: float
    revenue: float

    def __repr__(self):
        """Describe the demand endpoints, bandwidth and revenue."""
        return f'TrafficDemand({self.source}->{self.target}, bw={self.bandwidth}, rev={self.revenue})'

    def to_dict(self) -> dict:
        """Return a JSON-compatible representation."""
        return {'source': self.source, 'target': self.target, 'bandwidth': self.bandwidth, 'revenue': self.revenue}

    @classmethod
    def from_dict(cls, data: dict):
        """Create a demand from a JSON-compatible record."""
        return cls(source=data['source'], target=data['target'], bandwidth=float(data['bandwidth']), revenue=float(data['revenue']))
