from dataclasses import dataclass


@dataclass
class Metric:
    id: int
    type: str


@dataclass
class MetricValue:
    id: int
    metric_id: int
    timestamp: str
    value: str
