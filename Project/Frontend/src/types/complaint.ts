// Shape of the "File a Complaint" form. Field names are camelCase here;
// when the backend Complaint endpoint exists (Stage 6) the service layer
// will map them to the API's snake_case field names.
export interface ComplaintFormValues {
  stationId: string;
  crimeCategory: string;
  incidentDateTime: string; // value of <input type="datetime-local">
  incidentLocation: string;
  description: string;
  suspectDetails: string; // optional
  witnessDetails: string; // optional
  complainantName: string;
  complainantCnic: string;
  complainantPhone: string;
  complainantAddress: string; // optional
}

export type ComplaintFormErrors = Partial<Record<keyof ComplaintFormValues, string>>;

export interface ComplaintSubmitResult {
  referenceNumber: string;
}