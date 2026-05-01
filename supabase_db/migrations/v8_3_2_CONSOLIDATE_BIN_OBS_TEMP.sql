-- CR-20260430-194500: Rename ambient_temp to incubator_temp_f on bin_observation
ALTER TABLE public.bin_observation RENAME COLUMN ambient_temp TO incubator_temp_f;
