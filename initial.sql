-- Database: dwd

-- DROP DATABASE IF EXISTS dwd;

CREATE DATABASE dwd
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_Germany.utf8'
    LC_CTYPE = 'English_Germany.utf8'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

GRANT TEMPORARY, CONNECT ON DATABASE dwd TO PUBLIC;

GRANT CONNECT ON DATABASE dwd TO dwd_writer;

GRANT ALL ON DATABASE dwd TO postgres;


-- Role: dwd_writer
-- DROP ROLE IF EXISTS dwd_writer;

CREATE ROLE dwd_writer WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  NOBYPASSRLS
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:R6AyvhqpV5926a3I5aAWMQ==$2VnDnPOiYiGjO05TtHMc/7bKqSW7guZlTN08mn01FMc=:XPvQN1dRV0qYW/W0P9Bz80ybFaOIZwPQ0qp9Dsq/uhw=';


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
    temperature_published_timestamp timestamp(0) without time zone,
    CONSTRAINT station_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.station
    OWNER to postgres;

REVOKE ALL ON TABLE public.station FROM dwd_writer;

GRANT INSERT, SELECT, UPDATE ON TABLE public.station TO dwd_writer;

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

REVOKE ALL ON TABLE public.temperature FROM dwd_writer;

GRANT INSERT, SELECT, UPDATE ON TABLE public.temperature TO dwd_writer;

GRANT ALL ON TABLE public.temperature TO postgres;
