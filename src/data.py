from dataclasses import dataclass
from datetime import timedelta, date
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


def parse_timedelta(s: str) -> timedelta:
    return pd.Timedelta(s).to_pytimedelta()


@dataclass
class Route:
    "A route (trail, path, etc.)"

    id: str
    name: str
    country: str
    state: str
    distance: float
    mode: str
    link: str
    description: str

    @staticmethod
    def load(path: Path) -> Dict[str, "Route"]:
        df = pd.read_csv(path)
        route_dict: Dict[str, Route] = {}
        for _, row in df.iterrows():
            route_id = row["id"]
            route_dict[route_id] = Route(
                id=route_id,
                name=row["name"],
                country=row["country"],
                state=row["state"],
                distance=row["distance"],
                mode=row["mode"],
                link=row["link"],
                description=row["description"],
            )
        return route_dict


@dataclass
class Record:
    """A record time for a particular route"""
    
    route_id: str
    people: str
    time: timedelta
    link: str

    @staticmethod
    def load(path: Path) -> List["Record"]:
        df = pd.read_csv(path)
        record_list: List[Record] = []
        for _, row in df.iterrows():
            route_id = row["route_id"]
            record_list.append(
                Record(
                    route_id=route_id,
                    people=row["people"],
                    time=parse_timedelta(row["time"]),
                    link=row["link"],
                )
            )
        return record_list
    
    def calc_pace(self, distance: float) -> str:
        pace = int(self.time.seconds / distance * 2)  # seconds per km
        return f"{pace // 60}:{pace % 60:.0f} min/km"

    


@dataclass
class Haf:
    """A 'half as fast' attempt"""

    route_id: str
    date: date
    people: str
    time: timedelta
    distance: float
    complete: bool
    half_as_fast: bool
    link: str

    @staticmethod
    def load(path: Path) -> List["Haf"]:
        df = pd.read_csv(path)
        haf_list: List[Haf] = []
        for _, row in df.iterrows():
            haf_list.append(
                Haf(
                    route_id=row["route_id"],
                    date=row["date"],
                    people=row["people"],
                    time=parse_timedelta(row["time"]),
                    distance=row["distance"],
                    complete=row["complete"],
                    half_as_fast=row["half_as_fast"],
                    link=row["link"],
                )
            )
        return haf_list
    
    def percentage_complete(self, route_distance: float) -> str:
        return f"{self.distance / route_distance:.0%}"



@dataclass
class Data:
    """Data read from the CSV files"""

    route_dict: Dict[str, Route]
    haf_list: List[Haf]
    record_list: List[Record]

    @staticmethod
    def load(data_dir: Path) -> "Data":
        data = Data(
            route_dict=Route.load(data_dir / "route.csv"),
            haf_list=Haf.load(data_dir / "haf.csv"),
            record_list=Record.load(data_dir / "record.csv"),
        )
        data.validate()
        return data
        
    def validate(self) -> None:
        # every Haf must link to a Route
        route_id_set = {haf.route_id for haf in self.haf_list}
        bad_ids = route_id_set - set(self.route_dict)
        if len(bad_ids) > 0:
            raise ValueError(f"Some Hafs refer to these route IDs that don't exist: {bad_ids}")
        
        # every Record must link to a Route
        route_id_set = {record.route_id for record in self.record_list}
        if len(bad_ids) > 0:
            raise ValueError(f"Some Records refer to these route IDs that don't exist: {bad_ids}")
        
        # every Route must have at least one record
        missing = set(self.route_dict) - route_id_set
        if len(missing) > 0:
            raise ValueError(f"The following Routes do not have linked Records: {missing}")

    def iter_routes(self) -> List[Tuple[Route, Record, List[Haf]]]:
        """Return list of routes, each with the fastest relevant record, and a list of the 
        HAF attempts on that route.
        """
        result_list: List[Tuple[Route, Record, List[Haf]]] = []
        for route_id, route in self.route_dict.items():
            records = [record for record in self.record_list if record.route_id == route_id]
            record = sorted(records, key=lambda record: record.time)[0]  # take fastest
            haf_list = [haf for haf in self.haf_list if haf.route_id == route_id]
            haf_list = sorted(haf_list, key=lambda haf: haf.date)  # sort chronologically
            result_list.append((route, record, haf_list))
        return result_list