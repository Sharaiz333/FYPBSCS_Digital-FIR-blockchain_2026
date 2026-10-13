// TEMPORARY MOCK DATA (synthetic). Replaced by a call to GET /stations
// once the backend has a stations endpoint.
export interface StationOption {
  id: string;
  name: string;
  location: string;
}

export const MOCK_STATIONS: StationOption[] = [
  { id: "mock-station-1", name: "Saddar Police Station", location: "Rawalpindi" },
  { id: "mock-station-2", name: "Abbottabad City Police Station", location: "Abbottabad" },
  { id: "mock-station-3", name: "Blue Area Police Station", location: "Islamabad" },
];
