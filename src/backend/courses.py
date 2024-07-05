from enum import Enum

from pydantic import BaseModel

from src.backend.backend import Backend


class CourseSnapshotStatus(Enum):
    NOT_DOWNLOADED = "NOT_DOWNLOADED"
    DOWNLOADED = "DOWNLOADED"
    GENERATED_HTML = "GENERATED_HTML"


class CoursesProgressStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    DOWNLOADED_COURSES_LIST = "DOWNLOADED_COURSES_LIST"
    GENERATED_INDEX_FILE = "GENERATED_INDEX_FILE"


class CoursesSnapshot(BaseModel):
    status: CoursesProgressStatus
    courses_status: dict[str, CourseSnapshotStatus]

    def is_done(self) -> bool:
        return self.status == CourseSnapshotStatus.GENERATED_HTML

    def progress(self) -> tuple[str, int]:
        match self.status:
            case CoursesProgressStatus.NOT_STARTED:
                return "Starting...", 0
            case CoursesProgressStatus.DOWNLOADED_COURSES_LIST:
                return "Downloaded list of courses", 10
            case CoursesProgressStatus.GENERATED_INDEX_FILE:
                n_not_downloaded = sum(
                    1 for status in self.courses_status.values() if status == CourseSnapshotStatus.NOT_DOWNLOADED)
                n_downloaded = sum(
                    1 for status in self.courses_status.values() if status == CourseSnapshotStatus.DOWNLOADED)
                n_generated_html = sum(
                    1 for status in self.courses_status.values() if status == CourseSnapshotStatus.GENERATED_HTML)
                return (
                f"Downloading {n_not_downloaded}, Building {n_downloaded}, Done {n_generated_html} (out of {len(self.courses_status)})",
                int(90 * (
                        sum(
                            {
                                CourseSnapshotStatus.NOT_DOWNLOADED: 0,
                                CourseSnapshotStatus.DOWNLOADED: 1,
                                CourseSnapshotStatus.GENERATED_HTML: 2
                            }[course_status]
                            for course_status in self.courses_status.values()
                            if course_status == CourseSnapshotStatus.GENERATED_HTML
                        )
                        / (len(self.courses_status) * 2)
                )))
            case CoursesProgressStatus.GENERATED_INDEX_FILE:
                return "Done", 100
            case _:
                raise NotImplementedError


class CoursesBackend(Backend[CoursesSnapshot]):
    def start(self, snapshot: CoursesSnapshot | None = None):
        if snapshot is None:
            snapshot = CoursesSnapshot(
                status=CoursesProgressStatus.NOT_STARTED,
                courses_status={},
            )

        while not snapshot.is_done():
            snapshot = self._make_step(snapshot)
            self.savepoint_callback(snapshot)
            self.progress_callback(*snapshot.progress())

    def _make_step(self, snapshot: CoursesSnapshot) -> CoursesSnapshot:
        return snapshot
