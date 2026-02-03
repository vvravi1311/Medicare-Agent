from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class Application(BaseModel):
    applicationId: Optional[str] = Field(..., description="Unique identifier for the application")
    receivedDate: Optional[str] = Field(..., description="Date the application was received (YYYY-MM-DD)")
    requestedEffectiveDate: Optional[str] = Field(..., description="Requested policy effective date")
    channel: Optional[Literal['AGENT','BROKER','DIRECT','MGA']] = Field(
        'AGENT', description="Sales channel through which the application was submitted"
    )
    carrierCode: Optional[str] = Field(
        None, description="Carrier identifier when supporting multiple carriers"
    )

class Applicant(BaseModel):
    firstName: Optional[str] = Field(None, description="Applicant's first name")
    lastName: Optional[str] = Field(None, description="Applicant's last name")
    dateOfBirth: Optional[str] = Field(..., description="Applicant's date of birth (YYYY-MM-DD)")
    state: Optional[str] = Field(..., description="State of residence (2-letter code)")
    zip: Optional[str] = Field(None, description="ZIP code of residence")
    tobaccoUse: Optional[bool] = Field(False, description="Whether the applicant uses tobacco")
    heightInches: Optional[int] = Field(None, description="Height in inches (used for BMI)")
    weightPounds: Optional[int] = Field(None, description="Weight in pounds (used for BMI)")
    partAEffectiveDate: Optional[str] = Field(..., description="Medicare Part A effective date")
    partBEffectiveDate: Optional[str] = Field(..., description="Medicare Part B effective date")
    currentlyOnMA: Optional[bool] = Field(
        False, description="Whether the applicant is currently enrolled in Medicare Advantage"
    )
    currentCoverageType: Optional[
        Literal['NONE','MEDIGAP','MA','EMPLOYER_GROUP','UNION','SELECT','OTHER']
    ] = Field('NONE', description="Type of existing coverage at time of application")
    medicareEligibilityDate: Optional[str] = Field(
        None, description="Date the applicant first became eligible for Medicare"
    )


class Coverage(BaseModel):
    requestedPlanLetter: Optional[Literal[
        'A','B','C','D','F','G','K','L','M','N','HDG','HDF'
    ]] = Field(..., description="Requested Medigap plan letter")
    replacingCoverage: Optional[bool] = Field(
        False, description="Whether the applicant is replacing existing coverage"
    )
    replacingCoverageType: Optional[
        Literal['NONE','MEDIGAP','MA','SELECT','EMPLOYER_GROUP','UNION','OTHER']
    ] = Field('NONE', description="Type of coverage being replaced")
    priorCreditableCoverageMonths: Optional[int] = Field(
        0, description="Months of prior creditable coverage"
    )
    gapSinceCreditableCoverageEndDays: Optional[int] = Field(
        0, description="Days without coverage since creditable coverage ended"
    )


class RecentHospitalization(BaseModel):
    occurred: Optional[bool] = Field(False, description="Whether a recent hospitalization occurred")
    dischargeDate: Optional[str] = Field(
        None, description="Date of hospital discharge, if applicable"
    )


class Health(BaseModel):
    conditions: Optional[List[str]] = Field(
        default_factory=list, description="List of disclosed medical conditions"
    )
    medications: Optional[str] = Field(
        default_factory=list, description="List of current medications"
    )
    oxygenUse: Optional[bool] = Field(False, description="Whether the applicant uses oxygen")
    adlAssistance: Optional[bool] = Field(
        False, description="Whether the applicant needs help with Activities of Daily Living"
    )
    recentHospitalization: Optional[RecentHospitalization] = Field(
        default_factory=RecentHospitalization,
        description="Details of any recent hospitalization"
    )


class GiEvent(BaseModel):
    type: Optional[Literal[
        'MA_PLAN_TERMINATION','MA_MOVE_OUT_OF_SERVICE_AREA','MA_TRIAL_RIGHT_WITHIN_12M',
        'EMPLOYER_GROUP_ENDING','MEDIGAP_INSOLVENCY','SELECT_MOVE_OUT_OF_AREA',
        'CARRIER_RULE_VIOLATION_OR_MISLEADING'
    ]] = Field(..., description="Type of Guaranteed Issue qualifying event")
    triggeringDate: Optional[str] = Field(..., description="Date the GI event occurred")


class EvaluateRequest(BaseModel):
    application: Optional[Application] = Field(..., description="Application metadata")
    applicant: Optional[Applicant] = Field(..., description="Applicant demographic and Medicare details")
    coverage: Optional[Coverage] = Field(..., description="Requested coverage information")
    giEvents: Optional[List[GiEvent]] = Field(
        default_factory=list, description="List of applicable GI events"
    )
    health: Optional[Health] = Field(
        default_factory=Health, description="Applicant health and medical information"
    )
    context: Optional[dict] = Field(
        default_factory=dict, description="Additional contextual data for evaluation"
    )


class Reason(BaseModel):
    code: Optional[str] = Field(..., description="Machine-readable reason code")
    message: Optional[str] = Field(..., description="Human-readable explanation")


class RuleAudit(BaseModel):
    ruleId: Optional[str] = Field(..., description="Identifier of the evaluated rule")
    outcome: Optional[Literal['FIRED','SKIPPED']] = Field(..., description="Rule evaluation outcome")
    details: Optional[str] = Field(None, description="Additional rule evaluation details")


class PlanRestrictions(BaseModel):
    allowedPlanLetters: Optional[List[str]] = Field(
        default_factory=list, description="Plans the applicant is eligible for"
    )
    disallowedPlanLetters: Optional[List[str]] = Field(
        default_factory=list, description="Plans the applicant is not eligible for"
    )
    notes: Optional[List[str]] = Field(default_factory=list, description="Additional notes")


class WaitingPeriod(BaseModel):
    applies: Optional[bool] = Field(False, description="Whether a waiting period applies")
    months: Optional[int] = Field(0, description="Length of the waiting period in months")
    reason: Optional[str] = Field(None, description="Explanation for the waiting period")


class RatingGuidance(BaseModel):
    class_: Optional[Literal['PREFERRED','STANDARD','RATED']] = Field(
        default=None, alias='class', description="Recommended rating class"
    )
    suggestedFactor: Optional[float] = Field(
        None, description="Suggested rating factor (e.g., 1.15 for 15% rate-up)"
    )


class EvaluateResponse(BaseModel):
    decisionId: Optional[str] = Field(..., description="Unique identifier for the evaluation")
    status: Optional[Literal['ACCEPT_NO_UW','ACCEPT_WITH_UW','DECLINE','PENDED']] = Field(
        ..., description="Final underwriting decision status"
    )
    underwritingRequired: Optional[bool] = Field(
        ..., description="Whether manual underwriting is required"
    )
    reasons: List[Reason] = Field(
        default_factory=list, description="Reasons supporting the decision"
    )
    planRestrictions: Optional[PlanRestrictions] = Field(
        default_factory=PlanRestrictions, description="Plan eligibility restrictions"
    )
    waitingPeriod: Optional[WaitingPeriod] = Field(
        default_factory=WaitingPeriod, description="Waiting period determination"
    )
    ratingGuidance: Optional[RatingGuidance] = Field(
        None, description="Recommended rating class and factor"
    )
    requestsForInformation: Optional[List[str]] = Field(
        default_factory=list, description="Additional information requested from applicant"
    )
    audit: Optional[dict] = Field(
        None, description="Full rule audit trail for transparency"
    )


class StateOverride(BaseModel):
    state: Optional[str] = Field(..., description="State code the override applies to")
    continuousGi: bool = Field(False, description="Whether the state allows continuous GI rights")
    birthdayOrAnniversarySwitching: Optional[dict] = Field(
        None, description="Rules for switching plans during birthday/anniversary windows"
    )
    under65Access: Optional[Literal['NONE','LIMITED','ANY_AVAILABLE']] = Field(
        None, description="Medigap access rules for applicants under age 65"
    )
    notes: List[str] = Field(default_factory=list, description="Additional state-specific notes")


class DeclineCondition(BaseModel):
    code: str = Field(..., description="Unique decline condition code")
    label: str = Field(..., description="Short label for the decline condition")
    description: Optional[str] = Field(None, description="Detailed explanation")


class GiScenario(BaseModel):
    code: str = Field(..., description="GI scenario code")
    description: str = Field(..., description="Description of the GI scenario")
    lookbackDaysDefault: int = Field(
        63, description="Default lookback window for GI eligibility"
    )
    planLettersPermitted: List[str] = Field(
        default_factory=list, description="Plans permitted under this GI scenario"
    )