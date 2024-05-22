from faker import Faker
from .models import StudentID, Department, Student
import random

fake = Faker()

def seed_db(n=10) -> None:

    departments_objs = Department.objects.all()

    try:
            for i in range(0, n):
#                departments_objs = Department.objects.all()
                random_index = random.randint(0, len(departments_objs)-1)
                department = departments_objs[random_index]
                student_id = f'STU-0{random.randint(10, 999)}'
                name = fake.name()
                email = fake.email()
                age = random.randint(20, 40)
                address = fake.address()

                student_id_objs = StudentID.objects.create(student_id = student_id)
                student_objs= Student.objects.create(
                            department=department,
                            student_id = student_id_objs,
                            name = name,
                            email = email,
                            age = age,
                            address = address
                )

    except Exception as e:
           print(e)
