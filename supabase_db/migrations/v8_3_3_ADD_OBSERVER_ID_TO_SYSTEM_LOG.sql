-- CR-20260430-194500: Add observer_id to system_log for audit traceability
ALTER TABLE public.system_log ADD COLUMN IF NOT EXISTS observer_id uuid;
ALTER TABLE public.system_log ADD CONSTRAINT system_log_observer_id_fkey
    FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);
