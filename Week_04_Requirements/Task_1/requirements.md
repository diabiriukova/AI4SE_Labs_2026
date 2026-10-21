# Software Requirements

This document contains the accepted requirements and rejected or unresolved candidates produced from the configured source corpus.

## Priority scale

- **Must** — Required for the system to be acceptable; without it, a core objective fails.
- **Should** — Important and expected, but a justified implementation workaround is possible.
- **Could** — Useful enhancement that may be deferred without blocking acceptance.
- **Won't** — Explicitly out of scope for this release; retain it for traceability.

## Accepted requirements

### REQ-001: Support for Library Consortium

**Priority:** Must

The system must support a library consortium with 286 locations, 17 million annual circulations, and purchasing/processing over 900,000 items per year. It is highly desirable that searches and reports can be processed during open hours without disrupting other system functions.

**Source documents:** `early_draft_srs_galecia.txt`

### REQ-002: Operating System Compatibility

**Priority:** Must

The system must operate on a Linux or Solaris server environment to ensure compatibility with existing infrastructure and support for the library's operational needs.

**Source documents:** `early_draft_srs_galecia.txt`

### REQ-003: Web Browser Accessibility

**Priority:** Must

The system must be accessible through a web browser or a Windows-compatible client, ensuring that library staff can access the system from various devices and locations.

**Source documents:** `early_draft_srs_galecia.txt`

### REQ-004: Accessibility Compliance

**Priority:** Must

The system must be accessible with screen-reading software, screen-magnification software, and other assistive technology programs designed to increase accessibility, complying with Section 508 requirements.

**Source documents:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`

### REQ-005: Relational Database Requirement

**Priority:** Must

The system must use a fully relational database back-end to support complex queries and maintain data integrity across various reporting functionalities.

**Source documents:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`

### REQ-006: Development and Training Environment

**Priority:** Must

The system must provide a separate development and training environment to allow for testing and training without affecting the production environment.

**Source documents:** `interview_sysadmin_2009-05-10.txt`

### REQ-007: Management Processes Support

**Priority:** Must

The system must support the needs of a large, multiple-system library consortium, specifically one with 286 locations and 17 million annual circulations. It is essential that searches and reports can be processed during open hours without disrupting other system functions, ensuring that report generation does not slow down the circulation client.

**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`

### REQ-008: User-Friendly Query Tool

**Priority:** Should

The system should provide a user-friendly interface for designing queries against all record types, allowing staff to select fields, values, and use Boolean operators for complex queries.

**Source documents:** `early_draft_srs_galecia.txt`

### REQ-009: Report Writer Interface

**Priority:** Should

The system should include a report writer interface that allows staff to create custom reports using a web-based interface, featuring drag-and-drop field selection and basic filtering and sorting capabilities.

**Source documents:** `evergreen_reference_2009.txt`

### REQ-010: Canned Reports

**Priority:** Should

The system should provide pre-defined reports for common library functions, such as circulation counts and patron statistics, to facilitate quick access to essential data.

**Source documents:** `evergreen_reference_2009.txt`

### REQ-011: Report Scheduling

**Priority:** Should

The system should allow reports to be scheduled to run at regular intervals, such as daily, weekly, or monthly, to automate reporting processes and reduce manual workload.

**Source documents:** `evergreen_reference_2009.txt`

### REQ-012: Fine-Grained Permissions

**Priority:** Should

The system should provide distinct, fine-grained permission levels that limit who can create and clone reports, ensuring that sensitive data is protected and access is controlled.

**Source documents:** `evergreen_reference_2009.txt`

### REQ-013: Report Queue Visibility

**Priority:** Should

The system should provide visibility into the report queue, allowing staff to see where their report is in the queue of reports waiting to run.

**Source documents:** `evergreen_reference_2009.txt`

### REQ-014: Multiple Output Formats

**Priority:** Must

The system must support multiple output formats, including Excel, CSV, and HTML. This flexibility is necessary to accommodate different user needs and preferences for data presentation.

**Source documents:** `survey_results_2009.txt`

### REQ-015: Email Delivery of Reports

**Priority:** Should

The system should allow for the email delivery of reports. This feature enhances accessibility and ensures that users can receive reports directly in their inbox.

**Source documents:** `survey_results_2009.txt`

### REQ-016: Recurring Reports Scheduling

**Priority:** Should

The system should allow users to schedule recurring reports. This feature is beneficial for automating regular reporting tasks and ensuring timely access to important data.

**Source documents:** `survey_results_2009.txt`

### REQ-017: Real-Time Reporting

**Priority:** Should

The system should support real-time reporting for busy periods. This capability is essential for libraries to quickly assess current usage and make informed decisions.

**Source documents:** `survey_results_2009.txt`

### REQ-018: Report Cancellation

**Priority:** Should

The system should allow users to cancel a scheduled or running report. This feature is important for managing resources effectively and responding to changing needs.

**Source documents:** `survey_results_2009.txt`

### REQ-019: Null Handling

**Priority:** Should

The system should ensure that all nulls and blank fields are included in the results. This requirement is crucial for accurate data reporting and analysis.

**Source documents:** `survey_results_2009.txt`

### REQ-020: Survey Filtering

**Priority:** Should

The system should allow filtering by survey name rather than survey ID. This feature enhances usability and makes it easier for users to access relevant data.

**Source documents:** `survey_results_2009.txt`

### REQ-021: Snapshot Bills Report

**Priority:** Should

The system should provide a snapshot bills report going back in time. This feature is important for libraries to track financial transactions and analyze historical billing data.

**Source documents:** `survey_results_2009.txt`

### REQ-022: Last Circulation Date on Item Reports

**Priority:** Should

The system should allow users to indicate the last circulation date on item reports. This information is valuable for libraries to assess the usage of their collections.

**Source documents:** `survey_results_2009.txt`

### REQ-023: Check-in Date/Time Exclusion of Renewals

**Priority:** Should

The system should ensure that check-in date/time does not include renewals. This requirement is important for accurately tracking item usage and circulation statistics.

**Source documents:** `survey_results_2009.txt`

## Blacklist

### Candidate 1

**Candidate:** Support for Library Consortium
**Reason:** This requirement is essential and not conflicting; it is included in the main requirements.
**Source documents:** `early_draft_srs_galecia.txt`

### Candidate 2

**Candidate:** Operating System Compatibility
**Reason:** This requirement is fundamental and appears multiple times with consistent details; it is included in the main requirements.
**Source documents:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Candidate 3

**Candidate:** Web Browser Accessibility
**Reason:** This requirement is critical and duplicated; it is included in the main requirements.
**Source documents:** `early_draft_srs_galecia.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Candidate 4

**Candidate:** Accessibility Compliance
**Reason:** This requirement is duplicated with similar intent; it is included in the main requirements.
**Source documents:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Candidate 5

**Candidate:** Relational Database Requirement
**Reason:** This requirement is duplicated with consistent details; it is included in the main requirements.
**Source documents:** `early_draft_srs_galecia.txt`, `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### Candidate 6

**Candidate:** Development and Training Environment
**Reason:** This requirement appears multiple times with similar details; it is included in the main requirements.
**Source documents:** `interview_sysadmin_2009-05-10.txt`, `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Candidate 7

**Candidate:** Management Processes Support
**Reason:** This requirement is duplicated with similar details; it is included in the main requirements.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Candidate 8

**Candidate:** Report Queue Visibility
**Reason:** This requirement is duplicated; it is included in the main requirements.
**Source documents:** `evergreen_reference_2009.txt`, `survey_results_2009.txt`

### Candidate 9

**Candidate:** High-Level Process Descriptions
**Reason:** This requirement is duplicated; it is included in the main requirements.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Candidate 10

**Candidate:** Online Help System
**Reason:** This requirement is duplicated; it is included in the main requirements.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`

### Candidate 11

**Candidate:** Transaction Data Archiving
**Reason:** Not explicitly covered by any Requirement in the provided REQ list.
**Source documents:** `early_draft_srs_galecia.txt`

### Candidate 12

**Candidate:** Missing and Damaged Items Report
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `interview_cataloging_2009-05-08.txt`

### Candidate 13

**Candidate:** In-Transit Items Report
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `interview_cataloging_2009-05-08.txt`

### Candidate 14

**Candidate:** Last Copy Report
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `interview_cataloging_2009-05-08.txt`

### Candidate 15

**Candidate:** Data Quality Reports
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `interview_cataloging_2009-05-08.txt`

### Candidate 16

**Candidate:** Demographic Statistics
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `survey_results_2009.txt`

### Candidate 17

**Candidate:** Report Template Creation
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `survey_results_2009.txt`

### Candidate 18

**Candidate:** Help System
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `interview_sysadmin_2009-05-10.txt`

### Candidate 19

**Candidate:** Role-Based Access Control
**Reason:** Terminology differs from 'Fine-Grained Permissions' (REQ-012); concept overlaps but not a direct one-to-one match.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### Candidate 20

**Candidate:** OPAC Functionality Separation
**Reason:** Not covered by any Requirement in the provided REQ list; separate OPAC constraint appears only in candidate.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### Candidate 21

**Candidate:** Data Specifications Documentation
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### Candidate 22

**Candidate:** High-Level Process Descriptions
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### Candidate 23

**Candidate:** Online Help System
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### Candidate 24

**Candidate:** Error Reporting and Feedback
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

### Candidate 25

**Candidate:** Transaction History Maintenance
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `survey_results_2009.txt`

### Candidate 26

**Candidate:** Grouping Transactions
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `survey_results_2009.txt`

### Candidate 27

**Candidate:** Detailed Check-in and Check-out Reporting
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `survey_results_2009.txt`

### Candidate 28

**Candidate:** Holds Reporting
**Reason:** Not covered by any Requirement in the provided REQ list.
**Source documents:** `survey_results_2009.txt`

### Candidate 29

**Candidate:** HTML Compliance
**Reason:** Candidate includes HTML compliance; not present as a Requirement; terminology aligns with HTML-related considerations but not a listed REQ.
**Source documents:** `meeting_minutes/meeting_2009-07-20_minutes.txt`, `meeting_tech_subcommittee_2009-06-30.txt`

## Processing summary

- **Quality review passed:** True
- **Refinement iterations:** 1
- **Accepted requirements:** 23
- **Blacklisted candidates:** 29
- **Quality review issues:** Redundant/overlapping requirements: REQ-001 and REQ-007 both state large library consortium scope and non-disruptive search/report processing during open hours; consider consolidating to avoid duplicates.; Terminology gaps: Some candidate items use alternative terminology (e.g., 'Role-Based Access Control') that do not map one-to-one to requirements (e.g., 'Fine-Grained Permissions'); normalization needed to ensure consistent terminology across documentation.; Unmapped candidates present in the candidate set but not tied to any requirement (potential scope drift): examples include 'Transaction Data Archiving', 'Missing and Damaged Items Report', 'In-Transit Items Report', 'Last Copy Report', 'Data Quality Reports', 'Demographic Statistics', 'Report Template Creation', 'Help System', 'OPAC Functionality Separation', 'Data Specifications Documentation', 'High-Level Process Descriptions', 'Online Help System', 'Error Reporting and Feedback', 'Transaction History Maintenance', 'Grouping Transactions', 'Detailed Check-in and Check-out Reporting', 'Holds Reporting', 'HTML Compliance'.; HTML Compliance and related HTML/CSS/UX specifics appear in candidates but are not explicitly present in the requirements set; ensure alignment or remove extraneous items to avoid confusion.; Some candidate items imply capabilities (e.g., 'Report Template Creation', 'Data Specifications Documentation', 'High-Level Process Descriptions', 'Online Help System') that are not directly requested in the Requirements list; consider whether these should be formal REQ items or clearly scoped as out-of-scope.
