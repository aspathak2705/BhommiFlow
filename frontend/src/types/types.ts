export interface User {
  id: string;
  username: string;
  role: "citizen" | "officer";
  citizen_profile?: CitizenProfile;
  officer_profile?: OfficerProfile;
}

export interface CitizenProfile {
  full_name: string;
  email?: string;
  phone?: string;
  preferred_language: string;
  created_at: string;
  updated_at: string;
}

export interface OfficerProfile {
  full_name: string;
  department: string;
  designation: string;
  office: string;
  district: string;
  taluka: string;
  created_at: string;
  updated_at: string;
}

export interface LandParcel {
  id: string;
  case_id: string;
  district: string;
  taluka: string;
  village: string;
  survey_number?: string;
  subdivision_number?: string;
  property_type?: string;
  area?: number;
  area_unit?: string;
  description?: string;
}

export interface Person {
  id: string;
  full_name: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface CasePerson {
  id: string;
  role: "owner" | "heir" | "buyer" | "seller" | "applicant" | "other";
  notes?: string;
  person: Person;
}

export interface CaseEvent {
  event_id: string;
  case_id: string;
  event_type: string;
  actor_id: string | null;
  actor_role: string;
  timestamp: string;
  metadata_json?: string;
}

export interface Case {
  case_id: string;
  case_reference: string;
  citizen_id: string;
  case_type: string;
  title: string;
  description: string;
  status: "DRAFT" | "SUBMITTED" | "UNDER_REVIEW" | "ACTION_REQUIRED" | "CLOSED";
  priority: string;
  district: string;
  taluka: string;
  village: string;
  created_at: string;
  updated_at: string;
  land_parcels: LandParcel[];
  people: CasePerson[];
}
