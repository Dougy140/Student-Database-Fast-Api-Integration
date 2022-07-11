import os 
import time 
import cv2
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import List
from typing import Optional
from fastapi import FastAPI, Request
from fastapi import FastAPI, APIRouter, Body, HTTPException
from pydantic.types import UUID4
from uuid import UUID
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Any, Callable
from bson.objectid import ObjectId  
import uuid
cred = credentials.Certificate('key.json')

firebase_admin.initialize_app(cred)

db = firestore.client()

class StudentSchema(BaseModel):
	fullname: str = Field(...)
	reg_no: str = Field(...)
	course: Optional[str] = Field(None)
	pics: list = Field([])
	embeddings: list = Field([])
	augmentations: list = Field([])

	class Config:
		schema_extra = {
			"example":{
				"fullname":"Douglas Maina",
				"reg_no":"scm211-0756/2018",
				"course":"Bsc Maths and Computer science",
				"pics":["example.jpg"],
				"embeddings":[],
				"augmentations":[]
			}

		}

class StudentCreate(StudentSchema):
	id = uuid.uuid4()
	class config:
		schema_extra = {
		"example":{
		"fullname":"Douglas Maina",
		"reg_no":"scm211-0756/2018",
		"pics":["example.jpg"],
		"embeddings":[],
		"augmentations":[]
		}
		}

      
class StudentUpdate(BaseModel):
	fullname: Optional[str]
	reg_no: Optional[str]
	course: Optional[str]
	pics: Optional[list]
	embeddings: Optional[list]
	augmentations: Optional[list]

	class config:
		schema_extra={
			"example":{
				"fullname":"Douglas Maina",
				"reg_no":"scm211-0756/2018",
				"course":"Bsc Mathematics and computer science",
				"pics":["example.jpg"],
				"embeddings":[],
				"augmentations":[]
			}
		}
class Student(StudentSchema):
	class Config:
		orm_mode = True




##dATABASE

 
class StudentSchemaFirestore:

	collection_name = "student2_collections"


	def create(self, student_create: StudentCreate) -> dict:
		data = student_create.dict()

		data['id'] = str(data['id'])
		doc_reference = db.collection(self.collection_name).document(str(student_create.id))
		doc_reference.set(data)
		return self.get(student_create.id)

	def get(self, id: UUID) -> Student:
		doc_reference = db.collection(self.collection_name).document(str(id))
		doc = doc_reference.get()
		if doc.exists:
			return Student(**doc.to_dict())
		return

	def list(self) -> List[Student]:
		students_ref = db.collection(self.collection_name)
		return[
			Student(**doc.get().to_dict())
			for doc in students_ref.list_documents()
			if doc.get().to_dict()
		]


	def update(self, id:UUID, student_update: StudentUpdate) -> Student:
		data = student_update.dict()
		doc_reference = db.collection(self.collection_name).document(str(id))
		doc_reference.update(data)
		return self.get(id)

	def delete(self, id: UUID) -> None:
		db.collection(self.collection_name).document(str(id)).delete() 

##DAO
student_path = StudentSchemaFirestore()

class StudentService:
	def create_student(self, student_create:StudentCreate) -> Student:
		return student_path.create(student_create)

	def get_student(self, id: UUID) -> Student:
		return student_path.get(id)

	def list_students(self) -> List[Student]:
		return student_path.list()

	def update_student(self, id: UUID, student_update: StudentUpdate) -> Student:
		return student_path.update(id, student_update)

	def delete_student(self, id: UUID) -> None:
		return student_path.delete(id) 

##ROUTERS
app = FastAPI()
#router = APIRouter()
student_service = StudentService()

@app.post("/students/{id}", response_model= Student, tags=['student'])
def create_student(student_create: StudentCreate = Body(...)) -> Student:
	return student_service.create_student(student_create)

@app.get("/students/{id}", response_model=Student, tags=["Student"])
def get_student(id: UUID4) -> Student:
	student = student_service.get_student(id)
	if not student:
		raise HTTPException(status_code = 404, detail = "Student not found")

	return student

@app.get("/students", response_model=List[Student], tags=['student'])
def list_students() -> List[Student]:
	students = student_service.list_students()
	if not students:
		raise HTTPException(status_code=404, detail='students not found')
	return students

@app.put("/students/{id}", response_model=Student,tags=['student'])
def update_student(id:UUID4, student_update: StudentUpdate )-> Student:
	student = student_service.get_student(id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	return student_service.update_student(id, student_update)


@app.delete("/students/{id}", response_model =  Student, tags=['student'])
def delete_student(id: UUID4) -> Student:
	student = student_service.get_student(id)
	if not student:
		raise HTTPException(status_code=404, detail='student not found.')

	return student_service.delete_student(id)




  