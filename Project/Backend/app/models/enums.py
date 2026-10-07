from enum import Enum


class RoleName(str, Enum):
    # Matches FR-02 of the finalized proposal exactly. There is
    # deliberately no "SHO" role.
    CITIZEN = "citizen"
    POLICE_OFFICER = "police_officer"
    INVESTIGATING_OFFICER = "investigating_officer"
    SUPERVISORY_OFFICER = "supervisory_officer"
    AUDIT_REVIEW_OFFICER = "audit_review_officer"
    ADMIN = "admin"