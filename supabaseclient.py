import json
import os
import supabase
from WebsiteTester import SUPABASE_KEY
import time
from datetime import datetime, timedelta
import random
from supabase import create_client
from wonderwords import RandomSentence
from faker import Faker
from faker_vehicle import VehicleProvider

rs = RandomSentence()

class SupabaseClient:

    def configure_project_phases(self, project_id):
        phases = self.supabase.table("project_phases") \
            .select("*") \
            .eq("project_id", f"{project_id}") \
            .execute() 
        for phase in phases.data:
            dt =  datetime.now() + timedelta(days=random.randint(-30, 30))
            record = {            
                "phase_id":     phase['id'],
                "status":       random.choice(["completed", "in_progress", "pending"]),
                "created_at":   dt.isoformat()
            }
            print(f"  - Adding project phase: {phase['phase_name']}")
            response = self.supabase.table("project_tasks").update(record).eq("id", phase['id']).execute()
            response.raise_for_status()
        pass

    def add_project_timeline_entries(self, new_project_name, project_id, count = 15):    
        images = self.data['images']    
        for _ in range(count):
            record = {
                "project_id":   project_id,
                "entry_type":   random.choice(["progress", "photo", "milestone", "note", "issue", "solution"]),
                "title":        rs.simple_sentence(),
                "description":  rs.sentence() + "\n" + rs.sentence(),
                "photo_url":    random.choice(images),
                "created_by":   self.SESSION['user_id']
            }
            print(f"  - Adding project timeline entry: {record['title']}")
            self.supabase.table("project_timeline_entries").insert(record).execute()

    def add_component(self, project_id, count = 24):
        components = self.data['components']  
        vendors = self.data['ev_conversion_vendors']
        component_types = self.data['component_types']

        for _ in range(count):
            dt =  datetime.now() + timedelta(days=random.randint(-30, 30))
            record = {
                "project_id":           project_id,
                "component_name":       random.choice(components),
                "category":             random.choice(component_types),
                "vendor":               random.choice(vendors),
                "expected_delivery":    dt.isoformat(),
                "estimated_cost":       random.randint(100, 5000),
                "notes":                rs.simple_sentence(),
                "status":               random.choice(["ordered", "installed", "received", "tested"]),
                "model_number":         f"MDL-{random.randint(100,999)}",
            }

            print(f" ~ Adding Component entry: {record['component_name']}")
            self.supabase.table("project_components").insert(record).execute()
        
    def create_project(self, count = 10) -> str:
        e = json.load(open('car_dataset.json'))
        target_motors = self.data['target_motors']

        for _ in range(count):
            vehicle = random.choice(e)
            print(f"Creating project for vehicle: {vehicle['year']} {vehicle['make']} {vehicle['model']}")
            
            vehicle_make = vehicle['make']
            vehicle_model = vehicle['model']
            vehicle_year = vehicle['year']
            image_url = vehicle['hosted_url']
            new_project_name = f"{vehicle_year} {vehicle_make} {vehicle_model} ({random.randint(1000,9999)})"
            record = {
                "user_id":              self.SESSION['user_id'],
                "cluster_id":           os.getenv("TODO_CLUSTER_ID"),
                "project_title":        new_project_name,
                "vehicle_make":         vehicle_make,
                "vehicle_model":        vehicle_model,
                "vehicle_year":         vehicle_year,
                "vision_statement":     rs.simple_sentence() + " " + rs.simple_sentence() + " " + rs.simple_sentence(),
                "target_range":         random.randint(5, 100) * 10,
                "target_motor":         random.choice(target_motors),
                "target_battery_kwh":   random.randint(20, 200),
                "target_budget":        "$30K - $50K",
                "project_image_url":    image_url,
                "project_status":       random.choice(["Planning", "In Progress", "Completed", "On Hold"])
            }
            response = self.supabase.table("projects").insert(record).execute()
            project_id = response.data[0]['id']

            print(f"Created new project: {new_project_name} (ID: {project_id})")
            self.configure_project_phases(project_id)
            self.add_component(project_id)
            self.add_project_timeline_entries(new_project_name, project_id)
            self.create_conversion_phases(project_id)
        return project_id

    def create_conversion_phases(self, project_id):
        phases = self.data['project_phases']        
        i:int = 0
        for phase in phases:
            i += 1 
            record = {
                "phase_name":   phase['title'],
                "description":  phase['description'],
                "project_id":   project_id,
                "phase_order":  i,
                "status":       random.choice(["pending", "in_progress", "completed"])
            }
            print(f"  - Adding conversion phase: {phase['title']}")
            r = self.supabase.table("project_phases").insert(record).execute()

            for each_task in phase['subtasks']:
                task_record = {
                    "task_name":        each_task,
                    "phase_id":         r.data[0]['id'],
                    "status":           random.choice(["pending", "completed"]),
                    "priority":         random.choice(["low", "medium", "high"]),
                    "estimated_hours":  random.randint(1, 20),
                    "task_order":       phase['subtasks'].index(each_task) + 1
                }
                print(f"    - Adding conversion task: {each_task}")
                self.supabase.table("project_tasks").insert(task_record).execute()
        pass


    def __init__(self, config:dict ):    
        from dotenv import load_dotenv
        load_dotenv()   
        self.supabase_url = os.getenv("SUPABASE_URL") 
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        self.data = json.load(open('lists.json'))

        response = self.supabase.auth.sign_in_with_password({        
            "email":   os.getenv("ELCTROMOTIVE_USER"),
            "password": os.getenv("ELCTROMOTIVE_PASSWORD")
        })
        self.SESSION = config
        self.SESSION['user_id'] = response.user.id
        self.SESSION['BearerToken'] = response.session.access_token