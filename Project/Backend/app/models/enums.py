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

class VerificationStatus(str, Enum):
    NOT_REQUIRED = "not_required"  # staff accounts created by an admin
    PENDING = "pending"            # citizen registered, waiting for an officer
    VERIFIED = "verified"          # officer approved, citizen may log in
    REJECTED = "rejected"          # officer rejected, citizen may re-apply


class ComplaintStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REGISTERED = "registered"  # approved: an FIR now exists for this complaint
    REJECTED = "rejected"


class FIRStatus(str, Enum):
    REGISTERED = "registered"
    ASSIGNED = "assigned"
    INVESTIGATION_IN_PROGRESS = "investigation_in_progress"
    PENDING_REVIEW = "pending_review"
    CLOSED = "closed"


# Which status changes are legal. The workflow code consults these tables
# before it changes anything, so no endpoint can ever skip a stage.
COMPLAINT_TRANSITIONS: dict[ComplaintStatus, set[ComplaintStatus]] = {
    ComplaintStatus.SUBMITTED: {ComplaintStatus.UNDER_REVIEW, ComplaintStatus.REJECTED},
    ComplaintStatus.UNDER_REVIEW: {ComplaintStatus.REGISTERED, ComplaintStatus.REJECTED},
    ComplaintStatus.REGISTERED: set(),
    ComplaintStatus.REJECTED: set(),
}

FIR_TRANSITIONS: dict[FIRStatus, set[FIRStatus]] = {
    FIRStatus.REGISTERED: {FIRStatus.ASSIGNED},
    FIRStatus.ASSIGNED: {FIRStatus.ASSIGNED, FIRStatus.INVESTIGATION_IN_PROGRESS},  # ASSIGNED -> ASSIGNED = re-assign
    FIRStatus.INVESTIGATION_IN_PROGRESS: {FIRStatus.PENDING_REVIEW},
    FIRStatus.PENDING_REVIEW: {FIRStatus.CLOSED, FIRStatus.INVESTIGATION_IN_PROGRESS},
    FIRStatus.CLOSED: set(),
}
