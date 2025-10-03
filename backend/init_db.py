from models.database import Base, engine, SessionLocal
from models import job, candidate
from models.job import Job

def init():
    # Tạo bảng trong DB
    print("📦 Creating tables...")
    Base.metadata.create_all(bind=engine)

    # Thêm dữ liệu mẫu
    db = SessionLocal()
    new_job = Job(
        title="Python Developer",
        company="ABC Corp",
        description="Làm việc với FastAPI",
        location="Hanoi",
        skills="['Python','FastAPI']"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    print(f"✅ Inserted sample job with id {new_job.id}")

if __name__ == "__main__":
    init()
