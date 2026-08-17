-- Dummy data for local dev/testing only — never used in the actual demo.
INSERT INTO devices (device_id) VALUES ('device-a'), ('device-b')
ON CONFLICT DO NOTHING;

INSERT INTO records (id, device_id, local_counter, captured_at, location, survey_data, record_hash)
VALUES
  ('device-a:1', 'device-a', 1, now(),
   ST_SetSRID(ST_MakePoint(91.7362, 26.1445), 4326),
   '{"name": "Test Household 1", "household_size": 4, "notes": "dummy record"}',
   'dummyhash1'),
  ('device-b:1', 'device-b', 1, now(),
   ST_SetSRID(ST_MakePoint(91.8000, 26.2000), 4326),
   '{"name": "Test Household 2", "household_size": 2, "notes": "dummy record"}',
   'dummyhash2')
ON CONFLICT DO NOTHING;
