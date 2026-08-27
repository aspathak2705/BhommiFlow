export interface Teacher {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Class {
  id: string;
  teacher_id: string;
  name: string;
  grade: string;
  section: string;
  primary_language: string;
  created_at: string;
  updated_at: string;
}

export interface TeachingTask {
  id: string;
  teacher_id: string;
  class_id: string;
  subject: string;
  topic: string;
  duration_minutes: number;
  language: string;
  status: string;
  created_at: string;
  updated_at: string;
}
