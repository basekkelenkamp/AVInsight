from dataclasses import dataclass
from typing import Optional


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
    data_report_id: Optional[int] = None


@dataclass
class DataReport:
    date_id: str
    report_finished: bool
    first_timestamp: str
    last_timestamp: str
    daily_counts: str
    daily_max: str
    daily_avg: str
    thresholds: str
    total_points_count: str
    minute_data: str  # BLOB
    spike_data: str  # BLOB
