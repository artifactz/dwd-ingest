-- Table: public.station

-- DROP TABLE IF EXISTS public.station;

CREATE TABLE IF NOT EXISTS public.station
(
    id integer NOT NULL,
    date_from timestamp(0) without time zone,
    date_to timestamp(0) without time zone,
    altitude_m smallint,
    latitude_deg real,
    longitude_deg real,
    name character varying(80) COLLATE pg_catalog."default",
    region character varying(80) COLLATE pg_catalog."default",
    timestamp_added timestamp(3) with time zone,
    temperature_now_published_timestamp timestamp(0) without time zone,
    temperature_recent_published_timestamp timestamp(0) without time zone,
    CONSTRAINT station_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.station
    OWNER to postgres;

GRANT ALL ON TABLE public.station TO postgres;


-- Table: public.temperature

-- DROP TABLE IF EXISTS public.temperature;

CREATE TABLE IF NOT EXISTS public.temperature
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    station_id integer NOT NULL,
    "timestamp" timestamp(0) without time zone NOT NULL,
    quality smallint,
    pressure_hpa real,
    temperature_2m_c real,
    temperature_5cm_c real,
    humidity_percent real,
    dew_point_temperature_c real,
    timestamp_published timestamp(0) without time zone,
    timestamp_added timestamp(3) with time zone,
    CONSTRAINT temperature_pkey PRIMARY KEY (id),
    CONSTRAINT temperature_unique UNIQUE (station_id, "timestamp")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.temperature
    OWNER to postgres;

GRANT ALL ON TABLE public.temperature TO postgres;
