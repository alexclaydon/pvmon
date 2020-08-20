drop table clients, projects, records;

-- Disconnect all sessions other than those created by this client

SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid();

drop database pvprod;

-- Create the database

create database pvprod;

-- Switch the default connection to the new database, then set up the tables

create table if not exists clients (
    email varchar(100) primary key,
    first_name varchar(100) not null,
    last_name varchar(100) not null,
    is_active boolean not null default TRUE,
    create_date timestamptz not null default now()
);

create table if not exists projects (
    project_id serial,
    name varchar(100) not null,
    location varchar(100) default NULL,
    owner varchar(100) not null,
    create_date timestamptz not null default now(),
    primary key (project_id),
    foreign key (owner) references clients (email)
        on update cascade  -- Which means "update of clients will cascade to projects"
        on delete cascade  -- Which means "delete of clients will cascade to projects"
);

create table if not exists records (
    record_id serial,
    project_id bigint not null,
    sensor_num bigint not null default 1,
    sensor_id varchar(100) default NULL,
    observation_date timestamptz not null,
    total_prod_kwh bigint not null,
    total_sold_kwh bigint not null,
    sale_type varchar(100) not null check ( sale_type in ('x', 'y', 'z') ) default 'x',
    create_date timestamptz not null default now(),
    primary key (record_id),
    foreign key (project_id) references projects (project_id)
        on update cascade  -- Which means "update of projects will cascade to records"
        on delete cascade  -- Which means "delete of projects will cascade to records"
);

-- Populate the tables

INSERT INTO public.clients (email, first_name, last_name) VALUES ('admin@sanconjp.com', 'Stuart', 'Claydon');

INSERT INTO public.projects (name, owner) VALUES ('TEMP', 'admin@sanconjp.com');

-- Create views

CREATE VIEW all_products AS
select
       product_id,
       categories.name as "Category",
       manufacturers.name as "Manufacturer",
       products.name as "Product Name"
from products
       inner join categories on products.category_id = categories.category_id
       inner join manufacturers on products.manufacturer_id = manufacturers.manufacturer_id;


CREATE VIEW all_projects AS
select
    projects.project_id, name, location, owner,
    c.last_name,
    c.first_name,
    projects.create_date
from projects
    inner join clients c on projects.owner = c.email;

CREATE VIEW all_records AS
select
    records.record_id,
    records.project_id,
    records.sensor_num,
    records.sensor_id,
    records.observation_date,
    records.total_prod_kwh,
    records.total_sold_kwh,
    records.sale_type,
    records.create_date,
    p.name as "Project Name",
    c.last_name as "Owner Last Name",
    c.first_name as "Owner First Name"
from records
    inner join projects p on records.project_id = p.project_id
    inner join clients c on p.owner = c.email;