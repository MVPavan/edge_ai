from sqlalchemy import (
    Column,
    Table,
    ForeignKey,
    Integer,
    String,
    Boolean,
    UniqueConstraint,
    TIMESTAMP,
    Enum,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy import text as sa_text

# from sqlalchemy.dialects.postgresql import UUID
from app.db.utils.db_inits import Base
from app.db.utils.strings import (
    fr_task_type_strings,
    task_status_strings,
    fr_status_strings,
)  # job_status_strings,

fr_status_enum = Enum(*fr_status_strings.values(), name="fr_status")
fr_task_type_enum = Enum(*fr_task_type_strings.values(), name="fr_task_type")
# job_status_enum = Enum(*job_status_strings.values(), name="job_status")
task_status_enum = Enum(*task_status_strings.values(), name="task_status")

populate = Table(
    "populate",
    Base.metadata,
    Column("fr_user", String, ForeignKey("frusers.eid")),
    Column("fr_group", String, ForeignKey("frgroups.groupUUID")),  # UUID(as_uuid=True)
)


class FRUsers(Base):
    id = Column(Integer, primary_key=True, index=True)
    eid = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    fr_group = relationship(
        "FRGroups", secondary=populate, back_populates="fr_user", lazy="dynamic"
    )
    fr_log = relationship("FRTasks", back_populates="fr_user_link")

    def __repr__(self):
        return "<User EID : {}>".format(self.eid)


class FRGroups(Base):
    groupUUID = Column(
        String, primary_key=True
    )  # server_default=sa_text("uuid_generate_v4()"))
    organization = Column(String, nullable=False)
    team = Column(String, nullable=False)
    fr_user = relationship("FRUsers", secondary=populate, back_populates="fr_group")
    fr_log = relationship("FRTasks", back_populates="fr_group_link")
    __table_args__ = (UniqueConstraint("organization", "team", name="_group_uc"),)


class FRTasks(Base):
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(fr_task_type_enum, nullable=False)
    logtime = Column(TIMESTAMP(timezone=True), server_default=func.now())
    task_status = Column(task_status_enum, nullable=False)
    fr_status = Column(fr_status_enum)
    mdb_oid = Column(String)
    fr_group = Column(String, ForeignKey("frgroups.groupUUID"))
    fr_user = Column(String, ForeignKey("frusers.eid"))
    fr_group_link = relationship("FRGroups", back_populates="fr_log")
    fr_user_link = relationship("FRUsers", back_populates="fr_log")  # , lazy="dynamic")


# class CameraJobs(Base):
#     id = Column(Integer, primary_key=True, index=True)
#     job_type = Column(fr_task_type_enum)
#     job_status = Column(job_status_enum)
#     job_tasks = relationship("JobTasks", back_populates="task_job")#, lazy="dynamic")
