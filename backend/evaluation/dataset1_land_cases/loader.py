import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Dataset1Loader:
    @staticmethod
    def get_dataset_paths() -> List[str]:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        dataset_dir = os.path.join(base_dir, "datasets", "dataset1_land_cases")
        
        # Discover part1 and part2 files dynamically
        files = [
            "bhoomiflow_dataset1_land_cases_part1_50.json",
            "bhoomiflow_dataset1_land_cases_part2_50.json"
        ]
        paths = [os.path.join(dataset_dir, f) for f in files]
        for p in paths:
            if not os.path.exists(p):
                raise FileNotFoundError(f"Dataset 1 file missing at: {p}")
        return paths

    @staticmethod
    def load_dataset1() -> List[Dict[str, Any]]:
        """
        Loads, validates, and combines Dataset 1 parts into 100 cases.
        """
        paths = Dataset1Loader.get_dataset_paths()
        combined_cases = []
        case_ids_seen = set()

        for idx, path in enumerate(paths, start=1):
            with open(path, "r", encoding="utf-8") as f:
                cases = json.load(f)
                
            if len(cases) != 50:
                raise ValueError(f"Expected part {idx} to contain exactly 50 records. Found: {len(cases)}")
                
            for case in cases:
                case_id = case.get("case_id")
                if not case_id:
                    raise ValueError("Malformed case object missing case_id identifier.")
                
                # Check for duplicates across parts
                if case_id in case_ids_seen:
                    raise ValueError(f"Duplicate case_id detected: {case_id}")
                
                case_ids_seen.add(case_id)
                combined_cases.append(case)

        if len(combined_cases) != 100:
            raise ValueError(f"Logical Dataset 1 mismatch. Expected 100 combined cases, found: {len(combined_cases)}")

        return combined_cases

    @staticmethod
    def validate_relationships(case: Dict[str, Any]) -> List[str]:
        """
        Validates internal entity and reference constraints for a single synthetic Case scenario.
        """
        errors = []
        entities = case.get("case_entities", {})
        
        # Extract entity IDs
        persons = {p["person_id"] for p in entities.get("persons", []) if "person_id" in p}
        authorities = {a["authority_id"] for a in entities.get("authorities", []) if "authority_id" in a}
        parcels = {p["parcel_id"] for p in entities.get("land_parcels", []) if "parcel_id" in p}
        documents = {d["document_id"] for d in entities.get("documents", []) if "document_id" in d}

        # Validate relationships inside Events
        for evt in entities.get("events", []):
            p_id = evt.get("person_id")
            if p_id and p_id.startswith("P") and p_id not in persons:
                errors.append(f"Event {evt.get('event_id')} references undefined person: {p_id}")
            
            doc_id = evt.get("document_id")
            if doc_id and doc_id.startswith("DOC") and doc_id not in documents:
                errors.append(f"Event {evt.get('event_id')} references undefined document: {doc_id}")
                
            parcel_id = evt.get("parcel_id")
            if parcel_id and parcel_id.startswith("PAR") and parcel_id not in parcels:
                errors.append(f"Event {evt.get('event_id')} references undefined land parcel: {parcel_id}")

        # Validate relationships inside Conflicts
        for cfl in entities.get("conflicts", []):
            ent_a = cfl.get("entity_a")
            ent_b = cfl.get("entity_b")
            
            # Match only explicit ID structures (e.g. starting with standard prefixes P, DOC, E, PAR)
            all_valid_entities = persons | documents | parcels | {e.get("event_id") for e in entities.get("events", [])}
            
            # Helper to check if entity reference is a valid ID directly or matches an ID suffix
            def is_valid_ref(ent):
                if not ent:
                    return True
                if ent in all_valid_entities:
                    return True
                # Clean reference of enclosing characters to verify if it contains a valid ID
                cleaned = ent.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
                for valid_id in all_valid_entities:
                    if valid_id in cleaned or cleaned.endswith(valid_id) or f" {valid_id}" in cleaned:
                        return True
                return False

            # Run checks only if entity contains pattern-like string resembling IDs
            import re
            id_pattern = re.compile(r"\b[A-Za-z0-9_-]+\b")
            
            def has_id_pattern(ent):
                if not ent:
                    return False
                tokens = id_pattern.findall(ent)
                for t in tokens:
                    # Token must match one of standard ID prefixes AND end with digit to avoid matching generic text strings
                    if any(t.startswith(pref) for pref in ["P", "DOC", "E", "PAR", "D", "L", "C", "A"]) and len(t) <= 12:
                        if re.search(r"\d+$", t):
                            return True
                return False

            if ent_a and has_id_pattern(ent_a) and not is_valid_ref(ent_a):
                errors.append(f"Conflict {cfl.get('conflict_id')} entity_a references undefined entity: {ent_a}")
            if ent_b and has_id_pattern(ent_b) and not is_valid_ref(ent_b):
                errors.append(f"Conflict {cfl.get('conflict_id')} entity_b references undefined entity: {ent_b}")

        return errors
