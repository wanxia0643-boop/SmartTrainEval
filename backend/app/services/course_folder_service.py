"""Course folder service."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course_folder import CourseFolder
from app.schemas.course_folder import CourseFolderCreate, CourseFolderUpdate


class CourseFolderService:
    """Course folder business logic."""

    def create(self, db: Session, data: CourseFolderCreate) -> CourseFolder:
        """Create a new folder."""
        folder = CourseFolder(**data.model_dump(exclude_unset=True))
        db.add(folder)
        db.commit()
        db.refresh(folder)
        return folder

    def get(self, db: Session, folder_id: int) -> CourseFolder | None:
        """Get folder by ID."""
        return db.query(CourseFolder).filter(
            CourseFolder.id == folder_id,
            CourseFolder.is_deleted == 0,
        ).first()

    def list(self, db: Session, teacher_id: int, page: int = 1, page_size: int = 50) -> tuple[list[CourseFolder], int]:
        """List folders for a teacher."""
        query = db.query(CourseFolder).filter(
            CourseFolder.teacher_id == teacher_id,
            CourseFolder.is_deleted == 0,
        ).order_by(CourseFolder.sort_order.asc(), CourseFolder.create_time.desc())

        total = query.count()
        folders = query.offset((page - 1) * page_size).limit(page_size).all()
        return folders, total

    def update(self, db: Session, folder: CourseFolder, data: CourseFolderUpdate) -> CourseFolder:
        """Update folder."""
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(folder, key, value)
        db.commit()
        db.refresh(folder)
        return folder

    def remove(self, db: Session, folder_id: int) -> bool:
        """Soft delete folder."""
        folder = self.get(db, folder_id)
        if not folder:
            return False
        folder.is_deleted = 1
        db.commit()
        return True


course_folder_service = CourseFolderService()
