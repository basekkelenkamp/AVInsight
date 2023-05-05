from dataclasses import dataclass


@dataclass
class Metrics:
    id: int
    type: str


@dataclass
class MetricValues:
    id: str
    metric_id: int
    timestamp: int
    value: str
