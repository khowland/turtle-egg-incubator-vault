-- IMMUTABLE SCHEMA DUMP
-- Generated: 2026-05-14 12:14:51.228980

-- Table: bin
CREATE TABLE public.bin (
    bin_date date DEFAULT CURRENT_DATE NOT NULL,
    total_eggs integer,
    is_deleted boolean DEFAULT false,
    target_total_weight_g numeric(10,2),
    shelf_location text,
    substrate text,
    total_water_added_season_ml numeric(10,2) DEFAULT 0.0,
    last_moisture_deficit_g numeric(10,2),
    bin_notes text,
    created_at timestamp with time zone DEFAULT now(),
    modified_at timestamp with time zone DEFAULT now(),
    bin_code text,
    bin_id bigint NOT NULL,
    intake_id bigint,
    created_by_session bigint,
    updated_by_session bigint,
    deleted_by_session bigint,
    created_by_id bigint,
    modified_by_id bigint,
    session_id bigint,
    CONSTRAINT bin_intake_fkey FOREIGN KEY (intake_id) REFERENCES intake(intake_id),
    CONSTRAINT bin_observer_fkey FOREIGN KEY (created_by_id) REFERENCES observer(observer_id),
    CONSTRAINT bin_pkey PRIMARY KEY (bin_id),
    CONSTRAINT bin_session_fkey FOREIGN KEY (session_id) REFERENCES session_log(session_id),
    CONSTRAINT bin_total_eggs_check CHECK ((total_eggs <= 300)),
    CONSTRAINT unique_bin_code UNIQUE (bin_code)
);

-- Table: bin_observation
CREATE TABLE public.bin_observation (
    timestamp timestamp with time zone DEFAULT now(),
    observer_name text NOT NULL,
    incubator_temp_f numeric,
    humidity numeric,
    observation_notes text,
    is_deleted boolean DEFAULT false,
    bin_weight_g numeric(10,2),
    water_added_ml numeric(10,2),
    env_notes text,
    sub_stage_code text,
    modified_at timestamp with time zone DEFAULT now(),
    bin_id bigint,
    created_at timestamp with time zone,
    obs_id text,
    bin_observation_id bigint NOT NULL,
    session_id bigint,
    deleted_by_session bigint,
    created_by_id bigint,
    modified_by_id bigint,
    observer_id bigint,
    CONSTRAINT bin_obs_bin_fkey FOREIGN KEY (bin_id) REFERENCES bin(bin_id),
    CONSTRAINT bin_obs_observer_fkey FOREIGN KEY (observer_id) REFERENCES observer(observer_id),
    CONSTRAINT bin_obs_session_fkey FOREIGN KEY (session_id) REFERENCES session_log(session_id),
    CONSTRAINT bin_observation_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES bin(bin_id),
    CONSTRAINT bin_observation_pkey PRIMARY KEY (bin_observation_id)
);

-- Table: biological_property
CREATE TABLE public.biological_property (
    property_label text NOT NULL,
    data_type text DEFAULT 'BOOLEAN'::text,
    is_critical boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    stage_id bigint,
    property_id bigint NOT NULL,
    CONSTRAINT biological_property_pkey PRIMARY KEY (property_id),
    CONSTRAINT biological_property_stage_id_fkey FOREIGN KEY (stage_id) REFERENCES development_stage(stage_id)
);

-- Table: development_stage
CREATE TABLE public.development_stage (
    label text NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    milestone text,
    sub_code text,
    ordinal_rank integer,
    egg_stage_code text,
    stage_id bigint NOT NULL,
    CONSTRAINT development_stage_pkey PRIMARY KEY (stage_id)
);

-- Table: egg
CREATE TABLE public.egg (
    physical_mark integer,
    current_stage text DEFAULT 'Intake'::text,
    status text DEFAULT 'Active'::text,
    is_deleted boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    intake_date date,
    egg_notes text,
    last_chalk integer,
    last_vasc boolean,
    last_molding integer DEFAULT 0,
    last_leaking integer DEFAULT 0,
    last_dented integer DEFAULT 0,
    bin_id bigint,
    egg_code text,
    egg_id bigint NOT NULL,
    created_by_session bigint,
    updated_by_session bigint,
    deleted_by_session bigint,
    created_by_id bigint,
    modified_by_id bigint,
    session_id bigint,
    CONSTRAINT egg_bin_fkey FOREIGN KEY (bin_id) REFERENCES bin(bin_id),
    CONSTRAINT egg_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES bin(bin_id),
    CONSTRAINT egg_observer_fkey FOREIGN KEY (created_by_id) REFERENCES observer(observer_id),
    CONSTRAINT egg_pkey PRIMARY KEY (egg_id),
    CONSTRAINT egg_session_fkey FOREIGN KEY (session_id) REFERENCES session_log(session_id)
);

-- Table: egg_observation
CREATE TABLE public.egg_observation (
    egg_observation_id bigint NOT NULL,
    egg_observation_date timestamp with time zone DEFAULT now(),
    vascularity boolean,
    chalking integer,
    molding integer DEFAULT 0,
    leaking integer DEFAULT 0,
    observation_notes text,
    is_deleted boolean DEFAULT false,
    dented integer DEFAULT 0,
    discolored boolean DEFAULT false,
    moisture_deficit_g numeric(10,2),
    water_added_ml numeric(10,2),
    stage_at_observation text,
    void_reason text,
    sub_stage_code text,
    modified_at timestamp with time zone DEFAULT now(),
    bin_id bigint,
    created_at timestamp with time zone,
    session_id bigint,
    egg_id bigint,
    deleted_by_session bigint,
    created_by_id bigint,
    modified_by_id bigint,
    observer_id bigint,
    CONSTRAINT check_no_future_dates CHECK ((egg_observation_date <= CURRENT_DATE)),
    CONSTRAINT egg_obs_bin_fkey FOREIGN KEY (bin_id) REFERENCES bin(bin_id),
    CONSTRAINT egg_obs_egg_fkey FOREIGN KEY (egg_id) REFERENCES egg(egg_id),
    CONSTRAINT egg_obs_observer_fkey FOREIGN KEY (observer_id) REFERENCES observer(observer_id),
    CONSTRAINT egg_obs_session_fkey FOREIGN KEY (session_id) REFERENCES session_log(session_id),
    CONSTRAINT egg_observation_bin_id_fkey FOREIGN KEY (bin_id) REFERENCES bin(bin_id),
    CONSTRAINT eggobservation_chalking_check CHECK (((chalking >= 0) AND (chalking <= 2))),
    CONSTRAINT eggobservation_pkey PRIMARY KEY (egg_observation_id)
);

-- Table: hatchling_ledger
CREATE TABLE public.hatchling_ledger (
    hatch_date date DEFAULT CURRENT_DATE,
    hatch_weight_g numeric(10,2),
    incubation_duration_days integer,
    vitality_score text,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_deleted boolean DEFAULT false,
    hatchling_ledger_id bigint NOT NULL,
    egg_id bigint,
    intake_id bigint,
    session_id bigint,
    CONSTRAINT hatch_egg_fkey FOREIGN KEY (egg_id) REFERENCES egg(egg_id),
    CONSTRAINT hatch_intake_fkey FOREIGN KEY (intake_id) REFERENCES intake(intake_id),
    CONSTRAINT hatch_session_fkey FOREIGN KEY (session_id) REFERENCES session_log(session_id),
    CONSTRAINT hatchling_ledger_pkey PRIMARY KEY (hatchling_ledger_id)
);

-- Table: intake
CREATE TABLE public.intake (
    intake_name text NOT NULL,
    intake_date date DEFAULT CURRENT_DATE NOT NULL,
    condition text,
    notes text,
    is_deleted boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    finder_turtle_name text,
    intake_condition text,
    extraction_method text,
    discovery_location text,
    mother_weight_g numeric NOT NULL,
    clinical_metadata jsonb DEFAULT '{}'::jsonb,
    days_in_care numeric,
    intake_number integer,
    intake_id bigint NOT NULL,
    species_id bigint,
    created_by_session bigint,
    updated_by_session bigint,
    deleted_by_session bigint,
    created_by_id bigint,
    modified_by_id bigint,
    session_id bigint,
    CONSTRAINT intake_observer_fkey FOREIGN KEY (created_by_id) REFERENCES observer(observer_id),
    CONSTRAINT intake_pkey PRIMARY KEY (intake_id),
    CONSTRAINT intake_session_fkey FOREIGN KEY (session_id) REFERENCES session_log(session_id),
    CONSTRAINT intake_species_id_fkey FOREIGN KEY (species_id) REFERENCES species(species_id)
);

-- Table: observer
CREATE TABLE public.observer (
    display_name text NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    modified_at timestamp with time zone DEFAULT now(),
    observer_id bigint NOT NULL,
    CONSTRAINT observer_display_name_key UNIQUE (display_name),
    CONSTRAINT observer_pkey PRIMARY KEY (observer_id)
);

-- Table: session_log
CREATE TABLE public.session_log (
    user_name text NOT NULL,
    login_timestamp timestamp with time zone DEFAULT now(),
    user_agent text,
    modified_at timestamp with time zone,
    session_token text,
    session_id bigint NOT NULL,
    CONSTRAINT session_log_pkey PRIMARY KEY (session_id)
);

-- Table: species
CREATE TABLE public.species (
    common_name text NOT NULL,
    scientific_name text NOT NULL,
    incubation_min_days integer,
    incubation_max_days integer,
    optimal_temp_low numeric,
    optimal_temp_high numeric,
    vulnerability_status text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    intake_count integer DEFAULT 0,
    family text,
    is_subspecies boolean DEFAULT false,
    min_clutch_size integer,
    max_clutch_size integer,
    avg_egg_weight_grams numeric,
    shell_type text,
    pivot_temp_c numeric DEFAULT 28.5,
    species_code text,
    species_id bigint NOT NULL,
    CONSTRAINT species_common_name_key UNIQUE (common_name),
    CONSTRAINT species_pkey PRIMARY KEY (species_id),
    CONSTRAINT species_scientific_name_key UNIQUE (scientific_name)
);

-- Table: system_config
CREATE TABLE public.system_config (
    config_value text,
    description text,
    modified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    config_name text,
    config_key bigint NOT NULL,
    CONSTRAINT system_config_pkey PRIMARY KEY (config_key)
);

-- Table: system_log
CREATE TABLE public.system_log (
    system_log_id bigint NOT NULL,
    event_type text NOT NULL,
    event_message text,
    payload jsonb,
    timestamp timestamp with time zone DEFAULT now(),
    session_id bigint,
    observer_id bigint,
    CONSTRAINT sys_observer_fkey FOREIGN KEY (observer_id) REFERENCES observer(observer_id),
    CONSTRAINT sys_session_fkey FOREIGN KEY (session_id) REFERENCES session_log(session_id),
    CONSTRAINT systemlog_pkey PRIMARY KEY (system_log_id)
);
